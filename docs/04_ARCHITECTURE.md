# Architecture

## 1. Architectural style

Use a **Django modular monolith**.

Web delivery:

```text
Browser
  ↓
Django URL/view
  ↓
application/domain service when needed
  ↓
Django ORM / provider adapter
  ↓
Django template
  ↓
HTMX fragment update
```

Mobile delivery:

```text
React Native
  ↓
/api/v1
  ↓
DRF serializer/view
  ↓
same domain/application services
  ↓
ORM / provider adapter
```

The web and mobile paths share domain behaviour, not presentation code.

## 2. Application boundaries

Current implemented boundaries:

```text
apps/
├── common/
├── countries/
├── exchange/
├── culture/
├── media/
└── travel/
```

Planned durable boundaries are added only when their roadmap phase ships:

```text
apps/
└── accounts/   # PR12
```

### common
Strictly cross-cutting web/runtime infrastructure: health checks, request context/observability,
the repo-owned Vite bridge and design-preview presentation helpers. It owns no business model and
must not become a generic utility dumping ground.

### countries
Country/currency metadata and temporal relationships.

### exchange
FX provider integration, conversion rules, rate metadata and historical series. The converter page
uses a request-independent application orchestrator (`apps.exchange.application`) so Django views
remain transport/presentation adapters rather than cross-domain workflow owners.

### culture
Curated payment/cash/tipping context, TypicalPrice observations, StoryMoment facts and deterministic
money/culture composition.

### media
Managed media assets, rights/provenance, ingestion boundaries, derivatives, publication states and
runtime media selection. Media is independent from cultural fact ownership.

### accounts
Future identity, user preferences and authenticated ownership.

### travel
Owns the Saved & recent web surface and, later, authenticated favourite/trip persistence. PR11
Phase A intentionally stores anonymous favourites/recents in versioned browser localStorage; the
travel app renders the server shell but does not receive or persist that anonymous history.

## 3. Why not more apps?

App boundaries correspond to durable capabilities. Avoid generic “services”, “utils”, “core” and
“common” dumping grounds. The existing `apps.common` is a deliberate exception limited to
cross-cutting HTTP/build/observability infrastructure; domain behavior belongs in its owning app.

## 4. Web rendering

Django templates own full-page HTML.

HTMX requests may return partials.

When the same URL can render a full document or HTMX fragment, responses must account for HTTP caching semantics, including `Vary: HX-Request` where appropriate.

Do not create a parallel client-side state architecture.

## 5. Service-layer rule

A service function/class is justified when it coordinates:

- external provider access;
- multiple models;
- a transaction;
- non-trivial domain calculation;
- cross-interface behaviour shared by web and API.

Do not wrap ordinary ORM CRUD merely to say “service layer”.

Examples:

```text
convert_money(...)
get_latest_rate(...)
build_destination_context(...)
create_trip_budget(...)
```

## 6. Provider adapters

External data must sit behind explicit adapters.

Example:

```text
exchange/providers/
├── base.py
└── frankfurter.py
```

Provider responses are validated and normalized before entering the domain.

The rest of the code should not know Frankfurter's raw payload shape.

## 7. Caching

Start with Django's cache abstraction.

Cache classes:

### Latest FX
Short TTL based on provider update cadence.

Cache key includes:

- base;
- quote;
- provider scope when applicable.

### Historical FX
Long-lived because historical observations are immutable or rarely corrected.

### Country metadata
Long TTL.

### Cultural content
Database-backed; cache only if profiling justifies it.

Redis is not required for the first implementation. The cache backend remains configurable.

## 8. Database

Development can use SQLite only for low-friction local bootstrap if required.

Production and CI target PostgreSQL.

Reasons:

- production realism;
- constraints;
- indexing;
- future search capabilities;
- consistent deployment story.

## 9. Financial arithmetic

Never use binary floating point for money or rates.

Use `Decimal`.

Explicitly define:

- input quantization;
- intermediate precision;
- output rounding;
- currency minor units.

Do not round intermediate calculations earlier than necessary.

## 10. Transactions

Use `transaction.atomic()` only around operations that require multi-write atomicity.

Examples:

- creating a saved trip with dependent budget items;
- booking-like future flows if any.

Simple reads/conversions do not need transactions.

## 11. URL design

Web:

```text
/
 /convert/
 /countries/<iso2>/
 /history/
 /saved/
 /trips/
```

API:

```text
/api/v1/countries/
/api/v1/currencies/
/api/v1/rates/
/api/v1/conversions/quote/
/api/v1/destinations/<iso2>/context/
/api/v1/favourites/
/api/v1/trips/
```

Do not expose internal model naming accidentally as public API design.

## 12. Settings

Use environment-driven settings.

At minimum:

- `DJANGO_SECRET_KEY`;
- `DJANGO_DEBUG`;
- `DJANGO_ALLOWED_HOSTS`;
- `DATABASE_URL` or equivalent explicit DB settings;
- cache configuration;
- provider base URL/timeouts if configurable.

Production must fail fast when required secrets are absent.

## 13. Static assets

Tailwind builds CSS at development/build time.

Do not require a Node runtime in the production request path.

Static assets are collected and served using an explicit production strategy.

## 14. Observability

Minimum production signals:

- structured application logs;
- provider failure logs without leaking secrets;
- request correlation where useful;
- health/readiness endpoint;
- startup configuration validation.

Metrics/tracing can be added after the deployment baseline exists.

## 15. Dependency direction

Desired dependency rule:

```text
presentation
    ↓
application/domain
    ↓
models + provider interfaces
    ↓
infrastructure adapters
```

Templates never call external APIs.

Models do not perform network I/O.

Provider adapters do not render HTTP responses.

## 16. Anti-patterns

Reject by default:

- microservices;
- generic repository pattern around Django ORM;
- global event bus;
- CQRS for CRUD-scale needs;
- Redux-like web state;
- Celery before an actual asynchronous workload exists;
- Redis just because it is common;
- duplicated web/mobile business rules;
- remote API calls inside model `save()`;
- unsourced cultural content.


## 17. Historical conversion architecture

Historical conversion reuses the same exchange domain rather than creating a parallel subsystem.

Conceptual flow:

```text
requested date
     ↓
historical query validation
     ↓
provider adapter
     ↓
normalized historical RateQuote
     ↓
Decimal conversion
     ↓
historical result
     ├── HTML result
     ├── JSON API
     ├── historical chart
     └── story composer
```

There must be one normalized quote semantics shared by all presentation paths.

## 18. Historical observation lookup

The provider adapter is responsible for:

- translating requested date to provider request format;
- validating response;
- detecting missing observation;
- resolving provider-supported fallback policy;
- exposing actual effective date;
- exposing observation granularity where known;
- exposing coverage failures distinctly from transient provider failures.

Application/domain code should not inspect raw provider payloads.

## 19. Historical fallback policy

The domain does not pretend every calendar day has an observation.

For daily datasets, a candidate policy is:

- choose most recent supported observation on or before requested date;
- only within a bounded window;
- return both requested and effective dates.

For monthly/low-frequency datasets:

- preserve actual provider period/date;
- do not imply daily precision.

The precise provider policy must be contract-tested against Frankfurter/provider behaviour before implementation is frozen.

## 20. Historical cache

Use a distinct cache namespace for normalized historical observations.

Candidate key inputs:

- provider/provider-set;
- base;
- quote;
- requested/effective date policy;
- normalized effective date where known.

Historical observations can have very long TTLs, but invalidation must remain possible if a provider corrects source data.

## 21. Story composer

Storytelling is an application-layer composition service.

Concept:

```text
compose_money_story(
    historical_conversion,
    country_context?,
    currency_era?,
    transitions[],
    story_moments[],
    latest_comparison?
) -> StoryChapter[]
```

Rules:

- no network I/O inside templates;
- no raw provider payload in story layer;
- no LLM dependency in core storytelling;
- no chapter without source-backed facts where factual claims are involved;
- no story error can invalidate a successful conversion.

## 22. Story data path

```text
curated DB facts
+ normalized exchange data
        ↓
relevance/filtering
        ↓
deterministic story composer
        ↓
template chapters
```

Optional future AI rewriting sits after validated story context and before final presentation, with deterministic fallback.

## 23. Historical chart

Charts query time-series data through the same provider boundary.

Do not fetch an entire series merely to answer one date conversion.

Single historical conversion:

- single quote/date-oriented provider call.

Chart:

- explicit range query;
- aggregation/granularity chosen deliberately;
- cached separately.

## 24. Temporal context boundary

Current travel context and historical FX are separate data domains.

Historical mode must not automatically combine:

- 1998 FX result;
- 2026 typical prices;
- 2026 payment customs;

without explicit current-context labeling.

A future historical-purchasing-power service would be separate from `exchange` and use its own data adapters/methodology.

## 25. Historical API contract

The existing conversion quote API can accept an optional date rather than creating an unrelated endpoint.

Concept:

```text
POST /api/v1/conversions/quote/
```

Current request:

```json
{
  "amount": "100.00",
  "base": "EUR",
  "quote": "JPY"
}
```

Historical request:

```json
{
  "amount": "100.00",
  "base": "FIM",
  "quote": "USD",
  "date": "1998-06-15"
}
```

Response includes:

- `historical`;
- `requested_date`;
- `effective_date`;
- `observation_granularity`;
- `used_previous_observation`;
- provider/source metadata.

Web and mobile must interpret the same semantics.

## 26. Archived currency search boundary

Archived currency discovery should be driven by normalized currency metadata.

Do not hard-code FIM/DEM/etc. into templates.

The search/query layer can apply:

- current mode → active currencies prioritized/visible;
- historical mode → archived currencies eligible according to date/coverage.

## 27. Story observability

Useful structured logs/metrics may include:

- historical query success/failure class;
- fallback-observation use;
- out-of-coverage;
- story chapter availability.

Do not log private trip/account content merely for storytelling analytics.


## 28. External data-source architecture

External sources are classified by operational role.

### Class A — runtime source of truth

Used only when a user-facing request genuinely needs external data.

P0/P1:

- Frankfurter v2 for exchange-rate refresh.

Requirements:

- strict timeout;
- validated response;
- normalized provider adapter;
- cache;
- explicit stale/error state;
- provenance.

### Class B — scheduled/imported reference data

Fetched outside the user request path and persisted locally.

Examples:

- REST Countries metadata;
- Eurostat;
- OECD;
- World Bank statistical series.

The application continues using the last validated local snapshot when the upstream service is unavailable.

### Class C — editorial enrichment

Used to discover or ingest candidate cultural/story content.

Examples:

- Wikidata;
- Wikimedia Commons;
- Europeana.

Candidate data is reviewed/normalized before it becomes published product content.

### Class D — research/commercial candidate

Evaluated but not required by production.

Example:

- Numbeo for cost-of-living/item-price data.

This classification is defined in detail in `11_API_RESEARCH_AND_DATA_SOURCES.md`.

## 29. Critical request path

The desired request path is intentionally small:

```text
Browser / React Native
        ↓
Django
        ↓
local PostgreSQL + cache
        ↓
Frankfurter only when FX refresh is required
```

Country metadata, cultural facts, media metadata and official statistical observations must already be local by the time a user needs them.

Consequences:

- fewer outage modes;
- predictable latency;
- simpler tests;
- central licensing/provenance handling;
- no browser/mobile secret exposure.

## 30. No silent provider failover

A fallback FX source is not interchangeable merely because it returns the same currency codes.

Different providers may differ in:

- observation time/date;
- source institutions;
- blend methodology;
- frequency;
- available currencies;
- historical coverage.

Therefore a Frankfurter failure does not silently become an ECB or commercial-provider quote.

Recovery order:

```text
valid fresh cache
→ configured Frankfurter endpoint
→ safe same-semantics stale cache
→ explicit unavailable state
```

A self-hosted Frankfurter deployment can replace the public endpoint without changing domain semantics.

A different FX provider requires an explicit adapter/policy change and attribution.

## 31. Statistical adapter boundary

If historical purchasing-power work is approved, introduce statistical adapters only then.

Potential boundary:

```text
statistics/
└── sources/
    ├── eurostat.py
    ├── oecd.py
    └── world_bank.py
```

Do not create the app/module before a production feature needs it.

Statistical APIs are import dependencies, not page-render dependencies.

Their normalized observations retain:

- source;
- dataset/indicator ID;
- geography;
- period/frequency;
- unit/category;
- value;
- status/provisional metadata where available;
- retrieval metadata.

PPP/price-level and CPI/HICP datasets remain methodologically distinct.

## 32. Country metadata boundary

REST Countries is an import/enrichment source, not the domain schema.

The `countries` app owns canonical identifiers and normalized fields.

A sync command must:

- validate;
- map to ISO-style identifiers;
- be idempotent;
- avoid deleting valid local data because an upstream request failed;
- avoid committing or redistributing the provider's full raw dataset.

## 33. Cultural-source boundary

Wikidata, Wikimedia Commons and Europeana belong behind editorial/import tooling.

They are never called from a template or mobile client.

A publishable cultural/story record must have the provenance/licence fields required by its source class.

Media without sufficiently clear rights metadata is not publishable automatically.

## 34. External API implementation contract

Provider-specific details are governed by `12_EXTERNAL_API_CONTRACTS.md`.

Key rules:

- raw provider JSON never crosses into templates/API clients;
- adapters own parsing and schema validation;
- domain values use normalized types such as `Decimal`, ISO codes and explicit dates;
- finite timeouts are mandatory;
- retries are bounded and only used for safe/idempotent operations;
- secrets stay server-side;
- normal CI uses fixtures rather than the internet;
- health checks do not synchronously depend on all external services.


## 35. Web frontend delivery architecture

The web delivery path is intentionally HTML-first:

```text
Browser
  ↓
Django view
  ↓
Django template / named partial
  ↓
HTML
  ↓
HTMX progressively replaces small regions
```

A Vite/TypeScript asset layer enhances the rendered document but does not become a client application runtime.

Selected web frontend technologies are governed by:

- `13_FRONTEND_TECHNOLOGY_STRATEGY.md`;
- `14_WEB_FRONTEND_ARCHITECTURE.md`.

## 36. Frontend build-time/runtime separation

Build/development:

```text
Node 24 LTS
Vite 8
TypeScript 5.9
Tailwind 4
Biome
```

Production request path:

```text
browser
→ static built assets
→ Django
```

There is no Node server in the production request path.

## 37. Vite backend integration

Use Vite's official backend-manifest integration pattern.

Development:

- Vite dev server serves modules/HMR;
- Django serves HTML.

Production:

- `vite build` emits hashed static assets;
- `.vite/manifest.json` maps source entries to output;
- a small repo-owned Django template tag renders production asset tags.

Do not make a third-party Django/Vite integration package architecturally mandatory.

The repo-owned bridge is intentionally thin and unit-tested.

## 38. Web JavaScript ownership

Web TypeScript may own:

- HTMX lifecycle glue;
- accessible picker enhancement;
- dialog behavior;
- small anonymous local persistence;
- copy/share helpers;
- historical chart rendering.

It may not own:

- FX arithmetic;
- provider/source selection;
- historical observation fallback;
- country/currency domain validity;
- trust/freshness rules;
- story facts.

If those rules start appearing in TypeScript, the architecture has drifted.

## 39. Template fragment architecture

On Django 5.2 LTS, use `django-template-partials` for named inline fragments.

Reasons:

- shared initial/HTMX markup;
- fewer duplicate template branches;
- clean mapping between UI component and fragment response.

This is a compatibility choice.

Django 6+ native template partials should replace it when the backend eventually upgrades and the migration is justified.

## 40. HTMX integration

Use stable HTMX 2.x and `django-htmx`.

`django-htmx` provides:

- `request.htmx`;
- typed Django integration;
- HTTP helpers.

Vite owns the browser HTMX asset rather than loading a second vendored copy.

Cacheable views returning different full/partial representations must vary on `HX-Request`.

## 41. HTMX response integrity

For conversion and historical state, fragment boundaries are atomic.

A response that changes the result must include enough result-local metadata that the displayed:

- amount;
- pair;
- requested date;
- effective date;
- source status

always belong together.

Use HTMX synchronization/cancellation patterns to prevent obsolete requests from overwriting newer state.

## 42. Web native-platform preference

Before adding JavaScript UI libraries, prefer:

```text
semantic HTML
→ native browser API
→ focused small dependency
→ project-owned component
→ broad framework
```

Current examples:

- `<dialog>` for modal picker surfaces;
- `<details>/<summary>` for suitable disclosures;
- `<input type="date">` for web historical-date input;
- `Intl` for formatting;
- Clipboard/Web Share APIs when useful.

## 43. Mobile frontend architecture

The native mobile delivery path is:

```text
React Native / Expo
       ↓
typed API client
       ↓
TanStack Query
       ↓
Django /api/v1
```

Durable offline data is separate:

```text
Expo SQLite
       ↑ ↓
feature repositories
       ↑ ↓
screens/query functions
```

Detailed mobile frontend rules live in `15_MOBILE_FRONTEND_ARCHITECTURE.md`.

## 44. Mobile state ownership

Use three explicit state classes.

### UI state

React component/hooks.

Examples:

- search text;
- sheet open/closed;
- field draft.

### Remote server state

TanStack Query.

Examples:

- latest quote;
- destination context;
- story;
- time series.

### Durable local product state

Expo SQLite.

Examples:

- cached quotes;
- country/currency metadata;
- favourites;
- recent conversions;
- cached destination context.

Do not introduce a general global client-state store until a concrete unowned state problem appears.

## 45. Mobile API typing

Django's OpenAPI schema is the contract source.

Use:

- `openapi-typescript` for generated types;
- `openapi-fetch` for a small typed Fetch client.

Hand-written duplicate endpoint interfaces are discouraged.

## 46. Mobile historical visualization

The web and mobile chart implementations are presentation-specific.

Web:

- Chart.js.

Mobile:

- `react-native-svg`;
- a project-owned simple line-chart component.

Both consume the same normalized backend time-series contract.

Neither chart implementation owns rate semantics.

## 47. Frontend dependency principle

The project intentionally avoids cross-platform code sharing that creates worse platform code.

Share:

- domain/API semantics;
- copy terminology;
- design-token meaning;
- UX invariants.

Do not force sharing of:

- HTML/CSS components;
- React Native components;
- navigation primitives;
- chart rendering.

Architecture optimizes for clarity rather than percentage of shared frontend code.


## 48. Backend detailed-design contract

The high-level architecture in this file is expanded by:

- 16_BACKEND_SYSTEM_DESIGN.md
- 17_INFORMATION_FLOW_AND_REQUEST_LIFECYCLES.md
- 18_APPLICATION_SERVICES_AND_DOMAIN_ORCHESTRATION.md
- 19_DATA_CONSISTENCY_CACHING_AND_CONCURRENCY.md
- 20_API_SECURITY_OBSERVABILITY_AND_OPERATIONS.md
- 21_BACKEND_SCENARIO_CATALOG.md
- 22_DATA_IMPORT_JOBS_AND_MAINTENANCE.md

These documents are implementation constraints, not optional commentary.

## 49. Synchronous Django request model

The initial backend uses synchronous Django views and DRF views.

Do not introduce async views merely for provider I/O.

Django 5.2 still does not support transactions in native async mode, while this product requires clear ORM/transaction semantics and has only one normal runtime upstream provider.

A synchronous provider client with strict timeout is the default.

Reconsider async only after measured concurrency requirements justify it.

## 50. WSGI-first deployment

WSGI is sufficient for the initial production application.

ASGI is not a portfolio checkbox.

Adopt ASGI deliberately if the application later requires long-lived async connections, WebSockets or measured concurrent I/O that materially benefits.

## 51. Explicit transaction ownership

Global ATOMIC_REQUESTS is disabled.

Use short application-service transaction.atomic() blocks only where several durable writes form one invariant.

External network calls occur before opening the transaction.

After-commit cache invalidation or side effects use transaction.on_commit().

## 52. PostgreSQL concurrency policy

Use:

- database constraints for durable uniqueness/invariants;
- optimistic version checks for future multi-device aggregate edits where needed;
- select_for_update only for a demonstrated pessimistic-locking requirement.

Do not use broad locking as a default.

Concurrency-sensitive tests must run against PostgreSQL, not rely on SQLite behavior.

## 53. API schema generation

Use drf-spectacular for OpenAPI 3.

DRF's built-in OpenAPI generator is deprecated.

The generated schema is the source for mobile openapi-typescript types and is validated in CI.

## 54. Backend cache policy

Cache stores normalized reusable data, not domain truth.

For current FX, semantic freshness is separate from physical retention so a quote can remain available as an explicitly stale fallback.

Cache keys include all semantics that affect truth:

- current vs historical;
- provider policy;
- provider identity where pinned;
- pair;
- date/granularity for historical/series data.

## 55. Scheduled work policy

Slow-changing sources use management commands plus one canonical production scheduler.

No web request waits for REST Countries, Wikidata, Europeana, Eurostat, OECD or World Bank.

No Celery/task broker is introduced until a real asynchronous workload needs distributed execution/retry/status.

## 56. Backend fitness rule

Implementation is architecturally incorrect if:

- a view parses raw provider JSON;
- an API serializer performs FX arithmetic;
- a model performs network I/O;
- a cache is the sole copy of user/editorial state;
- a DB transaction contains remote HTTP;
- web and mobile call separate conversion implementations;
- raw upstream exceptions reach clients;
- a mutable user object can be updated without ownership enforcement;
- an import can wipe valid local data because the upstream response was partial.


## 57. Media architecture

Media is split into two delivery classes.

### Static release assets

Owned by the codebase:

- logo;
- icons;
- Quiet Atlas SVG patterns;
- small timeless illustrations.

Delivered through:

- Vite;
- Django staticfiles.

### Content media

Owned by product/editorial data:

- sourced archival media;
- contemporary editorial images;
- generated illustrations;
- derivatives.

Stored through Django's media Storage API, not Git.

## 58. Runtime media boundary

Normal user requests do not call:

- Wikimedia Commons search;
- Europeana search;
- OpenAI image generation;
- Stability image generation;
- Google image generation.

The request path reads only:

- published MediaAsset metadata from PostgreSQL;
- stored image derivatives.

This keeps imagery optional and failure-isolated.

## 59. Media ingestion/generation path

```text
source search / AI generator
        ↓
candidate
        ↓
rights / safety / relevance review
        ↓
MediaAsset metadata
        ↓
managed object storage
        ↓
publish
        ↓
user request can select it
```

No candidate auto-publishes.

## 60. Media storage

Development:

- FileSystemStorage / MEDIA_ROOT.

Production:

- Django Storage API;
- S3-compatible object storage through a backend such as django-storages when deployment requires it;
- CDN optional.

Application code must not depend directly on one cloud vendor.

## 61. AI generation boundary

AI generation is an editorial/background capability.

A provider adapter receives structured normalized generation requests.

The frontend/mobile never holds provider credentials or calls the image provider directly.

Core conversion does not wait for image generation.

## 62. Future on-demand generation

If a future user explicitly requests a generated illustration, generation becomes an asynchronous job.

That future feature is one concrete workload that can justify:

- task queue;
- broker;
- job states;
- per-user quota;
- idempotency;
- spend controls.

Do not add that infrastructure before the feature exists.

## 63. Historical visual truth boundary

A MediaAsset's visual authenticity class is part of domain truth.

Presentation must distinguish:

- real archival source;
- contemporary sourced media;
- AI-generated illustration;
- decorative asset.

AI output cannot be upgraded into evidence by styling or placement.


## 64. AI architecture position

AI is an optional infrastructure capability, not a source-of-truth domain.

Application flow:

```text
deterministic application/domain data
        ↓
capability-specific AI interface
        ↓
provider adapter
        ↓
Gemini Developer API
        ↓
structured candidate
        ↓
deterministic validation
        ↓
review/publish or discard
```

Core conversion/history/context remains fully functional with AI disabled.

## 65. Capability-specific AI interfaces

Do not create a generic `llm.generate(prompt)` service.

Use narrowly typed capabilities such as:

- NarrativeDrafter
- AltTextDrafter
- ImagePromptComposer
- ImageGenerator
- ContentModerator
- QualityAuditor

Each capability owns its own typed request/result schema.

## 66. Gemini provider isolation

A small infrastructure adapter owns:

- Google Gemini SDK/client construction;
- server-only auth key/project config;
- timeout/retry;
- provider error normalization;
- quota/usage metadata.

Domain/application code does not import provider model names.

## 67. Initial AI model routing

The public portfolio deployment intentionally uses one live free-tier model:

```text
runtime explanation → gemini-3.1-flash-lite
```

All paid-model routing and runtime image generation are disabled.

Stored/pre-generated media and deterministic story/context paths remain the default.

This minimizes dependencies, quota complexity and cost while still demonstrating a real typed AI integration.

## 68. Structured text output

Application-integrated text AI uses Gemini schema-constrained structured JSON output.

Schema correctness does not imply factual correctness.

Application validators still enforce:

- supplied fact IDs only;
- temporal/currency semantics;
- source references;
- output length;
- forbidden inferences.

## 69. No model-side retrieval in P1

Initial AI calls receive complete structured source packets.

Do not enable:

- web search;
- file search;
- DB tools;
- arbitrary function tools

for normal editorial generation.

The source/provenance system remains deterministic and local.

## 70. No autonomous agent loop

AI does not autonomously:

- search;
- retrieve;
- mutate;
- publish;
- call external business tools.

Each AI invocation is a bounded operation initiated by application/admin code.

## 71. AI external-call transaction rule

AI follows the same external-call rule as all providers:

```text
build input
→ call provider
→ validate candidate
→ open DB transaction if needed
→ persist candidate/approval
→ commit
```

No AI request runs while holding an intentional DB transaction or row lock.

## 72. AI persistence rule

Published AI-derived output becomes normal domain/editorial content.

Store enough generation metadata for traceability:

- capability;
- provider;
- model;
- prompt version;
- source packet/input hash;
- created/reviewed dates;
- moderation status;
- usage/cost estimate where useful.

Do not persist every raw provider response indefinitely by default.

## 73. AI failure isolation

AI failures affect only optional capabilities.

Examples:

- narrative draft unavailable;
- image generation unavailable;
- optional explanation unavailable.

They do not change:

- quote result;
- historical observation;
- local context;
- stored media;
- saved trips.

AI provider is never a liveness/readiness dependency.

## 74. AI privacy boundary

P0/P1 editorial AI receives only public/curated product data.

Do not send:

- user email/name;
- precise address;
- private trip notes;
- account history;
- auth credentials.

Any future user-facing personalized AI requires separate privacy/security review.

## 75. AI framework restraint

No LangChain/LlamaIndex/agent framework initially.

Direct provider SDK + typed application interfaces are simpler for the bounded use cases.

Add orchestration frameworks only after real repeated complexity justifies them.

## 76. AI retrieval restraint

No vector database/embedding layer initially.

Country/currency/date/story relevance is already represented structurally in PostgreSQL.

Use SQL/domain queries until semantic retrieval across a large unstructured corpus becomes a real requirement.
