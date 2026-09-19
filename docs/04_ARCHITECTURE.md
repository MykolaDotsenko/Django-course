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
