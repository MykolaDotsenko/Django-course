
# Information Flow and Request Lifecycles

This document defines the end-to-end flow of information through Cultural Currency Converter.

The goal is to make ownership, trust boundaries, cache behavior, failure modes and response semantics explicit before implementation.

---

# 1. Universal request lifecycle

~~~text
client
  ↓
edge / web server
  ↓
Django middleware
  ↓
transport validation
  ↓
application use case
  ↓
domain rules
  ↓
DB/cache/provider adapters as required
  ↓
explicit result or typed failure
  ↓
presentation mapping
  ↓
HTML or JSON
  ↓
client state update
~~~

Presentation never skips directly to an external provider.

---

# 2. Trust boundaries

## Client → Django

Untrusted:

- amount;
- currency/country codes;
- requested date;
- URL/query values;
- object IDs;
- API JSON;
- anonymous local-state sync payloads.

Actions:

- parse;
- validate syntax;
- normalize;
- authenticate;
- authorize.

## Django → external provider

Only validated identifiers become provider query parameters.

User input never controls the destination URL.

## External provider → Django

External JSON is untrusted.

Actions:

- HTTP status handling;
- schema validation;
- numeric/date parsing;
- pair/source consistency checks;
- normalization into domain values.

## Imported/editorial data → published data

Imported data is candidate data.

It requires:

- provenance;
- normalization;
- licence/rights handling when relevant;
- validation;
- editorial publication rules.

---

# 3. Current conversion — cold path

Example:

~~~text
POST /convert/
amount=100
base=EUR
quote=JPY
~~~

Flow:

~~~text
Django Form
  ↓
syntax validation
  ↓
ConverterSubmissionCommand
  ↓
run_converter_submission(...)
  ↓
currency metadata + current/historical quote use case
  ↓
application/domain validation
  ↓
base == quote?
  ├─ yes → local exact RateQuote(rate=1)
  └─ no
       ↓
semantic cache key
       ↓
fresh quote cache miss
       ↓
FrankfurterProvider.fetch_latest()
       ↓
validate + normalize RateQuote
       ↓
store normalized quote
       ↓
Decimal conversion
       ↓
ConversionResult
       ↓
HTML result + provenance
~~~

The provider does not calculate the final user amount.

---

# 4. Current conversion — hot cache path

~~~text
validated command
  ↓
semantic quote cache key
  ↓
fresh RateQuote hit
  ↓
no provider request
  ↓
Decimal conversion
  ↓
ConversionResult
~~~

Cache the reusable normalized quote rather than every amount/result combination.

One EUR/JPY quote can serve many amounts.

---

# 5. Provider failure with safe stale data

~~~text
fresh cache miss
  ↓
provider request
  ↓
timeout / upstream 5xx / invalid payload
  ↓
lookup same-semantics stale quote
  ├─ found
  │    ↓
  │ classify stale
  │    ↓
  │ Decimal conversion
  │    ↓
  │ StaleSuccess
  └─ absent
       ↓
       RateTemporarilyUnavailable
~~~

Stale quote identity includes:

- base;
- quote;
- provider policy;
- latest/historical mode.

Never reuse another pair.

---

# 6. HTTP 200 with invalid upstream payload

HTTP success is not domain success.

~~~text
provider returns 200
  ↓
schema/date/rate validation fails
  ↓
SourceDataInvalid
  ↓
structured provider error log
  ↓
safe stale fallback attempt
  ↓
stale-success or unavailable
~~~

No raw upstream exception or payload appears in the user response.

---

# 7. Same-currency fast path

Example:

~~~text
EUR → EUR
~~~

Flow:

~~~text
validate codes
  ↓
base == quote
  ↓
exact Decimal rate = 1
  ↓
calculate output locally
  ↓
return conversion
  ↓
optional country-specific context can still load
~~~

No external FX call is made.

---

# 8. Historical exact-date flow

Input:

~~~text
100 EUR → USD
requested date: 2016-06-15
~~~

Flow:

~~~text
parse date
  ↓
reject future date
  ↓
validate currency/date metadata
  ↓
historical cache lookup
  ↓ miss
  ↓
provider historical query
  ↓
normalize returned observation
  ↓
requested_date and effective_date preserved independently
  ↓
historical conversion
~~~

If both dates are equal, the UI may display them compactly, but the backend still stores them separately.

---

# 9. Weekend / missing historical observation

Example:

~~~text
requested: Sunday 1998-06-14
~~~

Flow:

~~~text
no exact observation
  ↓
HistoricalObservationPolicy
  ↓
latest available observation <= requested date
  ↓
gap within allowed policy?
  ├─ yes
  │   ↓
  │ effective_date = prior observation
  │ used_previous_observation = true
  │   ↓
  │ conversion
  └─ no
      ↓
      HistoricalObservationUnavailable
~~~

The user-selected date is never silently rewritten.

---

# 10. Historical out-of-coverage

~~~text
requested pair/date
  ↓
known lifecycle/coverage check
  ↓
impossible locally?
  ├─ yes → HistoricalOutOfCoverage
  └─ unknown → provider query
                 ↓
            normalize coverage result/error
~~~

When known, response may contain:

- earliest available date;
- latest available date;
- affected currency/provider context.

---

# 11. Historical country-currency suggestion

Example:

~~~text
country = FI
date = 1998
explicit currency = EUR
~~~

Flow:

~~~text
CountryCurrency.primary_for(FI, 1998)
  ↓
FIM
  ↓
explicit selection differs
  ↓
HistoricalCurrencySuggestion
  ↓
presentation:
"Finland used FIM on this date"
~~~

No automatic mutation.

---

# 12. Time-series/chart flow

~~~text
pair + period + grouping
  ↓
validate bounded range
  ↓
series cache lookup
  ↓ miss
  ↓
provider time-series request
  ↓
validate every observation
  ↓
normalize RateSeries
  ↓
cache
  ↓
derive summary:
  first / latest / high / low / selected
  ↓
HTML or JSON
~~~

Server controls data density.

Clients do not request arbitrary unlimited series.

---

# 13. Chart and historical conversion consistency

If the user requested 14 June but the valid observation is 12 June:

~~~text
requested date        14 Jun
effective observation 12 Jun
chart selected point  12 Jun
~~~

The chart may annotate the requested date, but it must not invent a 14 June observation.

---

# 14. Destination context flow

~~~text
destination country/city
  ↓
local PostgreSQL
  ↓
published CulturalProfile
  ↓
published/fresh-enough TypicalPrice rows
  ↓
provenance filters
  ↓
derive item equivalents
  ↓
DestinationContext
~~~

No external API call in the normal user request.

---

# 15. "What this buys" calculation flow

Given:

~~~text
converted amount = 17450 JPY
coffee = 500–650 JPY
~~~

Domain calculation:

~~~text
lower equivalent = amount / high price
upper equivalent = amount / low price
~~~

Presentation can round into a human-friendly range.

Templates do not perform the arithmetic.

---

# 16. Historical/current context temporal boundary

Historical mode does not automatically mix:

- old FX;
- current prices;
- current card/cash practice.

Default historical composition:

~~~text
historical conversion
historical chart
currency era
story/timeline
~~~

Current travel context is a separately labelled query/action. The web implementation loads it
only after explicit user intent; it never re-runs or rewrites the historical FX result.

---

# 17. Money story flow

~~~text
HistoricalConversion
  ↓
country/currency/date context
  ↓
currency-era lookup
  ↓
published StoryMoments
  ↓
currency transitions
  ↓
optional semantically-valid Then & Now
  ↓
deterministic StoryComposer
  ↓
StoryChapter[]
~~~

Story failure never changes the numeric conversion.

---

# 18. Story-fact selection flow

A StoryMoment must satisfy:

- published;
- relevant date interval;
- country/currency relevance;
- required provenance;
- verification policy;
- allowed category.

Then rank by:

- direct monetary relevance;
- temporal relevance;
- editorial relevance weight.

No filler chapter is generated to hit a desired length.

---

# 19. Country metadata import

~~~text
scheduler
  ↓
management command
  ↓
REST Countries adapter
  ↓
network fetch
  ↓
validate required full snapshot
  ↓
normalize CountryMetadataSnapshot[]
  ↓
calculate diff
  ↓
short transaction.atomic()
  ↓
upsert
  ↓
commit
  ↓
on_commit cache invalidation
  ↓
import summary
~~~

Network I/O completes before transaction starts.

---

# 20. Failed metadata import

Possible failures:

- timeout;
- authentication;
- quota;
- malformed response;
- suspiciously incomplete dataset.

Behavior:

~~~text
fetch/validation fails
  ↓
no write transaction
  ↓
existing local dataset remains
  ↓
command exits failure
  ↓
operational log/alert
~~~

Never interpret an upstream failure as an empty authoritative dataset.

---

# 21. Cultural-data ingestion

Example flow:

~~~text
explicit QID management command
  ↓
fixed Wikibase REST API endpoint + required User-Agent
  ↓
bounded Wikidata item response
  ↓
normalized candidate metadata
  ↓
StoryMoment status=needs_review
  ↓
human/source/date/causality verification
  ↓
approved
  ↓
explicit publish
~~~

No direct external-to-public pipeline.

---

# 22. Media ingestion

~~~text
media candidate
  ↓
extract canonical source
creator
licence
rights URI
attribution
  ↓
metadata complete?
  ├─ no → reject/not publishable
  └─ yes → editorial approval → publish
~~~

A remote image URL without rights metadata is not enough.

---

# 23. Anonymous web conversion

~~~text
GET /
  ↓
full server-rendered form

POST/HTMX conversion
  ↓
same Django form validation
  ↓
same application use case
  ↓
full page OR named HTML partial
~~~

If one URL can return full and HTMX representations, cache behavior varies on HX-Request.

---

# 24. Rapid HTMX updates

~~~text
request A: EUR → JPY
  ↓
user changes selection
  ↓
request B: EUR → AUD
  ↓
A becomes cancelled/obsolete
  ↓
B result fragment wins
~~~

Defense in depth:

- HTMX synchronization/cancellation;
- atomic result fragment contains its own pair/date labels;
- server result identity is never reconstructed from current browser fields.

---

# 25. Mobile online conversion

~~~text
screen input
  ↓
typed API call
  ↓
DRF serializer
  ↓
same quote_conversion use case
  ↓
ConversionResult
  ↓
API response decimal strings
  ↓
mobile validates expected contract
  ↓
persist authoritative snapshot to SQLite
  ↓
render
~~~

Mobile never calculates a substitute rate itself.

---

# 26. Mobile offline cached conversion

~~~text
requested exact semantic key
  ↓
network unavailable
  ↓
SQLite cache lookup
  ├─ exact match
  │    ↓
  │ OfflineCachedResult
  │ effective date + sync time visible
  └─ miss
       ↓
       OfflineUnavailable
~~~

No nearest-pair or nearest-currency fallback.

---

# 27. Mobile reconnect

~~~text
cached result remains visible
  ↓
network returns
  ↓
background/explicit refresh
  ↓
new request succeeds?
  ├─ yes → atomic replace + persist
  └─ no  → keep cached result
~~~

No blank loading state is required during refresh.

---

# 28. Anonymous favourite

Anonymous web favourite is browser-local.

Server conversion behavior is unaffected if localStorage is unavailable.

This state becomes a server concern only after explicit sign-in/import.

---

# 29. Authenticated favourite

~~~text
authenticate
  ↓
validate pair/context
  ↓
get_or_create
  ↓
database unique constraint
  ↓
canonical saved state
~~~

Repeated requests do not create duplicates. The persisted row is always selected and mutated
through the authenticated owner; a resource ID alone is never authorization.

---

# 30. Merge local favourites at sign-in

~~~text
client sends normalized set
  ↓
auth + input validation
  ↓
deduplicate input
  ↓
short transaction
  ↓
bulk upsert missing favourites
  ↓
commit
  ↓
return union
~~~

PR12A implements this as a bounded JSON web mutation: lexical validation and canonical
country/currency validation complete before the short write transaction, the user row is locked to
serialize competing merges, and the database unique constraint is the final duplicate barrier.

After a successful merge the browser removes only the merged local favourites. Recent history is
not included in this request and remains browser-local until PR12B defines an explicit policy.

---

# 31. Trip creation

~~~text
validate CreateTrip command
  ↓
obtain any external quote BEFORE transaction if needed
  ↓
transaction.atomic()
  ↓
create Trip
  ↓
create initial budget items
  ↓
commit
  ↓
on_commit side effects
~~~

No provider network call while a transaction is open.

---

# 32. Concurrent trip edit

When cross-device editing justifies optimistic concurrency:

~~~text
client version = 7
  ↓
update WHERE id=? AND version=7
  ├─ row updated → version 8
  └─ no row      → 409 Conflict
~~~

The client can then reload/reconcile.

Do not silently overwrite a newer version.

---

# 33. Delete user-owned object

~~~text
authenticated actor
  ↓
query constrained by actor ownership
  ↓
not found → 404
  ↓
delete → 204
~~~

Avoid leaking that an inaccessible object exists.

---

# 34. API throttling

~~~text
edge/platform abuse protection if present
  ↓
DRF fair-use throttle
  ↓
authentication / permissions
  ↓
use case
~~~

DRF throttling is not exact DDoS/security protection.

---

# 35. Countries/currencies mobile sync

~~~text
GET /api/v1/currencies/
  ↓
local PostgreSQL
  ↓
bounded normalized records
  ↓
HTTP validator candidate: ETag/Last-Modified
  ↓
mobile persists to SQLite
  ↓
offline local picker search
~~~

No runtime REST Countries request.

---

# 36. Web country/currency search

~~~text
search field
  ↓
HTMX local endpoint
  ↓
PostgreSQL search/filter
  ↓
historical/current mode filter
  ↓
HTML result rows
~~~

No API call per keystroke to an external source.

---

# 37. Liveness/readiness

Liveness:

~~~text
/health/live/
→ process can answer
~~~

Readiness:

~~~text
/health/ready/
→ critical config
→ PostgreSQL connectivity
~~~

Do not call optional/external providers.

---

# 38. Unknown exception

~~~text
exception
  ↓
request_id attached
  ↓
structured server log
  ↓
generic 500 response
~~~

API shape:

~~~json
{
  "code": "server_error",
  "detail": "An unexpected error occurred.",
  "retryable": true,
  "request_id": "..."
}
~~~

No stack trace or upstream detail to client.

---

# 39. Cache failure

~~~text
cache operation fails
  ↓
log
  ↓
continue DB/provider path where safe
~~~

Cache is not correctness-critical.

Do not return a wrong result merely because caching failed.

---

# 40. PostgreSQL failure

PostgreSQL is authoritative for local product state.

If unavailable:

- readiness fails;
- DB-backed requests fail safely;
- do not pretend stale cache is authoritative mutable state.

A future explicitly-designed limited FX-only mode would require separate product/operations approval.

---

# 41. Transaction rollback

~~~text
atomic
  ↓
write A
  ↓
write B violates constraint
  ↓
exception exits atomic
  ↓
rollback
  ↓
on_commit callbacks discarded
~~~

Database exceptions are caught around the transaction boundary, not hidden inside a broken transaction.

---

# 42. Cache invalidation after publish

~~~text
transaction
  ↓
publish/update durable record
  ↓
commit
  ↓
on_commit(invalidate affected keys)
~~~

Never expose uncommitted DB state through cache.

---

# 43. Source correction

~~~text
new verified source data
  ↓
normalize/compare
  ↓
durable update
  ↓
commit
  ↓
invalidate derived story/context cache
~~~

Historical content may still be corrected.

---

# 44. Provider-policy change

Changing from a blended provider policy to a pinned provider is not transparent configuration.

Required:

- ADR;
- new semantic cache namespace;
- attribution changes;
- fixtures/contracts;
- historical comparison review;
- no reuse of incompatible cache values.

---

# 45. Deployment

~~~text
dependency install
  ↓
frontend production build
  ↓
Django checks
  ↓
migration review/apply
  ↓
collectstatic
  ↓
start app
  ↓
readiness
~~~

Reference-data imports are separate from schema migration.

---

# 46. Post-deploy reference-data load

~~~text
deploy code/schema
  ↓
feature supports missing/not-yet-imported state
  ↓
run explicit import command
  ↓
validate
  ↓
write/publish local data
~~~

Deployment does not depend on third-party import API availability.

---

# 47. Information-flow invariants

1. Raw external JSON stops at the adapter boundary.
2. Forms/serializers stop at the presentation boundary.
3. Domain/use-case results contain no HTTP response objects.
4. Cache is never durable source of truth.
5. User input cannot select arbitrary server-side URLs.
6. Historical requested/effective dates never collapse.
7. Current cultural/pricing context never silently becomes historical.
8. Web and mobile use the same application/domain behavior.
9. Network I/O does not run while intentional DB locks/transactions are held.
10. Durable-write side effects execute after commit.
11. Stale data requires exact semantic cache identity.
12. Failure is represented explicitly, never with fake numeric data.


---

# 44. Implemented Money & culture request path

PR8 keeps story loading outside the conversion request:

successful conversion
→ render deterministic story URL
→ user explicitly opens Money & culture
→ GET /story/
→ validate country/currency/date/mode
→ read local CountryCurrency history + local PUBLISHED StoryMoment rows
→ deterministic StoryChapter[]
→ HTMX fragment OR full no-JS page

No Wikidata, Wikimedia, Europeana or AI provider call occurs in this request path.

Historical story selection excludes unpublished facts, undated facts and dated facts outside their reviewed temporal scope. Current storytelling can include reviewed past money-history moments. A composition exception produces a story-only unavailable state; it cannot invalidate or replace the already completed conversion.
