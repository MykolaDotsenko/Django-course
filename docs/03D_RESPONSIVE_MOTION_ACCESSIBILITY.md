# Responsive, Motion, Accessibility and Design QA

This document defines cross-cutting implementation constraints that keep the visual system usable across devices, input modes and accessibility settings.

---

# 1. Responsive philosophy

Responsive design is content-driven.

Do not ask:

> What does this look like on iPhone 15?

Ask:

> At what width does this relationship stop being understandable?

Use:

- page breakpoints for macro layout
- container queries for components

Tailwind 4's first-class container queries are preferred for reusable component adaptation.

---

# 2. Page width bands

These are design reference bands, not device targets.

## Compact

< ~640px

- stacked converter
- full-width actions
- vertical timeline
- compact metadata

## Medium

~640–1024px

- selective two-column layout
- result still strongly separated
- local value may be 2-column

## Wide

> ~1024px

- source/destination comparison
- richer side-by-side context
- max-width constrained content

Do not hard-code all layout decisions to these exact values; test intrinsic breakpoints.

---

# 3. 320 CSS px resilience

Core flow must remain usable around 320 CSS px width under reflow/zoom scenarios.

Requirements:

- no horizontal scroll for amount/pair/convert/result
- currency codes do not overlap
- status badges wrap
- source metadata wraps
- action labels remain visible
- focus ring not clipped

---

# 4. Large desktop

At 1440–1920px:

- content does not stretch indefinitely
- negative space increases
- story body stays narrow
- chart may grow moderately
- converter retains intentional width

Do not increase type size indefinitely with viewport.

---

# 5. Orientation

Mobile landscape must remain usable.

Avoid height assumptions that require:

- full viewport hero
- fixed panels
- bottom actions covering content

Scrollable flow wins.

---

# 6. Safe areas

React Native:

Respect:

- top notch/island
- bottom home indicator
- keyboard
- landscape cutouts

Web installed/PWA contexts may also need safe-area insets if used.

---

# 7. Virtual keyboard

On mobile:

- focused amount/search remains visible
- sticky/fixed actions do not cover field
- sheet adjusts to keyboard
- pressing return has predictable action

Do not auto-scroll page erratically on each validation update.

---

# 8. Text scaling

Native:

Support platform text scaling.

Web:

Layout survives browser font scaling/zoom.

Do not lock component height so increased text clips.

Headings and narrow intro/body copy permit emergency word wrapping when a single long token would
otherwise force horizontal scrolling at narrow reflow widths. Normal-width typography remains
unchanged.

Buttons can grow vertically.

---

# 9. Reflow ordering

When two-column converter stacks:

Correct order:

```text
Amount
From
Swap
To
Date
Convert
Result
```

Do not let CSS visual ordering differ from DOM reading order.

---

# 10. Container-query candidates

Use container queries for:

- From/To selector composition
- result horizontal vs stacked form
- local-value cards
- Then & Now
- provenance row
- story media placement

Avoid viewport media queries inside deeply reusable components where container context is what matters.

---

# 11. Breakpoint testing

Test at:

- just below component transition
- exact transition
- just above transition

Most responsive bugs occur around the threshold, not at canonical device widths.

---

# 12. Accessibility baseline

Target:

> WCAG 2.2 AA

This includes but is not limited to:

- keyboard operability
- focus visibility
- target sizing
- contrast
- semantic structure
- labels
- error identification
- reflow
- reduced motion support
- non-color-only communication

Automated tests supplement, not replace, manual review.

---

# 13. Focus appearance

Target a visible focus indicator at least equivalent in area to a 2 CSS px perimeter.

W3C's Focus Appearance understanding specifically describes a solid 2 CSS px perimeter as the simplest sufficient pattern.

Implementation must also ensure focus is not obscured by sticky UI.

---

# 14. Target sizing

WCAG 2.2 AA Target Size (Minimum):

- 24×24 CSS px or sufficient spacing under documented exceptions

Product target exceeds minimum for frequently used touch controls.

Recommended:

- web primary control: 44px+
- native mobile primary control: 48–56px

---

# 15. Contrast policy

Minimum WCAG AA contrast requirements apply.

Design policy:

- body text targets stronger than bare minimum where practical
- metadata never intentionally skirts threshold
- focus ring has clear adjacent contrast
- country accents cannot reduce required contrast

Automated contrast checks should run on token combinations.

---

# 16. Color blindness

Never encode alone by:

- red/green
- blue/orange
- saturation

Examples:

Historical selected point:

- marker shape + label + color

Cached result:

- “Cached” text + icon + color

Error:

- text + icon + border + color

---

# 17. Semantic landmarks

Web pages use:

- header
- nav
- main
- sections with headings
- footer

Do not create every layout from nested generic divs.

---

# 18. Heading hierarchy

One clear page H1.

Sections follow logical order.

Do not choose heading level for visual size.

Story chapter visual style maps onto semantic heading hierarchy.

---

# 19. Forms

Every input:

- visible label
- programmatic label
- hint association
- error association
- appropriate autocomplete where relevant

Country/currency picker trigger needs an accessible name describing current selection.

---

# 20. Live regions

Use minimally.

Appropriate:

- conversion completed
- meaningful update failure
- cached/offline status change

Avoid:

- typing echo
- loading pulses
- story content dump
- multiple simultaneous live regions

---

# 21. Screen reader source detail

The result reading order should be:

1. result
2. pair
3. reference type
4. effective date
5. optional cached/historical status
6. source detail affordance

Do not read decorative flags as duplicate country names.

Flag images should be decorative if country text is already present.

---

# 22. Accessible names

Icon-only visual buttons require text accessible names.

Examples:

- Swap source and destination
- Save currency pair
- Remove saved pair
- Close currency search

Avoid labels:

- Button
- Swap icon
- Star

---

# 23. Motion principles

Motion answers one of:

- what changed?
- where did it go?
- did my action register?
- what layer opened?

If none apply, motion is probably unnecessary.

---

# 24. Motion tokens

Candidate:

```css
--duration-instant: 100ms;
--duration-fast: 160ms;
--duration-base: 220ms;
--duration-slow: 300ms;

--ease-enter: cubic-bezier(...);
--ease-exit: cubic-bezier(...);
--ease-standard: cubic-bezier(...);
```

Tune visually during implementation.

Do not create 12 unique easing curves.

---

# 25. HTMX transitions

Use CSS transitions around stable fragment containers.

Do not animate:

- result number counting
- entire page
- form field positions on every request

Good:

- slight fade/crossfade result metadata
- context section appearance
- inline alert insertion

Ensure old/new result never overlap confusingly.

---

# 26. View transitions

Do not adopt browser View Transitions merely because available.

Use only if:

- browser support matches target
- transition improves spatial continuity
- reduced motion behavior is clean
- no progressive-enhancement regression

P0 does not require them.

---

# 27. Reduced motion mapping

When reduced motion is requested:

| Effect | Normal | Reduced |
|---|---|---|
| button press | subtle scale | fill change |
| panel enter | fade + small movement | instant/fade |
| swap | small orientation transition | instant |
| chart | optional draw/fade | instant |
| story navigation | subtle transition | instant |
| skeleton shimmer | restrained | static |

---

# 28. Scroll motion

Avoid programmatic smooth-scroll after conversion.

A result should appear where expected.

If mobile result is offscreen after submit, use carefully tested focus/scroll behavior only when needed.

Do not fight user scroll position.

---

# 29. Performance-aware design

Visual decisions must consider:

- CSS size
- font weight files
- image bytes
- JS requirement
- layout shift
- rendering cost

The design must not require a React web runtime to look premium.

---

# 30. Font performance

If Inter Variable is used:

- self-host WOFF2
- preload only critical font if measured
- use font-display strategy
- avoid loading 8 static weights

System fallback should produce a reasonable layout.

---

# 31. Image performance

For cultural media:

- responsive sizes
- modern format when permitted
- intrinsic dimensions
- lazy loading below fold
- no multi-megabyte hero
- blur/placeholders only if useful

Alt text follows content role.

Decorative image:

- empty alt / hidden appropriately

Informative image:

- meaningful concise alt

---

# 32. CLS protection

Reserve space for:

- flags
- contextual images
- charts
- loading sections

Do not insert a large alert above the amount field after result if it shifts the entire workflow unexpectedly.

---

# 33. LCP priorities

Likely LCP should be:

- text/converter surface

not a giant decorative image.

This is desirable.

Do not introduce above-fold imagery that harms first-use speed.

---

# 34. Microcopy QA

Design review includes wording because layout depends on it.

Test:

- long country names
- long currency names
- German/Finnish-style longer translations
- decimal grouping
- long source names
- historical labels

Do not size components only for “Japan / JPY”.

---

# 35. Localization resilience

Avoid fixed widths around labels.

Use logical properties:

- margin-inline
- padding-inline
- inset-inline

where appropriate.

Tailwind 4 supports logical-property utilities and modern CSS capabilities that improve RTL readiness.

---

# 36. RTL readiness

Do not assume:

- arrow right = forward
- source is semantically “left”
- destination is semantically “right”

DOM semantics remain From/To independent of visual direction.

Directional icons audited before RTL launch.

---

# 37. Cultural sensitivity review

Country theme/content review checks:

- stereotype risk
- religious/political symbol misuse
- flag misuse
- color connotations
- image rights
- representative accuracy
- current country naming

Cultural theming is optional.

Neutral theme is always a valid fallback.

---

# 38. Historical sensitivity

Historical storytelling avoids aestheticizing:

- war
- crisis
- colonial harm
- hyperinflation
- political upheaval

when context appears.

Use neutral factual tone and source attribution.

No “fun fact” treatment for serious events.

---

# 39. Design QA workflow

For each major feature:

## Pass 1 — Task

Can the user complete the task quickly?

## Pass 2 — Hierarchy

Can they identify primary, secondary, tertiary information?

## Pass 3 — Trust

Are source/date/status visible and comprehensible?

## Pass 4 — States

Test loading/error/stale/empty/partial.

## Pass 5 — Responsive

Test intrinsic widths and mobile.

## Pass 6 — Accessibility

Keyboard, focus, semantics, zoom, contrast.

## Pass 7 — Motion

Does motion help? Is reduced-motion correct?

## Pass 8 — Polish

Only now tune optical details.

---

# 40. Visual regression

Use screenshot tests selectively for:

- converter desktop/mobile
- result states
- historical state
- search picker
- story layout

Do not snapshot every minor component if maintenance cost outweighs value.

Pair visual regression with semantic/behavior tests.

---

# 41. Browser testing

At minimum target agreed modern browser matrix.

Tailwind 4 targets modern browsers; actual supported browser versions must be documented before production.

Test:

- Chromium
- Firefox
- Safari/WebKit

Particularly:

- date controls
- focus rings
- container queries
- sticky behavior
- typography metrics

---

# 42. Device testing

Emulators are insufficient for final mobile polish.

Before calling mobile UI production-ready, test at least:

- small physical phone class
- larger phone class
- iOS
- Android

Pay attention to:

- keyboard
- touch accuracy
- safe areas
- scroll
- font scaling

---

# 43. Design completion criteria

A key surface is design-complete only when:

- happy path is coherent
- empty state defined
- loading defined
- error defined
- stale/offline defined where relevant
- mobile defined
- keyboard behavior defined
- focus visible
- source/provenance present
- text scaling survives
- reduced motion survives
- long content survives
- token usage consistent

A Figma-perfect happy-path screenshot is not completion.

---

# 44. Quality target

Desired design maturity:

| Area | Target |
|---|---:|
| UX hierarchy | 98/100 |
| Accessibility | 98/100 |
| Responsive design | 98/100 |
| Trust/provenance presentation | 99/100 |
| Typography | 97/100 |
| Component consistency | 98/100 |
| Motion | 96/100 |
| Cultural distinctiveness | 96/100 |
| Performance-aware design | 98/100 |
| Overall product design | 98/100 |

These are design targets, not claims about current implementation.


---

# 45. Bilateral responsive invariant

The source/destination cultural relationship is semantic, not tied to horizontal positioning.

## Wide

Prefer simultaneous bilateral presentation when readable.

## Medium

Keep two sides together only while:

- country/currency names fit;
- amount/result hierarchy remains dominant;
- touch/focus targets stay comfortable.

Otherwise stack.

## Compact

Preserve this semantic order:

```text
source identity
→ amount/action
→ result
→ destination identity
→ trust
→ local context
```

Do not use CSS visual reordering that makes screen-reader/keyboard order differ from the logical task flow.

Cultural visuals may disappear at narrow widths before any core information or control is removed.

This is an intentional degradation path, not a loss of product identity.
