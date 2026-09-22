
# Application Services and Domain Orchestration

This document defines the backend use cases, service boundaries, input/output objects and error ownership.

The goal is to avoid two opposite failures:

1. fat views/serializers that own business logic;
2. architecture ceremony where every ORM call is wrapped by a meaningless service.

---

# 1. Use-case rule

Create an application service/use-case when behavior crosses a real boundary.

A use case is justified when it coordinates one or more of:

- provider access;
- cache;
- multiple models;
- transaction;
- non-trivial domain calculation;
- shared web/mobile behavior;
- authorization/business ownership.

A plain one-model read does not automatically need a service.

---

# 2. Command/query input objects

Use explicit immutable input objects where a use case has several semantically important parameters.

Example:

~~~python
@dataclass(frozen=True)
class QuoteConversionCommand:
    amount: Decimal
    base: CurrencyCode
    quote: CurrencyCode
    source_country: CountryCode | None
    destination_country: CountryCode | None
    requested_date: date | None
~~~

Benefits:

- no dependency on Django request object;
- web/API reuse;
- deterministic tests;
- easier validation boundaries.

Do not create DTOs for trivial one-argument helper functions.

---

# 3. Result objects

Application results should be explicit.

Example:

~~~python
@dataclass(frozen=True)
class ConversionResult:
    input_amount: Decimal
    output_amount: Decimal
    quote: RateQuote
    source_country: CountryCode | None
    destination_country: CountryCode | None
    status: ConversionStatus
~~~

Result objects do not contain:

- HttpResponse;
- DRF Response;
- rendered HTML;
- serializer instances.

---

# 4. Quote current conversion

Suggested public application function:

~~~text
quote_conversion(command) -> ConversionResult
~~~

Responsibilities:

1. validate supported currencies;
2. recognize same-currency fast path;
3. determine source policy;
4. obtain normalized quote from quote gateway/cache;
5. classify fresh/stale;
6. calculate Decimal output;
7. return provenance-rich result.

It does not:

- render;
- save conversion history by default;
- load cultural context;
- call mobile-specific code.

## 4.1 Converter submission orchestration

The implemented web converter calls one request-independent page-level use case:

~~~text
ConverterSubmissionCommand
→ run_converter_submission(...)
→ ConverterSubmissionResult
~~~

This orchestration layer coordinates:

- canonical currency metadata needed for minor units and historical lifecycle checks;
- current vs historical quote service selection;
- historical currency-era suggestions;
- optional destination context after a successful conversion.

It returns domain/application objects only. It does **not** know about `HttpRequest`, response
status codes, templates, HTMX headers or user-facing error copy.

Current destination context is deliberately non-fatal: on current conversions, a
context-composition failure is logged and returns `destination_context=None` while the trusted
conversion remains successful. Historical conversion does not compose current destination context
automatically; today's travel context is a separate validated culture query/action. This preserves
both the arithmetic invariant and the historical/current temporal boundary.

The Django view remains the composition/transport boundary: it parses form/request state, supplies
gateway factories, calls this one use case, maps known FX errors to HTTP/presentation states and
renders the result.

---

# 5. Quote historical conversion

~~~text
quote_historical_conversion(command)
→ HistoricalConversionResult
~~~

Responsibilities:

- validate requested date;
- validate lifecycle/coverage where known;
- preserve requested date;
- retrieve/normalize provider observation;
- apply historical fallback policy;
- expose effective observation date;
- calculate output.

Potential error outputs:

- UnsupportedCurrency;
- HistoricalOutOfCoverage;
- HistoricalObservationUnavailable;
- RateTemporarilyUnavailable.

---

# 6. Quote gateway boundary

Application code should not know cache transport details.

Conceptual helper:

~~~text
get_rate_quote(query) -> RateQuote
~~~

This can internally coordinate:

~~~text
fresh cache
→ provider
→ stale cache fallback
~~~

But avoid an abstract class hierarchy merely to represent this sequence.

A focused module/function is enough.

---

# 7. Provider interface

Minimal conceptual interface:

~~~python
class FxProvider(Protocol):
    def latest_quote(...) -> ProviderRateObservation: ...
    def historical_quote(...) -> ProviderRateObservation: ...
    def time_series(...) -> ProviderRateSeries: ...
~~~

Provider output is still normalized infrastructure output, not final application result.

The Frankfurter implementation owns HTTP shape.

---

# 8. Historical observation policy

Separate the provider data from product fallback policy.

Concept:

~~~text
resolve_historical_observation(
    requested_date,
    available_observations,
    policy
)
~~~

Policy answers:

- exact observation preferred;
- direction = on or before;
- maximum gap;
- lower-frequency semantics.

Provider does not silently decide UX truth.

---

# 9. Time-series query service

~~~text
get_rate_series(query) -> RateSeriesResult
~~~

Responsibilities:

- validate bounded date range;
- select grouping;
- cache series;
- normalize observations;
- derive summary stats;
- return granularity/source.

Do not mix chart pixel geometry into backend.

---

# 10. Country/currency lookup

Simple query logic belongs in QuerySets/managers.

Examples:

~~~python
Currency.objects.active()
Currency.objects.available_on(date)
CountryCurrency.objects.primary_for(country, date)
~~~

Use a service only if the result combines several sources/decisions.

---

# 11. Search currencies/countries

Web picker query:

~~~text
search_currency_options(
    query,
    mode=current|historical,
    date=None
)
~~~

Responsibilities:

- local DB only;
- search normalized names/codes;
- prioritize the user's current selection when the query is empty;
- prioritize exact currency/country matches when the user searches;
- prioritize active currencies in current mode;
- expose archived/historical status in historical mode;
- respect the selected historical date for country/currency relationships;
- bounded result count.

Implemented web ownership:

```text
Django request/view
→ parse transport-only side/query/date/current selection
→ search_currency_options(...)
→ presentation dictionaries
→ picker fragment
```

The query service receives typed values rather than `HttpRequest`, so the same relevance rules can
be reused by a future API/mobile surface and tested without fabricating HTTP state.

No provider call.

---

# 12. Destination context

~~~text
build_destination_context(query)
→ DestinationContext
~~~

Coordinates:

- CulturalProfile;
- published TypicalPrice rows;
- source freshness;
- equivalent counts;
- optional location scope.

Does not call external APIs at runtime.

---

# 13. Typical-price calculation

Use a pure domain function.

~~~text
calculate_purchase_equivalent(
    converted_amount,
    price_low,
    price_high
)
~~~

Return numeric range plus status such as:

- below_one;
- range;
- large_count.

Presentation owns final wording.

---

# 14. Payment guidance

Payment/cash/tipping data is read-only curated context.

Prefer QuerySet/read composition unless multiple rules justify a service.

Output object can preserve:

- statement;
- source;
- scope;
- verified_at;
- confidence/source class.

---

# 15. Money story composition

~~~text
build_money_story(query)
→ MoneyStory
~~~

Coordinates:

1. historical conversion identity;
2. country/currency era;
3. transitions;
4. published StoryMoments;
5. optional Then & Now;
6. deterministic chapter composer.

Story composition should be mostly pure after data has been loaded.

---

# 16. Then & Now comparison

Pure domain function:

~~~text
compare_rate_results(
    historical,
    latest
) -> ThenNowComparison
~~~

Requirements:

- same directional pair semantics;
- compatible provider policy;
- no retired-currency fake current quote;
- explicit percentage direction.

No investment-return interpretation.

---

# 17. Favourite save

~~~text
save_favourite(actor, command)
→ FavouriteResult
~~~

Responsibilities:

- authenticate actor;
- validate normalized pair/context;
- idempotent get/create;
- rely on DB unique constraint.

Do not use pessimistic locks.

---

# 18. Favourite delete

~~~text
delete_favourite(actor, favourite_id)
~~~

Query is ownership-scoped.

Repeated delete may return:

- 204 if API chooses idempotent semantics;
- 404 after absence.

Choose one behavior and keep it consistent.

---

# 19. Merge local favourites

~~~text
merge_favourites(actor, command)
→ MergeResult
~~~

Use a transaction if the merge is intended as one atomic import.

Inputs are bounded.

Do not accept thousands of arbitrary client records.

---

# 20. Recent conversions

P0/P1:

- anonymous recents can remain client-local.

If server history is introduced later:

~~~text
record_conversion_history(...)
~~~

should be explicitly opt-in/defined, not a hidden side effect of every quote request.

Privacy policy drives persistence.

---

# 21. Create trip

~~~text
create_trip(actor, command)
→ TripResult
~~~

Responsibilities:

- authorization;
- validate dates/home currency;
- atomic Trip + initial budget rows;
- optional pre-fetched reference quote metadata.

Network access occurs before transaction.

---

# 22. Update trip

~~~text
update_trip(actor, command)
~~~

Potential later optimistic version semantics.

Application service verifies actor and version before durable write.

A 409 Conflict is an expected application outcome, not a server failure.

---

# 23. Trip budget recalculation

Avoid mutating persisted budget values merely because current exchange rates changed.

Prefer explicit distinction:

- stored budget in home/destination currency;
- last quoted reference projection;
- current projection calculated on request.

If refreshed values are persisted, store quote provenance/effective date.

---

# 24. Account-related services

Keep account services narrow.

Examples:

- delete account;
- export user data;
- merge anonymous favourites;
- update explicit preferences.

Authentication plumbing belongs to Django/auth packages, not custom domain abstractions unless needed.

---

# 25. Authorization input

Application commands that mutate user-owned resources should receive an actor identity.

Concept:

~~~text
Actor
- user_id
- authenticated
~~~

Avoid passing whole HttpRequest into domain/service functions.

---

# 26. Ownership policy

Ownership belongs in durable backend logic.

Patterns:

- ownership-scoped QuerySet;
- permission helper;
- application service assertion.

Do not rely on serializer-only or UI-only checks.

---

# 27. Import service: countries

~~~text
fetch_country_snapshot()
→ validate_country_snapshot()
→ plan_country_diff()
→ apply_country_diff()
~~~

Separation allows:

- dry run;
- fixture tests;
- no DB write on invalid remote snapshot.

Management command merely orchestrates.

---

# 28. Import service: cultural facts

Potential flow:

~~~text
fetch_candidate()
→ normalize_candidate()
→ store_unpublished_candidate()
→ editorial verification
→ publish
~~~

Do not use bulk auto-publish for trust-sensitive historical claims.

---

# 29. Statistical import services

Future:

~~~text
sync_hicp_dataset(...)
sync_ppp_dataset(...)
~~~

Each dataset adapter keeps methodology/units explicit.

Do not create one generic “statistics fetcher” that loses dataset meaning.

---

# 30. Cache invalidation service

Avoid a global magical cache invalidator.

Each domain knows which cache namespaces it owns.

Examples:

- exchange invalidates exchange quote/series namespaces;
- culture invalidates destination/story namespaces.

Use transaction.on_commit after durable writes.

---

# 31. Request-independent use cases

A strong architecture test:

Can the use case be called from:

- Django view;
- DRF view;
- management command;
- test?

without constructing a fake HTTP request?

If no, transport concerns may have leaked inward.

---

# 32. Forms

Django Forms own:

- input parsing;
- field-level validation;
- user-friendly errors;
- conversion from raw text to typed command input.

They do not own:

- provider request;
- cache;
- historical fallback;
- Decimal business conversion.

---

# 33. DRF serializers

Serializers own:

- request/response shape;
- syntactic validation;
- conversion to typed command input.

They do not own:

- provider calls;
- persistence workflows beyond simple serializer-native CRUD where genuinely appropriate;
- domain arithmetic.

For trust-critical endpoints, explicit use-case invocation is preferred.

---

# 34. Model methods

Model methods are appropriate for local entity behavior.

Examples:

- mark_verified();
- publish() if rules are entity-local;
- display helpers with no external dependencies.

Avoid model methods that:

- make HTTP calls;
- coordinate several aggregates;
- send emails;
- mutate caches directly.

---

# 35. Signals

Use Django signals sparingly.

Avoid signals for core business workflows because control flow becomes implicit.

Good uses may include:

- framework integration;
- truly cross-cutting decoupled hooks.

Prefer explicit service call for:

- creating dependent business records;
- cache invalidation;
- critical side effects.

---

# 36. transaction.on_commit

Use explicit on-commit registration in the service that owns the write.

Good:

~~~text
publish story
→ commit
→ invalidate story cache
~~~

Avoid hiding critical behavior in post_save signal.

---

# 37. Domain exceptions

Use typed exceptions or result variants for expected domain/application failures.

Do not use generic ValueError for everything.

Suggested hierarchy:

~~~text
DomainError
ApplicationError
ProviderError
~~~

Presentation maps known errors to stable user/API states.

---

# 38. Exception ownership

## Provider adapter

Catches:

- HTTP timeout;
- connection;
- provider status;
- schema/parsing.

Emits normalized provider exception.

## Application

Decides:

- stale fallback;
- user-visible unavailability;
- coverage meaning.

## Presentation

Decides:

- HTTP status;
- error code;
- HTML copy.

---

# 39. Retry ownership

Provider HTTP client may retry only safe transient network cases under a strict latency budget.

Application should not wrap a provider call in uncontrolled retry loops.

Mobile should not retry aggressively when Django already retries/falls back.

One layer owns each retry.

---

# 40. Idempotency ownership

Examples:

- quote request: naturally repeatable;
- save favourite: unique constraint + get/create;
- delete favourite: repeatable policy;
- import: stable external IDs + upsert;
- trip create: potential idempotency key only if duplicate-create risk becomes real.

Do not introduce global idempotency middleware before there is a use case.

---

# 41. Validation layering

Example amount:

Transport/form:

- parse decimal text;
- reject empty/invalid characters.

Domain:

- supported range;
- nonnegative;
- precision rule.

Database:

- usually not persisted for basic conversion.

Example TypicalPrice:

Form/admin:

- helpful field errors.

Domain/model:

- low/high consistency.

Database:

- check low > 0;
- high >= low.

---

# 42. Query modules

If an app develops complex optimized read assembly, a queries.py/selectors.py module may be justified.

Example:

~~~text
culture/queries.py
- destination_context_queryset()
- published_story_moments(...)
~~~

Do not create a selector layer around every QuerySet.

---

# 43. Batch operations

Bulk import should prefer:

- bulk_create;
- bulk_update;
- upsert patterns where supported and clear.

But correctness/provenance beats minimizing query count.

Do not bypass model/constraint rules accidentally for speed.

---

# 44. Admin service reuse

Django admin actions should call the same application functions where behavior is non-trivial.

Example:

~~~text
admin action "Publish"
→ publish_story_moment(...)
~~~

Do not implement a second publication rule only inside ModelAdmin.

---

# 45. Service naming

Prefer verbs reflecting use cases:

- quote_conversion;
- build_destination_context;
- publish_story_moment;
- sync_country_metadata.

Avoid vague classes:

- DataManager;
- GeneralService;
- HelperService;
- BusinessLogicManager.

---

# 46. Class vs function

Default to functions/dataclasses.

Use a class when it has meaningful injected dependencies or lifecycle.

Example justified:

~~~python
class FrankfurterProvider:
    def __init__(self, client, config): ...
~~~

Example probably unjustified:

~~~python
class CurrencyService:
    @staticmethod
    def get_currency(...): ...
~~~

---

# 47. Dependency injection style

Do not add a DI framework.

Use ordinary Python construction/default factories.

Tests can inject:

- fake provider;
- fake clock;
- cache stub.

Example:

~~~text
quote_conversion(command, provider=default_provider, clock=system_clock)
~~~

or compose dependencies in a small application object if complexity grows.

---

# 48. Clock abstraction

A tiny clock abstraction can be justified for:

- stale classification;
- “future date” checks;
- deterministic tests.

Avoid scattered timezone.now()/date.today() where date semantics need control.

Could be as simple as passing now/today to pure domain functions.

No framework needed.

---

# 49. Configuration access

Do not read Django settings deep inside every pure domain function.

Infrastructure/application composition can read settings and pass:

- timeout;
- source policy;
- historical max-gap;
- cache freshness thresholds.

This improves testability.

---

# 50. Feature state

Use explicit enum/value types.

Examples:

~~~text
QuoteFreshness:
- fresh
- stale

ObservationGranularity:
- daily
- monthly
- quarterly
- unknown

ConversionMode:
- latest
- historical
~~~

Avoid boolean combinations that can form invalid states.

---

# 51. Status/result over booleans

Prefer:

~~~text
status = stale_success
~~~

over:

~~~text
success=true
stale=true
error=false
offline=false
~~~

when combinations have semantic meaning.

This reduces impossible state combinations.

---

# 52. Use-case test contract

Every use case test suite should cover:

- normal success;
- boundary values;
- provider/DB failure where relevant;
- stale/fallback;
- permission failure;
- idempotency;
- concurrency if mutation is shared;
- provenance fields.

Tests should assert domain result, not only rendered HTML.

---

# 53. No hidden side effects

quote_conversion() should not unexpectedly:

- write history;
- create user rows;
- send analytics events;
- update profile.

Any durable side effect should be explicit.

This protects privacy and makes the function safe for repeated web/mobile use.

---

# 54. Domain purity goal

The most important arithmetic and semantic rules should run without:

- database;
- network;
- Django request;
- templates.

Examples:

- convert amount;
- classify stale;
- compare Then & Now;
- choose historical observation from candidates;
- derive purchase-equivalent range.

This gives high-confidence unit tests.

---

# 55. Application acceptance criteria

The application layer is well designed when:

- views are thin;
- API and web call the same use cases;
- providers are swappable behind explicit adapter;
- durable writes define transaction boundaries;
- no service wraps trivial CRUD for ceremony;
- expected failures have typed outcomes;
- no HTTP object enters domain logic;
- imports can run from command/test without command-specific logic;
- core financial rules are pure and independently testable.
