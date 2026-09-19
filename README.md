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
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
             PostgreSQL        Django cache       JSON API v1
                 │                  │                  │
                 └──────────────┬───┘                  │
                                │                      │
                       Django Templates          React Native
                         + HTMX 2.x             + TypeScript
                         + Tailwind 4               + Expo
```

## Engineering principles

1. **Django first.** Web UI is server rendered. React is reserved for the mobile client.
2. **HTML over JSON for the web.** HTMX exchanges HTML fragments with Django views.
3. **JSON only at explicit API boundaries.** The mobile client uses a versioned API.
4. **Financial correctness.** Money and FX calculations use `Decimal`, explicit rounding and currency metadata.
5. **Source attribution.** Exchange rates, purchasing-power data and cultural facts must have provenance.
6. **Progressive enhancement.** Core conversion remains usable without client-side application state.
7. **Accessibility by default.** WCAG 2.2 AA is the baseline.
8. **Proportional architecture.** No microservices, event buses or repository layers without a concrete problem.
9. **Explicit stale-data semantics.** Cached/offline rates are labelled with their source time.
10. **Documentation is executable intent.** Non-trivial PRs must reference the relevant product/architecture documents.

## Documentation

Start with [docs/00_INDEX.md](docs/00_INDEX.md).

The handbook covers:

- product scope and success criteria;
- user journeys and UX states;
- design-system principles;
- Django/HTMX/Tailwind architecture;
- domain models and financial rules;
- React Native/API boundaries;
- quality, security and accessibility;
- implementation sequencing and ADRs;
- official references.

## Delivery strategy

The rebuild is intentionally incremental. The legacy blog implementation remains only until the foundation PR replaces it with the new project shell. Each following PR delivers one bounded vertical slice.

See [docs/08_IMPLEMENTATION_ROADMAP.md](docs/08_IMPLEMENTATION_ROADMAP.md).

## Current status

**Phase:** documentation and architecture foundation.

The existing `django-blog/` code is legacy course material and is not the target architecture.
