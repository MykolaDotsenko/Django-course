# Frontend Technology Strategy

Research date: **2026-09-19**.

This document selects the frontend technologies that best fit the already-defined UX, Quiet Atlas design system, historical converter, storytelling model and mobile/offline requirements.

The governing principle is:

> **Use the smallest technology surface that can implement the required experience without compromising accessibility, maintainability or visual quality.**

The product does not choose frameworks for portfolio novelty. Every dependency must earn its cost.

---

# 1. Final decision summary

## Web

| Concern | Selected technology | Decision |
|---|---|---|
| Rendering | Django Templates | ✅ Primary |
| Server-driven interactivity | HTMX 2.0.x stable | ✅ Primary |
| HTMX/Django bridge | django-htmx | ✅ Use |
| Named template fragments on Django 5.2 | django-template-partials | ✅ Use |
| Styling | Tailwind CSS 4.x | ✅ Primary |
| Design tokens | Tailwind `@theme` + CSS custom properties | ✅ Primary |
| Asset build | Vite 8.x | ✅ Primary |
| Client language | TypeScript 5.9 strict | ✅ Primary |
| Client behavior | Small typed modules + native Web APIs | ✅ Primary |
| Country/currency combobox navigation | @github/combobox-nav | ✅ Focused primitive |
| Modal search surface | native `<dialog>` | ✅ Primary |
| Disclosure | native `<details>/<summary>` | ✅ Primary |
| Historical date input | native `<input type="date">` first | ✅ Primary |
| Historical chart | Chart.js 4.x | ✅ Use, history-only |
| Typography asset | Inter Variable, self-hosted via Fontsource | ✅ Use |
| UI icons | local static Heroicons SVG partials | ✅ Use |
| Anonymous small persistence | localStorage | ✅ Limited use |
| Browser E2E | Playwright | ✅ Primary |
| Automated accessibility | @axe-core/playwright | ✅ Primary |
| TS/JS lint + format | Biome 2 | ✅ Primary |
| Type checking | `tsc --noEmit` | ✅ Primary |
| Django template lint/format | djLint | ✅ Primary |

## Mobile

| Concern | Selected technology | Decision |
|---|---|---|
| Framework | React Native | ✅ Primary |
| Runtime/toolchain | Expo SDK 57 stable | ✅ Primary now |
| React Native compatibility line | RN 0.86 via Expo 57 | ✅ Primary now |
| React | React 19.2.x via Expo matrix | ✅ Primary now |
| Navigation | Expo Router | ✅ Primary |
| Language | TypeScript strict | ✅ Primary |
| Styling | React Native StyleSheet + typed Quiet Atlas tokens | ✅ Primary |
| Native controls | @expo/ui selectively | ✅ Use |
| Historical date picker | @expo/ui DateTimePicker | ✅ Use |
| API types | openapi-typescript | ✅ Primary |
| API client | openapi-fetch | ✅ Primary |
| Remote server state | TanStack Query | ✅ Use |
| Durable offline data | expo-sqlite | ✅ Primary |
| Secure credentials later | expo-secure-store | ✅ When auth exists |
| Locale | expo-localization + Intl | ✅ Use |
| Haptics | expo-haptics | 🟢 Optional, restrained |

---

# 2. Technologies deliberately not selected

## Web React / Next.js

**Decision:** do not use.

Reasons:

- Django already owns server rendering;
- conversion flow is form/data driven rather than application-shell driven;
- HTMX fragments cover the dynamic interactions;
- React would create a second state/rendering architecture;
- hydration/runtime JS would increase payload and debugging surface;
- it would obscure the Django-first architectural signal.

React competency is demonstrated by the separate React Native client.

## Vue / Svelte

Not selected for the same reason.

They solve a client application problem the web product does not currently have.

## Alpine.js

**Decision:** do not add by default.

Why:

- HTMX already owns server-driven state;
- a second declarative attribute language would make responsibility less obvious;
- small TypeScript modules are easier to type, unit-test and search;
- native browser APIs cover disclosure/dialog behavior.

Reconsider only if repeated local-only interactive state becomes materially noisier than the dependency.

## Stimulus

Not selected initially.

It is a good server-rendered-web companion, but our JavaScript surface is small enough that typed modules plus event delegation are simpler.

## HTMX 4 beta

**Decision:** do not use production beta.

As of September 2026, HTMX 4 is still a beta release line while HTMX 2.0.10 is the maintained stable 2.x line.

Use stable 2.x until HTMX 4 is production-stable and migration value is clear.

## Bootstrap / DaisyUI / Flowbite / component kits

Not selected.

Quiet Atlas already defines a custom system.

A themed component kit would:

- constrain exact visual hierarchy;
- introduce CSS/JS that is mostly unused;
- encourage card/chrome patterns we explicitly rejected.

## jQuery

No need.

## Axios

No need.

Web interactions use HTMX/browser primitives.

Mobile API client uses `fetch` through `openapi-fetch`.

## Redux / Zustand on web

No global client state exists that justifies them.

## NativeWind on mobile

Not selected initially.

Although it resembles Tailwind, React Native and web have different layout/platform semantics.

Quiet Atlas tokens are shared semantically, not by forcing CSS utility concepts onto native UI.

## GSAP / Framer Motion for web

Not selected.

The design explicitly requires restrained state/microinteraction motion.

CSS transitions + browser APIs are sufficient.

## Custom JavaScript date picker

Not selected for P0/P1.

Native date input on web and @expo/ui on mobile provide better accessibility/platform behavior with less code.

## Service worker / Workbox on web

Not P0/P1.

Offline is a first-class mobile capability. Web PWA/offline support can be justified later by actual usage.

---

# 3. Web architecture score

Evaluation weights:

- product fit: 20
- accessibility: 15
- performance: 15
- maintainability: 15
- design freedom: 10
- progressive enhancement: 10
- testability: 5
- recruiter signal: 5
- dependency risk: 5

## Selected Django + HTMX + Tailwind + TypeScript/Vite

**98/100**

Strengths:

- server remains source of truth;
- nearly zero client business logic;
- excellent progressive enhancement;
- full Quiet Atlas design control;
- low runtime JS;
- HTML-first accessibility;
- modern typed tooling where JavaScript is genuinely needed.

## React SPA on Django API

**78/100**

Strong ecosystem but unnecessary duplication for this product.

## Next.js + Django

**69/100**

Two server/web frameworks would overlap substantially.

## Django + HTMX + Alpine

**91/100**

Perfectly viable, but adds another client-state syntax without enough current benefit.

## Django templates only, no HTMX

**85/100**

Simplest runtime, but loses the smooth fragment updates required by the designed experience.

---

# 4. Stable-version policy

Do not pin documentation to arbitrary patch versions forever.

Implementation rules:

- pin exact versions in lockfiles;
- use current stable patch within selected major/minor policy;
- Dependabot/Renovate may propose upgrades later;
- major upgrades require review against browser/runtime contracts.

Current researched anchors:

- Node 24 LTS;
- Vite 8 stable/current supported line;
- TypeScript 5.9;
- HTMX 2.0.10 stable;
- django-htmx 1.29 supports Django 5.2;
- Tailwind 4 stable;
- Chart.js 4.5.x;
- Expo SDK 57 stable.

Do not use Expo 58 beta or React Native canary merely because they are newer.

---

# 5. Browser support policy

Tailwind 4 currently targets modern browsers requiring at least:

- Chrome 111;
- Safari 16.4;
- Firefox 128.

This is accepted as the P0 web baseline.

Consequences:

- container queries are available;
- modern CSS design tokens are viable;
- older legacy browsers are explicitly not a target.

Features newer than this baseline must still be progressive enhancements.

Examples:

- Popover API: optional enhancement;
- View Transitions: optional enhancement.

Core conversion cannot depend on them.

---

# 6. Runtime JavaScript budget philosophy

The target is not “zero JavaScript”.

The target is:

> **zero unnecessary JavaScript.**

Required client JS categories:

- HTMX;
- accessible country/currency search enhancement;
- small UI helpers;
- local anonymous preferences/favourites;
- historical chart only on pages that contain a chart.

Everything else should remain HTML/CSS/server behavior.

---

# 7. Web dependency budget

Expected production JS dependencies:

```text
htmx.org
@github/combobox-nav
chart.js          [history chunk only]
```

Build/assets:

```text
vite
typescript
tailwindcss
@tailwindcss/vite
@fontsource-variable/inter
```

Development/test:

```text
@biomejs/biome
@playwright/test
@axe-core/playwright
```

Python-side web helpers:

```text
django-htmx
django-template-partials
djlint
```

The dependency list should stay approximately this small unless a feature clearly justifies expansion.

---

# 8. Why Vite is added

Tailwind alone could compile CSS, but the product also needs:

- TypeScript compilation;
- npm dependency bundling;
- font assets;
- Chart.js code splitting;
- source maps;
- minification;
- content hashing;
- development server/HMR;
- production manifest.

Vite handles these concerns in one asset pipeline.

Vite is **not** the application framework.

Django still renders HTML.

---

# 9. Why TypeScript is added

Client-side behavior is small but trust-sensitive.

Examples:

- preventing stale pair/result mismatch;
- combobox active-option behavior;
- historical chart data mapping;
- local persistence schema;
- HTMX lifecycle hooks.

Strict TypeScript provides high ROI here.

JavaScript business/domain logic is still intentionally minimal.

---

# 10. Template partial strategy

Django 6.0 now includes built-in template partials, but this project deliberately remains on Django 5.2 LTS.

Use `django-template-partials` as the compatibility bridge because it supports Django 5.2 and the template-loader fragment pattern needed by HTMX.

When the project eventually upgrades to a Django version with native partials, migrate away from the package rather than preserving it forever.

---

# 11. HTMX integration strategy

Use `django-htmx` for:

- reliable `request.htmx` detection;
- typed middleware integration;
- clean Django-side branching.

Do not use its script tag if HTMX is already bundled by Vite.

One asset pipeline owns browser JavaScript.

---

# 12. Native platform first

Before installing a JS component dependency, check whether the platform already solves the problem.

Priority order:

```text
semantic HTML
→ native browser API
→ small focused library
→ custom component
→ large UI framework
```

Examples:

- disclosure → `details/summary`;
- modal → `dialog`;
- date input → native date field;
- copy → Clipboard API;
- locale formatting → Intl;
- client URL state → URL/URLSearchParams.

---

# 13. Accessible combobox exception

Country/currency search is complex enough that custom keyboard navigation from scratch has poor ROI.

Use `@github/combobox-nav` as a small ARIA 1.2 keyboard-navigation primitive while retaining:

- our own HTML;
- our own server search;
- our own Quiet Atlas styles;
- our own fallback `select`;
- our own usability/accessibility tests.

This avoids adopting a full UI framework.

---

# 14. Chart exception

Historical line charts are sufficiently specialized to justify Chart.js.

Why Chart.js:

- mature;
- typed;
- responsive;
- enough control for one clean line;
- no need for a full visualization framework.

Accessibility remains our responsibility because canvas content is not screen-reader-readable by itself.

Every chart must have:

- text summary;
- selected/latest values;
- high/low;
- accessible data table.

---

# 15. Mobile version policy

As of research date:

- React Native 0.87 is stable;
- Expo's stable SDK 57 targets RN 0.86;
- Expo SDK 58 is beta and targets RN 0.88 RC.

For this project, **Expo SDK 57 stable wins**.

Reason:

- stable integrated ecosystem matters more than raw RN version number;
- SDK 57 already uses modern React Native/New Architecture;
- no feature requires canary/beta runtime.

Re-evaluate only when mobile implementation actually starts.

If Expo 58 is stable by then, upgrade after compatibility review.

---

# 16. Shared web/mobile philosophy

Share:

- domain semantics;
- API contracts;
- UX rules;
- design tokens conceptually;
- copy rules;
- source/provenance semantics.

Do not force code sharing where platforms differ.

Web owns:

- semantic HTML;
- Django templates;
- HTMX;
- CSS.

Mobile owns:

- native navigation;
- native controls;
- native offline storage;
- React component tree.

This is intentional.

---

# 17. Frontend architecture invariants

1. Django remains authoritative for web domain state.
2. Web does not call DRF merely to render HTML.
3. No global JavaScript store is introduced without demonstrated need.
4. HTMX responses are HTML fragments, not JSON reconstruction.
5. Client scripts do not recalculate FX/business rules.
6. A chart never becomes the only representation of historical data.
7. No critical control depends on hover.
8. No critical flow depends on a beta browser API.
9. Mobile never calls third-party data providers directly.
10. Mobile API types come from the backend OpenAPI schema.
11. Offline mobile values retain explicit freshness semantics.
12. Stable runtime versions are preferred to beta/canary novelty.
