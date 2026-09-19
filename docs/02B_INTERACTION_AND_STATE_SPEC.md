# Interaction and State Specification

This document defines the behaviour of the converter as a stateful user experience.

It exists to prevent a common class of bugs where each template/HTMX fragment looks correct in isolation but transitions between states produce misleading or inaccessible output.

---

## 1. State-model principle

The page should never be described only as:

```text
loading / success / error
```

That is too coarse for financial/contextual data.

The product distinguishes:

```text
empty
editing
ready
submitting
success-current
success-cached
success-same-currency
partial-context
validation-error
unsupported
provider-error-with-cache
provider-error-no-cache
offline-cached
offline-unavailable
```

Context enrichment has its own state and must not overwrite conversion state.

---

## 2. Converter state shape

Conceptually:

```text
ConverterState
├── input
│   ├── amount_raw
│   ├── source_currency
│   ├── destination_currency
│   ├── source_country?
│   └── destination_country?
│
├── conversion
│   ├── status
│   ├── result?
│   ├── rate?
│   ├── effective_at?
│   ├── fetched_at?
│   ├── provider?
│   └── stale?
│
├── destination_context
│   ├── status
│   ├── typical_prices[]
│   ├── payment_guidance?
│   └── cultural_profile?
│
└── ui
    ├── enhanced
    ├── updating
    └── error_summary?
```

This is conceptual documentation, not a requirement to create a giant client-side state object.

Django/server responses remain authoritative.

---

## 3. Primary state transitions

```text
EMPTY
  ↓ user enters/selects
EDITING
  ↓ minimum valid input
READY
  ↓ submit
SUBMITTING
  ├── valid rate → SUCCESS_CURRENT
  ├── same currency → SUCCESS_SAME_CURRENCY
  ├── validation → VALIDATION_ERROR
  ├── unsupported → UNSUPPORTED
  ├── provider fail + safe cache → PROVIDER_ERROR_WITH_CACHE
  └── provider fail + no cache → PROVIDER_ERROR_NO_CACHE
```

After any success:

```text
SUCCESS_*
  ↓ user edits
EDITING_WITH_PREVIOUS_RESULT
  ↓ enhanced update
UPDATING
```

The previous result remains visibly associated with its old pair until the new request succeeds.

It must never be relabelled as if it belongs to new inputs.

---

## 4. Empty state

### Conditions

- no destination currency;
- or no source currency;
- amount may or may not exist.

### UI

Show:

- amount control;
- From;
- To;
- disabled or submit-capable Convert according to HTML validation strategy;
- concise task explanation.

Do not show:

- zero result;
- fake default rate;
- empty context cards.

### Message

> Choose a source and destination to convert.

---

## 5. Editing state

The user is modifying one or more inputs.

### Rules

- do not erase previously entered fields;
- do not show field errors before the user has had a reasonable chance to complete input;
- if a previous successful result exists, visually distinguish it from the new pending inputs.

Possible status text:

> Update the conversion to use these changes.

With HTMX enhancement, a valid edit may transition automatically to Updating after debounce.

---

## 6. Ready state

Minimum conditions:

- parseable amount;
- supported source currency;
- supported destination currency.

Country context is not required for arithmetic.

The Convert button is the clear primary action.

---

## 7. Submitting / updating state

### First submit

Display a scoped progress indicator in the result region.

Do not:

- cover the screen;
- disable unrelated navigation;
- erase the form.

### Subsequent update

Keep the existing result to reduce layout shift.

Mark it clearly as updating if the pair/amount has changed.

Example:

```text
Updating EUR → JPY…
```

### Obsolete requests

If a user changes inputs again before a prior enhanced request finishes, the older response must not win.

This is a critical cross-request integrity requirement.

---

## 8. Success-current state

Display hierarchy:

1. converted result;
2. pair;
3. reference rate;
4. effective date;
5. source/provider;
6. compact informational disclaimer.

Example:

```text
100 EUR ≈ 17,450 JPY

Reference rate
1 EUR = 174.50 JPY

Effective 18 Sep 2026
ECB via Frankfurter

Reference rate only. Your bank/card/cash provider may apply a different rate or fees.
```

### Accessibility

A concise result summary can be announced once.

Do not announce every metadata line separately as multiple live-region events.

---

## 9. Success-same-currency state

### Same currency, no country difference

```text
100 EUR = 100 EUR
```

No external FX request is necessary.

### Same currency, different countries

Example:

Finland EUR → Italy EUR.

Primary copy:

> Same currency — compare local value and money customs.

The context sections remain meaningful.

Do not suppress the destination experience just because rate = 1.

---

## 10. Success-cached / stale state

Used when:

- the rate was previously valid;
- refresh failed or client is offline;
- pair matches exactly.

Display all of:

- cached/stale label;
- effective rate date;
- last successful fetch/sync;
- source;
- retry action.

Example:

```text
100 EUR ≈ 17,450 JPY

Cached reference rate
Effective 18 Sep 2026
Last synced 19 Sep 2026, 08:12

Retry
```

Do not use the word “current”.

---

## 11. Validation-error state

### Principles

- specific;
- local;
- recoverable;
- preserve input.

### Field error examples

Amount missing:

> Enter an amount.

Invalid characters:

> Enter a number, for example 1234.56 or 1234,56.

Negative:

> Enter zero or a positive amount.

Unsupported precision/range:

> Enter an amount below [documented limit].

### Error summary

For multiple errors, show a summary that links/focuses to the affected fields.

For one obvious local error, field-level feedback may be sufficient depending on final form pattern.

### Focus

After full form submission with errors, focus may move to the error summary if one exists.

For inline enhanced validation, avoid disruptive focus movement.

---

## 12. Unsupported state

Use when:

- currency known to product but provider/pair unsupported;
- historical currency unavailable for current conversion;
- destination context unsupported.

Differentiate arithmetic support from cultural-context support.

### FX unsupported

> A reference rate is not available for ABC → XYZ.

### Context unsupported

> Conversion is available, but local context is not available for this destination yet.

These are not the same error.

---

## 13. Provider-error-with-cache state

The system has a last safe same-pair quote.

UI keeps the cached result and adds recovery status.

This is degraded success, not total failure.

Primary emphasis stays on usable data plus age.

---

## 14. Provider-error-no-cache state

No safe conversion can be produced.

UI:

- retain form;
- explain the problem;
- retry;
- avoid technical details.

Example:

> The reference-rate service is temporarily unavailable. Your selections are still here. Try again.

Do not render 0, blank numeric placeholders or estimated fallback rates.

---

## 15. Destination-context states

Context is independent from conversion.

### Context loading

Conversion already visible.

Small scoped status:

> Loading local context…

### Context success

Show only sections with actual data.

### Context partial

Example:

- payment guidance available;
- typical prices unavailable;
- culture available.

Render available sections and one specific empty state for missing data.

### Context unavailable

> Local price and payment context is not available for this destination yet.

Do not turn this into a global page failure.

---

## 16. “What this buys” state rules

For each item, underlying data can be:

```text
published-current-enough
published-but-aging
missing
suppressed
```

Only publishable observations appear.

### Derived count

For a price range:

```text
converted_amount / high_price
→ lower count

converted_amount / low_price
→ upper count
```

Round to human-friendly whole/range values.

Avoid bizarre outputs:

- “0 coffees” may be better phrased as “less than one typical coffee”;
- huge counts can be abbreviated or capped for comprehension.

The exact display thresholds are a UI research question.

---

## 17. Shared-currency context prompt

If destination currency is shared and no destination country is known:

Conversion succeeds.

Below the result:

> Choose a destination country to see local prices and money customs.

Country selection enriches the existing result; it does not recalculate the monetary result unless the currency also changes.

---

## 18. Country selection changes currency

If a user has not explicitly chosen a currency, selecting a country can auto-suggest its primary currency.

If a user explicitly selected a different supported currency, country selection must not silently overwrite it without an understandable reason.

Track conceptual state:

```text
currency_source = suggested | explicit
```

This need not become a database field; it describes UX intent.

---

## 19. Swap transition

Before:

```text
100 EUR
Finland
→
JPY
Japan
```

After:

```text
100 JPY
Japan
→
EUR
Finland
```

Rules:

- amount numeric value preserved;
- contextual countries swapped;
- obsolete previous result remains clearly old until update completes;
- result announcement occurs after new result;
- focus stays on Swap.

---

## 20. First-submit vs enhanced-update behaviour

### No JavaScript

```text
Edit form → Submit → full response
```

### HTMX available

First conversion:

```text
Edit form → Convert → partial result
```

After first success:

```text
Valid amount edit → debounce → update result
Committed pair change → update result
Swap → update result
```

The submit button remains available in all cases.

The same server validation and domain service are used for both paths.

---

## 21. Browser history and navigation

HTMX interactions that materially change shareable conversion state should consider URL/history updates.

Requirements:

- Back must not produce nonsensical form/result mismatches;
- reload should reconstruct a valid conversion from URL state when present;
- cultural disclosure opening does not necessarily need history;
- country/pair changes likely do.

Final pushState/replaceState details are implementation decisions, but UX correctness must be tested.

---

## 22. Deep-link state

On loading a URL with conversion parameters:

### Valid

Populate form and render result.

### Partially invalid

Keep valid pieces; highlight invalid/unsupported field.

### Fully invalid

Fall back to clean converter without exception page.

Never trust URL parameters as provider/domain truth.

---

## 23. Recents and favourites state

### Save success

Provide subtle confirmation.

Do not use modal dialogs for simple save actions.

### Save duplicate

Do not create visible duplicates.

Prefer:

> Already saved

or simply maintain idempotent saved state.

### Storage unavailable

Core conversion unaffected.

Saved control explains inability only when user attempts it.

---

## 24. Authentication transition

When later account features exist:

### Anonymous → sign in

Preserve current conversion.

Do not redirect back to a blank converter.

### Local favourites → account

Conflict/merge strategy must be explicit.

Potential policy:

- union unique pairs;
- ask before importing history.

Do not silently duplicate.

---

## 25. Mobile offline state machine

```text
ONLINE_CURRENT
    ↓ network lost
ONLINE_RESULT_BECOMES_CACHED
    ↓ app restart
OFFLINE_CACHED
```

For uncached pair:

```text
OFFLINE
  ↓ request pair
OFFLINE_UNAVAILABLE
```

When network returns:

```text
OFFLINE_CACHED
  ↓ refresh
UPDATING
  ├── success → ONLINE_CURRENT
  └── fail → OFFLINE_CACHED
```

The cached result should remain usable during failed refresh.

---

## 26. Focus management rules

### Routine HTMX result update

Do not move focus.

### Full-form validation with error summary

Move focus to summary if that pattern is used.

### Dialog/drawer

If introduced:

- focus enters logically;
- Escape closes where expected;
- focus returns to trigger;
- background is not interactable if modal.

### Country search

A custom combobox must follow established accessible combobox interaction patterns.

Do not invent keyboard conventions.

---

## 27. Live-region rules

Use one restrained status region.

Announce:

- conversion success;
- meaningful error;
- stale status when it changes.

Do not announce:

- decorative context;
- every loading pulse;
- every keystroke;
- all price cards.

Potential result announcement:

> 100 euros is approximately 17,450 Japanese yen. Reference rate effective 18 September 2026.

---

## 28. Loading and latency thresholds

Do not show a spinner for operations that complete near-instantly if it would only flash.

For perceptible waits:

- show scoped progress;
- preserve layout;
- keep controls understandable.

For prolonged provider waits:

- timeout at infrastructure layer;
- recover to cache/error;
- never leave the interface indefinitely “loading”.

Exact timing thresholds are implementation/performance decisions and should be tested.

---

## 29. Visual status semantics

Use redundant cues.

### Current/reference

Text + metadata.

### Cached/stale

Status text + icon/badge where useful.

### Error

Text + error styling; never red alone.

### Updating

Text/progress semantics; do not reduce contrast of the existing result so far that it becomes unreadable.

---

## 30. Touch interaction

Frequent touch controls:

- From selector;
- To selector;
- amount;
- Swap;
- Convert/Update;
- Save.

These should have comfortably large hit areas and spacing, especially on mobile.

Do not make Swap a tiny circular icon between two large controls.

---

## 31. Selection-control fallback strategy

Ideal long-term:

- accessible searchable country/currency combobox.

Fallback:

- native/select-based experience.

Progression rule:

Do not replace a semantically solid fallback until the custom search control passes:

- keyboard test;
- screen-reader test;
- mobile touch test;
- 200+ option performance test;
- search relevance test.

---

## 32. Copy state matrix

| State | Primary phrase |
|---|---|
| Empty | Choose a source and destination to convert |
| Loading | Getting reference rate… |
| Current | Reference rate effective [date] |
| Cached | Cached reference rate · effective [date] |
| Offline | Offline · using cached reference rate |
| Same currency | Same currency — compare local value and money customs |
| Context missing | Local context is not available yet |
| Provider error | Reference rate is temporarily unavailable |
| Unsupported | A reference rate is not available for this pair |

Copy must remain plain and non-alarmist.

---

## 33. State integrity invariants

These are UX invariants and should become automated tests where possible.

1. A displayed result always belongs to the pair displayed with it.
2. A displayed cached result exposes its age/effective date.
3. A conversion result never depends on cultural content loading.
4. A country context never silently changes an explicitly chosen currency.
5. A provider error never clears valid user input.
6. An invalid amount never calls the provider.
7. Same-currency conversion does not require an external FX request.
8. Shared-currency selection does not force an arbitrary country.
9. No-JS form submission and HTMX submission apply identical validation.
10. Dynamic updates do not steal focus during normal use.
11. A screen reader receives at most one concise result announcement per completed update.
12. Approximate purchasing context is never displayed without source/scope metadata somewhere accessible.
13. Deep links cannot create a form/result mismatch.
14. Obsolete async/HTMX responses cannot overwrite newer input state.
15. Offline data from one pair cannot masquerade as another pair.

---

## 34. QA scenario matrix

Every major UX PR should verify at least:

### Input
- integer;
- decimal dot;
- decimal comma;
- zero;
- negative;
- invalid text;
- oversized amount.

### Pair
- normal pair;
- same currency;
- shared currency/no country;
- shared currency/explicit country;
- unsupported currency.

### Network
- normal;
- slow;
- timeout;
- malformed provider payload;
- cached fallback;
- no cache.

### Context
- full;
- partial;
- none;
- aging data.

### Interaction
- mouse;
- touch;
- keyboard;
- no JS;
- back/reload/deep link.

### Viewport/accessibility
- desktop;
- narrow mobile;
- high zoom/reflow;
- reduced motion;
- screen-reader-oriented semantics.

This matrix is a minimum, not exhaustive test code.
