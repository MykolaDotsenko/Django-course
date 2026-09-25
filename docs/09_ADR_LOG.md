# Decision Log

This file records durable decisions that help future developers understand *why* the current architecture looks the way it does.

A decision is not permanent. Each entry includes a reason to revisit it.

## ADR-001 — Django server-rendered web

**Status:** active

The web product currently uses Django templates with HTMX and focused TypeScript enhancements.

**Why:** the product is form/content heavy, benefits from server ownership and does not require SPA-wide client state.

**Revisit when:** a concrete user flow is materially simpler or better with a larger client application.

## ADR-002 — Modular monolith

**Status:** active

Business capabilities live in Django apps inside one deployable application.

**Why:** current scale does not justify distributed-system overhead.

**Revisit when:** independent scaling/deployment/ownership becomes a measured requirement.

## ADR-003 — Decimal and explicit financial semantics

**Status:** active

Money/rate calculations use Decimal semantics and preserve source/date meaning.

**Why:** binary floating point and implicit date semantics can produce misleading financial results.

**Revisit when:** only if an alternative preserves or improves correctness and explainability.

## ADR-004 — Country and currency are separate temporal concepts

**Status:** active

Country/currency relationships are modelled explicitly with time scope.

**Why:** currencies can be shared and can change over history.

**Revisit when:** domain requirements demonstrate a better equivalent model without losing temporal meaning.

## ADR-005 — External providers stay behind adapters

**Status:** active

Provider payloads are normalized before application/domain use.

**Why:** this limits vendor coupling and centralizes validation/failure semantics.

**Revisit when:** a provider becomes a durable first-party domain source whose schema is intentionally adopted.

## ADR-006 — PostgreSQL as production durable store

**Status:** active

Production-oriented persistence targets PostgreSQL; SQLite remains useful locally.

**Why:** PostgreSQL supports the constraints/concurrency behaviour expected for user-owned state.

**Revisit when:** deployment constraints or scale justify another durable store.

## ADR-007 — Progressive enhancement and accessibility

**Status:** active

Core web tasks are server-rendered and usable with minimal client behaviour; accessibility is considered in normal implementation/QA.

**Why:** resilience, simpler ownership and broader usability.

**Revisit when:** individual enhancements can improve UX without losing these properties.

## ADR-008 — AI is enrichment, not truth

**Status:** active

AI may synthesize trusted facts into bounded explanatory output. It does not establish FX rates, historical observations or published factual provenance.

**Why:** factual/financial correctness needs deterministic and attributable sources.

**Revisit when:** never based solely on model capability; only if the product can preserve equivalent trust/provenance guarantees.

## ADR-009 — Media authenticity over spectacle

**Status:** active

Use curated managed photography for premium destination imagery and authentic sourced archival media for historical evidence. Country hero/teaser surfaces do not fall back to cartoon or decorative illustrations; if suitable photography is unavailable, the layout remains image-free.

**Why:** weak or synthetic-looking imagery lowers trust and perceived product quality, while historical imagery can easily imply false authenticity.

**Revisit when:** a new visual medium can match the same premium, provenance and authenticity bar.

## ADR-010 — Current context is not automatically historical

**Status:** active

Historical conversion does not backdate current prices/payment customs.

**Why:** temporal truth matters more than filling a contextual card.

**Revisit when:** explicit historical context datasets exist.

## ADR-011 — Account recent history is opt-in

**Status:** active

Signing in does not silently upload browser-local recent history. Cross-device recording starts only after explicit opt-in.

**Why:** recent conversion history can reveal travel/financial context and deserves a clear privacy boundary.

**Revisit when:** only with an equally explicit consent/privacy model.

## ADR-012 — Future mobile technology is selected at implementation time

**Status:** active

React Native/Expo is a current candidate, not a permanently pinned roadmap commitment.

**Why:** mobile ecosystem versions and best practices change faster than the product roadmap.

**Revisit when:** mobile work becomes active; benchmark the then-current stable options.

## ADR-013 — Shared cache for deployed coordination

**Status:** active

Preview and production use a shared Redis-compatible Django cache; local/test execution can remain process-local unless a Redis URL is explicitly supplied.

**Why:** FX freshness/stale entries and short-lived AI cooldown/duplicate-generation locks must have coherent meaning across multiple application instances. Redis is used as an optimization/coordination layer, not a financial truth source, so cache failures fail open to provider access or deterministic fallback instead of corrupting domain semantics.

**Revisit when:** measured scale, hosting constraints or reliability evidence justify a different shared cache with equivalent cross-instance atomic add/TTL behaviour and failure semantics.

## ADR-014 — CSP is enforced on the public web surface with an explicit rollout mode

**Status:** active

The public application uses a same-origin Content Security Policy that blocks inline/eval script execution, embedded objects and framing. Test runs enforce the policy. Preview and production must explicitly choose report-only or enforcement mode. Django admin receives a separate compatibility policy rather than weakening public pages.

**Why:** CSP is most valuable when it is an executable browser boundary, but deploying a strict policy without compatibility evidence can break HTMX/Vite or framework-owned admin templates. Separating the public and admin policies preserves a stronger default while keeping rollout observable and reversible.

Violation reporting is bounded and privacy-minimized: raw document URLs/query strings are not persisted or logged.

**Revisit when:** Django admin no longer needs inline compatibility, Trusted Types becomes practical for the current browser/runtime surface, or deployment telemetry justifies tightening/removing a directive.

## Adding/changing a decision

Create or update an ADR when a change affects a durable project-wide choice.

Do not use ADRs for routine refactors, one-off UI details or dependency patch versions.

When replacing a decision, explain:

- what changed;
- why the previous reasoning no longer wins;
- what new evidence/requirement justifies the change.
