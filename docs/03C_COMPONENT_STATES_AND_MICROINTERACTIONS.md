# Component, State and Microinteraction Specification

This document defines behavior and visual states for reusable UI components.

The objective is consistency across:

- Django templates
- HTMX fragments
- React Native equivalents
- current/historical modes
- desktop/mobile

---

# 1. Component state contract

Every interactive component must explicitly consider:

```text
default
hover
focus-visible
pressed
selected
disabled
loading
error
success/confirmed
read-only
high-contrast
reduced-motion
```

Not every state appears visually for every component, but the implementation must consciously decide.

---

# 2. Button hierarchy

Use three core levels.

## Primary

For the single main action in a context.

Examples:

- Convert
- Save trip
- Confirm

Visual:

- solid accent
- high contrast
- 48–56px target height depending context

Only one primary action should dominate a component region.

## Secondary

Examples:

- Retry
- Use FIM
- View data
- Save pair

Visual:

- neutral/soft accent background or outlined
- less visual weight than primary

## Tertiary/text

Examples:

- Source details
- Keep EUR
- Clear
- Cancel

Visual:

- low chrome
- still obvious as interactive

## Destructive

Examples:

- Delete account
- Clear all history if irreversible

Danger styling appears only for destructive intent, not ordinary errors.

---

# 3. Button state table

## Default

- clear label
- no animation running

## Hover

- subtle fill/border shift
- no large scale-up

## Focus-visible

- external focus ring
- never rely on hover styling

## Pressed

- small tactile feedback
- approximately 0.98 scale if motion allowed
- immediate visual response

## Loading

Preferred:

```text
[ spinner ] Converting…
```

Rules:

- button width should not jump substantially
- prevent duplicate submission
- label communicates action in progress
- spinner not announced repeatedly

## Disabled

Use sparingly.

If disabled, reason should be inferable.

Do not disable Convert with no explanation when form errors could be shown on submit.

---

# 4. AmountField

Anatomy:

```text
Label
┌──────────────────────────────────────┐
│ 100.00                         EUR   │
└──────────────────────────────────────┘
hint/error
```

States:

### Empty

No fake completed-looking 0.00 result.

Placeholder can show example only if label remains visible.

### Filled

Large tabular numeric value.

### Focus

Strong focus ring.

### Error

- error border
- message below
- error icon optional
- retain entered text

### Updating

Do not put spinner inside field on every debounced update.

Result area shows update state.

---

# 5. Amount formatting

During typing:

- avoid reformatting that moves caret
- preserve user's raw text

After successful submit:

- display can normalize localized format

Example:

input:

```text
1234,5
```

result may display:

```text
1 234,50 EUR
```

depending locale.

---

# 6. CountryCurrencyTrigger

Anatomy:

```text
FROM
🇫🇮 Finland
Euro · EUR                         ▾
```

States:

- empty
- selected country + currency
- currency-only
- historical currency
- focus
- error if invalid/incompatible
- historical suggestion nearby

Empty copy:

> Select country or currency

Do not show only:

> EUR

when country context is known and important.

---

# 7. CountryCurrencySearch

Search field:

- autofocus only when opening does not harm accessibility context
- Escape closes on desktop
- mobile back action works naturally

Search matches:

- country
- official name if useful
- currency name
- ISO code
- common normalized aliases

Result sections may include:

```text
Countries
Currencies
Historical currencies
```

Do not over-section small result sets.

---

# 8. Search row

Minimum height:

- approximately 52–56px

Anatomy:

```text
[flag/icon] Primary label
            Secondary label      optional tag
```

Tags:

- Historical
- Multiple countries

Avoid:

- “Popular”
- “Trending”

unless based on explicit product data and useful.

---

# 9. Search keyboard interaction

A custom combobox must follow established accessible combobox behavior.

Expected:

- Up/Down changes active option
- Enter selects
- Escape closes
- typing filters
- Tab behavior remains predictable

Do not implement a custom listbox until keyboard and screen-reader behavior is tested.

Native/simple fallback is preferable to broken custom UX.

---

# 10. SwapButton

Visual:

- compact circular or rounded-square control
- not decorative floating object

State:

### Default

neutral control

### Hover

slight surface/border emphasis

### Pressed

brief tactile feedback

### Loading/update

button remains usable only if request cancellation/queue behavior is safe

### Focus

clear ring

Do not rotate the icon 360°.

If animated, use approximately 90–180° orientation cue max, and remove under reduced motion.

---

# 11. RateDateControl

Default compact selector:

```text
Rate date
Latest available ▾
```

Historical:

```text
Rate date
Historical · 15 Jun 1998 ▾
```

Picker states:

- latest
- exact historical
- out-of-coverage
- invalid future
- archived-currency suggestion

The control itself is neutral; historical mode uses a subtle semantic badge, not danger styling.

---

# 12. Date picker

Prefer platform/native date capabilities where they provide good accessibility.

Web:

- progressive enhancement can use a date input or accessible picker
- manual entry fallback must be clear

Constraints:

- no future historical date
- coverage feedback appears after selection
- min/max should not falsely imply pair-wide coverage before pair known

---

# 13. ConversionResult

Anatomy:

```text
eyebrow/status

100 EUR
≈ 17,450 JPY

1 EUR = 174.50 JPY

Reference rate · Effective 18 Sep 2026
ECB via Frankfurter

Source details
```

Variants:

- current
- stale/cached
- offline cached
- historical exact
- historical fallback observation
- same currency

Same component skeleton where possible.

---

# 14. Result update behavior

On subsequent HTMX update:

- keep existing result visible
- mark updating
- update atomically when new response arrives

Avoid:

- blanking result
- flashing skeleton
- showing old number under new pair labels

Critical visual invariant:

> A visible number and visible pair must always belong together.

---

# 15. Result announcement

Screen reader live-region summary:

> 100 euros is approximately 17,450 Japanese yen. Reference rate effective 18 September 2026.

Do not include:

- all source details
- all local-price cards
- all payment context

in the live announcement.

---

# 16. DataFreshnessBadge

Possible labels:

- Reference rate
- Cached
- Offline
- Historical reference
- Previous available observation

Badges are concise.

Date sits separately.

Do not write:

> LIVE

for daily reference data.

---

# 17. SourceDetails disclosure

Trigger:

> Source details

Panel content:

- source/provider
- provider policy
- effective date
- fetched timestamp
- reference-rate explanation
- relevant source link

Interaction:

- inline disclosure preferred on web if space allows
- bottom sheet/modal can be appropriate mobile-native

Do not use hover tooltip.

---

# 18. InlineAlert

Use for:

- stale notice
- historical currency suggestion
- partial context
- provider issue with usable cache

Variants:

- info
- warning
- error
- success

An alert should not visually dominate a still-usable result.

---

# 19. ErrorSummary

Use after full submission when multiple errors exist.

Anatomy:

```text
Check these details

• Enter an amount
• Choose a destination currency
```

Links/focus targets where appropriate.

Do not use for a single obvious inline error unless it improves recovery.

---

# 20. ContextSection

Reusable shell for:

- What this buys
- Paying locally
- Culture
- History

Anatomy:

- heading
- optional one-line intro
- content
- optional secondary action

Do not automatically wrap every section in a bordered card.

---

# 21. TypicalPriceCard

Anatomy:

```text
Coffee

¥500–650
typical range

≈ 26–34
for your amount

Tokyo · May 2026
[ source ]
```

Visual priority:

1. category
2. user's derived equivalent
3. original price range
4. scope/date

Do not make source text invisible.

---

# 22. TypicalPrice edge cases

## Converted amount < item price

> Less than one typical coffee

rather than:

> 0 coffees

## Extremely high count

Prefer human-readable grouping.

Avoid novelty phrases like:

> 10,532 coffees!

## Missing range

If only one value is sourced:

> around ¥500

not a fabricated low/high interval.

---

# 23. PaymentRow

Anatomy:

```text
Cards
Commonly accepted in urban areas
[details]
```

Label width may align in desktop rows.

Mobile stacks label above statement if needed.

Icons optional.

Do not encode:

- high/medium/low

with vague meters unless methodology exists.

---

# 24. StoryTeaser

Anatomy:

```text
The story behind this rate

Finland was still using the markka on this date.

Read the story →
```

One factual teaser maximum.

No AI-style dramatic prose.

---

# 25. StoryChapter

Anatomy:

```text
EYEBROW

Heading

1–3 paragraphs

optional media / data figure

Source
```

Paragraph width remains readable.

Avoid an accordion for every chapter; sequential story reading is better.

---

# 26. Timeline

Desktop horizontal variant:

- rail
- milestone dots
- labels
- selected-date marker

Mobile vertical variant:

- left rail
- chronological entries

States:

- normal milestone
- selected date
- transition
- current

No “completed” green semantics.

---

# 27. ThenNowComparison

Same data density both sides.

Do not visually crown one side.

Use labels:

- Then
- Latest reference

Both show:

- date
- amount
- result
- rate if useful

Summary beneath.

---

# 28. ChartPeriodControl

Options:

- 1Y
- 5Y
- 10Y
- Custom

Use segmented control/button group.

Selected state obvious beyond color.

Do not show MAX unless useful coverage actually exists.

---

# 29. RateChart

Interaction:

- hover/touch crosshair optional
- selected historical date pinned
- latest point labelled
- keyboard access where feasible
- text/table equivalent always available

Loading:

- preserve chart frame
- scoped loading state

Error:

> Historical series is unavailable.

Single-date conversion remains intact.

---

# 30. FavoriteButton

States:

- unsaved
- saved
- saving
- unavailable local storage

Use:

- star/bookmark icon + accessible label

On first use, small confirmation:

> Saved

No toast storm.

---

# 31. Toast policy

Use toasts only for short noncritical confirmation.

Good:

- Saved
- Removed from saved

Bad:

- form validation
- provider outage
- historical coverage error

Critical information remains in context.

---

# 32. Toast duration

If used:

- long enough to read
- no essential action only inside auto-dismiss toast
- pause/interaction accessibility if necessary

Prefer inline confirmation where practical.

---

# 33. Disclosure

Use disclosures for:

- source details
- methodology
- deeper payment details
- optional technical context

Disclosure summary must describe content.

Good:

> How this rate is sourced

Bad:

> More

---

# 34. Tabs

Avoid tabs unless content categories are peer-level and switching is frequent.

Potential legitimate use:

- Chart / Table

Avoid:

- Current / Prices / Culture / History / Story

as the main information architecture if it hides useful sequential context.

---

# 35. Chips

Use sparingly for:

- historical status
- current filter
- source class if needed internally/admin

Avoid filling UI with dozens of rounded pills.

---

# 36. Navigation link states

Global nav:

- default
- hover
- focus
- active/current page

Current page should remain identifiable without color alone.

---

# 37. Header behavior

Desktop:

- may become sticky only if navigation remains useful
- height approximately 56–64px

Mobile:

- safe area aware
- avoid shrinking/expanding header animation during core conversion

Header must not obscure focused controls under zoom/keyboard navigation.

---

# 38. Mobile bottom navigation

React Native long-term:

- Convert
- Explore
- Trips
- Saved

Use only when all destinations exist.

Do not show dead tabs “coming soon”.

Web mobile can remain simpler.

---

# 39. Loading indicator policy

Three levels:

## Local spinner

Button or small content operation.

## Inline progress

Context section loading.

## Page shell loading

Only initial application hydration/native startup if necessary.

No global full-screen spinner during a simple FX refresh.

---

# 40. Skeleton policy

Allowed:

- known rectangular media/list content
- slower contextual sections

Avoid:

- result number
- short rate refresh
- tiny controls

Shimmer animation should be restrained and disabled/reduced with motion preferences.

---

# 41. EmptyState

Anatomy:

```text
Heading
One sentence
Optional action
```

Examples:

> No saved pairs yet

> Save a pair you use often for quicker access.

[Back to converter]

No giant mascot illustration required.

---

# 42. Destructive confirmation

Use modal/dialog only when consequences justify interruption.

Examples:

- delete account
- clear all cloud history

Do not confirm:

- remove one favorite
- change currency
- swap

Undo is often preferable for lightweight actions.

---

# 43. Modal

Use rarely.

Requirements:

- clear title
- obvious close
- focus trap
- Escape where platform appropriate
- focus return
- no background interaction
- mobile adaptation

Do not put core conversion inside modal.

---

# 44. Bottom sheet

Mobile-native appropriate for:

- currency picker
- source details
- rate-date options

Avoid stacked sheets.

A second action should navigate or replace current sheet instead of piling layers.

---

# 45. Tooltips

Only for supplementary concise explanation.

Not for:

- labels
- required source
- rate date
- errors
- touch-critical help

Every tooltip-triggered action must have a touch/keyboard equivalent.

---

# 46. Link styling

Links should look like links.

Use:

- color + underline or other clear convention
- focus state
- visited styling where appropriate for editorial/source links

Do not make source links indistinguishable from muted metadata.

---

# 47. External link behavior

Avoid opening new tabs automatically unless there is strong reason.

If external data-source link behavior differs, communicate it accessibly.

---

# 48. Form hint vs error

Hint:

- before error
- neutral
- stable

Error:

- after validation
- specific

Do not replace hint with error if the hint remains useful for correction; both can coexist when concise.

---

# 49. Form validation timing

Validate:

- on submit
- on blur for clear local rules when useful
- after first error, more responsive validation can help

Avoid aggressively displaying errors while a user is still typing an incomplete value.

---

# 50. Autocomplete

Country/currency search:

- do not auto-select first result merely because it exists
- Enter selects explicit active option
- preserve typed query until selection

No surprising destination change.

---

# 51. Keyboard shortcuts

P0 does not need custom shortcuts.

Potential later:

- / focus search
- s swap

Only if discoverable and conflict-free.

Do not optimize portfolio sophistication at the cost of simplicity.

---

# 52. Cursor policy

Use pointer cursor for clear custom click targets where web convention supports it.

Text/selectable content remains appropriate cursor.

Do not make static cards appear clickable.

---

# 53. Disabled visual state

Disabled controls:

- lower emphasis but still readable
- preserve label contrast
- explain prerequisite nearby

Do not use opacity 0.3 globally.

---

# 54. High-contrast mode

Audit:

- custom borders
- focus ring
- selected states
- badges
- chart line distinctions

Do not depend on subtle surface difference alone.

---

# 55. Print/share screenshot mode

Potential later feature.

If implemented:

- hide navigation/actions
- preserve rate source/date
- preserve requested/effective date
- preserve product identity

A share card never omits provenance to look cleaner.

---

# 56. Component implementation rule

Every component PR should include:

- default screenshot
- mobile screenshot
- keyboard/focus check
- error/loading state where applicable
- reduced-motion behavior
- no-JS fallback when web form-related
- tests for semantic behavior

“Looks good in one screenshot” is not component completion.
