# Backend System Design

Research date: **2026-09-19**.

This document defines the target backend architecture for Cultural Currency Converter.

It is the high-level contract. Detailed request flows, consistency rules, failure handling, imports and scenario catalogs live in the companion backend documents.

---

# 1. Architecture north star

The backend is a **synchronous Django modular monolith** with explicit application/use-case boundaries and provider adapters.

The architecture optimizes for:

1. financial/data correctness;
2. transparent provenance;
3. graceful degradation;
4. low operational complexity;
5. testability;
6. clear ownership;
7. easy evolution into the React Native API without duplicating domain rules.

It deliberately does **not** optimize for:

- distributed-systems novelty;
- microservice count;
- maximum abstraction;
- asynchronous code percentage;
- event-driven architecture before there is an event-driven workload.

---

# 2. System context

```text
                           ┌──────────────────┐
                           │   Web browser    │
                           │ Django + HTMX UI │
                           └────────┬─────────┘
                                    │ HTML requests
                                    ▼
┌─────────────────┐       ┌───────────────────────┐       ┌─────────────────┐
│ React Native app│──────►│   Django monolith    │──────►│ Frankfurter v2  │
│ /api/v1         │ JSON  │                       │ HTTPS │ runtime FX only │
└─────────────────┘       │ presentation          │       └─────────────────┘
                          │ application/use cases │
                          │ domain rules          │
                          │ persistence/adapters  │
                          └───────┬──────┬────────┘
                                  │      │
                                  │      └───────────────┐
                                  ▼                      ▼
                         ┌────────────────┐      ┌─────────────────┐
                         │ PostgreSQL     │      │ Django cache    │
                         │ source of truth│      │ optimization    │
                         └────────────────┘      └─────────────────┘
                                  ▲
                                  │ imports/editorial workflows
              ┌───────────────────┼────────────────────────────┐
              │                   │                            │
        REST Countries         Wikidata/                  Eurostat /
                              Wikimedia /                 OECD /
                              Europeana                   World Bank
```

Only FX refresh is allowed to be a normal user-request-path external dependency by default.

Everything else should be local when the user needs it.

---

# 3. Runtime style: synchronous first

Core request handlers are synchronous Django views / DRF views.

Reasons:

- Django 5.2 transaction support remains synchronous;
- PostgreSQL transactions/row locks are important for future user-owned writes;
- only one normal runtime upstream call exists;
- a synchronous provider call with a hard timeout is operationally simpler;
- sync Django keeps middleware, ORM and error behavior straightforward.

Use a synchronous HTTP client in the Frankfurter adapter.

Do not mix sync/async request styles casually.

## Future async trigger

Reconsider async only when measured requirements appear, for example:

- multiple independent runtime upstreams that must run concurrently;
- long-lived streaming;
- WebSockets;
- high concurrent long-polling;
- another clearly measured I/O-bound path.

An async migration is an architecture decision, not a style preference.

---

# 4. Deployment protocol

Initial production baseline may use WSGI.

Do not require ASGI unless async behavior exists.

This keeps deployment conventional:

```text
reverse proxy / platform edge
          ↓
WSGI application server
          ↓
Django
```

If the hosting platform standardizes on ASGI, synchronous Django can still run, but do not advertise ASGI as a feature until the application uses it deliberately.

---

# 5. Django application boundaries

Implemented boundaries:

```text
apps/
├── common/
├── countries/
├── exchange/
├── culture/
├── media/
└── travel/
```

Planned boundaries are introduced only with their owning feature:

```text
apps/
└── accounts/   # identity/ownership, PR12
```

A future `statistics/` app is introduced only when historical purchasing-power methodology becomes production scope.

Avoid generic `core/`, `services/` or catch-all utility packages. `apps.common` is intentionally
narrow: health/readiness, request-context middleware, structured observability, the Vite template
bridge and design-preview presentation helpers. It must not own business entities or domain rules.

Project configuration remains under:

```text
config/
├── settings.py
├── urls.py
├── environment.py
└── database.py
```

Cross-domain code must protect a concrete infrastructure boundary rather than merely provide a
convenient import location.

---

# 6. App responsibility map

## common

Owns:

- health/readiness HTTP endpoints;
- request correlation and structured observability infrastructure;
- the repo-owned Django↔Vite manifest bridge;
- design-preview-only presentation helpers.

Does not own:

- business models;
- FX semantics;
- cultural facts;
- user-owned product state.

## accounts

Owns:

- identity;
- authentication integration;
- profile/preferences;
- user lifecycle;
- ownership helpers/policies.

Does not own:

- favourites domain;
- trips;
- FX logic.

## countries

Owns:

- Country;
- Currency;
- CountryCurrency;
- currency lifecycle metadata;
- current/historical country-currency lookup;
- normalized imported country metadata.

Does not own:

- rates;
- cultural stories;
- user saved state.

## exchange

Owns:

- conversion request/value objects;
- rate-provider interface;
- Frankfurter adapter;
- current/historical quote semantics;
- Decimal conversion;
- quote caching;
- time-series normalization;
- historical observation policy.

Does not own:

- country display metadata;
- purchasing-power price cards;
- user favourites.

## culture

Owns:

- payment/cash/tipping context;
- TypicalPrice;
- StoryMoment;
- currency/cultural story composition inputs;
- editorial provenance;
- cultural fact/source ingestion.

Does not own:

- exchange arithmetic.

## media

Owns:

- MediaAsset persistence/publication state;
- source/licence/creator/rights provenance;
- safe media-byte validation and derivatives;
- bounded Wikimedia/Europeana candidate ingestion;
- deterministic local media selection.

Does not own:

- StoryMoment factual content;
- payment/price facts;
- exchange arithmetic.

## travel

Owns:

- the Saved & recent presentation boundary;
- future authenticated FavouritePair persistence;
- server-side recent conversions only if explicitly introduced;
- future Trip and TripBudgetItem persistence;
- saved travel-specific state.

PR11 Phase A does **not** persist anonymous favourites or history in Django/PostgreSQL. The browser
owns that versioned localStorage state; Django only serves the page shell and validates pair-restore
URL parameters.

Does not own:

- rate provider calls directly;
- country metadata duplication.

---

# 7. Internal layering

Within an app, code follows these conceptual layers:

```text
presentation
    ↓
application/use case
    ↓
domain
    ↓
persistence + infrastructure adapters
```

This is a dependency-direction rule, not a folder-count rule.

---

# 8. Presentation layer

Examples:

- Django forms;
- Django views;
- HTMX fragment responses;
- DRF serializers/views;
- Django admin.

Responsibilities:

- parse transport input;
- call one application use case;
- map domain/application result to presentation;
- map known errors to user/API states.

Presentation does **not**:

- perform provider HTTP calls directly;
- calculate rates;
- decide fallback semantics;
- contain multi-model transaction workflows;
- embed cache-key construction.

---

# 9. Application layer

Application functions coordinate a user/business use case.

Examples:

```python
quote_conversion(command)
quote_historical_conversion(command)
build_destination_context(query)
build_money_story(query)
save_favourite(command)
merge_local_favourites(command)
create_trip(command)
update_trip_budget(command)
```

Use-case code may coordinate:

- domain value objects;
- ORM queries;
- provider interfaces;
- cache;
- transactions.

It should return explicit result objects, not HTTP responses.

---

# 10. Domain layer

Domain code contains rules whose correctness matters independently from Django transport.

Examples:

- MoneyAmount;
- RateQuote;
- HistoricalConversion;
- conversion arithmetic;
- rounding;
- requested/effective date semantics;
- quote freshness classification;
- historical fallback policy;
- source trust classification;
- story chapter composition.

Domain code should be mostly deterministic and easy to unit-test.

---

# 11. Persistence layer

Use Django ORM directly.

Do **not** introduce generic repositories around every model.

Appropriate reuse patterns:

- custom QuerySet;
- model Manager;
- focused query function/module for complex read composition.

Examples:

```python
Currency.objects.active_on(date)
CountryCurrency.objects.primary_for(country, date)
StoryMoment.objects.published_for(country, currency, date)
```

A repository abstraction is justified only if a domain genuinely has multiple interchangeable persistence implementations.

That is not currently true.

---

# 12. Infrastructure adapters

Adapters isolate external system semantics.

Examples:

```text
exchange/providers/frankfurter.py
countries/sources/rest_countries.py
culture/sources/wikidata.py
culture/sources/europeana.py
statistics/sources/eurostat.py
```

Responsibilities:

- HTTP transport;
- source-specific schema parsing;
- normalization;
- source-specific errors;
- provenance extraction.

They do not return raw provider dictionaries to application code.

---

# 13. Suggested app package shape

Use only files justified by the app.

Example for `exchange`:

```text
exchange/
├── models.py                 # only persisted exchange models if needed
├── domain/
│   ├── money.py
│   ├── quotes.py
│   └── history.py
├── services/
│   ├── quote_conversion.py
│   └── quote_history.py
├── providers/
│   ├── base.py
│   └── frankfurter.py
├── cache.py
├── forms.py
├── views.py
├── api/
│   ├── serializers.py
│   └── views.py
└── tests/
```

Do not create every directory on day one.

Start flat and split when the module earns it.

Architecture describes boundaries; it does not mandate empty packages.

---

# 14. Service-layer rule

Create a service/use-case function only when it coordinates at least one real boundary:

- provider call;
- transaction;
- cache;
- several models;
- non-trivial calculation;
- web/mobile shared behavior.

Do not wrap:

```python
Country.objects.get(pk=...)
```

inside:

```python
CountryService.get_country(...)
```

for ceremony.

---

# 15. Command/query distinction without CQRS

Application functions may be named conceptually as:

- command = changes durable state;
- query = reads/computes result.

But do not introduce CQRS infrastructure.

Examples:

```text
quote_conversion       query-like
get_destination_context query-like
save_favourite          command
create_trip             command
```

Same PostgreSQL/database model remains the source of truth.

---

# 16. Data source-of-truth hierarchy

## PostgreSQL

Authoritative for:

- curated local domain data;
- user-owned state;
- imported metadata snapshots that the product publishes;
- editorial publication status.

## Frankfurter

Authoritative external source for normalized FX observations under the selected provider policy.

## Cache

Never authoritative.

Cache can be:

- fresh optimization;
- explicitly stale fallback.

## Browser/mobile local storage

Never server source of truth for financial data.

It may preserve:

- previously authoritative quote snapshots;
- anonymous favourites;
- recent history.

---

# 17. API boundary

Web and mobile share application/domain behavior, not transport.

```text
Web
Django Form → use case → result → HTML

Mobile
DRF Serializer → same use case → result → JSON
```

This prevents two implementations of conversion/fallback semantics.

---

# 18. API versioning

Mobile API is namespaced:

```text
/api/v1/
```

Use DRF namespace/version semantics consistently.

Public URLs and serializer contracts are versioned together.

Do not branch business logic throughout the codebase on arbitrary version checks.

If v2 eventually appears:

- presentation adapter differs;
- application/domain logic remains shared where semantics are unchanged.

---

# 19. OpenAPI

Use **drf-spectacular** for OpenAPI 3 schema generation.

Reason:

- DRF's built-in OpenAPI generation is deprecated;
- DRF currently recommends drf-spectacular as the full-featured replacement;
- mobile types are generated from OpenAPI.

Schema generation must be deterministic in CI.

Generated schema is part of the mobile contract.

---

# 20. API view style

Prefer boring, explicit DRF generic/API views.

Do not automatically use ModelViewSet for every resource.

Good fit:

- read-only list endpoints → GenericAPIView/ListAPIView;
- quote calculation → APIView;
- favourite CRUD → explicit generic views or small ViewSet if it truly reduces duplication;
- trip resources → ViewSet may become appropriate later.

API structure follows use cases, not ORM table exposure.

---

# 21. Transport validation vs domain validation

DRF serializer / Django form validates:

- syntax;
- required fields;
- ISO-code format;
- date format;
- obvious numeric bounds.

Domain/application validates:

- currency supported on date;
- pair coverage;
- source-policy availability;
- historical semantics;
- ownership/business invariant.

Database validates:

- uniqueness;
- relational integrity;
- durable check constraints.

One rule may exist at several layers for user feedback + durable protection, but the responsibilities must be intentional.

---

# 22. Exception taxonomy

Define typed application/domain errors.

Concept:

```text
ApplicationError
├── InputValidationError
├── UnsupportedCurrency
├── UnsupportedPair
├── HistoricalOutOfCoverage
├── HistoricalObservationUnavailable
├── RateTemporarilyUnavailable
├── SourceDataInvalid
├── OwnershipViolation
├── Conflict
└── ResourceNotFound
```

Provider transport errors are translated before leaving infrastructure.

Views/API map known errors to stable responses.

Unknown errors become generic 500 handling plus request ID.

---

# 23. HTTP status mapping

Candidate API semantics:

```text
200 success
201 created durable resource
204 idempotent delete
400 malformed/validation
401 authentication required
403 authenticated but forbidden
404 resource not found
409 concurrency/idempotency conflict
422 semantically unsupported input if adopted consistently
429 policy throttle
503 transient rate/provider unavailable
500 unexpected server failure
```

Do not overfit status codes.

Stable machine-readable `code` matters more than clever distinctions.

---

# 24. API error envelope

Candidate:

```json
{
  "code": "historical_out_of_coverage",
  "detail": "Historical data for this pair starts on 1972-01-03.",
  "retryable": false,
  "fields": {},
  "request_id": "..."
}
```

Validation example:

```json
{
  "code": "validation_error",
  "detail": "Check the highlighted fields.",
  "retryable": false,
  "fields": {
    "amount": ["Enter zero or a positive amount."]
  },
  "request_id": "..."
}
```

Clients must not parse English strings to decide behavior.

---

# 25. Database default behavior

Use PostgreSQL autocommit as Django default.

Do not enable global `ATOMIC_REQUESTS`.

Why:

- many requests are read-only;
- provider requests must not hold transactions;
- global per-request transactions add unnecessary lock/transaction duration;
- explicit transaction boundaries are more understandable.

---

# 26. Explicit transaction rule

Use `transaction.atomic()` only around the minimum durable multi-write unit.

Examples:

- create Trip + initial budget items;
- merge local favourites when several rows must be reconciled as one unit;
- editorial publish operation spanning related rows if consistency requires it.

Never:

```text
begin transaction
→ call Frankfurter
→ wait on network
→ write
→ commit
```

External network I/O stays outside DB transactions.

---

# 27. After-commit side effects

If a database write requires:

- cache invalidation;
- enqueueing a future task;
- notification;
- derived refresh;

register it with `transaction.on_commit()`.

Do not mutate cache before the DB transaction is known to have committed.

This avoids cache/DB divergence on rollback.

---

# 28. Row locking

Use `select_for_update()` only where a real concurrent-write invariant requires pessimistic serialization.

Potential future example:

- two concurrent updates to one Trip budget aggregate where optimistic versioning is insufficient.

Do not lock rows for:

- simple quote reads;
- favourites when a unique constraint gives idempotency;
- imports that can use upsert/unique constraints.

Locks increase contention.

---

# 29. Optimistic concurrency

For user-owned aggregates likely to be edited from several devices, prefer an explicit version token once needed.

Candidate:

```text
Trip.version integer
```

Update request includes current version.

Server:

```text
UPDATE ... WHERE id=? AND version=?
```

No match:

```text
409 conflict
```

This is preferable to silently overwriting another device's newer trip budget.

Do not add version columns to every model preemptively.

---

# 30. Database constraints

Use database constraints for durable invariants.

Examples:

- unique currency code;
- unique country ISO code;
- unique CountryCurrency lifecycle record identity;
- unique favourite pair per user/context;
- positive TypicalPrice bounds;
- valid low <= high price;
- nonnegative ordering/relevance where relevant.

Application validation improves UX.

Database constraints prevent corruption.

---

# 31. Index policy

Index from query shapes, not guesses.

Expected useful indexes:

- Currency(code);
- Country(iso2/iso3);
- CountryCurrency(country, valid_from, valid_to);
- TypicalPrice(country, city, category, is_published);
- StoryMoment(date range/publication filters);
- FavouritePair(user, base, quote);
- Trip(user, updated_at).

Use PostgreSQL `EXPLAIN` when query volume/complexity warrants tuning.

Avoid indexing every foreign key/filter combination speculatively.

---

# 32. Read-query optimization

Use:

- `select_related()` for single-valued relations;
- `prefetch_related()` for collections;
- narrow field selection where payload materially matters.

Prevent N+1 in:

- destination-context assembly;
- Story page;
- saved trips;
- admin/editorial listings.

Do not prematurely micro-optimize basic country lookup.

---

# 33. Domain value types

Critical values should not travel as loosely structured dicts.

Examples:

```python
@dataclass(frozen=True)
class RateQuote:
    base: CurrencyCode
    quote: CurrencyCode
    rate: Decimal
    requested_date: date | None
    effective_date: date
    fetched_at: datetime
    provider_policy: ProviderPolicy
    providers: tuple[str, ...]
    granularity: ObservationGranularity
    stale: bool
```

Value types protect semantics across web/API/mobile.

---

# 34. Decimal policy

All backend financial arithmetic uses `Decimal`.

Provider numeric fields are parsed from string/decimal-safe representation.

Never:

```python
Decimal(float_value)
```

Use:

```python
Decimal(str_value)
```

only after provider validation if JSON parser produced a float, or configure parsing appropriately.

Output API serializes financial decimals as strings.

---

# 35. Time policy

Backend stores timezone-aware UTC timestamps for:

- fetched_at;
- created_at;
- updated_at;
- verified_at.

Date-only concepts remain `date`:

- historical requested date;
- effective observation date;
- country-currency validity dates.

Do not convert a date-only monetary observation into an arbitrary midnight timezone timestamp.

---

# 36. Current-date semantics

The user's local date can matter to UI, but provider/domain data uses explicit date semantics.

Server should not infer historical requested date from browser clock.

For “latest”:

- use provider latest reference semantics;
- return effective date explicitly.

For “historical”:

- require explicit requested date.

---

# 37. Source/provenance as first-class backend data

Every trust-sensitive observation includes source information.

Examples:

- rate provider(s);
- source URL where appropriate;
- observed/effective date;
- fetched/verified date;
- source trust class;
- licence metadata for media.

Presentation cannot manufacture provenance that backend did not provide.

---

# 38. Cache role

The cache is an acceleration/resilience layer.

Correctness must survive cache miss.

Cache failure should usually degrade to:

- DB/provider path;
- slower response;
- no data corruption.

Do not put user-owned state only in cache.

---

# 39. Cache backend evolution

Development:

- LocMemCache acceptable.

Production initial:

- use a shared production-capable backend when deployment scale requires cross-process consistency/performance.

Do not rely on LocMemCache for cross-process coordination because it is process-local.

Redis remains an infrastructure choice, not a domain dependency.

---

# 40. Background work

Initial background/scheduled operations use:

- Django management commands;
- platform scheduler / cron;
- optional GitHub Actions only where credentials/terms make sense.

No Celery in initial architecture.

Introduce a task queue only when requirements include:

- user-triggered long-running jobs;
- retryable asynchronous side effects;
- sustained import workload needing distributed workers;
- notifications/alerts at scale.

---

# 41. Management command design

Commands are thin adapters over reusable import/application services.

Good:

```text
manage.py sync_country_metadata
    ↓
sync_country_metadata()
```

Do not put all import business logic directly inside `handle()`.

This allows tests and alternate scheduling mechanisms.

---

# 42. Idempotency

Every scheduled import must be safe to run twice.

Use:

- stable external IDs;
- unique constraints;
- upsert/update-or-create logic where appropriate;
- source snapshot/version metadata.

A failed retry must not duplicate rows.

---

# 43. Admin as editorial operations UI

Django admin is appropriate for:

- StoryMoment;
- CulturalProfile;
- TypicalPrice;
- media provenance;
- publication status;
- verification timestamps.

Admin is not the consumer UI.

Custom admin actions can support:

- publish/unpublish;
- mark verified;
- revalidate source;
- preview story.

Do not build a separate CMS before admin limitations become real.

---

# 44. Settings architecture

Recommended split:

```text
config/settings/
├── base.py
├── development.py
├── test.py
└── production.py
```

or equivalent environment-driven single-file pattern if it stays simpler.

Requirements:

- no secret defaults in production;
- fail fast on missing critical settings;
- explicit external base URLs/timeouts;
- explicit cache backend;
- explicit database connection config;
- environment name available to logs.

Avoid an elaborate settings package if simple environment branching is cleaner.

---

# 45. Secret ownership

Server-only:

- Django secret key;
- database credentials;
- REST Countries key;
- Europeana key;
- future provider credentials.

Never expose them to:

- HTML;
- Vite public env;
- Expo public config;
- logs.

Frankfurter public endpoint needs no secret but still remains server-mediated.

---

# 46. Health endpoints

Use two concepts.

## Liveness

```text
/health/live/
```

Answers:

> Is the Django process alive?

No external calls.

## Readiness

```text
/health/ready/
```

Checks only dependencies required to serve safely, initially:

- database connectivity;
- critical configuration.

Do not call Frankfurter, Wikidata, REST Countries or statistical APIs from readiness.

An external provider outage must not trigger process restart loops.

---

# 47. Structured logging

Logs should be machine-readable in production.

Common fields:

- timestamp;
- level;
- logger;
- request_id;
- method;
- path/route name;
- status;
- duration_ms;
- user_id only where privacy policy allows;
- cache outcome;
- provider;
- normalized error code.

Never log:

- secrets;
- auth tokens;
- full request bodies by default;
- private trip notes;
- raw upstream payloads unless explicitly sanitized in debug tooling.

---

# 48. Request correlation

Generate/accept a bounded request ID.

Rules:

- validate incoming request ID format/length if accepted;
- otherwise generate server-side;
- return it in response header;
- include it in logs;
- include it in API error envelope.

This turns “rate unavailable” reports into traceable events without exposing internals.

---

# 49. Observability phase 1

Use:

- structured logs;
- request durations;
- provider latency/failure;
- cache hit/miss/stale fallback;
- DB slow-query review;
- health endpoints.

Do not require a full observability platform on day one.

## Implemented foundation

The phase-1 operational baseline now includes:

- `GET /health/live/` with no dependency checks;
- `GET /health/ready/` with database connectivity as the only dependency check;
- bounded `X-Request-ID` correlation;
- server-generated UUID4 when the incoming ID is absent or invalid;
- request ID returned in the response header;
- request-scoped correlation through `ContextVar` with cleanup after every request;
- JSON request logs with method, path, route, status and duration;
- privacy-bounded access logging that excludes query strings and request bodies.

Provider/cache-specific observability and OpenTelemetry remain later work tied to the corresponding features.

---

# 50. Observability phase 2

If deployment value justifies it, add OpenTelemetry for:

- request traces;
- provider spans;
- DB spans;
- correlation across services.

Instrumentation is optional infrastructure.

Domain code does not import telemetry SDK everywhere.

---

# 51. Metrics of interest

Backend operational metrics:

- request count/status/latency;
- quote latency;
- Frankfurter success/timeout/error;
- fresh-cache hit rate;
- stale fallback count;
- historical out-of-coverage count;
- import success/failure/duration;
- DB query duration;
- API throttle count.

Product analytics remain separate from operational telemetry.

---

# 52. Security boundary

All external input is untrusted:

- form values;
- URL query params;
- API JSON;
- local/mobile sync payload;
- external API JSON;
- imported metadata;
- editorial text.

Validation/sanitization occurs at the relevant boundary.

Django auto-escaping remains enabled.

---

# 53. CSRF

Browser unsafe methods use Django CSRF protection.

HTMX does not bypass CSRF.

Mobile token-authenticated API does not inherit browser session assumptions.

Authentication design is finalized when account sync ships.

---

# 54. CORS

Do not enable permissive CORS by default.

The web frontend is same-origin.

Native React Native requests are not browser CORS requests.

Add explicit allowed origins only if a real browser-based external client is introduced.

Never use wildcard + credentials.

---

# 55. SSRF

External provider base URLs are configuration, not user input.

User can provide:

- currency codes;
- dates;
- filters.

They cannot provide arbitrary URLs for the server to fetch.

Source URLs stored for provenance are links, not automatic fetch targets.

---

# 56. Rate limiting

DRF throttling may provide:

- anonymous fair-use control;
- per-user limits;
- scoped protection for expensive endpoints.

But it is not DDoS/security enforcement.

If public abuse becomes meaningful, use platform/edge rate limiting in addition.

No critical correctness rule depends on DRF throttle exactness.

---

# 57. Authentication and ownership

When account features ship:

- backend authorizes every object;
- ownership query filters by `request.user`;
- object IDs are never treated as authorization;
- hidden UI is not security.

Tests must cover cross-user read/update/delete attempts.

---

# 58. API data minimization

Mobile endpoints return only fields needed by the client.

Do not serialize full Django models automatically.

Benefits:

- stable contract;
- privacy;
- lower payload;
- easier mobile evolution.

---

# 59. Pagination

Paginate resources that can grow:

- recent history server-side;
- trips;
- editorial/admin API if exposed.

Do not paginate tiny static reference sets merely because DRF supports it.

Countries/currencies can be returned as bounded complete sets if payload remains small and offline search benefits.

---

# 60. Conditional HTTP caching

Strong candidates for ETag/Last-Modified:

- country/currency metadata;
- published cultural profile;
- story pages/content;
- source reference metadata.

Less useful:

- amount-specific conversion POST.

HTTP cache behavior is separate from internal FX cache.

---

# 61. Same-currency conversion

If:

```text
base == quote
```

then:

- no Frankfurter request;
- rate = 1 exactly;
- output = input under display/minor-unit policy;
- current destination cultural context can still load.

This is a domain fast path, not an upstream special case.

---

# 62. Provider outage philosophy

Do not turn provider failure into corrupted certainty.

Possible result states:

```text
fresh success
stale usable success
unavailable
```

Never:

- fabricate a rate;
- silently switch methodology;
- show zero;
- keep a previous different-pair result.

---

# 63. Import outage philosophy

Import sources are not runtime critical.

If REST Countries / Wikidata / Eurostat is down:

- scheduled import fails visibly;
- existing published local data remains;
- user-facing request still works;
- no local data deletion occurs because upstream returned incomplete/error response.

---

# 64. Schema migration policy

Every DB schema change:

- Django migration committed;
- migration tested against PostgreSQL;
- destructive migrations separated from data backfill where prudent;
- rollback/forward-fix strategy understood.

For large future tables, use expand/contract migration patterns where deployment needs zero downtime.

Do not optimize for zero-downtime complexity before deployment scale requires it.

---

# 65. Data migration policy

Data migrations must be:

- deterministic;
- bounded;
- tested;
- independent from live external APIs.

Never make a deployment migration call Frankfurter/REST Countries.

External data sync happens through explicit commands after deploy.

---

# 66. Delete semantics

Hard delete:

- anonymous local data when client clears it;
- ephemeral rows with no audit need.

User-owned server data:

- hard delete where privacy expectation demands actual deletion unless legal/audit requirements exist.

Editorial sourced data:

- unpublish may be preferable to delete so provenance/history remains.

Do not add soft-delete to every model.

---

# 67. Audit fields

Use `created_at` / `updated_at` where operationally useful.

Trust-sensitive curated content additionally uses:

- verified_at;
- source;
- observation/effective date.

Do not add an audit-trail framework until there is a real compliance/editorial-history requirement.

---

# 68. Feature flags

No generic feature-flag platform initially.

For incomplete features:

- do not route/expose them;
- or use explicit settings flag only when staged deployment requires it.

Avoid building a mini LaunchDarkly.

---

# 69. Dependency policy

Backend dependency is accepted only when it:

- solves a documented problem;
- is maintained;
- supports Django/Python versions;
- has acceptable license/security posture;
- materially reduces correct code.

Prefer standard Django/Python capabilities before packages.

---

# 70. Architecture fitness checks

The backend architecture is drifting if any of these appear:

- views contain provider JSON parsing;
- serializers perform business calculations;
- templates know cache keys;
- models make network requests;
- API and web calculate conversions differently;
- every model has a repository/service wrapper;
- Redis/Celery introduced without measured need;
- long transaction includes network I/O;
- raw provider error leaks to client;
- mobile dictates domain semantics independently.

---

# 71. Backend acceptance criteria

The system-design foundation is considered implemented only when:

- request/use-case/provider boundaries are visible in code;
- same use case powers web and API;
- transactions are explicit and short;
- no external request occurs while DB locks are held;
- database constraints protect durable invariants;
- cache miss/failure preserves correctness;
- stale FX behavior is explicit;
- all provider payloads normalize before domain entry;
- API has stable error codes/request IDs;
- OpenAPI generation is deterministic;
- imports are idempotent and runtime-independent;
- liveness/readiness do not depend on optional providers;
- structured logs can reconstruct a failed quote flow;
- tests cover concurrency/failure paths described in the backend scenario catalog.
