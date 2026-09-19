# Visual Foundations

This document defines the visual language of Cultural Currency Converter.

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

# 4. Core surface model

Use four semantic elevation layers.

## Surface 0 — Canvas

Page/background layer.

Purpose:

- establish calm visual field
- support edge-to-edge cultural atmosphere
- never compete with content

Suggested light token:

```css
--surface-canvas: oklch(0.985 0.004 245);
```

## Surface 1 — Primary content

Converter/result/content panels.

```css
--surface-primary: oklch(0.998 0.002 245);
```

Use only where grouping improves comprehension.

Do not put every section in a card.

## Surface 2 — Muted context

Metadata, inset details, low-priority grouped content.

```css
--surface-muted: oklch(0.965 0.006 245);
```

## Surface 3 — Elevated/interactive

Menus, popovers, command/search surfaces.

```css
--surface-elevated: oklch(1 0 0);
```

Shadow/elevation is reserved for elements that actually float over content.

---

# 5. Ink hierarchy

Use semantic text roles.

```css
--text-primary: oklch(0.22 0.014 250);
--text-secondary: oklch(0.43 0.014 250);
--text-tertiary: oklch(0.56 0.012 250);
--text-inverse: oklch(0.98 0.004 245);
```

Rules:

- important provenance never uses tertiary text if contrast becomes marginal
- timestamps may be secondary, not “fine print”
- disabled text is not simply faded to illegibility
- placeholders are never substitutes for labels

---

# 6. Core brand accent

The base product accent should feel Nordic and trustworthy rather than “bank blue”.

Candidate family:

```css
--accent-50:  oklch(0.97 0.02 225);
--accent-100: oklch(0.93 0.04 225);
--accent-300: oklch(0.78 0.09 225);
--accent-500: oklch(0.61 0.13 225);
--accent-600: oklch(0.53 0.12 225);
--accent-700: oklch(0.45 0.105 225);
--accent-800: oklch(0.36 0.08 225);
```

Use cases:

- primary action
- active/focus relationships
- selected navigation
- chart primary series
- subtle brand highlights

Never use accent simply to make a neutral paragraph look “interesting”.

---

# 7. Semantic status colours

Status colors communicate state, not market desirability.

## Positive/success

Use only for successful completion or valid status.

Do not use it to mean:

- currency gained
- “good rate”
- better country

## Warning

Use for:

- stale/cached data
- partial availability
- assumptions requiring attention

## Danger

Use for:

- validation error
- destructive action
- unrecoverable failure

## Informational

Use for:

- historical mode
- source/context note
- neutral provider information

Every status combines:

- text
- optional icon
- optional color

Never color alone.

---

# 8. Country accent system

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
