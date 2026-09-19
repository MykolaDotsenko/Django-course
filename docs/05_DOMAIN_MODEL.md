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
