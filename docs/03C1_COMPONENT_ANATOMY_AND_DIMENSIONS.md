# Component Specifications

This document defines the anatomy, sizing, hierarchy, visual states and accessibility behavior of the primary UI components.

The design language is **Quiet Atlas**.

A component is considered complete only when its default, hover, focus, pressed, disabled, loading, error and narrow-layout behavior are understood.

---

# 1. Component principles

Every component must satisfy all of these:

1. Its purpose is understandable without animation.
2. Its purpose is understandable without color.
3. Keyboard focus is visible.
4. Touch target is comfortable.
5. Text may expand without breaking layout.
6. Loading does not destroy layout.
7. Error does not destroy user input.
8. It works with high zoom/reflow.
9. It uses semantic design tokens.
10. It has no decorative detail that competes with the primary task.

---

# 2. AppShell

## Role

Owns:

- page canvas;
- global header;
- main landmark;
- footer;
- global max-width behavior;
- optional country atmosphere layer.

## Desktop geometry

```text
header      64px nominal
main        fluid
footer      content-driven
max-width   1200–1280px
gutter      32–48px
```

## Mobile geometry

```text
header      56px nominal
gutter      16px
safe areas  respected
```

## Rules

- no fixed viewport-height content that traps zoomed users;
- main content starts visually close to header;
- country atmosphere cannot reduce text/control contrast;
- decorative background is `pointer-events: none`.

---

# 3. Header

## Purpose

Orient, not advertise.

## Desktop anatomy

```text
[Brand]          [Convert] [Explore] [Saved]             [utility]
```

P0 only renders navigation destinations that actually exist.

## Mobile anatomy

```text
[Brand]                                             [Menu]
```

or, if only two destinations exist:

```text
[Brand]                                         [Sources]
```

Avoid a hamburger menu before there is enough navigation to justify one.

## Dimensions

- desktop min-height: 64px;
- mobile min-height: 56px;
- nav item hit area: >=44px high;
- brand mark should fit within ~120–160px width.

## Style

- transparent/canvas by default;
- optional subtle border after scroll;
- no heavy shadow;
- no oversized logo;
- no permanent glass blur unless scroll layering genuinely benefits.

## Sticky behavior

If sticky:

- keep height stable;
- use `backdrop-filter` only as enhancement;
- ensure opaque fallback;
- never obscure keyboard focus.

---

# 4. Brand mark

## Direction

The brand should feel like a cartographic/data utility rather than a bank.

Possible mark concepts:

- abstract two-way exchange path;
- latitude/longitude intersection;
- paired currency/country nodes;
- restrained monogram.

Avoid:

- dollar sign as universal symbol;
- globe with arrows cliché;
- coins;
- flags;
- bank-building icon.

## Wordmark

Preferred:

> Cultural Currency

Optional secondary:

> Converter

Do not force the full name into every small mobile header.

---

# 5. ConverterStage

## Role

The signature interaction surface.

It visually groups:

- amount;
- From;
- To;
- Swap;
- rate date;
- primary action.

## Desktop

Recommended max width:

```text
960–1120px
```

Padding:

```text
32px at >=1024px
24px around tablet range
20px compact
```

Radius:

```text
24px outer
```

Border:

```text
1px subtle structural border
```

Background:

`--surface`

Shadow:

none by default.

## Mobile

- full available width;
- 16–20px internal padding;
- 16–20px radius;
- controls stack.

## Density

The stage should feel substantial but not like a dashboard card.

Avoid inner card nesting for each field unless it improves interactivity.

---

# 6. AmountField

## Role

Primary numeric entry.

## Anatomy

```text
Amount
┌──────────────────────────────────────┐
│ 100.00                          EUR  │
└──────────────────────────────────────┘
hint/error
```

## Dimensions

Desktop:

- height: 64px;
- horizontal padding: 16–20px;
- numeric type: 24–30px.

Mobile:

- height: 60px;
- numeric type: 22–28px.

## Typography

- tabular figures;
- font weight 500–600;
- no ultrabold display style while editing;
- currency code 14–16px, medium weight.

## States

### Empty

Placeholder can show:

`0.00`

only if a visible Amount label remains and placeholder does not look like submitted data.

### Focus

Use dual-ring strategy where needed:

```css
box-shadow:
  0 0 0 2px var(--surface),
  0 0 0 4px var(--focus);
```

### Error

- danger border;
- explicit text below;
- focus ring still independently visible.

### Disabled

Avoid for ordinary form flow.

If unavailable:

- keep label readable;
- provide reason.

## Input behavior

- decimal keyboard hint on mobile;
- no currency symbols typed into numeric field;
- no auto-grouping while user is actively editing if it changes caret position;
- formatting may normalize after successful conversion.

---

# 7. FieldLabel

## Style

- 14px;
- 20px line-height;
- 600 weight;
- primary text.

## Required/optional

Do not append noisy `*` unless a form contains a meaningful mix of optional/required fields.

Prefer explicit:

> Optional

for optional contextual fields when needed.

---

# 8. FieldHint

## Style

- 13–14px;
- secondary text;
- 18–20px line-height.

## Rule

Only add hint text when it prevents a likely error.

Do not explain obvious controls.

---

# 9. FieldError

## Anatomy

```text
[error icon optional] Enter an amount such as 1234.56.
```

## Style

- 14px;
- danger text;
- 20px line-height;
- 6–8px below field.

## Rule

Specific > generic.

Good:

> Enter zero or a positive amount.

Bad:

> Invalid input.

---

# 10. CountryCurrencyTrigger

## Role

Open the country/currency picker.

## Anatomy — country context

```text
FROM

[flag] Finland
       Euro · EUR                              [chevron]
```

## Anatomy — currency only

```text
FROM

[€] Euro · EUR
    Used by multiple countries                [chevron]
```

## Geometry

Desktop:

- min-height: 72px;
- padding: 12–16px;
- radius: 12px.

Mobile:

- min-height: 68px;
- full width.

## Hierarchy

Country name:

- 16px;
- 600.

Currency detail:

- 13–14px;
- secondary.

Flag/media:

- 24–28px;
- never the sole identifier.

## States

Default:
- surface;
- control border.

Hover:
- subtle soft surface;
- border emphasis.

Focus:
- focus ring.

Selected:
- no dramatic color fill needed.

Error:
- danger border + text.

Historical archived currency:
- compact `Historical` chip;
- archive-blue semantics.

---

# 11. SwapButton

## Role

Swap full source/destination context.

## Geometry

Preferred hit target:

```text
48×48px
```

Visual icon may be 20px.

Desktop:

- positioned visually between From/To;
- must not overlap text or become inaccessible at zoom.

Mobile:

- placed between stacked controls;
- may rotate arrow icon orientation;
- accessible name remains unchanged.

## Style

- secondary/quiet button;
- white or soft surface;
- control border;
- no primary-brand fill.

## Hover

- soft brand surface;
- brand icon.

## Pressed

- minimal translation/scale;
- 80–120ms.

## Focus

Strong ring.

## Tooltip

Optional for pointer users:

> Swap

but accessible name is always present in markup.

---

# 12. RateDateControl

## Role

Switch between latest available and historical date.

## Default anatomy

```text
Rate date
Latest available                               [chevron]
```

## Historical anatomy

```text
Rate date
Historical · 15 Jun 1998                       [calendar]
```

## Design

- compact secondary control;
- not visually equal to Amount/From/To;
- minimum 44px hit height.

## Interaction

P0 web:

- standard/select/disclosure with accessible date input;
- avoid building a custom date picker unless native behavior proves inadequate.

Mobile native:

- platform date picker/sheet.

## Historical status

Use archive blue as label/icon accent, not whole-control fill.

---

# 13. PrimaryButton

## Default

```text
Convert
```

## Geometry

Desktop:

- min-height: 48px;
- horizontal padding: 20–24px;
- radius: 12px.

Mobile:

- min-height: 52px;
- full width in form flow.

## Color

- background `#0B6B61`;
- text white;
- contrast ~6.38:1.

## Hover

`#085A52`

## Pressed

- slightly darker;
- optional scale 0.99.

## Focus

Do not rely on color shift.

Use external focus ring with sufficient contrast.

## Loading

Keep width stable.

Preferred:

```text
[small progress] Converting…
```

Do not replace with spinner-only button.

## Disabled

Avoid disabled submit unless form state makes intent obvious.

If disabled:
- opacity not below readable level;
- cursor/state clear;
- form should still expose why action is unavailable.

---

# 14. SecondaryButton

Use for:

- Source details;
- Save pair;
- Retry;
- Keep EUR;
- View table.

Style:

- surface/transparent;
- control border or text treatment;
- min 44px height for standalone button;
- brand text when action is neutral.

Do not make four secondary buttons look like four primary CTAs.

---

# 15. Tertiary/TextButton

Use for low-priority actions:

- Clear;
- Cancel;
- Learn about reference rates.

Rules:

- still has adequate target area;
- underline or strong hover/focus affordance for link-like action;
- destructive text action uses danger semantics only if destructive.

---

# 16. ConversionResult

## Role

The most important reading object after submission.

## Anatomy

```text
100 EUR
≈ 17,450 JPY

1 EUR = 174.50 JPY
Reference rate · Effective 18 Sep 2026
ECB via Frankfurter
```

## Layout

Desktop:

- may bridge source/destination columns;
- center alignment acceptable for short result block.

Mobile:

- left alignment often improves scanning;
- avoid centered long metadata.

## Result type

Desktop target:

- 48–64px depending width.

Mobile:

- 36–48px.

Use fluid `clamp()`.

## Long values

Do not overflow.

Rules:

- reduce fluid type within bounded range;
- allow wrapping between amount and currency code;
- never shrink below readability just to preserve one line.

## Approximation

The `≈` is secondary but visible.

Do not animate count-up.

---

# 17. RateMeta

## Content order

1. rate;
2. data class;
3. effective date;
4. provider/source;
5. fetched/synced time when relevant.

## Style

- 13–14px;
- secondary text;
- 20px line-height.

Provenance must not become 10px fine print.

## Interactive source

`Source details` is visible, keyboard reachable and not hover-only.

---

# 18. StatusBadge

## Types

- Reference;
- Historical;
- Cached;
- Offline;
- Partial;
- Saved.

## Geometry

- 28–32px height;
- padding 8–10px;
- pill radius;
- 12–13px label.

## Rule

Status badge is supporting metadata, not a giant banner.

Always accompany unfamiliar status with explanatory text nearby.

---

# 19. Cached/StaleResult

Keep same result typography.

Add:

```text
Cached reference
Effective 18 Sep 2026
Last synced 19 Sep · 08:12
```

Use warning-soft surface only around status metadata, not entire result.

This preserves confidence and prevents an alert-heavy appearance.

---

# 20. SourceDetails

## Desktop

Prefer anchored popover for concise details or side sheet for richer explanation.

## Mobile

Use bottom sheet/full-page detail.

## Content

```text
Rate source
Frankfurter v2

Contributing provider(s)
...

Effective date
...

Fetched
...

About this reference rate
...
```

## Rules

- not tooltip-only;
- source URLs identifiable;
- sheet/dialog focus management correct;
- close control 44px target minimum.

---

# 21. TypicalPriceCard

## Purpose

Translate destination amount into local context.

## Anatomy

```text
Coffee
¥500–650 typical

≈ 26–34
for your amount

Tokyo · May 2026
[Source]
```

## Desktop

Three items maximum in primary row.

## Mobile

Stacked list/card.

Avoid horizontal scroll for P0.

## Style

- soft surface or subtle border;
- radius 16px;
- padding 20px;
- no oversized emoji;
- small line icon optional.

## Value emphasis

The derived equivalent count is visually stronger than the source price range, because it answers the user’s contextual question.

But source scope/date remains visible.

---

# 22. PaymentGuidance

## Format

Rows, not four separate cards.

```text
Cards      Common in urban areas
Cash       Useful for smaller businesses
ATMs       …
Tipping    …
```

## Desktop

Label column:

- ~120–160px.

Value:

- flexible.

## Mobile

Stack each row:

```text
Cards
Common in urban areas
```

## Detail

A disclosure may reveal sources/caveats.

Do not use traffic-light colors.

---

# 23. CulturalTeaser

## Purpose

Invite exploration after practical task.

## Anatomy

```text
Explore money & culture

Why Japan uses the yen, how money etiquette works,
and the story behind its currency.

[Explore Japan]
```

## Style

This is where cultural atmosphere can become more expressive:

- subtle pattern;
- controlled image;
- destination accent.

Still:

- text contrast remains strong;
- primary converter style is not replaced;
- teaser remains one section, not mini landing page.

---

# 24. HistoricalCurrencySuggestion

## Scenario

Finland + 1998 + EUR.

## Component

```text
Finland used the Finnish markka (FIM) on this date.

[Use FIM]    Keep EUR
```

## Style

- archive-blue informational icon/accent;
- no warning yellow;
- no error red.

## Action hierarchy

`Use FIM`:
- secondary outlined/soft brand-history action.

`Keep EUR`:
- tertiary text action.

The product suggests; it does not scold.

---

# 25. ThenNowComparison

## Desktop

```text
THEN                             LATEST REFERENCE
15 Jun 2016                      18 Sep 2026
100 EUR ≈ X USD                  100 EUR ≈ Y USD
1 EUR = ...                      1 EUR = ...
```

Use one parent surface with a quiet divider.

Do not render one side green and one side red.

## Mobile

Stack:

1. Then;
2. Latest.

Divider between.

## Difference sentence

One neutral line underneath.

No “winner”, “gain”, arrow-up green.

---

# 26. RateChart

## Role

Answer one question:

> How did this reference rate move over the selected period?

## Visual specification

- one main line;
- 2px stroke nominal;
- brand accent;
- selected historical point 6–8px marker;
- latest point clearly distinguishable;
- quiet grid;
- no filled gradient required;
- no candlesticks;
- no volume;
- no trading indicators.

## Axes

- minimal tick count;
- locale-aware labels;
- readable 12–13px minimum;
- avoid rotated x-axis labels when possible.

## Period controls

```text
1Y  5Y  10Y  Custom
```

Use compact segmented group, not dozens of pills.

## Tooltip

Supplemental.

Everything important appears in visible summary/table.

## Missing data

Show gap.

Never connect a line across a long missing period unless methodology explicitly justifies it.

---

# 27. StoryTeaser

## Anatomy

```text
The story behind this rate

Finland was still using the markka on this date.

[Read the story]
```

## Style

- archive/history accent;
- editorial spacing;
- no clickbait;
- no large hero image required.

---

# 28. StoryChapter

## Anatomy

```text
[CATEGORY]

Heading

1–3 short paragraphs.

optional figure/media

Source
```

## Width

Readable column:

```text
640–760px
```

## Vertical rhythm

- 80–112px between major chapters desktop;
- 56–80px mobile.

## Typography

Long-form body:

- 17–18px;
- 1.6–1.75 line-height.

Do not use 14px dashboard copy for editorial stories.

---

# 29. CurrencyTimeline

## Desktop

Horizontal only when labels fit.

## Mobile

Vertical.

## Anatomy

```text
milestone
  ●────────────●────────────●
date         selected      transition
```

## Rules

- selected date strongest;
- milestone text readable without chart geometry;
- no autoplay;
- no horizontal overflow as sole access on mobile.

---

# 30. PickerDialog

This is one of the highest-risk UX components and must be built carefully.

## Desktop

Preferred:

- anchored large popover or dialog;
- width 420–520px;
- max-height ~70vh;
- search sticky within panel;
- list scrolls.

## Mobile web

Prefer full-screen dialog/page over tiny bottom sheet for large search lists.

## React Native

Native full-screen sheet/search screen.

## Focus

On open:

- focus search field if it does not trigger harmful keyboard behavior;
- otherwise focus dialog heading/container then user tabs to search.

On close:

- return focus to original trigger.

## Dismiss

- Escape desktop;
- explicit Close/Cancel;
- outside click only as convenience, not only method.

---

# 31. PickerSearch

## Anatomy

```text
Search country, currency or code
[ Japan                                      ]
```

## Geometry

- 48–52px height;
- search icon decorative;
- clear button when text exists.

## Result matching

Support:

- country;
- currency name;
- ISO code.

Do not visually bold every character match if it creates noise.

---

# 32. PickerRow

## Geometry

- minimum 56px;
- 12–16px horizontal padding.

## Anatomy

```text
[flag] Japan
       Japanese yen · JPY
```

Optional trailing:

`Historical`

## Selected state

- checkmark;
- soft accent background.

Do not rely only on row color.

---

# 33. InlineAlert

Use only when a message needs contextual emphasis.

Types:

- info;
- warning;
- error;
- success.

## Anatomy

```text
[icon] Heading optional
       Message
       Action optional
```

## Geometry

- 16px padding;
- radius 12px;
- soft semantic background.

Avoid alert boxes for ordinary provenance.

---

# 34. ErrorSummary

Use after full form submission when multiple errors exist.

## Position

Before the form fields, within converter stage.

## Content

- concise heading;
- linked list of errors.

## Focus

Programmatically focus summary after failed full submission where appropriate.

Inline HTMX validation should not repeatedly steal focus.

---

# 35. ScopedLoadingIndicator

Preferred hierarchy:

1. textual status;
2. small progress icon/indicator;
3. skeleton only if geometry is valuable.

Examples:

> Getting reference rate…

> Updating…

Avoid global overlay.

---

# 36. Skeleton

Use sparingly.

Allowed:

- image/media;
- known repeated cards with perceptible delay.

Avoid:

- fast FX result;
- text content that can simply retain previous valid value.

No shimmering across half the page.

---

# 37. EmptyState

## Anatomy

```text
Heading
One useful sentence.
Optional action.
```

Example:

> Choose a destination to convert.

No giant illustration required.

---

# 38. FavoriteButton

## Role

Save a pair.

## Unselected

```text
[bookmark icon] Save pair
```

## Selected

```text
[filled bookmark] Saved
```

Do not use star ratings metaphor.

## Feedback

State change itself + optional subtle status message.

No modal.

---

# 39. Disclosure

Use for:

- source methodology;
- payment caveats;
- story details.

## Rules

- label describes content;
- chevron rotates only as supplemental signal;
- `aria-expanded` semantics;
- no animated height that becomes sluggish with long content.

---

# 40. Modal / Sheet

Use sparingly.

Appropriate:

- picker on mobile;
- source details;
- destructive confirmation;
- account flow where necessary.

Not appropriate:

- conversion result;
- every cultural detail;
- generic marketing.

## Accessibility

- focus trap for true modal;
- background inert;
- close button;
- Escape desktop;
- focus return.

---

# 41. Footer

## Content

- Data sources;
- About;
- Privacy;
- Accessibility;
- GitHub/project link if public portfolio deployment.

## Style

- border-top or spacing, not heavy colored band;
- 14px;
- generous vertical padding 32–48px.

---

# 42. Component-state matrix

Every interactive component must specify:

| State | Required visual feedback |
|---|---|
| Default | recognizable purpose |
| Hover | subtle enhancement only |
| Focus-visible | strong ring/outline |
| Pressed | immediate tactile feedback |
| Selected | text/icon + optional color |
| Disabled | readable but unavailable |
| Loading | stable geometry + status |
| Error | explicit message + semantic styling |
| Success | clear confirmation |
| Reduced motion | same information, less transform |

---

# 43. Nested-card rule

Avoid:

```text
card
  └─ card
      └─ card
          └─ chip
```

Prefer:

- one parent grouping surface;
- internal spacing;
- dividers only where needed.

Nested surfaces are justified only when they communicate distinct interaction/elevation.

---

# 44. Icon-button rule

An icon-only button is acceptable only when:

- action is universally familiar;
- accessible name exists;
- hit target is >=44px for frequent touch use;
- tooltip exists on desktop when useful.

Primary workflow actions should generally include text.

---

# 45. Content truncation

Never truncate:

- currency code;
- amount;
- error;
- status;
- effective date.

Country/currency labels:

- prefer wrap;
- truncate only in constrained navigation contexts with full accessible name retained.

---

# 46. Component acceptance test

Before a component is considered design-complete:

- default visually clear;
- hover not required;
- focus visible;
- touch target comfortable;
- error copy defined;
- loading state defined;
- narrow layout defined;
- high zoom defined;
- reduced motion defined;
- long text tested;
- RTL risk reviewed;
- contrast checked in actual context;
- source/provenance discoverable where relevant.
