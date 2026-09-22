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

**Selected initial client:**

- `httpx` in synchronous mode.

Reasons:

- explicit timeout model;
- mature testing/mocking ecosystem;
- clean transport abstraction;
- one client can also support future async work if architecture later changes.

The backend intentionally remains synchronous for the initial implementation. Do not use async `httpx` merely because the library supports it.

Do not add both `requests` and `httpx` without a concrete reason.

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

### Transaction boundary

External HTTP is completed **outside** any intentional PostgreSQL write transaction or row lock.

Correct order:

```text
fetch
→ validate
→ normalize
→ open transaction
→ durable writes
→ commit
```

Never hold database locks while waiting for a third-party API.

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

P0 request path should normally use at most a small retry count. The current Frankfurter runtime
adapter allows one retry for transient idempotent GET failures (selected 5xx, timeout, URL/network,
HTTP/read or socket-reset failures) and never retries authentication, unsupported-query or
rate-limit responses.

Caching is preferable to repeated upstream hammering.

---

# 6. User-Agent policy

All outbound requests identify the application where provider guidance expects it.

Example:

```text
CulturalCurrencyConverter/0.1 (+https://github.com/MykolaDotsenko/cultural-currency-converter-)
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

Fresh/stale classification is an application/cache concern derived from the normalized observation plus product freshness policy. The provider adapter itself does not invent a `stale` flag.
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
- provider identifiers when expanded;
- pinned-provider attribution identity when attribution is requested.

For a pinned-provider request with expanded attribution, the returned provider list must be a string
array, must be non-empty and must contain the requested provider identifier. Missing, malformed or
contradictory attribution is an invalid payload; provenance is not inferred from the query when the
provider claims to have returned attribution.

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
- currencies[]
  - code
  - name
  - symbol?
  - minor_units
- flag_url?
- source_version
- fetched_at
```

Only map fields we intentionally own. Languages and other source fields that are not represented by
the canonical Country/Currency model are intentionally excluded.

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

The provider boundary also normalizes transport/shape failures into `CountrySourceError`, validates
pagination progress/count metadata and caps one import fetch at 10 pages. This limit is a safety
guard against a provider that continuously advertises `more=true`; it is comfortably above the
expected REST Countries dataset size at 100 records/page and fails closed rather than looping.

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
- source name plus an absolute credential-free HTTPS source URL;
- observation date/period;
- explicit verification metadata where the model requires it.

Presentation queries fail closed on invalid provenance even if a row entered the database through a
programmatic write that bypassed model-form/`full_clean()` validation.

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


# 42. Backend integration alignment

External adapters are infrastructure.

They are called from application/use-case code, never directly from:

- Django templates;
- DRF serializers;
- model `save()`;
- React Native;
- web TypeScript.

The application layer decides:

- whether a cached quote is fresh;
- whether a stale fallback is acceptable;
- whether an error is user-visible/retryable;
- whether data can be persisted/published.

## 43. Provider/cache failure ownership

Provider adapter emits normalized transport/source failures.

The quote application path then decides:

```text
fresh cache hit
→ return

cache miss
→ provider

provider failure
→ exact-semantic stale cache

no acceptable stale
→ RateTemporarilyUnavailable
```

Raw `httpx` exceptions never cross the application boundary.

## 44. Import apply boundary

For slow-changing sources such as REST Countries/Wikidata/statistics:

```text
remote fetch
→ full/required validation
→ normalization
→ diff/staging
→ short DB transaction
→ commit
→ on_commit cache invalidation
```

A partial/malformed upstream response cannot be interpreted as an instruction to delete valid canonical data.

## 45. Import concurrency

Recurring imports must be idempotent.

If the same job can overlap, use one simple overlap-prevention mechanism appropriate to deployment:

- scheduler non-overlap guarantee;
- DB/advisory lock;
- import-run lock row.

Do not introduce a distributed task framework only to solve duplicate cron starts.


# 46. Image-generation provider contract

Image generation is not part of the normal conversion request path.

A provider adapter receives a structured request:

```text
GeneratedImageRequest
- role
- country
- currency nullable
- target_date nullable
- temporal_scope
- verified_visual_facts[]
- style_version
- aspect_ratio
- prompt_version
```

It returns:

```text
GeneratedImageCandidate
- bytes/file
- mime_type
- width
- height
- provider
- model
- generation_id nullable
- created_at
- provider_safety_metadata
- seed/parameters nullable
```

Raw provider response does not become MediaAsset directly.

## 47. Generation prompt ownership

The backend builds prompts from structured normalized fields.

Browser/mobile cannot provide arbitrary provider prompt strings in automatic flows.

Prompt template and style are versioned.

Historical facts included in the prompt must come from curated/sourced domain data.

## 48. Generation timeout/retry

Because editorial generation is off the user request path, its timeout/retry policy may be longer than FX.

Still:

- finite timeout;
- bounded retries;
- provider 4xx/safety refusal not retried blindly;
- 429 respects reasonable Retry-After;
- command/job failure remains visible.

Core product never waits for generation.

## 49. Image provider secrets

Provider API keys are server-only.

No key enters:

- Vite public config;
- Expo config;
- HTML;
- generated media metadata returned to clients;
- logs.

Published clients only receive approved MediaAsset URLs/metadata.

## 50. AI provider portability

The application domain does not depend on OpenAI/Stability/Google-specific output fields.

Provider/model identity is recorded for provenance/operations, but published-media selection works against MediaAsset.

This makes model deprecation a generation-tooling issue rather than a page-runtime outage.


# 51. Gemini text-generation contract

Google Gemini Developer API Free Tier is the initial live AI provider.

Primary model:

```text
gemini-3.1-flash-lite
```

The backend uses the official server-side Google Gen AI SDK/API and schema-constrained structured JSON output.

Provider-specific response objects stop inside the adapter.

## 52. Text model routing

Public demo:

```text
runtime explanation → gemini-3.1-flash-lite
```

No automatic paid escalation.

The application asks for a capability, not a model name.

## 53. Runtime image-generation contract

Public demo runtime image generation is disabled.

Current Gemini 3.1 Flash Image / Flash Lite Image API pricing lists no Free Tier, so the portfolio does not make billable image calls.

Images are:

- sourced;
- generated manually/offline during development;
- reviewed;
- stored as MediaAsset.

Provider adapter remains future/optional tooling only.

## 54. Demo safety contract

The zero-cost public demo does not add a separate paid moderation API.

Safety uses:

- provider safety/refusal behavior;
- schema validation;
- semantic validators;
- no arbitrary user prompt;
- human review for stored editorial/media assets.

If user-authored generative prompts are added later, reassess dedicated moderation.

## 55. AI timeout/retry

Text and image capabilities have separate bounded policies.

Retry only selected transient conditions:

- connection failure;
- provider 5xx;
- 429 under bounded Retry-After policy.

Do not blind-retry:

- refusal;
- moderation/safety block;
- invalid input;
- budget block;
- auth/config error.

## 56. Structured-output semantic validation

Provider schema adherence is followed by application validation.

Examples:

- fact IDs must exist in supplied packet;
- output cannot introduce unknown source URLs;
- dates/currencies must match packet;
- lengths are bounded;
- historical causal claims follow policy.

AI output is not accepted merely because JSON parses.

## 57. AI source packet

Text generation receives a normalized packet created by application/domain code.

Do not send:

- raw QuerySet serialization;
- arbitrary HTML;
- database credentials;
- complete application state;
- arbitrary user prompt as system-level instruction.

## 58. AI tool policy

P0/P1 Gemini calls do not enable:

- web search;
- file search;
- shell/code execution;
- arbitrary function tools;
- MCP;
- database access.

All source retrieval occurs before the AI call through deterministic application code.

## 59. Provider error normalization

Map Gemini SDK/provider failures into project-level categories:

```text
AIProviderTimeout
AIProviderUnavailable
AIRateLimited
AIInvalidResponse
AIRefusal
AISafetyBlocked
AIBudgetExceeded
AIConfigurationError
```

Raw provider exceptions never reach templates/mobile.

## 60. Usage metadata

Capture when available:

- provider/model;
- input/output tokens;
- reasoning/usage metadata;
- image count;
- latency;
- response/provider request ID;
- estimated cost.

Usage metadata is operational.

It does not enter historical/domain truth.

## 61. Explanation cache

Before a Gemini live call, check the persistent application cache using the normalized packet/prompt/model/locale identity.

Repeated identical demo interactions should normally be served without consuming provider quota.

Correctness/fallback must not depend on any provider-side cache behavior.

## 62. Gemini free-tier privacy/data controls

Google currently marks Gemini Developer API Free Tier content as used to improve Google products.

Therefore public-demo live AI sends only public/non-sensitive structured product data.

Do not send:

- names/emails;
- precise user location;
- private trip notes;
- authentication data;
- account history.

A future feature needing private data must move to an appropriate data-control tier/provider or remain deterministic.

## 63. Provider model lifecycle

AI model names can change/deprecate.

Model upgrade procedure:

```text
provider announces/desired upgrade
→ run project eval set
→ compare trust/style/cost/latency
→ update routing config
→ deploy
```

Existing published AI-derived media/prose does not regenerate automatically.
