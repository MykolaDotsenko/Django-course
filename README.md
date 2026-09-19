# Cultural Currency Converter

> **Convert money. Understand local value. Discover culture.**

Cultural Currency Converter is a Django-first travel-money intelligence product that explains not only **how much** money converts to, but **what that amount means locally**.

The repository is being rebuilt from an early Django course project into a production-minded portfolio case study.

## Product thesis

A conventional FX calculator answers:

> 100 EUR = X JPY

Cultural Currency Converter goes further:

- converts money using attributable exchange-rate data;
- explains local purchasing context;
- surfaces payment customs, cash/card usage and tipping norms;
- adds curated cultural and currency-history context;
- supports saved pairs, recent conversions and later trip budgets;
- exposes the same backend domain to a React Native mobile client.

The primary product loop is:

```text
Convert → Understand → Explore → Save → Return
```

## Target architecture

```text
                           Official / curated data
                     ┌──────────────┴──────────────┐
                     │                             │
              Frankfurter v2              Country/culture data
                     │                             │
                     └──────────────┬──────────────┘
                                    ▼
                         Django modular monolith
                    presentation → use cases → domain
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
             PostgreSQL        Django cache       JSON API v1
                 │                  │                  │
                 └──────────────┬───┘                  │
                                │                      │
                       Django Templates          React Native
                         + HTMX 2.x              + Expo 57*
                         + Tailwind 4             + Expo Router
                         + TypeScript             + TanStack Query
                         + Vite 8                 + Expo SQLite
                                                  + TypeScript

                    * stable compatibility matrix re-checked
                      immediately before mobile implementation
```

## Engineering principles

1. **Django first.** Web UI is server rendered. React is reserved for the mobile client.
2. **HTML over JSON for the web.** HTMX exchanges HTML fragments with Django views.
3. **JSON only at explicit API boundaries.** The mobile client uses a versioned API.
4. **Financial correctness.** Money and FX calculations use `Decimal`, explicit rounding and currency metadata.
5. **Source attribution.** Exchange rates, purchasing-power data and cultural facts must have provenance.
6. **Progressive enhancement.** Core conversion remains usable without client-side application state; Vite/TypeScript enhance HTML rather than create a SPA.
7. **Accessibility by default.** WCAG 2.2 AA is the baseline.
8. **Proportional architecture.** No microservices, event buses or repository layers without a concrete problem.
9. **Explicit stale-data semantics.** Cached/offline rates are labelled with their source time.
10. **Documentation is executable intent.** Non-trivial PRs must reference the relevant product/architecture documents.
11. **Explicit backend ownership.** Views/forms/serializers handle transport; application use cases coordinate; pure domain code owns financial semantics; provider adapters own external JSON.
12. **Short transactions.** Network I/O never runs while PostgreSQL transactions/row locks are intentionally held; durable invariants use constraints and explicit transaction boundaries.
13. **Media authenticity before spectacle.** Real sourced archival media is preferred for historical evidence; AI imagery is reviewed, stored and visibly labelled as illustration rather than generated on every country/year change.
14. **AI synthesizes; it does not establish truth.** The public demo uses Gemini 3.1 Flash-Lite's free tier for one bounded live explanation feature; paid AI and runtime image generation are disabled by default. FX, historical observations, provenance and published facts remain deterministic and sourced.

## Documentation

Start with [docs/00_INDEX.md](docs/00_INDEX.md).

The handbook covers:

- product scope and success criteria;
- user journeys and UX states;
- design-system principles;
- Django/HTMX/Tailwind/Vite/TypeScript web architecture;
- domain models and financial rules;
- React Native/Expo/API/offline architecture;
- explicit frontend technology decisions and rejected alternatives;
- backend system design, request/data flows and application-service boundaries;
- PostgreSQL transactions, constraints, cache/concurrency policy;
- API/security/observability/operations and 148 backend scenarios;
- scheduled imports, maintenance and failure behavior;
- sourced historical media, object-storage strategy and controlled AI illustration pipeline;
- zero-cost Gemini free-tier explanation, structured outputs, persistent cache, deterministic fallback, evals and privacy/quota governance;
- quality, security and accessibility;
- implementation sequencing and ADRs;
- developer workflow, Definition of Ready/Done and PR review contract;
- requirement-to-test traceability and fixture strategy;
- environment/configuration/secrets boundaries;
- migration, seeding, release and rollback runbooks;
- content/i18n terminology and performance budgets;
- official references.

## Delivery strategy

The rebuild is intentionally incremental. The repository/Django foundation is now complete: root product shell, consolidated Python quality tooling, validated environment configuration, PostgreSQL-backed CI, health endpoints, request correlation and structured logging. The next implementation milestone is the server-rendered Quiet Atlas design system and converter shell.

See [docs/08_IMPLEMENTATION_ROADMAP.md](docs/08_IMPLEMENTATION_ROADMAP.md).

## Current status

**Phase:** foundation complete → server-rendered product shell next.

The Django product shell, runtime configuration, PostgreSQL path and observability baseline are executable and CI-backed. Product implementation can now build on this foundation without carrying legacy course scaffolding or speculative infrastructure.
