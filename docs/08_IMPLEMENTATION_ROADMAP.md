# Implementation Roadmap

The roadmap is ordered to maximize working software and recruiter-visible evidence while minimizing speculative infrastructure.

The numbering below describes **implementation sequence**, not the already-open documentation PR numbers on GitHub.

---

## Phase 0 — Documentation foundation

Before production code changes:

- product specification;
- UX flows;
- user-case catalog;
- interaction/state model;
- storytelling/historical converter specification;
- UI system;
- detailed visual foundations, screen blueprints, component states and design QA;
- architecture;
- domain model;
- mobile/API strategy;
- quality/security/accessibility;
- ADR log;
- references;
- API/data-source research matrix;
- external API integration contracts;
- backend system design;
- request/information-flow contracts;
- application-service/domain orchestration rules;
- consistency/cache/concurrency rules;
- API/security/observability/operations rules;
- backend scenario catalog;
- scheduled import/maintenance architecture.

Implementation starts only after the documentation is coherent enough to act as an engineering contract.

---

## Implementation PR 1 — Repository and Django foundation

**Execution split:** this product milestone is intentionally delivered as bounded implementation slices:

1. **PR 1A — structural product-root migration:** move the validated Django/Quiet Atlas shell to repository root, remove the unrelated blog domain and keep existing media/QA behaviour green;
2. **PR 1B — Python dependency/tooling foundation;**
3. **PR 1C — environment-driven settings and secret/config validation;**
4. **PR 1D — PostgreSQL integration and database CI;**
5. **PR 1E — health, request-ID and structured-observability baseline.**

Each slice must be independently reviewable and green. Merging PR 1A does **not** mean the remaining foundation acceptance criteria are complete.

**Execution status after PR 1E:** PR 1A–1E are implemented. The foundation milestone is complete; subsequent work starts at Implementation PR 2.

**Goal:** replace legacy course scaffolding with a clean product shell.

Deliverables:

- move the real Django project to repository root or otherwise remove unnecessary nesting;
- remove blog `post` domain;
- Django 5.2 LTS on a current supported patch;
- environment-driven settings;
- PostgreSQL-ready config;
- Ruff + pytest + pytest-django;
- pre-commit;
- initial CI;
- health endpoint;
- production settings checks;
- synchronous Django request baseline;
- WSGI-first deployment baseline;
- explicit autocommit configuration with no global ATOMIC_REQUESTS;
- request-ID middleware;
- structured logging baseline;
- separate /health/live/ and /health/ready/ endpoints;
- PostgreSQL-backed integration test path;
- safe `.env.example`;
- README run instructions.

Acceptance:

- no hard-coded secret key;
- `DEBUG` environment-controlled;
- readiness checks PostgreSQL but does not call Frankfurter or other optional providers;
- liveness has no dependency checks;
- no provider/network call occurs inside a DB transaction;
- request ID appears in logs and response metadata where defined;
- clean migration state;
- test/quality commands documented;
- CI green.

---

## Implementation PR 2 — Design system and server-rendered shell

**Execution split:** this product milestone is delivered as bounded, independently reviewable slices:

1. **PR 2A — frontend toolchain:** Node 24, npm lockfile, Vite 8, TypeScript 5.9 strict, Biome 2, Tailwind 4, HTMX 2 and read-only frontend CI;
2. **PR 2B — Django↔Vite bridge:** repo-owned manifest template tag, development tags, production manifest resolution and focused Python tests;
3. **PR 2C — Quiet Atlas foundations:** semantic tokens, typography, global shell and country-atmosphere scopes;
4. **PR 2D — converter primitives:** AmountField, CountryCurrencyTrigger, SwapButton, ConvertButton and initial Result/provenance primitives;
5. **PR 2E — responsive bilateral experience:** desktop dual-context composition, mobile stacked identity, container-query/reflow behavior and interaction states;
6. **PR 2F — browser quality:** djLint completion, Playwright/axe coverage, responsive/reduced-motion/high-contrast QA and performance evidence.

Each slice must preserve the PR 2 acceptance criteria relevant to its scope. Later slices must not bypass the ownership model established in `14_WEB_FRONTEND_ARCHITECTURE.md`.

**Execution status after PR 2B:** PR 2A–2B are implemented. The locked frontend build baseline and repo-owned Django↔Vite asset bridge are CI-backed, including development tags, production manifest traversal, imported CSS/modulepreload ordering, cache behavior and malformed-manifest failure paths. PR 2C is next; no Quiet Atlas presentation layer or converter business logic is claimed complete by PR 2B.

**Goal:** establish visual/accessibility foundation before domain complexity.

Deliverables:

- Node 24 LTS build-tool baseline;
- Vite 8 asset pipeline using the official backend-manifest pattern;
- repo-owned, tested Django Vite manifest template tag;
- TypeScript 5.9 strict;
- Biome 2 checks;
- djLint template checks;
- Tailwind 4 through `@tailwindcss/vite`;
- semantic CSS/theme-token layer based on `03A_VISUAL_FOUNDATIONS.md`;
- self-hosted primary typography strategy with system fallback;
- responsive app shell;
- 4px spacing/radius/elevation scales;
- neutral core + controlled country-accent system;
- focus/reduced-motion/high-contrast rules;
- primary converter shell from `03B_SCREEN_BLUEPRINTS.md`;
- signature bilateral source/destination workspace for large screens;
- independent restrained source/destination atmosphere channels within one stable Quiet Atlas shell;
- AmountField, CountryCurrencyTrigger, SwapButton, ConvertButton and initial Result primitives using exact anatomy/sizing from `03C1_COMPONENT_ANATOMY_AND_DIMENSIONS.md`;
- explicit hover/focus/pressed/loading/error states from `03C_COMPONENT_STATES_AND_MICROINTERACTIONS.md`;
- container-query behavior for reusable components;
- 320px/reflow and mobile layouts;
- django-template-partials for Django 5.2 named fragments;
- django-htmx integration;
- stable HTMX 2.x bundled through Vite;
- local self-hosted Inter Variable asset;
- small local SVG icon partial strategy;
- no React/Alpine/Stimulus on web;
- no decorative above-fold media dependency.

Acceptance:

- converter remains the visual focal point;
- source and destination remain simultaneously identifiable on large screens;
- bilateral cultural atmosphere does not alter control mechanics or focus order;
- result/provenance hierarchy is readable without decorative effects;
- all primary controls have strong keyboard focus and comfortable touch targets;
- component behavior survives 320px/reflow and text expansion;
- reduced-motion mode contains no essential animated information;
- no raw one-off colour values bypass semantic tokens without justification;
- Vite development and production manifest paths are tested;
- strict TypeScript/Biome/Vite build gates are green;
- core page remains useful without JavaScript;
- visual design review reaches the documented 95+/100 target with no critical accessibility/trust defect.

---

## Implementation PR 3 — Countries, currencies and temporal relationships

**Goal:** model country/currency relationships correctly for both current and historical modes.

Deliverables:

- Country;
- Currency;
- CountryCurrency;
- active/historical metadata;
- constraints;
- REST Countries v5 import adapter/management command for selected current metadata;
- reusable sync service outside the command;
- dry-run/diff support where practical;
- full-snapshot sanity validation;
- idempotent upsert semantics;
- network fetch before write transaction;
- no request-path dependency on REST Countries;
- no committed raw provider dump;
- failed/partial upstream snapshot cannot delete existing canonical data;
- deterministic fixture subset;
- current vs historical selector query rules.

Acceptance:

- EUR can map to multiple countries;
- historical relationships are supported;
- archived currencies are representable;
- no hard-coded selector lists in templates.

---

## Implementation PR 4 — FX domain and Frankfurter adapter

**Goal:** implement trusted normalized exchange-rate data.

Deliverables:

- provider interface;
- Frankfurter v2 adapter;
- explicit default blend source policy;
- support for pinned provider policy internally when justified;
- strict timeout and bounded retry policy;
- normalized RateQuote;
- Decimal conversion service;
- latest/current semantic cache;
- physical-retention vs semantic-freshness distinction;
- historical cache namespace;
- provider-policy-aware versioned cache keys;
- safe stale fallback;
- provider/source attribution;
- no silent provider switching;
- cache failure remains correctness-safe;
- provider HTTP 200 invalid-payload path;
- same-currency fast path with no provider call;
- unit + fixture-based contract tests;
- optional manual/scheduled live smoke test.

Acceptance:

- current quote semantics are explicit;
- requested/effective date fields are supported;
- malformed provider data cannot enter domain state;
- observation granularity can be represented.

---

## Implementation PR 5 — HTMX current-conversion vertical slice

**Goal:** deliver the first complete user flow.

Deliverables:

- amount validation;
- source/destination controls;
- progressively enhanced searchable country/currency picker using native dialog + server-rendered HTMX results;
- @github/combobox-nav only for accessible keyboard navigation of enhanced search;
- explicit accessible fallback when enhancement is unavailable;
- explicit first Convert;
- progressive HTMX updates after success;
- swap;
- signature bilateral source/destination presentation on large screens;
- stacked bilateral identity on mobile without compressed split-screen behavior;
- result partial;
- reference-rate/effective-date/source metadata;
- stale fallback semantics;
- browser history/bookmark strategy;
- accessible result announcement;
- HTMX request synchronization so obsolete responses cannot overwrite newer pair state;
- CSP-friendly external TypeScript behavior with no inline event-handler dependency;
- Playwright P0 flow + axe state scans.

At this point the basic product is useful and already expresses the product's signature idea: conversion connects two cultural/currency contexts, even before the deeper Explore data layers ship.

---

## Implementation PR 6 — Historical FX converter

**Goal:** make selected-date conversion a first-class product capability.

Deliverables:

- Latest available / Historical date mode;
- historical date validation;
- exact-date lookup;
- requested date vs effective observation date;
- weekend/holiday/missing-observation policy;
- out-of-coverage handling;
- archived-currency discovery;
- country/date historical-currency suggestions;
- historical deep links;
- historical result partial;
- web/API-ready domain semantics;
- E2E tests for exact/fallback/out-of-coverage cases.

Acceptance:

- no historical result hides the observation date used;
- no future date succeeds;
- no archived currency receives a fabricated current quote;
- lower-frequency data never pretends to be daily.

---

## Implementation PR 7 — Historical charts and Then & now

**Goal:** explain rate movement without becoming a trading product.

Deliverables:

- time-series provider path;
- Chart.js 4 web visualization loaded as a lazy/dynamic Vite chunk only on historical chart surfaces;
- 1Y / 5Y / 10Y/custom ranges where coverage supports them;
- selected historical point;
- latest comparison for semantically valid pairs;
- high/low/text summary;
- accessible table/text fallback;
- long-lived time-series cache.

Acceptance:

- chart and converter share normalized rate semantics;
- aggregation/granularity is explicit;
- no investment-return language.

---

## Implementation PR 7A — Media asset pipeline

**Goal:** support sourced historical/editorial media and optional reviewed AI illustrations without making images a runtime dependency.

Deliverables:

- MediaAsset model and publication states;
- source/licence/creator/rights metadata;
- temporal precision/date ranges;
- Django FileSystemStorage in development;
- production-ready Django Storage abstraction for S3-compatible media;
- media selection service by country/currency/date/role;
- responsive derivatives and content hashes;
- Wikimedia Commons / Europeana candidate-ingestion tooling;
- no hot search API in user request path;
- Quiet Atlas programmatic fallback;
- generated-media metadata/AI label contract;
- optional management-command ImageGenerator adapter proof of concept after provider benchmark;
- no auto-publishing;
- security validation for image bytes/SVG.

Acceptance:

- missing image never breaks a page;
- selecting a country/year creates no AI API call;
- sourced media cannot publish without required provenance/rights;
- historical AI illustration cannot masquerade as archival evidence;
- media bytes are not stored in PostgreSQL or committed as a growing content library.

---

## Implementation PR 7B — AI integration foundation

**Goal:** add bounded, provider-isolated editorial AI without making AI a source of truth or runtime requirement.

Deliverables:

- Google Gemini server-side provider adapter;
- capability-specific interfaces instead of generic free-form LLM service;
- Gemini structured outputs for text capabilities;
- single live runtime model: Gemini 3.1 Flash-Lite Free Tier;
- explicit “Explain this” endpoint as the only recruiter-visible live AI feature;
- persistent explanation cache by normalized packet hash;
- deterministic fallback on quota/provider failure;
- image generation disabled in public runtime;
- pre-generated/stored images for the portfolio demo;
- StorySourcePacket / fact-ID grounding contracts;
- versioned prompts and JSON schemas;
- normalized provider errors;
- usage/latency/cost logging;
- fake provider for CI;
- explicit feature flags;
- no AI call inside DB transaction;
- no web-search/tool-agent loop;
- no automatic paid-model fallback;
- no AI call before explicit user action.

Acceptance:

- the whole product works with no Gemini key when AI features are disabled;
- normal CI makes zero live provider calls;
- unknown fact IDs invalidate narrative candidates;
- historical AI output cannot auto-publish;
- AI keys never reach browser/mobile;
- model names are configuration/provider concerns rather than domain imports;
- live eval command can compare model/prompt versions before promotion.

---

## Implementation PR 8 — Currency eras and deterministic storytelling

**Goal:** add the “story behind this rate” without sacrificing trust.

Deliverables:

- StoryMoment or minimal equivalent;
- curated source/provenance fields;
- currency-era lookup;
- currency transition story support;
- deterministic StoryChapter composer;
- Wikidata targeted ingestion for candidate structured facts;
- optional Wikimedia Commons / Europeana media enrichment with rights metadata;
- no runtime SPARQL dependency;
- progressive story disclosure;
- story partial/unavailable states;
- editorial/admin workflow;
- optional AI narrative draft action built on the PR 7B capability layer;
- deterministic StoryComposer remains canonical fallback;
- AI draft shows supporting fact IDs and remains review-gated;
- accessibility coverage.

Acceptance:

- story never blocks conversion;
- missing facts produce shorter stories, not filler;
- causal claims require explicit source support;
- AI is not required.

---

## Implementation PR 9 — Cultural payment context

**Goal:** add practical current destination intelligence.

Deliverables:

- CulturalProfile;
- curated payment/cash/tipping data;
- provenance fields;
- admin editing;
- destination context section;
- graceful no-data state.

Historical mode must not automatically backdate current payment customs.

---

## Implementation PR 10 — Typical prices / purchasing context

**Goal:** answer “what does this amount roughly mean locally?” and complete the P0 compact Explore triad together with payment context and money/culture storytelling.

Deliverables:

- TypicalPrice model;
- city/national scope;
- ranges;
- provenance;
- observation date;
- source trust class;
- confidence;
- curated/official source ingestion where available;
- no mandatory Numbeo dependency;
- equivalent-count calculation;
- transparent disclaimers.

Historical mode keeps current price context separate unless explicit historical price data exists.

---

## Implementation PR 11 — Favourites and recent conversions

**Goal:** improve repeat-use value.

Phase A:

- anonymous browser-local recent/favourites;
- clear local persistence controls.

Phase B:

- durable user sync after accounts are introduced;
- authenticated FavouritePair database uniqueness guarantee;
- concurrent duplicate-save test.

---

## Implementation PR 12 — Accounts and ownership

**Goal:** support cross-device saved state.

Deliverables:

- signup/login/profile;
- ownership rules;
- durable favourites/history;
- deletion/privacy controls;
- authorization tests;
- ownership-scoped queries for every user-owned resource;
- account deletion/privacy lifecycle defined;
- cross-user read/update/delete regression cases from backend scenario catalog.

Basic current and historical conversion remain anonymous.

---

## Implementation PR 13 — Versioned mobile API

**Goal:** expose stable mobile contracts.

Deliverables:

- DRF;
- `/api/v1`;
- current/historical conversion endpoint;
- countries/currencies;
- requested/effective-date fields;
- destination context;
- story endpoint/embedded story contract only if justified;
- drf-spectacular OpenAPI 3 schema;
- schema generation suitable for openapi-typescript;
- stable API error envelope + machine-readable codes + request_id;
- URL namespace versioning under /api/v1;
- explicit Decimal-string/date semantics;
- contract tests;
- throttling/rate-abuse baseline where necessary, documented as fair-use rather than DDoS security;
- CI schema validation + generated-mobile-type drift check.

---

## Implementation PR 14 — React Native / Expo foundation

**Goal:** establish mobile product independently from web UI.

Deliverables:

- Expo SDK 57 stable compatibility matrix as current baseline, re-checked immediately before implementation;
- React Native 0.86.x / React 19.2.3 through Expo matrix;
- Node 24 LTS;
- TypeScript strict configuration;
- Expo Router stable navigation shell;
- React Native StyleSheet + typed Quiet Atlas tokens;
- @expo/ui selective native-control baseline;
- openapi-typescript generated contracts;
- openapi-fetch typed API client;
- TanStack Query remote-state layer;
- Expo SQLite database + migrations for explicit durable offline data;
- environment config;
- Jest/jest-expo + React Native Testing Library;
- Maestro smoke-test setup;
- loading/error/offline design foundation.

Acceptance:

- no beta Expo SDK/experimental navigation dependency is required;
- no Redux/Zustand/NativeWind is introduced without a demonstrated need;
- OpenAPI generated types match backend schema;
- SQLite migration and relaunch persistence are tested;
- navigation and core accessibility semantics are covered.

---

## Implementation PR 15 — Mobile current + historical conversion

Deliverables:

- current conversion;
- historical date mode;
- swap;
- destination money context;
- historical story entry point;
- native historical date selection through @expo/ui;
- cached last-successful data persisted in Expo SQLite with exact semantic pair/date keys;
- TanStack Query cancellation/refresh integration;
- explicit stale/offline state;
- saved pairs;
- historical mobile line chart using react-native-svg + small project-owned typed LineChart when the chart surface is introduced;
- Maestro high-value conversion/offline smoke path.

---

## Implementation PR 16 — Trips and budget

Deliverables:

- Trip;
- budget;
- daily budget interpretation;
- web UI;
- API;
- mobile UI;
- Trip transaction boundaries;
- optimistic version conflict semantics when multi-device editing is introduced;
- no external FX call while Trip write transaction is open.

Only implement after core conversion/context proves stable.

---

## Implementation PR 17 — Historical purchasing-power research/prototype

**Goal:** determine whether the product can responsibly answer “what could this money buy then?”

This is a research/prototype phase, not guaranteed production scope.

Research and prototype adapters:

- Eurostat HICP for EU inflation/time change;
- Eurostat PPP/price-level datasets for European cross-country comparison;
- OECD SDMX PPP/price-level datasets;
- World Bank CPI/PPP indicators for global coverage;
- national statistical-office requirements where methodology demands;
- source/dataset metadata and licensing;
- base-period methodology;
- domestic purchasing power vs cross-country price levels.

No feature ships until methodology is explainable and testable.

---

## Implementation PR 18 — Production hardening

Deliverables:

- PostgreSQL deployment;
- production shared cache when justified;
- explicit cache-degradation behavior;
- provider timeout hierarchy;
- static assets;
- security headers;
- structured observability/request IDs;
- provider/cache/import operational metrics/logs;
- database backup/restore runbook;
- provider and data-source incident playbooks;
- production startup/system checks;
- performance profiling;
- final Playwright matrix;
- accessibility review;
- screenshots/social preview;
- GitHub metadata;
- demo deployment.

---

# Sequencing rules

1. Do not start a visually exciting later feature while an earlier trust/domain dependency is unfinished.
2. Historical conversion must exist before historical storytelling.
3. Storytelling must not introduce a second rate-calculation path.
4. Historical purchasing power remains separate from historical FX until methodology is proven.
5. Current cultural/payment data must never be silently presented as historical.
6. The project should remain deployable and understandable after every implementation PR.


# External data sequencing rule

External integrations follow this order:

```text
research source
→ document provenance/licence/cost
→ define normalized contract
→ fixture tests
→ adapter
→ import/cache policy
→ user-facing integration
```

Do not place a third-party API into a user request path simply because an endpoint exists.

For source decisions, implementation must reference:

- `11_API_RESEARCH_AND_DATA_SOURCES.md`;
- `12_EXTERNAL_API_CONTRACTS.md`.


# Frontend technology sequencing rule

Frontend work follows:

```text
UX/design requirement
→ native/platform capability check
→ selected architecture contract
→ smallest justified dependency
→ accessibility/failure state
→ tests
→ implementation
```

For frontend technology decisions, implementation PRs must consult:

- `13_FRONTEND_TECHNOLOGY_STRATEGY.md`;
- `14_WEB_FRONTEND_ARCHITECTURE.md`;
- `15_MOBILE_FRONTEND_ARCHITECTURE.md`.

Do not add a client framework or state library as a convenience shortcut around the documented ownership model.


# Backend implementation sequencing rule

Backend changes follow this order:

```text
scenario / invariant
→ transport boundary
→ application use case
→ pure domain rule where possible
→ persistence/provider boundary
→ transaction/cache/concurrency policy
→ failure/observability behavior
→ tests
→ presentation/API wiring
```

Every non-trivial backend PR must reference the relevant BE-* scenarios from `21_BACKEND_SCENARIO_CATALOG.md`.

Before adding an abstraction, answer:

- Which invariant or repeated boundary does it protect?
- Why is direct Django ORM / a plain function insufficient?
- Does it reduce or increase the number of places where business truth can exist?

Do not introduce generic repository, DI, async, Redis, Celery, CQRS or event-bus infrastructure without a documented scenario that requires it.


# Media implementation sequencing rule

Media follows:

```text
need for visual
→ is factual evidence required?
   ├─ yes → sourced archival/editorial media
   └─ no  → can CSS/SVG solve it?
             ├─ yes → programmatic Quiet Atlas visual
             └─ no  → reviewed generated illustration
→ rights/provenance/authenticity metadata
→ optimized derivative
→ publish
→ local/stored selection at runtime
```

Do not put image search/generation into the conversion request path.


# AI implementation sequencing rule

AI changes follow:

```text
deterministic source data
→ capability-specific typed input packet
→ model routing/config
→ structured provider call
→ semantic validation
→ moderation/review where required
→ candidate persistence
→ explicit publication/use
```

Before an AI PR merges, it must answer:

- Why is AI better than deterministic code for this exact task?
- What happens when AI is disabled/unavailable?
- What facts is the model allowed to use?
- What schema and validators constrain the output?
- What eval set proves the model/prompt is acceptable?
- What is the cost/latency budget?
- Does any personal data leave our system?
- Can the model trigger side effects? If yes, why is that necessary?

Default answer for side effects is **no**.


---

# Signature experience sequencing rule

The original-concept restoration does **not** introduce a new parallel roadmap.

It is delivered through existing implementation slices:

```text
PR 2  → bilateral visual shell + atmosphere tokens
PR 3  → correct country/currency relationships
PR 5  → working dual-context converter
PR 8  → Money & culture story path
PR 9  → Payment context path
PR 10 → Everyday value path
PR 11 → saved cultural pairs / recent context
P1    → optional pronunciation/audio + richer sourced comparison
```

P0 is considered culturally complete only when the converter can provide these three first-level deeper paths:

```text
Everyday value
Payment context
Money & culture
```

Do not create a separate large “culture dashboard” milestone.

The bilateral experience belongs inside the existing converter architecture.


---

# Development execution rule

Every roadmap PR is executed through the common development contract:

```text
Definition of Ready
→ bounded PR
→ acceptance criteria
→ implementation
→ requirement-traceable tests
→ CI / browser QA
→ docs/ADR update when behaviour changes
→ merge
```

Before coding any roadmap slice, consult:

- `30_DEVELOPER_WORKFLOW_AND_PR_CONTRACT.md`;
- `31_TEST_STRATEGY_AND_TRACEABILITY.md`.

When applicable also consult:

- `32_ENVIRONMENT_CONFIGURATION_AND_SECRETS.md`;
- `33_DATA_MIGRATIONS_FIXTURES_AND_SEEDING.md`;
- `34_RELEASE_DEPLOYMENT_AND_ROLLBACK_RUNBOOK.md`;
- `35_CONTENT_I18N_AND_COPY_CONTRACT.md`;
- `36_PERFORMANCE_BUDGETS_AND_PROFILING.md`.

Do not expand an implementation PR because another improvement is nearby. Add it to the roadmap/backlog or split it into a new PR unless it is required for the current acceptance criteria.
