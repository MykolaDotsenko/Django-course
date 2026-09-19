# Visual Foundations

This document defines the visual language of Cultural Currency Converter.

The design language is named **Quiet Atlas**.

The intended character is:

> **Nordic editorial utility — calm enough for money, warm enough for culture.**

The interface should feel trustworthy before it feels impressive. The “wow” comes from coherence, precision, contextual storytelling and beautifully controlled transitions — not from visual noise.

---

# 1. Design north star

A user should feel three things in sequence:

1. **I understand what to do.**
2. **I trust what I am seeing.**
3. **This feels distinct and memorable.**

The design therefore optimizes for:

```text
clarity
→ trust
→ contextual richness
→ delight
```

A visually striking choice is rejected if it lowers clarity or trust.

---

# 2. Product aesthetic

## Core style

- Nordic restraint
- editorial precision
- generous negative space
- strong numerical typography
- calm layered surfaces
- subtle cultural accents
- tactile but restrained interaction
- modern data visualization
- warm, human storytelling

## Explicitly avoid

- crypto/trading dashboard aesthetics
- casino-green/red price movement styling
- excessive glassmorphism
- neon gradients
- giant decorative blobs
- 3D coins
- spinning globes
- flag-heavy interfaces
- tourism collage layouts
- card-on-card-on-card stacking
- decorative animations during conversion
- “AI-looking” purple gradients as a default brand language

---

# 3. Visual hierarchy

The page hierarchy is fixed:

```text
1. Conversion task
2. Conversion result
3. Trust/provenance
4. Local meaning
5. Payment context
6. Historical/story context
7. Secondary actions
8. Decorative/cultural atmosphere
```

This hierarchy survives:

- desktop
- tablet
- mobile
- light theme
- dark theme if introduced
- historical mode
- country theme
- reduced-motion mode
- high zoom/reflow

Country theming may alter atmosphere, never hierarchy.

---

# 4. Canonical colour and surface system

The implementation palette is intentionally small. These values are the canonical light-theme starting point; country atmosphere is layered on top without replacing product semantics.

## 4.1 Light theme — Quiet Atlas

```css
--canvas:              #F6F7F3;
--surface:             #FFFFFF;
--surface-soft:        #EEF2EE;
--surface-accent:      #DCEFEB;

--text-primary:        #14211D;
--text-secondary:      #596660;
--text-tertiary:       #66736C;
--text-inverse:        #FFFFFF;

--border-subtle:       #D7DED9;
--border-control:      #7B8982;

--brand:               #0B6B61;
--brand-hover:         #085A52;
--brand-soft:          #DCEFEB;

--history:             #345E7D;
--history-soft:        #E4EDF4;

--success:             #2D6A4F;
--success-soft:        #E5F2E9;

--warning:             #9A5A13;
--warning-soft:        #FFF2D8;

--danger:              #A93632;
--danger-soft:         #FCE8E7;

--focus:               #0B6B61;
```

## 4.2 Verified contrast targets

The palette is chosen so normal body/status text can meet WCAG AA without relying on oversized type.

Measured contrast examples:

| Foreground | Background | Approx. contrast |
|---|---|---:|
| #14211D | #FFFFFF | 16.60:1 |
| #14211D | #F6F7F3 | 15.43:1 |
| #596660 | #FFFFFF | 6.01:1 |
| #66736C | #FFFFFF | 4.96:1 |
| #0B6B61 | #FFFFFF | 6.38:1 |
| #FFFFFF | #0B6B61 | 6.38:1 |
| #FFFFFF | #345E7D | 6.90:1 |
| #FFFFFF | #A93632 | 6.44:1 |
| #0B6B61 | #DCEFEB | 5.35:1 |
| #345E7D | #E4EDF4 | 5.82:1 |
| #9A5A13 | #FFF2D8 | 4.93:1 |
| #A93632 | #FCE8E7 | 5.47:1 |

These values still require component-level testing because contrast depends on actual adjacent pixels and states.

## 4.3 Surface hierarchy

### Canvas

`#F6F7F3`

Use for:

- global page background;
- large quiet breathing areas;
- subtle country atmosphere.

### Surface

`#FFFFFF`

Use for:

- converter stage;
- important interactive panels;
- menus/sheets/dialogs.

### Soft surface

`#EEF2EE`

Use for:

- inset metadata;
- quiet supporting groups;
- read-only context.

### Accent surface

`#DCEFEB`

Use sparingly for:

- selected state;
- brand-supportive highlight;
- calm contextual emphasis.

Do not alternate backgrounds merely to make every section look different.

## 4.4 Border hierarchy

`--border-subtle` is for grouping where the boundary is supplementary.

`--border-control` is used where the visible boundary is itself necessary to recognize an input/control.

Do not use a very low-contrast border as the only way to discover a control.

## 4.5 Brand colour

The brand colour is **fjord teal**:

`#0B6B61`

It communicates:

- calm;
- trust;
- travel/geography;
- Nordic identity without literal flag colours.

Primary uses:

- primary action;
- selected navigation;
- selected chart series;
- focus relationship;
- small brand accents.

The brand colour is **not** used for:

- every heading;
- every icon;
- every card border;
- generic decoration.

This follows the principle that a brand accent gains meaning through scarcity.

## 4.6 Historical colour

Historical mode uses **archive blue**:

`#345E7D`

It communicates temporal/informational context without creating nostalgic sepia styling.

Historical mode changes:

- status accent;
- timeline marker;
- selected historical point;
- small date-context surfaces.

It does not recolour the whole application.

## 4.7 Status colours

### Success

`#2D6A4F`

Only:

- operation succeeded;
- valid completion;
- saved state confirmation.

Never:

- "good currency";
- rate increased;
- country is cheaper.

### Warning

`#9A5A13`

Use for:

- cached/stale quote;
- partial data;
- assumption requiring attention.

### Danger

`#A93632`

Use for:

- field validation;
- destructive action;
- unrecoverable error.

### Informational/history

`#345E7D`

Use for:

- historical mode;
- source/context note;
- neutral informational status.

Every status also has text and, when useful, iconography. Colour is never the only carrier of meaning.

## 4.8 Optional dark theme palette

Dark mode is not required for first release, but its intended palette is documented to prevent arbitrary inversion later.

```css
--dark-canvas:         #0D1512;
--dark-surface:        #121D19;
--dark-surface-soft:   #182620;
--dark-text-primary:   #F2F7F4;
--dark-text-secondary: #AAB8B1;
--dark-border:         #2B3A34;

--dark-brand:          #78D1C4;
--dark-history:        #8FB5D1;
--dark-warning:        #E7B567;
--dark-danger:         #F08A85;
--dark-success:        #83C99F;
```

The dark palette is a separate design pass, not an automatic inversion.

---

# 5. Text hierarchy

Use semantic text roles.

```text
primary   → core task/result/content
secondary → supporting explanation/provenance
tertiary  → nonessential metadata only
inverse   → text on strong filled controls
```

Rules:

- important provenance never uses low-contrast tertiary treatment;
- timestamps are secondary, not fine print;
- disabled text remains readable;
- placeholders never substitute for labels.

---

# 6. Country accent system

Country accents are contextual atmosphere, not brand replacement.

Each country can provide:

```text
country_accent
country_accent_soft
country_pattern
country_image
```

Rules:

1. Accent must pass contrast in its actual role.
2. Accent never changes error/success semantics.
3. Accent never changes button location or control hierarchy.
4. One screen uses at most one primary destination accent plus neutral base.
5. Source-country and destination-country accents must not create a “team A vs team B” competition.
6. Avoid literal flag-color gradients as default theming.
7. Avoid culturally stereotyped motifs.
8. Cultural patterns are low-contrast and decorative only.

Example:

Finland may use:

- cool lake blue
- pale ice neutral
- extremely subtle water/forest geometry

Japan may use:

- warm mineral neutral
- restrained vermilion accent
- subtle geometric reference

But controls remain the same components.

---

# 9. Historical-mode accent

Historical mode should not become sepia.

Use temporal semantics instead:

- small “Historical reference” label
- date prominence
- timeline rail
- subtle desaturated informational accent
- editorial typography shift only where meaningful

Avoid:

- fake paper texture
- faux-aged photographs
- brown overlay over all content
- typewriter fonts
- clock animations

The historical experience should feel archival and precise, not nostalgic.

---

# 10. Typography strategy

## Primary family

Prefer one high-quality variable sans family.

Candidate:

> **Inter Variable**, self-hosted if used.

Fallback:

```css
font-family:
  Inter,
  ui-sans-serif,
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  sans-serif;
```

Do not load fonts from a runtime third-party CDN.

## Optional editorial family

A serif may be introduced only in long-form Story pages if it materially improves editorial character.

It must not appear in:

- inputs
- buttons
- amounts
- rate metadata
- tables
- charts

P0 can ship sans-only.

---

# 11. Type scale

Use a restrained modular scale with fluid behavior for large headings.

Suggested semantic scale:

```text
display-result  clamp(2.25rem, 7vw, 4.75rem)
display-page    clamp(2rem, 5vw, 3.75rem)
heading-1       clamp(1.75rem, 3vw, 2.5rem)
heading-2       1.5rem
heading-3       1.25rem
body-lg         1.125rem
body            1rem
body-sm         0.875rem
meta            0.8125rem minimum candidate
```

Rules:

- do not go below comfortable metadata size merely to fit more
- result amount uses tabular numerals if supported
- chart axes remain legible at mobile size
- font weight hierarchy is preferred over many font sizes
- avoid light/thin weights

Apple’s current typography guidance explicitly recommends minimizing typefaces and avoiding very light weights for legibility.

---

# 12. Numeric typography

Money is a first-class typographic object.

Use:

- tabular figures
- clear decimal separation
- currency code adjacent
- locale-aware grouping
- strong baseline alignment

Example:

```text
17 450
JPY
```

or:

```text
17,450 JPY
```

depending on locale.

Do not visually emphasize symbol over code where symbol is ambiguous.

Use the approximation symbol deliberately:

```text
100 EUR ≈ 17,450 JPY
```

---

# 13. Line length

Editorial text:

- ideal 55–75 characters per line
- max approximately 80 for body copy

Utility panels:

- content width follows task, not arbitrary max-width prose rules

Long story chapters should not span full desktop viewport.

---

# 14. Spacing system

Use a 4px base rhythm.

Semantic spacing tokens:

```text
1  = 4px
2  = 8px
3  = 12px
4  = 16px
5  = 20px
6  = 24px
8  = 32px
10 = 40px
12 = 48px
16 = 64px
20 = 80px
24 = 96px
```

Preferred relationships:

- icon ↔ label: 8px
- label ↔ field: 8px
- field ↔ hint/error: 6–8px
- related controls: 12–16px
- component internal padding: 16–24px
- major sections: 48–80px depending viewport

Do not use arbitrary 13px/19px/27px gaps without a measured reason.

---

# 15. Grid system

## Desktop

- max content width: approximately 1200–1280px
- 12-column grid
- 24–32px gutters
- page side padding: 32–48px

## Tablet

- 8-column conceptual grid
- 24px page padding

## Mobile

- 4-column conceptual grid
- 16px page padding
- 12px minimum only on very narrow devices where needed

The grid guides relationships, not every pixel.

---

# 16. Container strategy

Use viewport breakpoints for page-level navigation.

Use Tailwind 4 container queries for reusable components whose layout depends on actual available width.

Examples:

- converter panel
- result card
- Then & Now comparison
- typical-price grid
- story chapter collection

This avoids components knowing the entire device viewport.

Tailwind 4 supports first-class container queries and CSS theme variables, which fits this design-system approach.

---

# 17. Width rules

## Converter

Desktop ideal width:

- approximately 880–1120px depending split layout

Do not stretch form controls across 1600px merely because monitor allows it.

## Story

- 640–760px readable column
- supplemental timeline/media may extend wider

## Tables/charts

- may use wider content region
- labels remain readable without excessive whitespace

---

# 18. Border system

Borders are quiet structural cues.

Suggested:

```css
--border-subtle: oklch(0.90 0.006 245);
--border-default: oklch(0.84 0.008 245);
--border-strong: oklch(0.70 0.01 245);
```

Use:

- 1px default structural border
- 2px for selected/error/focus-adjacent relationships where semantically useful

Avoid dark box outlines around every card.

---

# 19. Radius system

Use a restrained radius scale.

```text
sm  8px
md  12px
lg  16px
xl  24px
pill 999px
```

Rules:

- inputs/buttons: 10–12px
- primary panels: 16–24px
- status chips: pill
- do not make every surface a giant 32px rounded rectangle
- nested radii decrease inward

---

# 20. Shadow system

Use almost no shadow for static content.

Suggested roles:

## Shadow 1

Subtle interactive hover/elevation.

## Shadow 2

Popover/menu.

## Shadow 3

Modal/sheet only.

Cards should normally rely on:

- spacing
- border
- background

instead of shadow.

---

# 21. Materials and translucency

Web:

Use translucency rarely and only when it clarifies functional layering.

Good:

- sticky floating navigation/action shell over scrolling content

Bad:

- every card uses blur backdrop

React Native/iOS:

System materials/Liquid Glass can be used for navigation/control layers where platform conventions make sense.

Do not copy Apple Liquid Glass into web content surfaces just because it is fashionable.

Apple’s guidance treats material as a hierarchy/control-layer tool, not a generic content decoration.

---

# 22. Iconography

Use one coherent icon family.

Requirements:

- simple stroke/fill language
- optical consistency
- 16/20/24px standard sizes
- text labels for ambiguous actions
- no emoji as core UI icons
- flags remain country context, not interface controls

Swap:

- icon + accessible label
- visually simple
- no spinning globe

Historical:

- calendar/timeline icon
- avoid clock cliché where date context is clearer

---

# 23. Image language

Cultural imagery should be:

- editorial
- authentic
- quiet
- contextually relevant
- secondary to data

Avoid:

- generic stock-travel hero images
- obvious AI travel clichés
- oversaturated postcard photography
- full-bleed images behind critical text
- using flags as giant backgrounds

Recommended placements:

- Explore pages
- Story chapter break
- country profile header
- optional contextual side panel

Never place visually busy imagery behind amount/rate data.

---

# 24. Decorative pattern language

Patterns may reference:

- geography
- craft
- architecture
- natural forms
- currency engraving geometry

Rules:

- opacity very low
- no semantic information
- hidden from assistive tech
- no cultural motif without review
- one motif per context, not a collage

---

# 25. Light theme

Light mode is primary.

Desired character:

- cool off-white canvas
- near-black ink
- quiet borders
- one strong accent
- cultural accent used sparingly

Avoid pure #ffffff + pure #000 everywhere because it can feel harsh and generic.

---

# 26. Dark theme

Dark mode is optional after light mode reaches full quality.

If implemented:

- design separately, not invert colors mechanically
- preserve status semantics
- reduce saturation
- avoid glowing accent edges
- keep provenance readable
- charts get dark-theme-specific palette

Do not ship a mediocre dark theme solely for feature completeness.

---

# 27. Focus design

Keyboard focus is a first-class visual state.

Target:

- at least equivalent to a 2 CSS px visible perimeter
- strong contrast against adjacent colors
- offset where needed to avoid border collision

Candidate:

```css
outline: 2px solid var(--focus);
outline-offset: 2px;
```

Focus must remain visible over:

- country accents
- error states
- elevated menus
- historical mode
- dark theme

Do not suppress browser focus without a superior replacement.

---

# 28. Touch targets

WCAG 2.2 AA minimum target-size guidance is 24×24 CSS px or sufficient spacing.

Our product deliberately aims above this:

## Web touch-heavy controls

Target approximately 44px minimum height.

## Primary mobile controls

Target 48–56px visual/hit height where practical.

Critical controls:

- currency picker
- amount field
- swap
- Convert
- date selector
- save
- bottom navigation

Tiny icon buttons are not acceptable for primary workflows.

---

# 29. Hover

Hover is enhancement only.

Hover may provide:

- subtle background shift
- border emphasis
- elevation
- icon translation by 1–2px

Never reveal essential:

- source
- date
- error
- action label

only on hover.

Touch users must lose nothing.

---

# 30. Pressed/active state

Pressed feedback should feel tactile but calm.

Candidate:

- reduce scale to 0.98–0.99 for custom buttons
- shorten shadow
- darken/shift fill slightly

Duration:

- approximately 80–120ms

Disable scale motion in reduced-motion mode if it becomes distracting.

---

# 31. Motion system

Motion must communicate:

- relationship
- state change
- continuity
- direct manipulation

Not decoration.

Suggested duration families:

```text
instant feedback     80–120ms
small UI transition  140–180ms
panel transition     180–240ms
large navigation     240–320ms maximum
```

Preferred easing:

- decelerating ease-out on enter
- slightly faster ease-in on exit
- spring only for mobile native direct manipulation where subtle

Avoid:

- 500ms form transitions
- bounce on financial results
- number count-up
- autoplay timeline travel
- constant floating objects

---

# 32. Reduced motion

When `prefers-reduced-motion: reduce`:

- remove transforms that imply travel
- replace animated position changes with instant/opacity changes
- avoid smooth auto-scroll
- no chart drawing animation
- no background parallax

Information remains identical.

---

# 33. Responsive principle

Do not design desktop and then collapse it.

Design three intentional experiences:

## Wide

Comparison and context can coexist.

## Compact

Prioritize task flow and sectional disclosure.

## Mobile

One-hand utility first.

Layout decisions follow available space/content, not device brand names.

---

# 34. Reflow

At narrow widths/high zoom:

- no horizontal scroll for core converter
- From/To stack
- Swap becomes vertical orientation if useful
- result remains first after controls
- metadata wraps gracefully
- source links remain tappable
- story timeline becomes vertical

Charts may scroll only if an accessible summary/table is also available and the chart cannot be meaningfully compressed.

---

# 35. Skeleton/loading visuals

Prefer stability over skeleton theater.

Use a skeleton only if:

- content geometry is predictable
- wait is perceptible
- placeholder reduces layout shift

Do not show skeleton for a result that usually returns almost immediately.

For updates:

- keep previous result
- mark “Updating…”
- preserve layout

---

# 36. Empty-state visual language

Empty states should be quiet.

Structure:

```text
short heading
one sentence
one useful action if needed
```

Avoid large illustrations unless the page would otherwise be visually empty and the illustration has clear brand value.

---

# 37. Error visual language

Errors should look serious but not alarming.

Use:

- semantic icon
- clear text
- specific field/message
- recovery action

Do not:

- shake forms
- flash red page background
- use exclamation icons everywhere
- erase user input

---

# 38. Data visualization palette

Charts need a dedicated semantic palette.

Rules:

- current/primary pair: core accent
- comparison line: neutral contrasting hue
- historical selected point: stronger marker
- stale/missing periods: pattern/gap, not fake interpolation
- positive/negative market-color semantics are avoided

Tooltips are supplemental.

All important values also exist in:

- visible text summary
- accessible table/description

---

# 39. Chart density

Default chart should communicate one question.

Do not show:

- 5 overlays
- candlesticks
- RSI
- volume
- trading indicators

This is not a trading terminal.

Preferred:

- one clean line
- selected point
- high/low/current
- period controls

---

# 40. Visual consistency audit

Every feature PR should check:

- token usage
- spacing scale
- radius scale
- typography role
- state colors
- focus state
- hover/pressed
- loading
- error
- mobile layout
- high zoom
- reduced motion
- source/provenance visibility

A one-off visually attractive exception is not automatically acceptable.

---

# 41. Tailwind implementation model

Tailwind 4 uses semantic theme variables.

Example direction:

```css
@theme {
  --font-sans: Inter, ui-sans-serif, system-ui, sans-serif;

  --color-canvas: ...;
  --color-surface: ...;
  --color-ink: ...;
  --color-muted: ...;
  --color-accent: ...;

  --radius-control: 0.75rem;
  --radius-panel: 1rem;

  --ease-product: cubic-bezier(...);
}
```

Country-specific atmosphere belongs in normal CSS custom properties scoped to context when it should not generate global utilities.

Do not fill templates with arbitrary hex values.

---

# 42. CSS architecture rule

Tailwind utilities remain the primary composition mechanism.

Use custom component CSS for:

- complex visual primitive
- pseudo-element
- cultural background pattern
- chart-specific styling
- reusable state that becomes unreadable as repeated utility soup

Do not create an enormous semantic class layer that recreates Bootstrap.

---

# 43. Design review scorecard

Every screen can be scored /100:

| Criterion | Weight |
|---|---:|
| Task clarity | 15 |
| Information hierarchy | 12 |
| Trust/provenance visibility | 10 |
| Typography | 8 |
| Spacing/layout | 8 |
| Accessibility | 12 |
| Responsive behavior | 10 |
| Interaction states | 8 |
| Cultural distinctiveness | 6 |
| Motion restraint | 4 |
| Performance-aware design | 4 |
| Visual polish/coherence | 3 |

Target before declaring a key screen done:

> **95+/100 with no critical trust/accessibility defect.**

---

# 44. Visual principle summary

The interface should look expensive because it is:

- precise
- quiet
- proportioned
- consistent
- context-aware

—not because it contains more effects.
