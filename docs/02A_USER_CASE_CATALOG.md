# User Case Catalog

This catalog turns the product idea into testable user situations.

Priority legend:

- **P0** — required for the first useful web release;
- **P1** — high-value follow-up;
- **P2** — later product expansion;
- **Research** — behaviour must be tested before implementation is treated as settled.

Each user case identifies:

- user intent;
- preconditions;
- primary path;
- important edge cases;
- expected UX outcome.

---

# A. Core Conversion

## UC-001 — Quick currency conversion

**Priority:** P0

### User intent

> I know an amount and two currencies. Tell me roughly what the amount becomes.

### Preconditions

- supported base currency;
- supported quote currency;
- amount entered.

### Primary path

1. User enters amount.
2. User selects From currency.
3. User selects To currency.
4. User activates Convert.
5. System retrieves or reuses a valid reference rate.
6. System calculates result.
7. System shows:
   - converted amount;
   - base/quote;
   - reference rate;
   - effective date;
   - source/provider;
   - transaction-rate disclaimer.

### UX outcome

The user can answer the arithmetic question in seconds without interacting with cultural content.

### Edge cases

- provider timeout;
- unsupported pair;
- stale same-pair cache;
- amount = 0;
- very large amount;
- decimal comma;
- same currency.

---

## UC-002 — Country-first travel conversion

**Priority:** P0

### User intent

> I am travelling from one country to another. I think in countries more naturally than currency codes.

### Example

Finland → Japan.

### Primary path

1. Search/select Finland.
2. Product suggests EUR.
3. Search/select Japan.
4. Product suggests JPY.
5. User enters amount.
6. Convert.
7. Result includes Japan-specific context.

### UX outcome

A user does not need to know ISO currency codes.

### Important rule

Country selection suggests currency; it does not silently overwrite an explicitly chosen currency without confirmation.

---

## UC-003 — Currency-first conversion without countries

**Priority:** P0

### User intent

> I only need EUR → USD. I do not care which countries use them.

### Primary path

1. User searches EUR.
2. Selects currency-only Euro.
3. User searches USD.
4. Selects currency-only US dollar.
5. Converts.

### UX outcome

The product behaves like a normal currency converter.

### Follow-up

The destination-context section may say:

> Choose a destination country to see local prices and money customs.

Country is not mandatory for arithmetic.

---

## UC-004 — Search by currency name/code/country name

**Priority:** P0

### User intent

> I know “yen”, “JPY” or “Japan”, but not necessarily all three.

### Expected matches

- Japan
- Japanese yen
- JPY

should all make the intended option easy to find.

### Acceptance

Search is tolerant of case and common spacing differences.

Do not depend on flags.

---

## UC-005 — Swap pair

**Priority:** P0

### User intent

> Reverse the direction quickly.

### Example

100 EUR → JPY becomes 100 JPY → EUR.

### Primary path

1. User activates Swap.
2. Full source/destination context exchanges.
3. Amount stays numerically unchanged.
4. Result updates.
5. Focus remains on Swap.

### Acceptance

No page reset and no country/currency mismatch.

---

## UC-006 — Same currency, same country context

**Priority:** P0

### Example

EUR → EUR with no meaningful country difference.

### Expected behaviour

Show:

> Same currency — 100 EUR remains 100 EUR.

Do not call provider unnecessarily if no contextual comparison is required.

---

## UC-007 — Same currency, different country context

**Priority:** P0 differentiator

### Example

Finland (EUR) → Italy (EUR).

### User intent

> The currency is the same, but what does this money mean at my destination?

### Expected behaviour

- monetary conversion = 1:1;
- destination context remains available;
- typical prices/payment customs/cultural content use Italy;
- product explicitly explains why the page is still useful.

### UX copy

> Same currency. Compare local value and money customs.

This is a signature use case that demonstrates why Country and Currency are separate concepts.

---

# B. Amount Input and Validation

## UC-010 — Decimal point amount

**Priority:** P0

Input:

```text
12.50
```

Expected:

valid.

---

## UC-011 — Decimal comma amount

**Priority:** P0

Input:

```text
12,50
```

Expected:

valid when unambiguous.

The displayed result uses locale-aware formatting; internal money remains canonical Decimal.

---

## UC-012 — Ambiguous grouped amount

**Priority:** P0

Input examples:

```text
1,234
1.234
```

where the intended grouping/decimal meaning cannot be safely inferred.

Expected:

do not silently guess.

Provide a clear example of accepted input without thousands separators.

---

## UC-013 — Invalid text amount

**Priority:** P0

Input:

```text
100 euros
```

Expected:

- no provider call;
- amount retained;
- field error;
- focus stays predictable.

---

## UC-014 — Negative amount

**Priority:** P0

Expected:

reject with specific error.

---

## UC-015 — Zero amount

**Priority:** P0 policy

Expected current decision:

zero may be accepted as valid arithmetic.

Result/context equivalents are zero.

This avoids an arbitrary business rule unless user testing shows it is confusing.

---

## UC-016 — Excessive amount

**Priority:** P0

Expected:

enforce a documented upper bound to prevent accidental/unhelpful values and abuse.

Do not silently clamp the amount.

---

## UC-017 — Excessive decimal precision

**Priority:** P0

Expected:

- do not mutate the field while typing;
- validate/normalize on successful conversion;
- final display respects currency minor-unit rules;
- calculation keeps sufficient intermediate precision.

---

# C. Country / Currency Relationship

## UC-020 — Currency used by many countries

**Priority:** P0

Example:

EUR.

### User intent

> Convert to EUR now; choose culture only if useful.

Expected:

- allow EUR conversion immediately;
- do not force Finland/France/Germany/etc.;
- destination context invites country selection when absent.

---

## UC-021 — Country with primary current currency

**Priority:** P0

Example:

Japan → JPY.

Expected:

Selecting Japan suggests JPY.

User may override only where product/domain rules permit a meaningful alternative.

---

## UC-022 — Country with multiple meaningful currencies

**Priority:** P1 / domain dependent

Expected:

do not pretend one relationship is universal.

Show available supported currency relationships with primary status/context.

---

## UC-023 — Historical currency

**Priority:** P2

Example:

DEM.

Expected:

Historical currency discovery belongs to currency-history/historical-rate contexts, not the normal current-conversion selector unless supported explicitly.

---

## UC-024 — Unsupported currency

**Priority:** P0

Expected:

- clear unsupported state;
- preserve user selections;
- offer supported alternatives/search;
- no generic “Something went wrong”.

---

# D. Trust, Freshness and Provider Behaviour

## UC-030 — Fresh/current reference rate

**Priority:** P0

Expected UI:

- result;
- reference rate;
- effective date;
- contributing/source provider;
- fetched time if useful.

Do not call it “live” unless provider semantics support real-time data.

---

## UC-031 — Weekend / no new official daily rate

**Priority:** P0

Scenario:

User converts on a day when the latest official/reference observation is from a previous business day.

Expected:

- show the real effective date;
- do not present the calendar-day fetch as the rate date;
- no alarming “error” merely because the reference rate is from Friday.

---

## UC-032 — Provider unavailable, same pair cached

**Priority:** P0

Expected:

- retain safe cached same-pair result;
- mark stale/cached;
- show effective/sync time;
- allow retry.

---

## UC-033 — Provider unavailable, no cache

**Priority:** P0

Expected:

- explain that reference rate is unavailable;
- no invented conversion;
- retain form;
- retry action.

---

## UC-034 — Provider unavailable after pair changed

**Priority:** P0 critical

Expected:

Never render previous-pair data under the new pair.

Example forbidden state:

User changes EUR/JPY → EUR/AUD, request fails, UI labels old JPY result as AUD.

This must be prevented architecturally and tested.

---

## UC-035 — Provider returns malformed/invalid response

**Priority:** P0

Expected:

Treat as unavailable.

Do not leak provider payload or stack trace.

Do not store malformed data as valid cache.

---

## UC-036 — Rate source details

**Priority:** P1

User wants to understand where the number came from.

Expected:

A source detail view/disclosure explains:

- provider;
- official contributing source(s) where available;
- effective date;
- reference-rate nature.

Keep this optional; do not overwhelm the default result.

---

# E. Local Purchasing Context

## UC-040 — Understand what converted amount buys

**Priority:** P0 differentiator

Example:

17,450 JPY.

Expected:

Show a short set of relatable approximate equivalents.

Each equivalent is derived from sourced observed/range data.

---

## UC-041 — Range-based context

**Priority:** P0

If typical coffee range is 500–650 JPY:

Do not show one exact count.

Prefer:

> roughly 26–34 coffees

with transparent underlying range.

---

## UC-042 — City-specific context

**Priority:** P0

Example:

Tokyo observation.

Expected:

Label Tokyo.

Never imply it is Japan-wide.

---

## UC-043 — Country-level context

**Priority:** P1

When a source genuinely describes a broader national estimate, label it accordingly.

Country-level data should not be visually indistinguishable from city observations.

---

## UC-044 — No price context

**Priority:** P0

Expected:

> Local price context is not available for this destination yet.

Conversion and payment guidance still work.

No synthetic default.

---

## UC-045 — Old contextual observation

**Priority:** P1

Expected:

Show observation date.

If content exceeds an editorial freshness policy, flag it for review or suppress publication rather than pretending it is current.

---

# F. Payment Guidance

## UC-050 — Traveller wants to know card vs cash

**Priority:** P0 differentiator

Expected:

Concise answer with qualified language.

Example:

> Cards are commonly accepted in cities; some cash may still be useful for smaller businesses.

Source/provenance accessible.

---

## UC-051 — Tipping customs

**Priority:** P0/P1 depending on data readiness

Expected:

- concise practical guidance;
- avoid absolute wording;
- identify variation when relevant.

---

## UC-052 — Dynamic currency conversion warning

**Priority:** P1

User is offered to pay in home currency at merchant/ATM.

Expected:

Explain concept neutrally:

> The merchant or ATM may set its own conversion rate. Compare it with paying in local currency before accepting.

Do not provide financial-advice certainty beyond supported facts.

---

## UC-053 — Bank/card fee estimate

**Priority:** P2

Expected:

Never invent a “typical fee” without explicit assumptions.

If later implemented, the user must see:

- fee model;
- percentage/fixed assumption;
- provider source or user-entered assumption;
- estimated nature.

---

# G. Cultural Experience

## UC-060 — Explore currency history

**Priority:** P1

Expected:

User can learn:

- currency introduction;
- previous currency where relevant;
- important historical context;
- source.

This does not block conversion.

---

## UC-061 — Explore destination culture

**Priority:** P1

Expected categories:

- money etiquette;
- languages;
- food;
- traditions;
- notable places;
- practical travel context.

Keep content curated and sourced.

---

## UC-062 — Culture data missing

**Priority:** P0 graceful degradation

Expected:

Conversion and practical money context remain fully usable.

Do not display empty decorative cards.

---

# H. Historical Rates

## UC-070 — Inspect recent historical trend

**Priority:** P1

User intent:

> Is today's reference rate unusual compared with recent months?

Expected:

- period selection;
- chart;
- current/end value;
- high/low;
- textual summary.

No trading recommendation.

---

## UC-071 — Chart inaccessible or not useful visually

**Priority:** P1 accessibility

Expected:

Equivalent textual/table data exists.

The chart is enhancement, not the sole source of meaning.

---

## UC-072 — Sparse historical provider coverage

**Priority:** P1

Expected:

Show only periods with supported data.

Do not interpolate long gaps unless explicitly documented.

---

# I. Saved State and Repeat Use

## UC-080 — Save favourite pair anonymously

**Priority:** P1

Expected:

Store locally.

No account required.

---

## UC-081 — Reopen favourite

**Priority:** P1

Expected:

Restores:

- source currency;
- destination currency;
- optional source/destination countries.

Amount policy should be explicit; defaulting to last amount is a research question.

---

## UC-082 — Recent conversions

**Priority:** P1

Expected:

Bounded list.

User can:

- repeat;
- swap;
- remove;
- clear all.

---

## UC-083 — Clear local history

**Priority:** P1 privacy

Expected:

Immediate and understandable.

No hidden cloud copy if user is anonymous.

---

## UC-084 — Account sync

**Priority:** P2

Expected:

After sign-in, user understands what will sync.

Do not silently merge conflicting histories without a policy.

---

# J. Share / Deep Link

## UC-090 — Share conversion

**Priority:** P1

Expected:

Share URL stores only non-sensitive conversion state.

Example:

```text
amount=100
from=EUR
to=JPY
to_country=JP
```

---

## UC-091 — Open invalid deep link

**Priority:** P1

Expected:

- validate every parameter;
- ignore/fix invalid parts;
- explain unsupported values where needed;
- never crash.

---

# K. Accessibility

## UC-100 — Keyboard-only conversion

**Priority:** P0

Expected:

Full P0 flow is operable with:

- Tab;
- Shift+Tab;
- Enter/Space;
- arrow keys only where native/appropriate.

No keyboard trap.

---

## UC-101 — Screen-reader conversion

**Priority:** P0

Expected reading order communicates:

1. amount;
2. source;
3. destination;
4. action;
5. result;
6. reference-rate status.

Dynamic update announcement is concise.

---

## UC-102 — High zoom/reflow

**Priority:** P0

Expected:

No horizontal scrolling required for the core conversion flow at supported reflow conditions.

Content order remains logical after columns stack.

---

## UC-103 — Reduced motion

**Priority:** P0

Expected:

No information depends on animation.

Decorative transitions are removed/reduced.

---

## UC-104 — Motor impairment / imprecise touch

**Priority:** P0

Expected:

- adequately sized targets;
- enough spacing;
- Swap is easy to hit;
- small icon buttons are avoided for frequent actions.

---

# L. Mobile / Offline

## UC-110 — One-handed conversion in transit

**Priority:** Mobile P0

Expected:

Frequent controls remain comfortably reachable.

No precision gesture required.

---

## UC-111 — App resumes after interruption

**Priority:** Mobile P0

Expected:

Return to the last useful conversion state.

Do not lose selections because the OS backgrounded the app.

---

## UC-112 — Offline cached pair

**Priority:** Mobile P1

Expected:

Cached result is clearly marked:

- Offline/Cached;
- effective date;
- last synced time.

---

## UC-113 — Offline uncached pair

**Priority:** Mobile P1

Expected:

> This pair is not available offline yet.

Offer:

- saved/cached pairs;
- retry when online.

Never substitute another pair.

---

## UC-114 — Offline cultural/payment context

**Priority:** Mobile P1

Expected:

Previously cached published context may display with source/verification metadata.

No network-only blocker for the converter shell.

---

# M. Trips and Budget

## UC-120 — Create trip budget

**Priority:** P2

Expected inputs:

- destination country;
- dates;
- home currency;
- total budget.

Output:

- destination-currency equivalent;
- approximate per-day budget.

---

## UC-121 — Allocate categories

**Priority:** P2

Possible categories:

- accommodation;
- food;
- transport;
- activities;
- flexible/other.

Expected:

Simple planning aid, not prescriptive budgeting.

---

## UC-122 — Trip crosses rate changes

**Priority:** P2

Expected:

Trip planning clearly distinguishes:

- saved/planning reference;
- current refreshed reference.

Do not rewrite historical user-entered budgets silently.

---

# N. Failure, Recovery and Edge Cases

## UC-130 — HTMX enhancement fails

**Priority:** P0

Expected:

The full HTML form submission still works.

---

## UC-131 — Cultural enrichment fails

**Priority:** P0

Expected:

Conversion remains successful.

Display no global failure screen.

---

## UC-132 — Typical-price data fails

**Priority:** P0

Expected:

Payment/culture sections may still render.

---

## UC-133 — Session/local storage unavailable

**Priority:** P1

Expected:

Core conversion works.

Saving/favourites degrade gracefully.

---

## UC-134 — User disables cookies/storage

**Priority:** P1

Expected:

No essential conversion feature depends on persistence.

---

## UC-135 — Very slow response

**Priority:** P0

Expected:

- visible scoped loading state;
- form state retained;
- previous safe result not unnecessarily blanked;
- cancel/obsolete request semantics prevent wrong-pair rendering.

---

# O. Localization

## UC-140 — Decimal-comma locale

**Priority:** P0

Expected:

Amount entry is understandable and recoverable.

Display formatting follows locale when implemented.

---

## UC-141 — Device locale does not equal home currency

**Priority:** P0

Expected:

User can immediately override any suggestion.

No copy implies the app “knows” the user's home currency.

---

## UC-142 — Right-to-left UI language

**Priority:** P2 readiness

Expected architecture:

- logical properties where practical;
- icons with directional meaning audited;
- content does not assume left=source/right=destination semantically.

---

# P. Privacy and Data Control

## UC-150 — Anonymous user converts

**Priority:** P0

Expected:

No sign-in.

No need to reveal personal identity.

---

## UC-151 — User clears all local saved data

**Priority:** P1

Expected:

A clear action removes:

- favourites;
- recent history;
- non-essential remembered state.

Explain what remains server-side, if anything.

---

## UC-152 — User deletes account

**Priority:** P2

Expected:

Data-deletion behaviour is explicit.

Do not conflate logout with deletion.

---

# Q. Research Cases

These need prototype testing before behaviour is frozen.

## R-001 — Default source suggestion

Question:

Does browser-locale suggestion save time or create more errors for travellers?

Variants:

- no default;
- locale currency suggested;
- last-used only.

---

## R-002 — Combined country/currency search

Question:

Should the main picker combine country and currency results or use two linked controls?

Measure:

- time to first result;
- errors;
- comprehension of shared currencies;
- keyboard accessibility.

---

## R-003 — Swap semantics

Question:

Should the source numeric amount remain unchanged, or should the previous result become the new amount?

Current hypothesis:

Keep numeric source amount unchanged.

---

## R-004 — Auto-update after first conversion

Question:

Does debounced updating improve perceived speed or create surprise/extra network activity?

---

## R-005 — Purchasing-context categories

Question:

Which categories are universally understandable and genuinely useful?

Candidates:

- coffee;
- casual meal;
- local transit;
- groceries;
- budget accommodation.

Avoid categories that vary too dramatically or invite misleading comparisons.

---

## R-006 — Provenance visibility

Question:

How much source information should be visible next to the result without overwhelming casual users?

---

# R. Cross-case product rules

These rules apply across the catalog.

1. **No source truth, no trusted claim.**
2. **Never show previous-pair data as current-pair data.**
3. **Currency and country are separate concepts.**
4. **Approximate context is labelled approximate.**
5. **Core conversion never requires an account.**
6. **Enrichment cannot break the core task.**
7. **Accessibility behaviour is part of each use case, not a separate afterthought.**
8. **Offline/cached data always exposes age.**
9. **No provider response is trusted before validation.**
10. **No user input is reinterpreted silently when meaning is ambiguous.**


# H2. Historical Converter and Storytelling

## UC-073 — Convert on an exact historical date

**Priority:** P1

### User intent

> I want to know what this amount converted to on a specific past date.

### Example

100 EUR → USD on 15 June 2016.

### Expected behaviour

- preserve the requested date;
- retrieve the appropriate historical reference observation;
- show amount/result/rate;
- show actual effective observation date;
- show provider/source;
- mark the result as Historical reference, not current/live.

---

## UC-074 — Historical date with no exact observation

**Priority:** P1 critical trust case

### Example

User selects Sunday 14 June 1998.

### Expected behaviour

- do not invent a Sunday observation;
- apply the documented provider/fallback policy;
- show both requested date and actual observation date;
- explain that the previous available observation was used;
- never hide the date substitution.

---

## UC-075 — Historical country suggests archived currency

**Priority:** P1 differentiator

### Example

Country: Finland  
Date: 15 June 1998  
Currency currently selected: EUR

### Expected behaviour

Show:

> Finland used the Finnish markka (FIM) on this date.

Action:

> Use FIM

Alternative:

> Keep EUR

### Critical rule

Do not silently replace the user's explicit currency selection.

---

## UC-076 — Select an archived currency

**Priority:** P1

### User intent

> I want to convert Finnish markka, Deutsche Mark or another retired currency during its supported historical period.

### Expected behaviour

- archived currencies are discoverable in historical mode;
- active-period/provider coverage is visible;
- current mode does not become cluttered with archived codes;
- selected date must be compatible with available historical coverage.

---

## UC-077 — Historical date outside coverage

**Priority:** P1

### Expected behaviour

Explain:

> Historical data for this pair starts on [date].

Offer:

- earliest supported date;
- change currency;
- source/coverage details.

Do not imply that provider-wide earliest history applies to every pair.

---

## UC-078 — Then & now comparison

**Priority:** P1

### Preconditions

The same currency pair has valid historical and current/latest reference observations.

### Expected behaviour

Show:

- historical conversion;
- latest reference conversion;
- clearly directional rate difference.

### Copy rule

Good:

> The latest reference conversion gives about 8% more USD per 100 EUR than the selected 2016 observation.

Bad:

> You would have made 8%.

No investment-return framing.

---

## UC-079 — Historical FX is not historical purchasing power

**Priority:** P1 trust case

### User intent

> What could 100 FIM buy in 1998?

### Expected behaviour

The product explains that FX conversion alone cannot answer that question.

Do not use current typical-price cards as historical evidence.

If a future historical purchasing-power module exists, expose it as a separate calculation with its own methodology/source.

---

## UC-080H — Open the story behind a historical conversion

**Priority:** P1

### User intent

> Explain what monetary/cultural era I am looking at.

### Expected behaviour

Story may contain:

- conversion summary;
- currency era;
- currency transition;
- valid Then & now comparison;
- temporally relevant sourced historical/cultural context.

### Critical rule

Historical conversion succeeds even if no story content exists.

---

## UC-081H — Archived currency has no valid current market comparison

**Priority:** P1

### Example

FIM → USD in 1998.

### Expected behaviour

Do not fabricate a current FIM/USD market quote.

Instead show a currency transition/timeline where sourced.

---

## UC-082H — Story fact is missing or weakly sourced

**Priority:** P1

### Expected behaviour

Omit the chapter.

Do not fill the story with generic trivia or AI-generated claims.

---

## UC-083H — Historical event near a rate movement

**Priority:** P1 trust case

### Expected behaviour

A historical event may be displayed as contextual information.

The app does not claim:

> Event X caused the currency move

unless a reliable cited source explicitly supports that causal relationship.

---

## UC-084H — Share historical conversion/story

**Priority:** P2

### Expected behaviour

Shareable state can contain:

- amount;
- pair;
- requested date;
- country context.

Rendered/shared result must still expose actual observation date when it differs from requested date.

No private account/trip data is added to the URL.

---

## UC-085H — Historical chart highlights selected point

**Priority:** P1/P2

### Expected behaviour

The chart uses the same normalized historical quote semantics as the converter.

The selected date/observation is highlighted.

The chart has text/table equivalent.

---

## UC-086H — Monthly/low-frequency archived series

**Priority:** P1

### Expected behaviour

If provider data is monthly rather than daily:

- state the observation granularity;
- do not imply day-level precision;
- show the actual period/date used.

---

## UC-087H — Historical deep link reload

**Priority:** P1

### Example

```text
?amount=100&from=FIM&to=USD&date=1998-06-15
```

### Expected behaviour

Reload reproduces:

- requested date;
- pair;
- amount;
- historical result semantics.

Any fallback observation remains separately labelled.
