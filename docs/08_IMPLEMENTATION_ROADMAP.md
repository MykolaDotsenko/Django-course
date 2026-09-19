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
- external API integration contracts.

Implementation starts only after the documentation is coherent enough to act as an engineering contract.

---

## Implementation PR 1 — Repository and Django foundation

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
- safe `.env.example`;
- README run instructions.

Acceptance:

- no hard-coded secret key;
- `DEBUG` environment-controlled;
- clean migration state;
- test/quality commands documented;
- CI green.

---

## Implementation PR 2 — Design system and server-rendered shell

**Goal:** establish visual/accessibility foundation before domain complexity.

Deliverables:

- Tailwind 4 build;
- semantic CSS/theme-token layer based on `03A_VISUAL_FOUNDATIONS.md`;
- self-hosted primary typography strategy with system fallback;
- responsive app shell;
- 4px spacing/radius/elevation scales;
- neutral core + controlled country-accent system;
- focus/reduced-motion/high-contrast rules;
- primary converter shell from `03B_SCREEN_BLUEPRINTS.md`;
- AmountField, CountryCurrencyTrigger, SwapButton, ConvertButton and initial Result primitives using exact anatomy/sizing from `03C1_COMPONENT_ANATOMY_AND_DIMENSIONS.md`;
- explicit hover/focus/pressed/loading/error states from `03C_COMPONENT_STATES_AND_MICROINTERACTIONS.md`;
- container-query behavior for reusable components;
- 320px/reflow and mobile layouts;
- no React on web;
- no decorative above-fold media dependency.

Acceptance:

- converter remains the visual focal point;
- result/provenance hierarchy is readable without decorative effects;
- all primary controls have strong keyboard focus and comfortable touch targets;
- component behavior survives 320px/reflow and text expansion;
- reduced-motion mode contains no essential animated information;
- no raw one-off colour values bypass semantic tokens without justification;
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
- no request-path dependency on REST Countries;
- no committed raw provider dump;
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
- latest/current cache;
- historical cache namespace;
- safe stale fallback;
- provider/source attribution;
- no silent provider switching;
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
- explicit first Convert;
- progressive HTMX updates after success;
- swap;
- result partial;
- reference-rate/effective-date/source metadata;
- stale fallback semantics;
- browser history/bookmark strategy;
- accessible result announcement;
- Playwright P0 flow.

At this point the basic product is useful.

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

**Goal:** answer “what does this amount roughly mean locally?”

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

- durable user sync after accounts are introduced.

---

## Implementation PR 12 — Accounts and ownership

**Goal:** support cross-device saved state.

Deliverables:

- signup/login/profile;
- ownership rules;
- durable favourites/history;
- deletion/privacy controls;
- authorization tests.

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
- schema/OpenAPI;
- contract tests;
- throttling/rate-abuse baseline where necessary.

---

## Implementation PR 14 — React Native / Expo foundation

**Goal:** establish mobile product independently from web UI.

Deliverables:

- Expo stable SDK;
- TypeScript strict configuration;
- navigation shell;
- API client;
- environment config;
- typed server contracts;
- loading/error/offline design foundation.

---

## Implementation PR 15 — Mobile current + historical conversion

Deliverables:

- current conversion;
- historical date mode;
- swap;
- destination money context;
- historical story entry point;
- cached last-successful data;
- explicit stale/offline state;
- saved pairs.

---

## Implementation PR 16 — Trips and budget

Deliverables:

- Trip;
- budget;
- daily budget interpretation;
- web UI;
- API;
- mobile UI.

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
- production cache when justified;
- static assets;
- security headers;
- observability;
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
