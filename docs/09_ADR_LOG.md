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


---

## ADR-020 — Frankfurter v2 blend is the default FX source policy

**Status:** accepted

Use Frankfurter v2's default institutional/official-source blend for general current and historical conversion.

Reasons:

- broad current and archived-currency coverage;
- provider attribution;
- historical/time-series support;
- no public API key;
- open-source self-host escape hatch.

A pinned source such as ECB is a distinct source policy, not an invisible fallback.

---

## ADR-021 — No silent FX provider switching

**Status:** accepted

A provider outage cannot silently substitute a rate from a source with different methodology.

Recovery order is:

- valid cache;
- configured Frankfurter endpoint;
- safe same-pair stale cache;
- explicit unavailable state.

Changing provider semantics requires a deliberate adapter/policy decision and updated attribution.

---

## ADR-022 — Only FX is a runtime external dependency by default

**Status:** accepted

The critical user request path may call Frankfurter when a rate refresh is required.

Country metadata, cultural/story data, media metadata and official statistical observations are imported or curated into local storage.

This minimizes latency, quota risk and outage coupling.

---

## ADR-023 — REST Countries is import-only reference metadata

**Status:** accepted

REST Countries v5 can seed/update selected normalized country fields.

It is not called on every page request and does not define our domain schema.

The project does not commit or redistribute a full raw provider dataset.

Current authentication, pricing and terms must be re-checked before production automation.

---

## ADR-024 — Cultural knowledge sources are editorial inputs

**Status:** accepted

Wikidata, Wikimedia Commons and Europeana are discovery/import sources.

They are not runtime source-of-truth dependencies for conversion.

Rules:

- structured facts require verification for trust-sensitive claims;
- media requires per-record/per-file rights metadata;
- published story content is stored locally with provenance;
- runtime SPARQL is not required.

---

## ADR-025 — Official statistical APIs are imported behind dedicated adapters

**Status:** accepted for future purchasing-power work

Potential sources:

- Eurostat HICP/PPP;
- OECD PPP/price-level data;
- World Bank CPI/PPP indicators.

They are not interchangeable:

- CPI/HICP measures price change through time;
- PPP/price-level indices support cross-country price-level comparisons.

No historical purchasing-power feature ships until methodology is explicit and tested.

---

## ADR-026 — Numbeo is not a required P0/P1 dependency

**Status:** accepted

Numbeo provides useful current/historical item-price data but is not selected as a mandatory source because:

- current API cost is disproportionate for the portfolio stage;
- data is crowdsourced;
- commercial/API licensing creates additional dependency.

Keep the domain capable of supporting a future licensed price provider without coupling `TypicalPrice` to Numbeo's schema.

---

## ADR-027 — Clients never call third-party data APIs directly

**Status:** accepted

Django owns all external data-source policies.

The browser receives server-rendered HTML/HTMX fragments.

React Native calls our versioned Django API.

Benefits:

- no leaked keys;
- one cache/fallback policy;
- consistent Decimal/date semantics;
- centralized provenance and licensing;
- simpler offline behaviour.

---

## ADR-028 — External data contracts are explicit and provider-specific

**Status:** accepted

Do not create one generic external-API abstraction that erases semantic differences.

Each provider gets a small adapter responsible for:

- transport;
- validation;
- normalization;
- provenance;
- provider-specific errors.

Shared HTTP utilities may handle transport mechanics, but they do not decide domain meaning.
