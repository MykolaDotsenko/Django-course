# Domain Model

## 1. Domain principles

The model must distinguish:

- currency from country;
- rate from converted amount;
- authoritative facts from approximate context;
- current currency relationships from historical ones;
- anonymous browser state from user-owned durable data.

## 2. Country

Suggested fields:

```text
Country
- iso2: char(2), unique
- iso3: char(3), unique
- name
- official_name
- capital
- region
- subregion
- flag_asset / flag_reference
- is_active
- metadata_source
- metadata_verified_at
```

Avoid storing every field offered by a third-party countries API.

## 3. Currency

```text
Currency
- code: ISO-style code, unique
- name
- symbol
- minor_units
- is_active
```

Currency code is the stable public identifier.

## 4. CountryCurrency

A many-to-many relationship is required because:

- one currency can be shared by multiple countries;
- countries may have historic currencies;
- some jurisdictions use multiple currencies.

```text
CountryCurrency
- country
- currency
- is_primary
- valid_from
- valid_to
- source
```

Constraint goals:

- prevent duplicate active relationships;
- support historical relationships without overwriting history.

## 5. RateQuote value object

A fetched rate is conceptually:

```text
RateQuote
- base_currency
- quote_currency
- rate: Decimal
- effective_date/time
- fetched_at
- provider
- provider_sources[]
- stale: bool
```

P0 does not need to persist every quote in the database.

Cache normalized quotes; persist only when a durable audit/history requirement is introduced.

## 6. Conversion result

```text
Conversion
- input amount
- base
- quote
- rate
- output amount
- rate effective timestamp/date
- provider attribution
```

Conversion is a domain calculation, not necessarily a database row.

## 7. CulturalProfile

```text
CulturalProfile
- country: one-to-one
- summary
- payment_customs
- cash_usage
- tipping
- atm_notes
- dcc_warning
- source_notes
- verified_at
```

Large free-text blobs should remain structured enough that the UI can render sections independently.

## 8. CulturalFact

```text
CulturalFact
- country
- category
- title
- body
- source_url
- source_name
- verified_at
- display_order
- is_published
```

Suggested categories:

- currency_history;
- language;
- food;
- tradition;
- landmark;
- practical_travel.

## 9. TypicalPrice

```text
TypicalPrice
- country
- city: nullable
- category
- label
- amount_low: Decimal
- amount_high: Decimal, nullable
- currency
- source_url
- source_name
- observed_at
- confidence
- is_published
```

### Critical rule
A city-specific observation must never be presented as a universal national price.

## 10. FavouritePair

```text
FavouritePair
- user
- source_country
- source_currency
- destination_country
- destination_currency
- created_at
```

Unique constraint across owner + pair.

Anonymous favourites may initially remain client-local.

## 11. ConversionHistory

For signed-in durable history:

```text
ConversionHistory
- user
- amount
- base_currency
- quote_currency
- result
- rate
- rate_effective_at
- provider
- created_at
```

Do not store history automatically before privacy behaviour is explicit.

## 12. Trip

Later phase:

```text
Trip
- user
- destination_country
- start_date
- end_date
- home_currency
- budget_amount
- notes
- created_at
- updated_at
```

Constraints:

- end date >= start date;
- non-negative budget.

## 13. TripBudgetItem

```text
TripBudgetItem
- trip
- category
- planned_amount
- actual_amount: nullable
- currency
```

## 14. Data provenance

Every external datum that affects trust should support:

- source;
- effective/observed date;
- fetched/verified date;
- confidence/quality class where applicable.

## 15. Money rules

- use `Decimal`;
- no float conversion;
- normalize currency codes to uppercase;
- reject unknown currencies at boundaries;
- respect minor-unit metadata for final display;
- rate precision may exceed display precision;
- do not silently convert between country and currency concepts.

## 16. Domain invariants to test

- source and destination codes exist;
- country/currency combinations are valid for the selected context;
- rate > 0;
- amount obeys configured limits;
- result is deterministic for same amount/rate/rounding;
- stale rate retains original effective timestamp;
- historical country/currency relationships remain queryable;
- approximate prices cannot be published without source metadata.


## 17. Historical rate semantics

Historical queries require two separate temporal concepts.

### Requested date

The date the user asked about.

### Effective date

The actual provider observation used.

These can differ because:

- weekend;
- holiday;
- missing observation;
- low-frequency historical series.

The domain must never overwrite one with the other.

Concept:

```text
HistoricalRateQuery
- amount
- base_currency
- quote_currency
- requested_date
- provider_scope?
```

The normalized `RateQuote` contains the actual effective observation.

## 18. Observation granularity

Historical/provider data may be:

- daily;
- monthly;
- other/unknown.

Granularity affects what the UI is allowed to claim.

A monthly observation must not be represented as exact daily market/reference data.

The provider adapter owns raw provider interpretation and exposes normalized granularity where reliable.

## 19. Currency lifecycle

Currency availability is temporal.

Extend currency/domain metadata conceptually with:

```text
Currency
- code
- name
- symbol
- minor_units
- active_from?
- active_to?
- is_active
- coverage_from?
- coverage_to?
```

Important distinction:

- currency lifecycle;
- provider data coverage.

A currency can historically exist before the provider's available dataset.

Do not infer one from the other.

## 20. CountryCurrency historical relationship

The existing relationship becomes critical for historical UX.

```text
CountryCurrency
- country
- currency
- is_primary
- valid_from
- valid_to
- usage_role?
- source
```

The minimum implementation should support:

- current primary currency;
- historical primary currency;
- sourced date range.

If euro-transition nuance requires accounting/legal/cash milestones, use explicit transition metadata instead of forcing every milestone into `valid_from`.

## 21. CurrencyTransition candidate

Only introduce this model when stories require more than CountryCurrency date ranges.

```text
CurrencyTransition
- country
- from_currency
- to_currency
- transition_type
- announced_date?
- accounting_start?
- legal_tender_start?
- cash_changeover_date?
- legacy_end_date?
- fixed_conversion_rate?
- source_name
- source_url
- verified_at
```

Do not populate speculative or unavailable milestones.

## 22. StoryMoment

A story uses structured facts rather than free-generated narrative.

```text
StoryMoment
- countries: many-to-many
- currencies: many-to-many
- category
- title
- summary
- start_date
- end_date: nullable
- source_name
- source_url
- source_published_at: nullable
- verified_at
- relevance_weight
- is_published
```

Suggested categories:

- currency_introduction;
- currency_retirement;
- redenomination;
- monetary_union;
- cash_changeover;
- central_bank;
- cultural_money_fact;
- sourced_economic_context.

A StoryMoment does not claim that an event caused a rate movement unless its source explicitly supports that causal relationship.

## 23. StoryChapter value object

Story output is assembled, not stored as opaque generated prose.

Concept:

```text
StoryChapter
- kind
- title
- body
- source_refs[]
- temporal_scope
- relevance
```

Potential kinds:

- conversion;
- currency_era;
- transition;
- then_now;
- historical_moment;
- explore.

The story composer may return fewer chapters when data is incomplete.

## 24. Historical conversion result

Concept:

```text
HistoricalConversion
- input_amount
- base
- quote
- requested_date
- effective_date
- observation_granularity
- rate
- output_amount
- provider
- provider_sources[]
- used_previous_observation
```

It is a domain result/value object, not necessarily a database row.

## 25. Historical purchasing power boundary

Historical FX and historical domestic purchasing power are separate domains.

Do not add inflation-adjusted values to HistoricalConversion.

A future purchasing-power model would require explicit inputs such as:

```text
PurchasingPowerObservation
- country
- indicator/source
- period
- index/value
- base_period
- methodology
```

The model is intentionally not implemented until source/methodology research is complete.

## 26. Additional historical invariants

- requested date <= today;
- effective date <= requested date when using previous-observation fallback;
- historical result preserves requested date even when observation differs;
- no historical rate can exist outside normalized provider/pair coverage;
- observation granularity is exposed when it affects precision;
- archived/current status does not determine provider coverage automatically;
- country/date suggestions are sourced;
- archived currency cannot receive a fabricated current market quote;
- story facts must be published, temporally relevant and sourced;
- current TypicalPrice rows are not reused as historical purchasing-power observations.


## 27. Backend value objects

Critical cross-interface concepts should use explicit immutable value objects rather than loose dictionaries.

Recommended concepts:

- CurrencyCode
- CountryCode
- MoneyAmount
- ProviderPolicy
- RateQuote
- RateSeries
- ConversionResult
- HistoricalConversionResult
- QuoteFreshness
- ObservationGranularity
- DestinationContext
- PurchaseEquivalent
- ThenNowComparison
- StoryChapter

These objects are transport-agnostic.

Django forms, DRF serializers and React Native contracts map to/from them.

## 28. Conversion status

Use an enum/result state rather than several independent booleans.

Candidate values:

- fresh_success
- stale_success
- same_currency
- historical_exact
- historical_previous_observation

Failure states remain typed application errors.

This avoids impossible combinations such as success=true and unavailable=true.

## 29. Trip optimistic concurrency

When cross-device Trip editing becomes production scope, Trip may add:

- version: positive integer

Mutating commands include the version they read.

A successful update increments it.

A stale version produces a conflict rather than silent overwrite.

Do not add version fields to unrelated models without a concurrency need.

## 30. Favourite uniqueness

Authenticated FavouritePair should have a database uniqueness guarantee covering the canonical identity required by product semantics.

Candidate dimensions:

- user;
- base currency;
- quote currency;
- optional source country;
- optional destination country.

Normalize nullable/context semantics carefully so duplicate logical favourites cannot appear under concurrent requests.

## 31. TypicalPrice durable constraints

Database/model validation should guarantee:

- amount_low > 0;
- amount_high is null or >= amount_low;
- currency required;
- geography scope explicit;
- source required for publishable records;
- observed period/date required for publishable records.

Publication policy may be stricter than the database check.

## 32. StoryMoment publication constraints

A published StoryMoment must have, at minimum:

- category;
- temporal scope;
- source identity/URL;
- verified_at according to policy;
- relevant country and/or currency association.

Some rules are cross-relation and therefore enforced through application/admin validation rather than a single SQL check.

## 33. Imported source metadata

Imported canonical/reference rows should preserve enough source metadata to debug or refresh them without copying the entire raw payload.

Useful fields can include:

- source identifier;
- source external ID;
- fetched_at;
- source_updated_at/version where available;
- verified_at;
- import/source class.

The domain owns normalized values, not the provider schema.

## 34. ImportRun candidate

Introduce ImportRun only when recurring scheduled jobs need durable run history beyond structured logs.

Candidate fields:

- source;
- job_name;
- started_at;
- finished_at;
- status;
- source_version;
- counts;
- normalized error_code;
- small metadata JSON.

Do not create this table before it adds operational value.

## 35. Domain model concurrency rule

Durable correctness is protected at the lowest sensible layer:

- database constraint for uniqueness/range;
- transaction for multi-write invariant;
- optimistic version for multi-device aggregate conflict;
- application validation for cross-entity/domain rules.

Do not rely only on a pre-save "does this exist?" query where a concurrent request can race it.
