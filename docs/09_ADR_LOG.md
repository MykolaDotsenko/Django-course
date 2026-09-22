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

Tailwind is the CSS build/reset/token/utility foundation, not a utility-only rendering mandate.
Quiet Atlas may expose project-owned semantic `.qa-*` component classes for stable Django/HTMX
surfaces when that keeps responsive, state and accessibility behavior coherent.

Do not introduce a third-party component framework by default, and do not grow a parallel generic
component framework. Semantic component CSS must stay token-driven, shallow and tied to real product
components. Design semantics live in tokens/components, not raw utility duplication or repeated raw
CSS values.

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


---

## ADR-029 — Quiet Atlas is the core visual language

**Status:** accepted

The product design language is named **Quiet Atlas** and uses a restrained direction described as:

> **Nordic editorial utility — calm enough for money, warm enough for culture.**

The design combines:

- clear travel utility;
- strong numerical typography;
- generous whitespace;
- quiet surfaces;
- sourced editorial storytelling;
- subtle contextual country accents.

It explicitly avoids trading-dashboard, crypto, casino, tourism-collage and generic “AI gradient” aesthetics.

---

## ADR-030 — Semantic design tokens own visual decisions

**Status:** accepted

Color, typography, spacing, radius, border, elevation and motion are defined as semantic/system tokens before use in components.

Tailwind 4 theme variables are the preferred web implementation mechanism.

Country theming modifies constrained contextual variables rather than scattering raw colors through templates.

---

## ADR-031 — Country theming cannot change interaction architecture

**Status:** accepted

Country context may alter:

- accent;
- pattern;
- imagery;
- limited editorial atmosphere.

It cannot alter:

- control positions;
- focus order;
- semantic states;
- component hierarchy;
- validation behavior;
- trust/provenance presentation.

The neutral theme remains a complete fallback.

---

## ADR-032 — Whitespace and typography precede card chrome

**Status:** accepted

The product avoids “card soup”.

Use cards only when a boundary/grouping is meaningful.

Prefer:

- spacing;
- type hierarchy;
- borders;
- section rhythm

before introducing additional elevated containers.

This keeps information density high without visual noise.

---

## ADR-033 — Historical mode is visually archival, not nostalgic

**Status:** accepted

Historical mode uses:

- date prominence;
- timeline semantics;
- neutral informational accent;
- editorial composition.

It deliberately avoids:

- sepia;
- fake paper;
- typewriter fonts;
- theatrical clock/time-machine motion.

Historical trust is more important than nostalgia.

---

## ADR-034 — Motion must explain state or continuity

**Status:** accepted

Custom motion is permitted only when it communicates:

- action feedback;
- state transition;
- spatial continuity;
- layer change.

Rejected defaults include:

- number count-up;
- bouncing conversion results;
- autoplay historical timelines;
- decorative parallax;
- looping floating objects.

Reduced-motion mode removes non-essential transforms and chart/story animation.

---

## ADR-035 — Responsive components prefer intrinsic/container-based adaptation

**Status:** accepted

Use:

- viewport breakpoints for macro page/navigation changes;
- Tailwind 4 container queries for reusable component adaptation.

Mobile is intentionally composed as a task flow rather than a compressed desktop split-screen.

Core conversion must remain usable under approximately 320 CSS px reflow conditions.

---

## ADR-036 — Light theme ships before optional dark theme

**Status:** accepted

Light mode is the primary design baseline.

Dark mode ships only when it can match:

- contrast;
- chart quality;
- state clarity;
- country-theme safety;
- provenance readability.

Feature completeness is not a reason to ship a lower-quality dark theme.


---

## ADR-037 — Web remains Django templates + stable HTMX, not a SPA

**Status:** accepted

The web interface remains server-rendered Django HTML progressively enhanced by stable HTMX 2.x.

Do not introduce React, Next.js, Vue or Svelte for the web application unless the product later develops client-application requirements that the current architecture cannot reasonably satisfy.

Reasons:

- Django already owns authoritative web state;
- designed interactions map cleanly to HTML fragments;
- progressive enhancement is valuable for reliability/accessibility;
- lower runtime JavaScript;
- no duplicated web/mobile business state.

React competency is demonstrated separately in the native client.

---

## ADR-038 — Vite 8 + TypeScript are the web asset/enhancement toolchain

**Status:** accepted

Add Vite 8 and strict TypeScript to the Django web frontend.

Vite owns:

- CSS/JS development;
- Tailwind Vite plugin;
- TypeScript bundling;
- font assets;
- code splitting;
- hashed production assets;
- manifest generation.

It does not own:

- routing;
- HTML rendering;
- business state.

Node is a build/development dependency, not a production request server.

---

## ADR-039 — Node 24 LTS is the frontend build runtime baseline

**Status:** accepted

Use Node 24 LTS rather than Node 26 Current.

Reasons:

- production tooling should prefer LTS;
- compatible with Vite 8 and Expo 57;
- reduces build-tool churn;
- one Node major can support both web and mobile work.

Pin through repository/CI configuration.

---

## ADR-040 — Use repo-owned Vite manifest integration for Django

**Status:** accepted

Follow Vite's official backend-integration manifest contract.

Implement a small tested Django template tag/adapter that:

- emits Vite dev-server modules in development;
- reads `.vite/manifest.json` in production;
- renders CSS/modulepreload/script tags.

Do not make a third-party Django/Vite bridge an architectural dependency unless future complexity clearly justifies it.

---

## ADR-041 — Tailwind 4 is integrated through the official Vite plugin

**Status:** accepted

Use:

```text
tailwindcss
@tailwindcss/vite
```

rather than an extra PostCSS pipeline.

Quiet Atlas tokens use Tailwind 4 CSS-first `@theme` plus constrained CSS custom properties.
Project-owned semantic component CSS consumes those tokens and coexists with Tailwind utilities;
`@apply` is not the default abstraction mechanism.

Browser baseline follows Tailwind 4's modern-browser requirements.

---

## ADR-042 — Django 5.2 uses django-template-partials as a temporary fragment bridge

**Status:** accepted

Because Django 5.2 LTS does not yet have Django 6.0's built-in template partials, use `django-template-partials` for named reusable fragments.

This is intentionally replaceable.

When backend upgrade to Django 6+ occurs, migrate to native template partials rather than preserving the compatibility package indefinitely.

---

## ADR-043 — django-htmx provides server integration; Vite owns browser HTMX assets

**Status:** accepted

Use `django-htmx` for:

- `request.htmx`;
- middleware typing;
- HTTP helpers.

Do not load a second vendored HTMX copy from its template tag if HTMX is already bundled through Vite.

One browser asset pipeline owns JavaScript.

---

## ADR-044 — Native web platform APIs precede UI libraries

**Status:** accepted

Default dependency order:

```text
semantic HTML
→ native browser API
→ small focused dependency
→ custom component
→ broad framework
```

Examples:

- dialog → `<dialog>`;
- disclosure → `<details>/<summary>`;
- historical date → `<input type="date">`;
- formatting → `Intl`.

No Alpine/Stimulus layer is added initially.

---

## ADR-045 — Use a focused combobox-navigation primitive, not a component framework

**Status:** accepted

The country/currency search is complex enough to justify `@github/combobox-nav` for ARIA keyboard navigation.

The project still owns:

- markup;
- Django/HTMX search;
- styles;
- selection;
- fallback;
- accessibility testing.

If the enhanced combobox proves unreliable in assistive-technology testing, prefer a simpler dialog/list fallback over adding a full UI framework.

---

## ADR-046 — Chart.js is web-history-only and lazy loaded

**Status:** accepted

Use Chart.js 4 only for historical line-chart surfaces.

It is dynamically imported so ordinary conversion does not pay the chart runtime cost.

The canvas chart is supplemental; text summary/table remains the accessible information source.

Do not add a trading visualization framework.

---

## ADR-047 — Web client state stays local and bounded

**Status:** accepted

Do not introduce Redux/Zustand/global web stores.

Use:

- server state in Django/HTML;
- local element/module state;
- bounded versioned localStorage only for small anonymous convenience data.

No IndexedDB or service worker is required in P0/P1.

---

## ADR-048 — Web frontend targets CSP-friendly external behavior

**Status:** accepted

Avoid:

- inline event handlers;
- inline behavior scripts;
- `hx-on` JavaScript expressions by default;
- runtime CDN scripts/fonts.

Prefer external TypeScript listeners and self-hosted assets.

Evaluate HTMX hardening options such as disabling eval/script-tag processing after E2E confirms no required behavior breaks.

---

## ADR-049 — Expo stable compatibility matrix wins over standalone RN version chasing

**Status:** accepted

At the 2026-09-19 research point, select:

```text
Expo SDK 57 stable
React Native 0.86.x
React 19.2.3
```

even though standalone RN 0.87 is newer.

Reason:

- the Expo compatibility matrix is the mobile runtime product;
- stable integrated dependencies matter more than a higher RN number;
- Expo beta SDKs are not production defaults.

Re-check immediately before mobile implementation.

---

## ADR-050 — Expo Router is the mobile navigation layer

**Status:** accepted

Use stable Expo Router navigation.

Do not use experimental/alpha navigation stack APIs for core production flows.

Routes/deep links can model current conversion, historical conversion, Explore, Saved and Trips as those features ship.

---

## ADR-051 — Mobile remote state and durable offline state are separate

**Status:** accepted

Use:

- TanStack Query for active remote server-state lifecycle;
- Expo SQLite for intentionally durable offline product data.

Do not persist the whole QueryClient as the primary offline architecture.

This keeps:

- cache keys;
- effective dates;
- stale semantics;
- migrations

explicit and auditable.

---

## ADR-052 — Mobile API types are generated from Django OpenAPI

**Status:** accepted

Use:

- `openapi-typescript`;
- `openapi-fetch`.

Do not hand-maintain duplicate endpoint DTO types.

Generated schema drift is a CI failure.

---

## ADR-053 — React Native StyleSheet + typed Quiet Atlas tokens, not NativeWind

**Status:** accepted

Share design-token meaning between web/mobile, not CSS utility classes.

Reasons:

- native layout semantics differ;
- StyleSheet keeps platform behavior explicit;
- avoids a styling abstraction that primarily exists to mimic the web.

Revisit only if implementation demonstrates materially lower complexity with another approach.

---

## ADR-054 — No Redux/Zustand in the initial mobile client

**Status:** accepted

State ownership is already covered by:

- React local state;
- Expo Router navigation;
- TanStack Query remote state;
- Expo SQLite durable state;
- SecureStore later for secrets.

A generic global store would currently add overlap, not clarity.

---

## ADR-055 — Mobile historical chart uses react-native-svg + project-owned LineChart

**Status:** accepted

The mobile history visualization is intentionally narrow:

- one line;
- selected/latest markers;
- simple axes;
- high/low.

Use `react-native-svg` and small typed project-owned geometry code rather than a full chart framework.

The accessible text summary remains authoritative.

---

## ADR-056 — Mobile testing uses Expo-native Jest/RNTL plus Maestro smoke

**Status:** accepted

Use:

- Jest;
- jest-expo;
- @testing-library/react-native;
- Expo Router testing utilities;
- Maestro for high-value black-box E2E.

Do not use UI snapshot testing as the primary correctness signal.


---

## ADR-057 — Backend request handling is synchronous Django

**Status:** accepted

Use synchronous Django/DRF request handlers initially.

Django 5.2 transactions are not supported in native async mode, and the product has only one normal runtime upstream dependency.

A sync HTTP client with strict timeout is simpler and safer.

Reconsider async only after measured requirements justify it.

---

## ADR-058 — WSGI is sufficient for the initial deployment

**Status:** accepted

Do not require ASGI until the product has an actual async/long-lived connection use case.

Using ASGI later remains possible.

---

## ADR-059 — Global ATOMIC_REQUESTS stays disabled

**Status:** accepted

Use Django's autocommit default.

Open short explicit transaction.atomic() blocks only around multi-write durable invariants.

Remote HTTP calls must happen outside transactions.

---

## ADR-060 — Post-commit side effects use transaction.on_commit

**Status:** accepted

Cache invalidation and future asynchronous side effects that depend on a successful DB write are registered after commit.

Do not expose rolled-back DB state through cache.

---

## ADR-061 — Database constraints protect durable invariants

**Status:** accepted

Use PostgreSQL/Django constraints for durable uniqueness and range rules.

Application pre-checks provide UX but are not the only protection against concurrency.

---

## ADR-062 — Pessimistic row locking is exceptional

**Status:** accepted

Do not use select_for_update by default.

Prefer:

- unique constraints;
- atomic writes;
- optimistic version conflicts for multi-device aggregates.

Use row locks only for a demonstrated serialization requirement and test them on PostgreSQL.

---

## ADR-063 — Cache is optimization and explicit stale fallback, never authority

**Status:** accepted

Correctness must survive cache miss/eviction/failure.

For FX, physical retention may exceed semantic freshness so a quote can be used only as an explicitly labelled stale fallback.

Cache keys include all truth-affecting semantics.

---

## ADR-064 — No distributed cache lock or stampede framework initially

**Status:** accepted

Low-volume duplicate cold provider fetches are acceptable.

Introduce request coalescing/Redis locking only after metrics show provider cost or traffic requires it.

Correctness never depends on single-flight behavior.

---

## ADR-065 — Application services exist only for real orchestration boundaries

**Status:** accepted

A service/use-case is justified for provider/cache/transaction/multi-model/non-trivial shared behavior.

Do not wrap simple Django ORM CRUD in generic service/repository classes.

---

## ADR-066 — No generic repository or dependency-injection framework

**Status:** accepted

Django ORM remains the persistence API.

Use ordinary Python dependency injection/fakes where tests require it.

Do not add a DI container.

---

## ADR-067 — Raw provider payloads stop at infrastructure adapters

**Status:** accepted

External JSON is validated and normalized into explicit values before entering application/domain code.

Views, serializers, templates and mobile contracts never depend on Frankfurter/REST Countries raw shapes.

---

## ADR-068 — DRF OpenAPI uses drf-spectacular

**Status:** accepted

DRF's built-in OpenAPI generation is deprecated.

Use drf-spectacular for OpenAPI 3 and generate mobile TypeScript contracts from that schema.

---

## ADR-069 — API errors have stable machine codes and request IDs

**Status:** accepted

Expected failures map to a stable envelope with:

- code;
- human detail;
- field errors where relevant;
- retryable where useful;
- request_id.

Clients never parse English error strings for behavior.

---

## ADR-070 — Request IDs and structured logs are baseline observability

**Status:** accepted

Every request receives a bounded opaque request ID that is returned and logged.

Phase-one observability uses structured logs, request/provider/cache timings and health endpoints.

OpenTelemetry is optional later infrastructure.

---

## ADR-071 — Liveness/readiness never depend on optional external providers

**Status:** accepted

Liveness checks process availability.

Readiness checks critical local configuration and PostgreSQL.

Frankfurter, Wikidata, REST Countries and statistical APIs are not health dependencies that trigger restart loops.

---

## ADR-072 — Slow-changing external data is imported, not fetched on user request

**Status:** accepted

Use management commands + a canonical production scheduler for country metadata, cultural ingestion and future statistical datasets.

Imports are idempotent and preserve the last valid local snapshot on upstream failure.

---

## ADR-073 — No Celery until a concrete async workload requires it

**Status:** accepted

Management commands/platform scheduler are sufficient initially.

A broker/task queue becomes justified only for real user-triggered long jobs, distributed retries, notifications/rate alerts or sustained worker workloads.

---

## ADR-074 — Import network I/O finishes before canonical DB write transaction

**Status:** accepted

Fetch, validate and normalize remote data before opening the transaction that applies the canonical snapshot.

This avoids long locks and partial remote-dependent transactions.

---

## ADR-075 — Historical and current cache identities are semantic and versioned

**Status:** accepted

Quote/series cache keys include:

- namespace version;
- current/historical mode;
- provider policy;
- provider when pinned;
- pair;
- effective/request mapping where appropriate;
- range/grouping for series.

A provider-policy change requires a new semantic namespace rather than reusing incompatible entries.

---

## ADR-076 — Multi-device aggregate edits use optimistic conflicts when needed

**Status:** accepted for future Trip editing

When cross-device Trip updates become real, add a version field/check.

A stale update receives 409 Conflict rather than silently overwriting newer server state.

Do not add optimistic-version columns to all models preemptively.

---

## ADR-077 — Scheduled imports are idempotent and fail closed

**Status:** accepted

A failed, malformed or suspiciously incomplete external snapshot must not wipe valid canonical data.

Small canonical snapshot applies are atomic after full validation.

Large future datasets may use staging + publish/activate semantics.


---

## ADR-078 — Static assets and content media are separate systems

**Status:** accepted

Use Django/Vite staticfiles only for release-owned brand/UI assets.

Sourced historical media and generated editorial illustrations are content media stored through Django's media Storage API.

Do not put a growing country/year media library into Git.

---

## ADR-079 — Core country/year selection never triggers image generation

**Status:** accepted

Changing a country, currency or historical date reads already-published media or uses a programmatic fallback.

It does not call an image-generation API.

Reasons:

- latency;
- variable cost;
- nondeterminism;
- provider failure;
- historical hallucination;
- offline/recruiter-demo stability.

---

## ADR-080 — Real sourced historical media outranks AI reconstruction

**Status:** accepted

For factual/editorial historical context, selection priority is:

1. relevant real sourced media;
2. broader but honestly dated real media;
3. approved AI editorial illustration;
4. programmatic Quiet Atlas fallback.

AI output is never historical evidence.

---

## ADR-081 — Historical AI imagery requires visible authenticity labeling

**Status:** accepted

If generated media could reasonably be mistaken for an archival photograph or factual reconstruction, it must display a visible label such as:

> AI-generated editorial illustration

or:

> Artistic reconstruction · not an archival photograph

Alt text alone is insufficient.

---

## ADR-082 — Published media is stored and versioned, never regenerated on page load

**Status:** accepted

Approved generated/sourced media is stored as an immutable/versioned asset.

Store:

- provenance;
- content hash;
- source/provider metadata;
- generation prompt/model metadata where applicable.

A model upgrade does not silently alter existing pages.

---

## ADR-083 — Media bytes live outside PostgreSQL

**Status:** accepted

PostgreSQL stores MediaAsset metadata and storage key.

File/object storage stores image bytes and derivatives.

Development can use FileSystemStorage.

Production can use S3-compatible storage through Django's Storage API.

---

## ADR-084 — AI image providers sit behind a server-side adapter

**Status:** accepted

Potential providers include OpenAI, Stability AI and Google image-generation services.

No provider is permanently selected before an actual Quiet Atlas benchmark and current pricing/terms review.

Browser/mobile never receive provider API keys or call image-generation providers directly.

---

## ADR-085 — Media search APIs are ingestion tools, not user-request dependencies

**Status:** accepted

Wikimedia Commons and Europeana are queried during editorial/import workflows.

Normal page requests use only local published media metadata/storage.

Do not display “first search result” directly from an archive API.

---

## ADR-086 — Future on-demand AI generation is an explicit async feature

**Status:** accepted for future scope

If users later request custom artistic country/year imagery, generation is a separate explicit action.

It requires:

- asynchronous job state;
- idempotency;
- quota;
- caching;
- spend control;
- moderation.

This would be a real justification for introducing task-queue infrastructure.

It is not part of core conversion.


---

## ADR-087 — Gemini free tier is the initial live AI provider

**Status:** accepted (revised for portfolio economics)

Use Google Gemini Developer API Free Tier as the initial live runtime provider.

Selected live model:

```text
gemini-3.1-flash-lite
```

Reasons:

- current free-tier input/output pricing is $0;
- Structured Outputs are supported;
- task is intentionally bounded and grounded;
- quota exhaustion can fall back deterministically;
- no billing-dependent runtime AI is needed for a portfolio demo.

OpenAI/Anthropic/paid Gemini remain optional development benchmarks only.

---

## ADR-088 — AI synthesizes sourced data; it does not establish truth

**Status:** accepted

AI may rewrite/summarize/illustrate verified product data.

AI may not:

- generate FX rates;
- decide historical observations;
- create unsourced historical facts;
- determine source truth/licensing;
- become the sole source of published factual claims.

---

## ADR-089 — AI is optional and never a core readiness dependency

**Status:** accepted

Core product must work when AI is disabled/unavailable.

AI provider status is not part of /health/ready/.

Fallbacks are deterministic/manual/stored content.

---

## ADR-090 — AI interfaces are capability-specific

**Status:** accepted

Do not expose a generic `llm.generate(prompt) -> str` abstraction to application/domain code.

Use typed interfaces such as:

- NarrativeDrafter;
- AltTextDrafter;
- ImagePromptComposer;
- ImageGenerator;
- ContentModerator;
- QualityAuditor.

This preserves semantics and prevents untyped prompt sprawl.

---

## ADR-091 — Gemini structured JSON output is the text integration path

**Status:** accepted (revised for zero-cost runtime)

Live application output uses Gemini schema-constrained structured JSON.

Plain free-form output is allowed only for explicitly non-integrated editorial/manual workflows.

Schema validity is necessary but not sufficient; semantic validators still run.

---

## ADR-092 — Public demo uses one free live model and no runtime image model

**Status:** accepted (revised for portfolio economics)

Initial production configuration:

- Gemini 3.1 Flash-Lite → live structured explanation;
- no paid text fallback;
- no runtime image-generation model;
- deterministic/cached fallback for live explanation.

One model is easier to evaluate, operate and keep free.

---

## ADR-093 — No autonomous agent/tool loop in P0/P1

**Status:** accepted

Initial AI calls have no:

- web-search tool;
- database tool;
- shell;
- arbitrary URL fetch;
- publish/write tool.

Application code prepares complete source packets and invokes one bounded generation.

This keeps provenance, side effects and costs explicit.

---

## ADR-094 — Model knowledge is not evidence

**Status:** accepted

A model may not add historical/cultural facts simply because they are in its pretrained knowledge.

Factual output must be supportable by supplied fact/source IDs.

Unknown fact IDs invalidate a candidate.

---

## ADR-095 — Prompts and schemas are versioned production code

**Status:** accepted

Every production AI capability has:

- prompt version;
- schema version;
- eval set;
- promotion history.

Prompt/model changes require representative evals before production promotion.

---

## ADR-096 — Published AI-derived content is review-gated initially

**Status:** accepted

Historical story prose, cultural prose, historical illustration and editorial image metadata generated by AI require review before publication.

Only low-risk internal classifications may later become auto-accepted after measured eval history.

---

## ADR-097 — AI calls happen outside DB transactions

**Status:** accepted

Build input and call AI before opening any durable write transaction.

Persist candidates only after generation/validation.

Never hold PostgreSQL locks while waiting for model output.

---

## ADR-098 — AI normal CI uses fakes, not live provider calls

**Status:** accepted

Normal CI:

- adapter fixtures;
- prompt/schema validation;
- stored eval outputs;
- deterministic validators.

Live provider evals are explicit/manual/scheduled/model-upgrade workflows.

This prevents cost/flakiness/outage coupling.

---

## ADR-099 — AI model upgrades are eval-gated

**Status:** accepted

A model alias/snapshot change must be evaluated for:

- unsupported claims;
- temporal precision;
- schema/refusal behavior;
- style;
- latency;
- cost.

A higher benchmark score or newer version is not enough.

---

## ADR-100 — No vector database/RAG initially

**Status:** accepted

Current factual retrieval is precise through PostgreSQL country/currency/date/source relationships.

Do not add embeddings/vector infrastructure until there is a genuine semantic-search problem over a large unstructured corpus.

---

## ADR-101 — No AI orchestration framework initially

**Status:** accepted

Use direct provider SDK behind typed adapters.

LangChain/LlamaIndex/agent frameworks are not justified by a handful of bounded calls.

Reconsider only when repeated orchestration complexity exceeds direct code.

---

## ADR-102 — AI privacy follows minimum-necessary payload

**Status:** accepted

P0/P1 editorial AI uses public/curated product data only.

Do not send user identity, precise location, private trip notes or account history.

Future personalized AI requires separate privacy/security decision.

---

## ADR-103 — AI runtime target is €0/month

**Status:** accepted (revised for portfolio economics)

The default public demo configuration uses only free-tier live text and zero runtime image generation.

When free quota/application quota is reached:

```text
cached result
→ deterministic fallback
```

There is no automatic paid overflow.

---

## ADR-104 — Provider fallback is explicit, not automatic multi-vendor retry

**Status:** accepted

Do not automatically send failed prompts to Google/Anthropic unless that provider/capability has been separately benchmarked and approved.

A second provider is added only for demonstrated resilience/quality/regulatory/economic value.
