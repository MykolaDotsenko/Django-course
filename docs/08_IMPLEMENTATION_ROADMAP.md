# Implementation Roadmap

The roadmap is ordered to maximize working software and recruiter-visible evidence while minimizing speculative infrastructure.

## PR 1 — Documentation foundation

**Goal:** establish one product/engineering contract before implementation.

Deliverables:

- product specification;
- UX flows;
- UI system;
- architecture;
- domain model;
- mobile/API strategy;
- quality/security/accessibility;
- ADR log;
- references;
- PR roadmap.

No production behaviour changes.

---

## PR 2 — Repository and Django foundation

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

## PR 3 — Design system and server-rendered shell

**Goal:** establish the visual/accessibility foundation before domain complexity.

Deliverables:

- Tailwind 4 build;
- semantic base template;
- responsive app shell;
- design tokens;
- focus/reduced-motion rules;
- initial converter skeleton;
- no React on web.

---

## PR 4 — Countries and currencies

**Goal:** model country/currency relationships correctly.

Deliverables:

- Country;
- Currency;
- CountryCurrency;
- constraints;
- seed/import management command;
- deterministic fixture subset for tests;
- country/currency selector partials.

Acceptance:

- EUR can map to multiple countries;
- historical relation shape is supported;
- no hard-coded selector lists in templates.

---

## PR 5 — FX domain and Frankfurter adapter

**Goal:** implement trusted conversion before UI enrichment.

Deliverables:

- provider interface;
- Frankfurter v2 adapter;
- strict timeout;
- normalized RateQuote;
- Decimal conversion service;
- Django cache;
- stale fallback semantics;
- unit + contract tests.

---

## PR 6 — HTMX conversion vertical slice

**Goal:** deliver the first complete user flow.

Deliverables:

- amount validation;
- source/destination controls;
- convert;
- swap;
- result partial;
- freshness/provider metadata;
- browser history/bookmark strategy;
- accessible live-result announcement;
- Playwright P0 flow.

At this point the product is usable.

---

## PR 7 — Cultural payment context

**Goal:** add the first differentiator.

Deliverables:

- CulturalProfile;
- curated payment/cash/tipping data;
- provenance fields;
- admin editing;
- destination context section;
- graceful no-data state.

---

## PR 8 — Typical prices / purchasing context

**Goal:** answer “what does this amount mean locally?”

Deliverables:

- TypicalPrice model;
- city/national scope;
- ranges;
- provenance;
- observation date;
- confidence;
- equivalent-count calculation;
- transparent disclaimers.

---

## PR 9 — Favourites and recent conversions

**Goal:** improve repeat-use value.

Phase A:
- anonymous browser-local recent/favourites where privacy-safe.

Phase B:
- durable user sync after accounts are introduced.

---

## PR 10 — Accounts and ownership

**Goal:** support cross-device saved state.

Deliverables:

- signup/login/profile;
- ownership rules;
- durable favourites/history;
- deletion/privacy controls;
- authorization tests.

Do not make basic conversion require login.

---

## PR 11 — Historical FX context

**Goal:** provide useful non-trading trend context.

Deliverables:

- provider time-series adapter;
- 1M / 1Y / 5Y ranges;
- accessible chart + text/table fallback;
- long-term caching.

---

## PR 12 — Versioned mobile API

**Goal:** expose stable mobile contracts.

Deliverables:

- DRF;
- `/api/v1`;
- conversion endpoint;
- countries/currencies;
- destination context;
- schema/OpenAPI;
- contract tests;
- throttling/rate-abuse baseline where necessary.

---

## PR 13 — React Native / Expo foundation

**Goal:** establish the mobile product independently from the web UI.

Deliverables:

- Expo stable SDK;
- TypeScript strict configuration;
- navigation shell;
- API client;
- environment config;
- typed server contracts;
- loading/error/offline design foundation.

---

## PR 14 — Mobile core conversion

Deliverables:

- convert;
- swap;
- destination money context;
- cached last-successful data;
- explicit stale/offline state;
- saved pairs.

---

## PR 15 — Trips and budget

Deliverables:

- Trip;
- budget;
- daily budget interpretation;
- web UI;
- API;
- mobile UI.

Only implement after core conversion/context proves stable.

---

## PR 16 — Production hardening

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

## Sequencing rule

Do not start a later PR because it looks visually exciting if an earlier domain/trust dependency is unfinished.

The project should remain deployable and understandable after every PR.
