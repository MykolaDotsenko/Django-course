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

## 2. Target app boundaries

```text
apps/
├── accounts/
├── countries/
├── exchange/
├── culture/
└── travel/
```

### accounts
Identity, user preferences and authenticated ownership.

### countries
Country/currency metadata and relationships.

### exchange
FX provider integration, conversion rules, rate metadata and historical series.

### culture
Curated cultural profile, money etiquette and typical-price context.

### travel
Favourites, recent conversions, saved trips and budgets.

## 3. Why not more apps?

App boundaries should correspond to durable domain capabilities. Avoid “services”, “utils”, “core” and “common” dumping grounds unless a concrete cross-domain responsibility exists.

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
