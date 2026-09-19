# Architecture Decision Record Log

This file records durable decisions. Each decision can later move to an individual ADR file if discussion becomes large.

## ADR-001 — Django 5.2 LTS as backend baseline

**Status:** accepted

Use the Django 5.2 LTS line rather than chasing the newest major release.

Reasons:

- long-term security support;
- mature ecosystem;
- portfolio signal of version judgement rather than novelty;
- existing repository already started on 5.2.

Use the latest supported 5.2 patch during implementation.

---

## ADR-002 — Server-rendered web with HTMX

**Status:** accepted

The web application uses Django templates + HTMX.

React is not used for the web UI.

Reasons:

- conversion is form/server-data oriented;
- HTML fragments are sufficient;
- smaller runtime/dependency surface;
- demonstrates Django-first product engineering;
- progressive enhancement remains straightforward.

---

## ADR-003 — Tailwind CSS 4 for styling

**Status:** accepted

Use Tailwind 4 if the documented browser support matches project targets.

Do not introduce a component framework by default.

Design semantics live in tokens/components, not raw utility duplication.

---

## ADR-004 — React Native + Expo for mobile

**Status:** accepted

Mobile is a real React Native application using TypeScript.

Select a stable Expo SDK and its supported React Native version as a compatibility set rather than forcing the numerically newest RN release.

---

## ADR-005 — DRF only for explicit mobile API

**Status:** accepted

Django REST Framework serves `/api/v1`.

The Django web UI does not call this API; it receives HTML directly.

---

## ADR-006 — Frankfurter v2 as initial FX provider

**Status:** accepted for P0

Reasons:

- no API key;
- official/central-bank source aggregation;
- provider attribution;
- historical coverage;
- time-series support;
- open-source/self-hostable fallback.

The adapter boundary keeps replacement possible.

---

## ADR-007 — Decimal for all money/rate arithmetic

**Status:** accepted

No float enters domain-level money calculations.

Rate normalization and output quantization are explicitly tested.

---

## ADR-008 — Modular monolith

**Status:** accepted

Use bounded Django apps rather than microservices.

Split a service only if operational scaling or ownership boundaries later justify it.

---

## ADR-009 — Django cache abstraction before Redis

**Status:** accepted

Code depends on Django's cache API.

Redis is an infrastructure choice introduced only when deployment/load requirements justify it.

---

## ADR-010 — PostgreSQL production target

**Status:** accepted

Production and meaningful CI verification use PostgreSQL.

SQLite may remain an optional low-friction local mode if it does not hide database-specific behaviour.

---

## ADR-011 — Data provenance is a domain requirement

**Status:** accepted

Trust-sensitive external data must carry source and effective/observed/verified time metadata.

Unsourced “typical prices” and cultural facts are not publishable.

---

## ADR-012 — Culture is progressive enrichment

**Status:** accepted

The converter remains the primary workflow.

Culture may enrich the experience but cannot block or visually dominate conversion.

---

## ADR-013 — No AI in financial source-of-truth path

**Status:** accepted

AI may summarize already-sourced cultural content in later phases.

AI cannot generate exchange rates, fees, prices or unsourced factual claims used as trusted product data.

---

## ADR-014 — WCAG 2.2 AA baseline

**Status:** accepted

Accessibility is an implementation constraint, not a final polish phase.


---

## ADR-015 — Historical FX is separate from historical purchasing power

**Status:** accepted

The historical converter uses published historical exchange-rate observations.

It does not infer inflation-adjusted buying power from FX rates.

A future historical purchasing-power feature requires its own CPI/PPP/price-level methodology and source adapters.

---

## ADR-016 — Requested date and effective observation date are separate concepts

**Status:** accepted

Historical queries preserve:

- the date selected by the user;
- the actual provider observation date used.

Weekend/holiday/low-frequency fallback can never be hidden by overwriting requested date.

---

## ADR-017 — Archived currencies are first-class historical entities

**Status:** accepted

Historical mode may expose provider-supported archived currencies such as FIM/DEM/etc.

Current/default conversion UI prioritizes active currencies.

Country/date may suggest a relevant historical currency, but an explicit user currency choice is never silently changed.

---

## ADR-018 — Storytelling is deterministic and source-backed by default

**Status:** accepted

The story layer is composed from:

- normalized conversion data;
- sourced currency-era/transition facts;
- sourced StoryMoment records;
- semantically valid comparisons.

An LLM is not required for core storytelling and cannot be the source of historical facts, rates or causal claims.

---

## ADR-019 — Story failure cannot invalidate conversion

**Status:** accepted

Historical/current conversion is the source-of-truth task.

Story/chart/cultural modules are progressive enrichment.

If story data is incomplete or unavailable, the successful conversion remains unchanged.
