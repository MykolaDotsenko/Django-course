# Web Frontend Architecture

Research date: **2026-09-19**.

This document is the implementation contract for the Django web frontend.

Companion documents:

- [Frontend technology strategy](13_FRONTEND_TECHNOLOGY_STRATEGY.md)
- [Quiet Atlas design system](03_UI_DESIGN_SYSTEM.md)
- [Component anatomy](03C1_COMPONENT_ANATOMY_AND_DIMENSIONS.md)
- [Component states and microinteractions](03C_COMPONENT_STATES_AND_MICROINTERACTIONS.md)
- [Responsive/motion/accessibility](03D_RESPONSIVE_MOTION_ACCESSIBILITY.md)

---

# 1. Architecture goal

The web frontend must implement a premium, highly interactive experience while preserving a simple ownership model:

```text
Django owns state and HTML
HTMX owns server-driven replacement
TypeScript owns small client-only behavior
CSS/Tailwind owns presentation and motion
browser APIs own familiar platform behavior
```

No second application framework is introduced.

---

# 2. Rendering ownership

## Django owns

- initial page HTML;
- form state;
- validation;
- current/historical conversion state;
- source/provenance state;
- country/currency search result markup;
- local-value context;
- payment context;
- storytelling content;
- saved state when server-backed;
- error copy.

## HTMX owns

- submitting fragment requests;
- swapping small HTML regions;
- URL/history updates where explicitly configured;
- progressive partial refresh.

## TypeScript owns

- initialization after fragment swaps;
- native-dialog lifecycle helpers;
- accessible combobox keyboard navigation;
- local anonymous persistence;
- optional copy/share helper;
- chart rendering;
- small presentation-only state.

## CSS owns

- responsive layout;
- component visual states;
- reduced motion;
- container queries;
- transitions;
- country atmosphere.

This line should stay obvious when reading the repository.

---

# 3. Proposed repository layout

```text
/
├── apps/
│   ├── countries/
│   ├── exchange/
│   ├── culture/
│   └── ...
│
├── templates/
│   ├── base.html
│   ├── components/
│   │   ├── app_header.html
│   │   ├── button.html
│   │   ├── inline_alert.html
│   │   └── ...
│   └── pages/
│
├── frontend/
│   ├── src/
│   │   ├── app.ts
│   │   ├── styles/
│   │   │   ├── app.css
│   │   │   ├── tokens.css
│   │   │   ├── base.css
│   │   │   └── utilities.css
│   │   ├── behaviors/
│   │   │   ├── htmx.ts
│   │   │   ├── dialog.ts
│   │   │   ├── combobox.ts
│   │   │   ├── clipboard.ts
│   │   │   ├── local-storage.ts
│   │   │   └── chart.ts
│   │   ├── charts/
│   │   │   ├── rate-chart.ts
│   │   │   └── rate-chart-types.ts
│   │   ├── storage/
│   │   │   ├── schema.ts
│   │   │   └── preferences.ts
│   │   └── types/
│   │       └── dom.ts
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── biome.json
│   └── vite.config.ts
│
├── static/
│   ├── icons/
│   └── build/             # production build output, generated
│
└── tests/
    └── e2e/
```

Exact placement can vary if Django app-local templates improve cohesion, but responsibilities remain the same.

---

# 4. Asset pipeline

Use:

- Node 24 LTS;
- npm;
- Vite 8;
- TypeScript 5.9;
- Tailwind CSS 4 via `@tailwindcss/vite`.

Node exists at build/development time only.

Production Django does not require a Node process.

---

# 5. Why npm

Use the package manager bundled with Node LTS.

Reasons:

- one less tool/bootstrap dependency;
- package-lock is widely understood;
- dependency set is intentionally small;
- no monorepo/workspace complexity requires pnpm.

If the repository later becomes a serious multi-package workspace, package-manager choice can be revisited.

---

# 6. Node version

Pin Node 24 LTS through at least one repo-visible mechanism:

- `.nvmrc`;
- `package.json#engines`;
- CI action/tool version.

Do not use Node 26 Current for production tooling by default.

LTS stability has higher ROI.

---

# 7. Vite responsibility

Vite owns only static asset development/build.

It does not own routing, HTML rendering or application state.

Inputs:

```text
frontend/src/app.ts
frontend/src/styles/app.css
```

Output:

```text
static/build/
├── .vite/manifest.json
└── assets/
    ├── app-[hash].js
    ├── app-[hash].css
    ├── inter-....woff2
    └── dynamically imported chunks
```

---

# 8. Vite/Django integration

Use the official Vite backend-integration model.

## Development

Django template helper renders:

```html
<script type="module" src="http://localhost:5173/@vite/client"></script>
<script type="module" src="http://localhost:5173/frontend/src/app.ts"></script>
```

Development origin is configuration-driven.

## Production

`vite build` generates:

```text
static/build/.vite/manifest.json
```

A small repo-owned Django template tag:

```text
{% vite_asset "frontend/src/app.ts" %}
```

reads the manifest and renders:

- CSS files;
- imported CSS;
- modulepreload links where useful;
- module script with hashed filename.

## Why repo-owned integration

Do not make a Django/Vite bridge package a critical architecture dependency when Vite itself documents the manifest contract.

The bridge should be:

- very small;
- typed/tested Python;
- cached after load in production;
- development-aware;
- fail-fast on missing production manifest.

Unit tests cover representative manifest graphs.

## Implemented PR 2B bridge

The repository now owns the bridge in `apps/common/templatetags/vite.py`.

Runtime policy:

- local + `DEBUG=True` uses the Vite development server;
- test, preview and production use the generated manifest path;
- development renders `@vite/client` before the configured entry module;
- production renders entry CSS first, recursively imported CSS second, the entry module third and recursive static-import modulepreloads last, matching Vite's documented backend integration order;
- dynamic imports are not eagerly preloaded;
- repeated imported CSS is deduplicated while preserving first-seen order;
- the parsed production manifest is cached per manifest path for process lifetime;
- missing or malformed manifests/chunks fail fast with `ViteManifestError`;
- entry/output paths are constrained to canonical relative POSIX paths;
- development origin rejects credentials, paths, query strings and fragments;
- HTML is produced with Django `format_html()` / `format_html_join()`, not raw `mark_safe()`.

Current settings:

```text
VITE_DEV_SERVER_ENABLED = local environment AND DEBUG
VITE_DEV_SERVER_ORIGIN = http://127.0.0.1:5173
VITE_MANIFEST_PATH = static/build/.vite/manifest.json
```

The bridge intentionally adds no environment variable or third-party Django/Vite package. If deployment later needs a configurable non-local asset origin, that becomes an explicit configuration-contract change rather than an accidental runtime knob.

---

# 9. Vite configuration

Conceptual:

```ts
import { defineConfig } from "vite";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss()],
  build: {
    manifest: true,
    outDir: "../static/build",
    emptyOutDir: true,
    rolldownOptions: {
      input: {
        app: "./src/app.ts",
      },
    },
  },
});
```

Final paths depend on working directory.

Do not add React/Vue plugins.

---

# 10. Vite entry strategy

Use one small core entry:

```text
app.ts
```

Chart code is dynamically imported only when the page contains:

```text
[data-rate-chart]
```

Concept:

```ts
if (document.querySelector("[data-rate-chart]")) {
  void import("./charts/rate-chart");
}
```

Benefits:

- no Chart.js on normal conversion sessions;
- cacheable separate chunk;
- simpler template integration.

Do not create dozens of page entrypoints until bundle profiling justifies them.

---

# 11. Tailwind integration

Use the official Vite plugin.

```css
@import "tailwindcss";
```

Use `@theme` for semantic product tokens.

Concept:

```css
@theme {
  --font-sans: "Inter Variable", ui-sans-serif, system-ui, sans-serif;

  --color-canvas: #f6f7f3;
  --color-surface: #ffffff;
  --color-ink: #14211d;
  --color-muted: #596660;
  --color-brand: #0b6b61;
  --color-history: #345e7d;

  --radius-control: 0.75rem;
  --radius-panel: 1.5rem;
}
```

The actual token source remains `03A_VISUAL_FOUNDATIONS.md`.

---

# 12. Tailwind source discovery

Django templates must be explicitly discoverable by Tailwind if automatic source detection does not cover repository-relative paths.

Use `@source` in CSS where necessary.

Do not generate Tailwind class names dynamically in Python like:

```text
"text-" + color
```

because the build cannot reliably discover arbitrary composed utilities.

Use:

- complete class literals;
- data attributes;
- semantic custom properties.

---

# 13. Country themes

Country atmosphere uses constrained custom properties.

Example:

```html
<body
  data-destination-country="JP"
  style="--country-accent: ...;"
>
```

Prefer server-rendered attributes/classes referencing a vetted theme map rather than arbitrary inline provider data.

Better:

```html
<body data-country-theme="jp">
```

CSS:

```css
[data-country-theme="jp"] {
  --country-accent: ...;
  --country-soft: ...;
}
```

No user/external API value can become arbitrary CSS.


## 13.1 Bilateral theme ownership

Country atmosphere applies independently to source and destination presentation regions when both countries are known.

Rules:

- source and destination may expose different semantic theme tokens at the same time;
- the global Quiet Atlas shell remains stable;
- controls keep identical anatomy/behavior on both sides;
- theme resolution is presentation state, not FX-domain state;
- a missing source/destination theme falls back to neutral without affecting conversion;
- destination may receive stronger editorial emphasis, but source identity remains visible.

The web must not implement country atmosphere by replacing component trees or shipping one stylesheet per country.

Preferred model:

```text
global Quiet Atlas tokens
+ source-context token scope
+ destination-context token scope
```

---

# 14. CSS layering

Use a simple conceptual order:

```text
Tailwind base
→ Quiet Atlas tokens
→ global base defaults
→ utilities
→ rare complex custom component CSS
```

Avoid a large handcrafted BEM component framework on top of Tailwind.

Avoid `@apply` as a default abstraction mechanism.

If a repeated visual concept is truly a component, prefer a Django template partial.

---

# 15. TypeScript compiler policy

Use strict TypeScript.

Conceptual `tsconfig`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noEmit": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true,
    "useDefineForClassFields": true
  }
}
```

Vite emits JavaScript.

`tsc --noEmit` is a correctness gate.

---

# 16. JavaScript module philosophy

Each behavior module should be small and named after a UI capability.

Good:

```text
combobox.ts
dialog.ts
local-storage.ts
rate-chart.ts
```

Avoid:

```text
utils.ts
helpers.ts
common.ts
misc.ts
```

unless a genuinely cohesive shared concept emerges.

---

# 17. No frontend business rules

TypeScript does not decide:

- exchange rate;
- monetary rounding;
- currency validity;
- historical fallback observation;
- data freshness policy;
- typical-price confidence;
- story facts.

It may format already-authoritative values for presentation only when semantics are preserved.

---

# 18. HTMX version policy

Use stable HTMX 2.0.x.

Pin exact stable version in lockfile at implementation time.

As of this research:

- 2.x remains the default/stable line in django-htmx;
- 4.x is still beta.

Do not choose HTMX 4 beta for portfolio novelty.

---

# 19. HTMX ownership model

HTMX attributes belong on the element that owns the user action.

Example:

```html
<form
  method="post"
  action="/convert/"
  hx-post="/convert/"
  hx-target="#conversion-result"
  hx-swap="outerHTML"
>
```

Without JavaScript/HTMX, normal form submission still works.

---

# 20. First submit vs subsequent enhancement

Follow UX spec:

- first conversion has explicit Convert;
- after successful result, valid changes may auto-refresh;
- Convert remains available.

Do not make initial page immediately fire rate requests merely because fields receive defaults.

---

# 21. HTMX race/concurrency policy

The converter has a critical integrity invariant:

> Old response must never overwrite newer input state.

Use `hx-sync` deliberately.

Example conceptual strategy:

```text
form:abort
```

or another tested synchronization mode appropriate to the final markup.

Additionally:

- server response renders its own pair metadata;
- result/pair are swapped atomically as one fragment;
- TypeScript must not relabel an old number with new field labels.

Race tests are mandatory.

---

# 22. HTMX fragment boundaries

Prefer smallest meaningful atomic region.

Examples:

```text
#conversion-result
#destination-context
#save-pair-control
#country-search-results
#historical-chart-section
```

Avoid swapping entire:

- `body`;
- app shell;
- converter form

for routine updates.

---

# 23. HTMX history policy

Use history only when state is genuinely shareable.

Candidate state:

- amount;
- base;
- quote;
- source/destination countries;
- historical requested date.

Options:

- server `HX-Push-Url`;
- `hx-push-url`.

Do not push:

- disclosure open state;
- loading state;
- ephemeral validation detail.

Back/forward must restore a coherent form + result.

---

# 24. HTMX cache semantics

When the same URL returns full HTML for normal requests and a partial for HTMX:

```text
Vary: HX-Request
```

is mandatory on cacheable responses.

Use Django's `vary_on_headers` or equivalent.

No cache entry may serve fragment HTML as a full document.

---

# 25. HTMX error semantics

Server should return meaningful HTTP status.

Client handling distinguishes:

- field validation;
- rate unavailable;
- authorization;
- generic server failure.

Do not convert every failure to HTTP 200 purely to make swapping easy.

Define explicit HTMX error behavior/tests.

---

# 26. HTMX lifecycle integration

`app.ts` registers lifecycle listeners once.

Relevant events may include:

- `htmx:beforeRequest`;
- `htmx:afterRequest`;
- `htmx:beforeSwap`;
- `htmx:afterSwap`;
- `htmx:load`.

Behavior initialization must be idempotent.

Example:

```text
HTMX swaps picker fragment
→ htmx:load
→ initialize only uninitialized picker
```

Use data markers or WeakSet where necessary.

---

# 27. CSP-friendly HTMX policy

Avoid inline JavaScript:

- no `onclick`;
- no inline `<script>` business behavior;
- avoid `hx-on` JavaScript expressions by default.

Use external TypeScript event listeners.

Evaluate HTMX config:

```text
allowEval = false
allowScriptTags = false
selfRequestsOnly = true
```

after compatibility tests.

If a feature requires loosening CSP-related behavior, document the exact reason.

---

# 28. CSRF

Django CSRF remains authoritative.

For HTMX POST/DELETE-like requests, configure the CSRF header through inherited HTML configuration or request hooks.

Do not duplicate tokens into manually constructed fetch wrappers unless a specific non-HTMX request exists.

---

# 29. Template partials

Use `django-template-partials` on Django 5.2 for named fragments.

Example concept:

```django
{% partialdef conversion-result %}
  ...
{% endpartialdef %}
```

The same template can then provide:

- full page;
- named HTMX fragment.

This reduces drift between initial and dynamic markup.

When upgrading to Django 6+ later, migrate to Django's native template partials.

---

# 30. django-htmx

Use middleware for:

```python
if request.htmx:
    ...
```

and typed request support.

Do not use `django-htmx` to inject a separate vendored HTMX script if our Vite bundle already owns HTMX.

One asset path only.

---

# 31. Country/currency picker progressive enhancement

The picker must remain usable if enhanced search fails.

## Baseline fallback

A normal `<select>` or other server-rendered accessible fallback capable of completing the form.

## Enhanced mode

Trigger opens a native `<dialog>`.

Inside:

```text
search input
↓
HTMX server search
↓
HTML listbox/result rows
↓
@github/combobox-nav keyboard navigation
```

Selection updates hidden/real form values and closes dialog.

No DRF JSON endpoint is required.

---

# 32. Why server-render picker search

Country/currency dataset is manageable, but server rendering gives:

- identical filtering rules;
- historical-date-aware results;
- no duplicated normalization;
- easy archived-currency suggestions;
- HTML accessibility ownership.

Search can be extremely fast from local PostgreSQL.

Use debounced HTMX input.

---

# 33. Combobox semantics

The enhanced search must follow ARIA combobox/listbox expectations.

`@github/combobox-nav` may manage keyboard active-option behavior.

We still own:

- accessible labels;
- DOM roles/attributes;
- result text;
- selection;
- server filtering;
- focus return;
- tests.

If screen-reader testing reveals poor behavior, fall back to a simpler dialog/list model rather than forcing a custom combobox.

---

# 34. Dialog strategy

Use native `<dialog>` for modal web picker/source surfaces where appropriate.

Benefits:

- browser modality;
- focus semantics;
- Escape;
- backdrop;
- less custom focus-trap code.

Still test:

- Safari;
- Firefox;
- Chromium;
- zoom;
- screen readers.

Do not automatically use `dialog` for nonmodal disclosures.

---

# 35. Disclosure strategy

Use native `<details>/<summary>` for suitable low-complexity disclosures:

- source methodology;
- contextual caveats.

Use custom disclosure button only if interaction/design requirements exceed native behavior.

Do not replace semantic native elements solely for animation control.

---

# 36. Historical date control

P0/P1 web uses native:

```html
<input type="date">
```

with:

- visible label;
- min/max where semantically known;
- server validation;
- localized browser UI.

A custom calendar is not justified until user research demonstrates a real problem.

---

# 37. Popover API

The Popover API can be used as optional enhancement where its browser support matches the exact control.

It is not a core dependency because our Tailwind-supported browser baseline starts earlier than universal modern Popover support.

No essential action depends on it.

---

# 38. View Transitions API

Optional later enhancement only.

Potential uses:

- Story page continuity;
- selected historical point continuity.

Not required for:

- conversion result;
- form state;
- picker;
- error recovery.

Progressive fallback is instant/no-transition rendering.

---

# 39. Chart.js boundary

Chart.js is loaded only for historical graph surfaces.

Input arrives from server as safe structured data.

Preferred data transport:

- JSON in a `<script type="application/json">` element with Django `json_script`;
- or data endpoint only if chart data volume/lazy interaction later requires it.

Avoid large JSON inside arbitrary data attributes.

---

# 40. Chart date handling

Avoid a Chart.js date adapter dependency unless necessary.

For our line chart:

- server supplies normalized ISO dates / epoch values;
- use a linear x-axis;
- format labels/tooltips with `Intl.DateTimeFormat`.

This keeps dependencies smaller.

If real time-scale functionality later justifies an adapter, add one deliberately.

---

# 41. Chart accessibility

Canvas chart is not the information source of truth.

Every chart section provides:

- heading;
- text summary;
- selected value;
- latest value;
- high/low;
- accessible data table toggle.

Canvas can have a concise accessible label, but screen-reader users must not be forced to interpret pixels.

---

# 42. Chart interaction

P0:

- pointer hover tooltip;
- click/tap selected point if useful;
- period controls are real buttons;
- keyboard users can access equivalent selected values/table.

Do not build draggable finance-terminal interactions.

---

# 43. Icon strategy

Use Heroicons only as a source library.

Selected icons are stored/rendered as local static SVG template partials.

Benefits:

- zero icon runtime;
- exact aria/decorative control;
- no third-party network;
- tree-shaking irrelevant because only used files exist.

Rules:

- decorative icon: `aria-hidden="true"`;
- icon-only button: accessible name on button;
- do not use SVG title as the sole accessible name.

---

# 44. Font strategy

Use Inter Variable through Fontsource/npm and Vite.

No Google Fonts runtime request.

Benefits:

- predictable privacy;
- no third-party availability;
- CSP simpler;
- caching under our origin.

Fallback remains a high-quality system sans stack.

The app must look correct if custom font fails.

## Implemented PR 2C typography and shell foundation

The web bundle pins `@fontsource-variable/inter==5.3.0` and imports its variable weight axis through Vite. Font files are emitted as same-origin hashed WOFF2 assets with Fontsource unicode ranges; no runtime font CDN is used.

Quiet Atlas styling is split by responsibility:

```text
app.css
├── Tailwind 4
├── tokens.css   → semantic palette/type/spacing/radius/elevation/motion
├── base.css     → document defaults, focus, selection, forced-colors basics
└── shell.css    → AppShell, design-QA layout and bilateral atmosphere scopes
```

The base Django template owns:

- one reusable Vite entry;
- skip-link target;
- semantic header/main/footer landmarks;
- stable page frame;
- no navigation destination that does not yet exist.

Country atmosphere is represented by vetted `data-country-theme` scopes. The first QA examples are Finland and Japan. Their accents affect only decorative presentation variables; text/status semantics, focus order and component mechanics remain global Quiet Atlas behavior.

A DEBUG-only `/_design/shell/` surface exists to inspect these foundations without exposing unfinished product UI. It contains no converter form and makes no FX claim.

---

# 45. localStorage scope

Use only for small anonymous convenience state.

Candidate schema:

```ts
interface LocalPreferencesV1 {
  version: 1;
  lastPair?: {
    base: string;
    quote: string;
    sourceCountry?: string;
    destinationCountry?: string;
  };
  favourites: Array<...>;
  recent: Array<...>;
}
```

Rules:

- bounded recent list;
- explicit schema version;
- parse/validate before use;
- storage failure does not break conversion;
- no authentication token;
- no sensitive trip details.

---

# 46. No IndexedDB initially

Current anonymous state is small.

IndexedDB adds:

- async complexity;
- schema/migration code;
- debugging overhead.

Use only if web later stores large/offline datasets.

Offline product priority remains React Native.

---

# 47. Formatting APIs

Use standard `Intl` for presentation:

- `Intl.NumberFormat`;
- `Intl.DateTimeFormat`;
- `Intl.PluralRules` later if needed.

Server-rendered content remains correct without JS.

TypeScript enhancements use the same visible semantics.

---

# 48. Share API

If implemented:

- Web Share API where supported;
- clipboard fallback.

Share URL is canonical server URL.

No third-party sharing SDK.

---

# 49. Motion implementation

Use CSS transitions.

TypeScript should not orchestrate animations unless a native/browser state API requires it.

Motion tokens live in CSS.

Respect:

```css
@media (prefers-reduced-motion: reduce)
```

No animation library in P0/P1.

---

# 50. Client-side validation

Browser validation may assist.

Django validation is authoritative.

Do not duplicate complex validation rules in TypeScript.

Examples:

- `required`;
- input mode;
- basic min/max attributes

can improve client experience.

Historical coverage remains server/domain validation.

---

# 51. Browser support

Baseline follows Tailwind 4:

- Chrome 111+;
- Safari 16.4+;
- Firefox 128+.

Test current latest browsers in CI/locally through Playwright where supported.

Do not silently claim legacy browser support.

---

# 52. Graceful degradation

With JavaScript disabled:

Must work:

- current conversion;
- historical conversion;
- validation;
- source/provenance;
- culture/story navigation.

May degrade:

- searchable dialog becomes select/full page;
- auto update requires submit;
- chart becomes text/table/static alternative;
- local anonymous convenience features may be unavailable.

This is a deliberate quality signal.

---

# 53. Web performance budgets

Initial design budgets, subject to measured refinement:

## Core first-load JS

Goal:

> **< 100 kB compressed total application/vendor JS before optional chart**

This should be achievable with HTMX + tiny modules.

## Chart

Loaded only on history surface.

## CSS

Keep compiled CSS comfortably below generic UI-framework scale.

Do not optimize bytes blindly; track growth.

## Fonts

Prefer one variable WOFF2 family/subset strategy.

Do not load multiple editorial families in P0.

---

# 54. Image performance

No above-fold hero image required.

Cultural images:

- lazy loaded;
- explicit width/height/aspect ratio;
- appropriate responsive sizes;
- rights/provenance retained.

Do not preload below-fold culture imagery.

---

# 55. JavaScript execution performance

Avoid:

- client rendering loops;
- scroll listeners for decoration;
- resize listeners where CSS solves layout;
- MutationObserver for general initialization if HTMX events suffice.

Use:

- event delegation;
- CSS container queries;
- IntersectionObserver only where lazy behavior genuinely requires it.

---

# 56. Lint/format tooling

## TypeScript / JavaScript / JSON

Biome 2.

Use:

```text
biome check
biome check --write
```

Biome does not replace TypeScript type checking.

Run:

```text
tsc --noEmit
```

## Django templates

Use djLint.

## CSS

Tailwind/CSS stays formatted consistently through project tooling; do not add Stylelint unless CSS-specific bugs justify it.

Dependency minimization applies to developer tooling too.

---

# 57. Unit testing client modules

Use minimal tests only where logic exists.

Candidates:

- localStorage parsing/migration;
- chart mapping;
- formatter boundary logic.

Do not unit-test trivial DOM attribute assignment if Playwright already tests the flow.

A dedicated JS unit-test framework is deferred until client logic volume justifies one.

---

# 58. Playwright E2E

Playwright is the primary web behavior test.

Critical flows:

- no-JS full conversion;
- HTMX conversion;
- rapid amount changes/race safety;
- pair swap;
- picker keyboard use;
- historical exact date;
- weekend effective date;
- stale result;
- back/forward deep link;
- chart/table;
- responsive mobile viewport.

---

# 59. Automated accessibility

Use `@axe-core/playwright`.

Run after meaningful UI states are reached:

- initial converter;
- validation errors;
- result;
- picker open;
- historical state;
- source details;
- Story page.

Automated axe results are not a substitute for:

- keyboard testing;
- screen reader review;
- zoom/reflow;
- reduced motion;
- forced colors.

---

# 60. Visual regression

Use Playwright screenshots selectively.

Baseline candidates:

- converter desktop;
- converter mobile;
- successful result;
- stale/historical result;
- picker;
- chart;
- Story page.

Avoid screenshot testing every text fragment.

---

# 61. CSS/design token checks

A review/CI convention should prevent arbitrary values from proliferating.

Not every arbitrary Tailwind value is forbidden.

Allowed when:

- truly content/layout-specific;
- documented;
- not a repeated semantic token.

Repeated arbitrary colors/radii/spacings are a design-system failure.

---

# 62. Security

## No CDN runtime assets

Self-host:

- HTMX bundle;
- fonts;
- icons;
- JS/CSS.

## CSP

Target a strict Content Security Policy.

Avoid inline script/style behavior that forces `unsafe-inline`.

## Third-party DOM

No untrusted API HTML enters the page.

## URLs

External source URLs are validated/sanitized server-side.

## localStorage

Treat as user-controlled/untrusted data.

---

# 63. Dependency review

Every frontend runtime dependency must answer:

1. What user/engineering problem does it solve?
2. Can native platform solve it?
3. Is it active/maintained?
4. Does it add runtime JS?
5. What is its accessibility impact?
6. Can it be removed/replaced later?
7. Is its license acceptable?
8. Does it require CDN/network access?

---

# 64. Package update strategy

Use exact lockfile.

CI can run:

- npm ci;
- npm run check;
- npm run build.

Automated dependency PRs can be enabled later.

Major frontend dependency upgrades are not auto-merged.

---

# 65. Production build

Canonical pipeline:

```text
npm ci
↓
tsc --noEmit
↓
biome check
↓
vite build
↓
Django collectstatic
↓
Python tests / deployment checks
```

Ordering can be optimized in CI but every gate remains.

---

# 66. Development workflow

Two development processes are acceptable:

```text
Django dev server
Vite dev server
```

Use a simple task runner/script to launch both.

Do not introduce Docker Compose only to avoid opening two terminals if local system setup is simpler.

---

# 67. No hidden framework

A common failure mode is claiming “Django + HTMX” while recreating a SPA through increasingly large client scripts.

Guardrail:

If a feature requires:

- complex client router;
- dozens of cross-page client stores;
- client-side business entity cache;
- heavy optimistic domain logic,

stop and revisit architecture.

Do not drift accidentally.

---

# 68. Web implementation acceptance

The frontend foundation is accepted when:

- Django renders a useful no-JS converter shell;
- Vite dev/prod asset tags work;
- production manifest tag is tested;
- Tailwind Quiet Atlas tokens compile;
- TypeScript strict check is green;
- HTMX fragment update works;
- `Vary: HX-Request` behavior is tested where applicable;
- race/obsolete request path is covered;
- picker has keyboard-accessible enhanced and fallback paths;
- CSP does not require broad `unsafe-inline`;
- chart code is absent from normal converter bundle;
- Playwright + axe run in CI;
- Lighthouse-style performance problems are not introduced by design assets.
