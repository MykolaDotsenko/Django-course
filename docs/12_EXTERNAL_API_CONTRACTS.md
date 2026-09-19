# External API Integration Contracts

This document defines how Cultural Currency Converter talks to third-party APIs.

The product deliberately avoids a generic “API client” abstraction that hides important semantic differences. Each data domain gets a small explicit adapter with a normalized output contract.

---

# 1. Core rule

> **External JSON is untrusted infrastructure data until it has been validated and normalized.**

Flow:

```text
third-party response
      ↓
transport validation
      ↓
provider-specific parser
      ↓
normalized domain DTO/value object
      ↓
application service
      ↓
cache / persistence / presentation
```

Templates and React Native never consume third-party payloads directly.

---

# 2. Adapter boundaries

Proposed structure:

```text
apps/
├── exchange/
│   └── providers/
│       ├── base.py
│       └── frankfurter.py
│
├── countries/
│   └── sources/
│       └── rest_countries.py
│
├── culture/
│   └── sources/
│       ├── wikidata.py
│       ├── wikimedia_commons.py
│       └── europeana.py
│
└── statistics/
    └── sources/
        ├── eurostat.py
        ├── oecd.py
        └── world_bank.py
```

The `statistics` app is optional until historical purchasing-power work is approved.

Do not create empty adapters before the corresponding feature exists.

---

# 3. HTTP transport policy

Use one well-understood Python HTTP client.

Candidate:

- `httpx`.

Reason:

- explicit timeout model;
- sync/async capability;
- mature testing/mocking ecosystem.

Do not add both requests and httpx without a concrete reason.

---

# 4. Timeout policy

Every external request has finite timeouts.

Initial policy candidate for user-facing FX requests:

```text
connect: ~2 s
read:    ~3–4 s
total user-facing budget: bounded
```

Exact values should be measured during implementation.

Import/editorial jobs can tolerate longer timeouts.

No request can wait indefinitely.

---

# 5. Retry policy

Retries are conservative.

Safe candidates:

- connection reset;
- selected 5xx;
- 429 when `Retry-After` is reasonable;
- idempotent GET only.

Do not retry:

- 400/404/422 validation/coverage errors;
- malformed application inputs;
- authentication failure without credential change.

P0 request path should normally use at most a small retry count.

Caching is preferable to repeated upstream hammering.

---

# 6. User-Agent policy

All outbound requests identify the application where provider guidance expects it.

Example:

```text
CulturalCurrencyConverter/0.1 (+https://github.com/MykolaDotsenko/Django-course)
```

For Wikimedia, include meaningful contact information in the deployed configuration as required by their usage guidance.

Do not embed private personal contact data directly in source code.

Use configurable operator/contact metadata.

---

# 7. Error taxonomy

Provider-specific errors normalize into a small internal taxonomy.

Concept:

```text
ExternalDataError
├── InvalidRequest
├── Unsupported
├── OutOfCoverage
├── AuthenticationError
├── RateLimited
├── Timeout
├── UpstreamUnavailable
├── InvalidPayload
└── PolicyViolation
```

Presentation should not expose raw exceptions.

---

# 8. Provenance contract

Every trust-sensitive normalized observation supports provenance.

Concept:

```text
SourceAttribution
- source_id
- source_name
- source_url
- source_class
- provider_keys[]
- retrieved_at
- effective_at/date?
- licence_id?
- licence_url?
```

Not every field is required for every source.

---

# 9. Frankfurter normalized contract

## RateQuote

```text
RateQuote
- base_currency
- quote_currency
- rate: Decimal
- requested_date: date | null
- effective_date: date
- fetched_at: datetime
- provider_policy: "blend" | "pinned"
- provider_keys[]
- historical: bool
- observation_granularity
- stale: bool
```

Raw JSON never leaves `FrankfurterProvider`.

## Validation

Validate:

- base code;
- quote code;
- positive Decimal rate;
- date format;
- returned pair identity;
- requested/effective temporal relationship;
- provider identifiers when expanded.

Reject:

- zero/negative rate;
- unexpected pair;
- invalid date;
- non-decimal numeric shape that cannot be safely parsed;
- structurally incomplete response.

## Calculation

Provider never calculates final amount.

Application:

```text
convert(amount, quote)
```

owns Decimal arithmetic.

---

# 10. Frankfurter provider policy object

Avoid magic query-string construction spread across code.

Concept:

```text
FxSourcePolicy
- mode: blend | pinned
- provider_key: nullable
- include_attribution: bool
```

P0 default:

```text
mode = blend
include_attribution = true
```

No UI provider selector required.

---

# 11. FX cache key

Concept:

```text
fx:v1:{mode}:{provider?}:{base}:{quote}:{date/latest}
```

Do not key only by pair if provider policy/date changes semantics.

For time series:

```text
fx-series:v1:{mode}:{provider?}:{base}:{quote}:{from}:{to}:{group}
```

Version prefix permits schema/policy invalidation.

---

# 12. Stale cache safety

A cached result may be used only if all semantic keys match:

- same base;
- same quote;
- same provider policy;
- same historical/latest mode;
- compatible requested date policy.

Never serve EUR/JPY cache under EUR/AUD after an upstream failure.

---

# 13. Historical observation policy

Provider adapter returns what upstream published.

Application policy decides whether a previous observation is acceptable for a requested non-observation date.

Do not hide this inside a generic HTTP client.

Concept:

```text
HistoricalObservationPolicy
- direction: on_or_before
- max_gap_days
```

The selected effective date is returned explicitly.

---

# 14. REST Countries normalized contract

Country import output:

```text
CountryMetadataSnapshot
- iso2
- iso3
- name
- official_name?
- capital?
- region?
- subregion?
- languages[]
- currency_codes[]
- flag_url?
- source_version
- fetched_at
```

Only map fields we intentionally own.

Do not persist the entire 90+ field response “just in case”.

---

# 15. REST Countries import behaviour

Management command concept:

```text
python manage.py sync_country_metadata
```

Properties:

- idempotent;
- atomic per country or whole import;
- dry-run;
- diff summary;
- validation;
- no destructive removal without explicit policy.

A source outage must not delete existing countries.

---

# 16. Wikidata normalized contract

Use targeted entity/property extraction.

Candidate:

```text
WikidataFactCandidate
- entity_qid
- property_id
- value
- qualifiers
- reference_urls/ids
- fetched_at
```

This is an ingestion candidate, not automatically a published StoryMoment.

Editorial process decides which facts become product content.

---

# 17. Wikimedia media contract

Candidate:

```text
MediaCandidate
- source = wikimedia_commons
- file_title
- canonical_page_url
- original_file_url
- thumbnail_url?
- creator?
- licence_id
- licence_url
- attribution_text
- source_entity_ids[]
- fetched_at
```

Missing/ambiguous licence metadata means:

> not publishable automatically.

---

# 18. Europeana record contract

Candidate:

```text
HeritageRecordCandidate
- europeana_id
- title
- institution/provider
- record_url
- media_url?
- rights_uri
- date/context?
- place?
- fetched_at
```

A record must pass rights checks before its media is displayed.

---

# 19. Statistical observation contract

Use one normalized structure for official statistical series without pretending their methodologies are identical.

```text
StatisticalObservation
- source
- dataset_id
- indicator_id
- geography_code
- period
- frequency
- value: Decimal
- unit
- category_code?
- status?
- fetched_at
- metadata_url
```

Methodology stays attached to dataset/indicator metadata.

---

# 20. Eurostat adapter

Responsibilities:

- construct narrow dataset queries;
- decode JSON-stat/SDMX response;
- map dimensions;
- preserve dataset code;
- preserve unit/category/status;
- reject ambiguous/missing dimension mapping.

Do not write calculations against positional array indexes without a tested dimension mapping layer.

---

# 21. OECD adapter

Responsibilities:

- query SDMX dataflow;
- pin dataset/version where appropriate;
- map dimension codes;
- preserve analytical category/base reference area;
- cache structure metadata;
- normalize observations.

A dataset-version change should trigger contract tests before production import.

---

# 22. World Bank adapter

Responsibilities:

- use Indicators API v2;
- request only required country/indicator/date ranges;
- paginate when needed;
- retain indicator metadata;
- retain data-source attribution/licence notes.

Do not issue “all countries × all years × many indicators” queries on a user request.

---

# 23. Statistical import idempotency

Unique identity candidate:

```text
source
+ dataset_id
+ indicator_id
+ geography
+ period
+ category
+ unit
```

An updated official value replaces/versions the existing normalized observation according to dataset policy.

Record:

- fetched_at;
- optional revision marker;
- source status/provisional flag when available.

---

# 24. Numbeo adapter boundary

No implementation in P0.

Still define the policy if added later:

```text
PriceObservation
- place_scope
- item_code
- label
- low
- average
- high
- currency
- contributors/data_points
- observed_period
- source_class = commercial_crowdsourced
- licence/source
```

Never normalize a crowdsourced average into the same trust label as an official fare.

---

# 25. Curated TypicalPrice contract

For P0 manual/editorial prices:

```text
TypicalPrice
- country
- city?
- category
- label
- amount_low
- amount_high?
- currency
- observed_at
- source_name
- source_url
- source_class
- confidence
- verified_at
```

A record cannot be published without:

- geography;
- currency;
- source;
- observation date/period.

---

# 26. Source priority is domain-specific

Never implement one global “best source” ranking.

Examples:

## EUR/JPY rate

Frankfurter blend.

## ECB-specific reference rate

ECB provider series.

## Finland HICP

Eurostat.

## Global CPI fallback

World Bank.

## Helsinki transit ticket

official transport operator, not OECD PPP.

## Cultural event

official archive / Wikidata references / Europeana depending event.

---

# 27. Secrets configuration

Environment variables are namespaced.

Examples:

```text
REST_COUNTRIES_API_KEY
EUROPEANA_API_KEY
EXTERNAL_API_USER_AGENT
EXTERNAL_API_CONTACT
FRANKFURTER_BASE_URL
```

Avoid provider names in generic frontend settings.

No secret enters `NEXT_PUBLIC_*`, Expo public env, HTML, logs or analytics.

---

# 28. Logging

Log enough to debug without leaking secrets.

Good fields:

- provider;
- endpoint class, not full secret URL;
- status code;
- latency;
- normalized error class;
- cache hit/miss;
- pair/date for FX where acceptable;
- request correlation ID.

Never log:

- bearer tokens;
- API keys;
- auth headers;
- raw personal trip notes.

---

# 29. Metrics

Useful provider metrics:

- requests;
- success rate;
- latency;
- timeout count;
- 429 count;
- invalid-payload count;
- cache hit ratio;
- stale fallback count;
- historical out-of-coverage count.

Do not introduce a full observability platform before deployment warrants it.

Structured logs may be sufficient initially.

---

# 30. Circuit-breaker decision

No dedicated circuit-breaker framework in P0.

Reason:

- additional state/complexity;
- request volume is small;
- caching + short timeout + bounded retry already provides graceful behaviour.

If production metrics show repeated upstream failure causing load/latency, introduce a simple measured circuit policy later.

---

# 31. Backoff policy

For import jobs:

- exponential backoff;
- jitter;
- honor `Retry-After`;
- bounded total attempts.

For user-facing FX:

- keep latency budget small;
- usually cache + at most minimal retry;
- prefer fast stale fallback over long retry storm.

---

# 32. Schema-change resilience

Provider JSON fields can be added.

Parsers:

- ignore unknown fields;
- validate required fields;
- do not fail because an additive optional field appears.

Breaking changes:

- contract tests;
- pinned API version where available;
- changelog monitoring for critical runtime providers.

---

# 33. Test strategy

Every adapter gets:

## Parser unit tests

Fixtures:

- normal payload;
- edge value;
- missing required field;
- malformed number;
- error payload.

## Transport tests

Simulate:

- timeout;
- 429;
- 500;
- invalid JSON.

## Contract smoke test

Optional scheduled/manual live test against real provider.

Do not make normal CI depend on internet availability.

---

# 34. Fixture policy

Fixtures must be:

- small;
- representative;
- legally safe to store;
- clearly marked with source/retrieval date;
- stripped of secrets.

Do not check in entire third-party datasets when terms prohibit redistribution.

---

# 35. Data deletion/correction

External data can be corrected.

For locally persisted imported content:

- support re-import/upsert;
- keep verification/retrieval timestamps;
- remove/suppress records whose licence or factual status changes;
- allow editorial unpublish.

Historical facts are not “immutable because old”.

---

# 36. Mobile contract

React Native never calls:

- Frankfurter;
- REST Countries;
- Wikidata;
- Eurostat;
- OECD;
- World Bank;
- Europeana

directly.

Mobile calls:

```text
Django /api/v1
```

Benefits:

- one source policy;
- one cache;
- no leaked keys;
- consistent Decimal/date semantics;
- consistent provenance;
- simpler offline cache.

---

# 37. Web contract

Django templates/HTMX call application services.

They do not call external APIs from JavaScript.

Benefits:

- progressive enhancement;
- no CORS dependency;
- no key exposure;
- one error model;
- accessible server-rendered states.

---

# 38. Provider health endpoint policy

Public `/health/` should not synchronously call every external provider.

Health should answer:

- app process;
- database readiness;
- required local configuration.

External providers are reported through logs/observability, not made a hard liveness dependency.

Otherwise a Frankfurter outage could cause our deployment platform to restart a healthy Django app repeatedly.

---

# 39. Import scheduling

Do not add Celery only to schedule imports.

Initial options:

- management commands;
- deployment cron;
- GitHub Actions scheduled workflow only if credentials/data policy permit;
- platform scheduler.

Add Celery only when genuine asynchronous application workloads appear.

---

# 40. Security threats

## SSRF

Never accept arbitrary external URLs from users and fetch them server-side.

Adapters have fixed allowlisted base URLs.

## Key leakage

Redact query/header secrets.

## Oversized payload

Set reasonable response size/streaming constraints where relevant.

## HTML injection

Third-party descriptions are text data, not trusted HTML.

Escape by default.

## Image/media safety

Do not proxy arbitrary user-provided media URLs.

Curated external media must be approved/normalized.

---

# 41. Final dependency rule

The critical request path should be:

```text
user
↓
Django
↓
local DB/cache
↓
Frankfurter only when FX refresh is required
```

Everything else is local data by the time the user needs it.

This is intentional.

It gives us:

- lower latency;
- fewer outages;
- clearer licensing;
- better testability;
- better provenance;
- less code;
- stronger portfolio architecture.
