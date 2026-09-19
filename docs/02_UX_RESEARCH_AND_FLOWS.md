# UX Research and User Flows

## 1. UX principle

> **Utility first → context second → culture third.**

The user must be able to complete the primary conversion before being asked to explore anything decorative.

## 2. Primary desktop composition

The signature layout is a two-country comparison.

```text
┌──────────────────────────┬──────────────────────────┐
│ SOURCE                   │ DESTINATION              │
│ 🇫🇮 Finland              │ 🇯🇵 Japan                │
│ EUR                      │ JPY                      │
│                          │                          │
│ 100.00                   │ 17,450                   │
│                          │                          │
│ rate + freshness         │ local value context      │
│                          │ payment + culture        │
└──────────────────────────┴──────────────────────────┘
```

The visual atmosphere may react to the selected countries, but control positions and interaction patterns remain stable.

## 3. Mobile web composition

Two columns collapse into one ordered task:

```text
Amount
Source country / currency
↓
Destination country / currency
Converted amount
Rate + freshness
What this buys
Money tips
Culture
```

No horizontal dependency is required to understand the result.

## 4. Core flow

### F1 — first conversion

1. Land on converter.
2. Source is preselected from a non-invasive default or empty state.
3. Enter amount.
4. Select source country/currency.
5. Select destination country/currency.
6. Submit or trigger debounced conversion.
7. Result region updates.
8. Focus remains predictable.
9. Screen reader receives a concise result announcement.

### F2 — swap

1. Activate Swap.
2. Source/destination country and currency values exchange.
3. Amount remains in the source amount field unless product testing proves another model clearer.
4. Result recalculates.
5. User receives no focus jump.

### F3 — invalid amount

Invalid examples:

- empty;
- non-numeric;
- negative;
- zero if business rules disallow it;
- excessive precision;
- amount beyond configured safe range.

The server owns validation. HTMX renders field-level and summary feedback.

### F4 — provider failure

Do not clear the last trusted result for the same pair.

Show:

- last successful result;
- explicit “stale” label;
- rate effective time/date;
- retry action.

Never show previous-pair data under a new pair.

### F5 — country/currency relationship

Selecting a country should suggest its primary current currency.

Selecting a currency must not assume a single culture. For multi-country currencies, the user can choose a specific country context.

Example:

```text
EUR
├── Finland
├── France
├── Germany
└── ...
```

## 5. “What this buys” interaction

Keep the initial section compact.

Example:

```text
What ¥17,450 can roughly buy

☕ Coffee          ~35
🍜 Casual meals   ~14
🚇 Metro rides    ~85
```

Each item must expose supporting metadata on demand:

- city / national scope;
- observed price;
- source;
- observation date;
- confidence;
- disclaimer.

Avoid false precision. Prefer ranges when the underlying source supports ranges.

## 6. Payment-context hierarchy

Order by practical travel value:

1. card acceptance;
2. cash usefulness;
3. ATM notes;
4. tipping;
5. DCC / fee warning;
6. cultural nuance.

Use neutral language such as:

- “commonly accepted”;
- “often useful”;
- “typically not expected”.

Avoid universal statements when practice varies.

## 7. Cultural exploration

Culture is opened progressively through a drawer/section rather than competing with the converter.

Suggested categories:

- currency history;
- languages;
- capital;
- food;
- notable places;
- traditions;
- money etiquette.

Every factual card has provenance.

## 8. Historical rates

Historical context is explanatory, not trading-oriented.

Initial ranges:

- 1M;
- 1Y;
- 5Y;
- MAX when provider coverage is suitable.

Accessible chart requirements:

- text summary;
- keyboard-independent understanding;
- min/max/current values;
- data table or equivalent fallback.

## 9. Empty states

### No pair selected
Explain the task in one sentence.

### No contextual price data
Do not invent estimates. Show “Context data is not available for this destination yet.”

### No cultural profile
Conversion still works.

### No network / mobile offline
Use cached data only when its timestamp is available.

## 10. Latency strategy

Never block the arithmetic result on cultural content.

Desired dependency chain:

```text
conversion result
     │
     ├── money context
     └── culture
```

The converter is the critical path; enrichment may load independently.

## 11. Accessibility interaction rules

- all country/currency controls have text labels;
- flags are supplementary, never the sole identifier;
- focus is not moved after routine HTMX updates;
- errors receive programmatic association;
- result announcement is short and non-repetitive;
- reduced-motion preference disables decorative transitions;
- target sizes follow WCAG 2.2 expectations;
- colour never carries status alone.

## 12. UX anti-patterns

Do not:

- auto-play cultural audio;
- animate every conversion;
- use flags as currency symbols;
- hide timestamps behind hover-only UI;
- replace native controls without a demonstrated need;
- make a modal the primary conversion surface;
- require registration for basic conversion;
- present city-specific prices as national averages.
