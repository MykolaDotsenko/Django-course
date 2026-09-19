# Engineering Handbook Index

This handbook is the single source of truth for the Cultural Currency Converter rebuild.

## Documents

1. [Product specification](01_PRODUCT_SPEC.md)
2. [UX research and experience blueprint](02_UX_RESEARCH_AND_FLOWS.md)
   - [User case catalog](02A_USER_CASE_CATALOG.md)
   - [Interaction and state specification](02B_INTERACTION_AND_STATE_SPEC.md)
   - [Storytelling and historical converter](02C_STORYTELLING_AND_HISTORICAL_CONVERTER.md)
3. [UI design system](03_UI_DESIGN_SYSTEM.md)
   - [Visual foundations](03A_VISUAL_FOUNDATIONS.md)
   - [Screen-by-screen blueprints](03B_SCREEN_BLUEPRINTS.md)
   - [Component anatomy and dimensions](03C1_COMPONENT_ANATOMY_AND_DIMENSIONS.md)
   - [Component states and microinteractions](03C_COMPONENT_STATES_AND_MICROINTERACTIONS.md)
   - [Responsive, motion, accessibility and design QA](03D_RESPONSIVE_MOTION_ACCESSIBILITY.md)
4. [Architecture](04_ARCHITECTURE.md)
5. [Domain model](05_DOMAIN_MODEL.md)
6. [Mobile and API](06_MOBILE_AND_API.md)
7. [Quality, security and accessibility](07_QUALITY_SECURITY_ACCESSIBILITY.md)
8. [Implementation roadmap](08_IMPLEMENTATION_ROADMAP.md)
9. [Architecture decision log](09_ADR_LOG.md)
10. [Official references](10_REFERENCES.md)
11. [API research and data-source strategy](11_API_RESEARCH_AND_DATA_SOURCES.md)
12. [External API integration contracts](12_EXTERNAL_API_CONTRACTS.md)
13. [Frontend technology strategy](13_FRONTEND_TECHNOLOGY_STRATEGY.md)
14. [Web frontend architecture](14_WEB_FRONTEND_ARCHITECTURE.md)
15. [Mobile frontend architecture](15_MOBILE_FRONTEND_ARCHITECTURE.md)
16. [Backend system design](16_BACKEND_SYSTEM_DESIGN.md)
17. [Information flow and request lifecycles](17_INFORMATION_FLOW_AND_REQUEST_LIFECYCLES.md)
18. [Application services and domain orchestration](18_APPLICATION_SERVICES_AND_DOMAIN_ORCHESTRATION.md)
19. [Data consistency, caching and concurrency](19_DATA_CONSISTENCY_CACHING_AND_CONCURRENCY.md)
20. [API, security, observability and operations](20_API_SECURITY_OBSERVABILITY_AND_OPERATIONS.md)
21. [Backend scenario catalog](21_BACKEND_SCENARIO_CATALOG.md)
22. [Data import, scheduled jobs and maintenance](22_DATA_IMPORT_JOBS_AND_MAINTENANCE.md)
23. [Media, historical imagery and generative image strategy](23_MEDIA_AND_GENERATIVE_IMAGE_STRATEGY.md)
24. [AI product strategy and model selection](24_AI_PRODUCT_STRATEGY.md)
25. [AI integration architecture](25_AI_INTEGRATION_ARCHITECTURE.md)
26. [AI prompting, evaluations, safety and cost](26_AI_PROMPTS_EVALS_SAFETY_AND_COST.md)
27. [Static image generation plan](27_STATIC_IMAGE_GENERATION_PLAN.md)

## UX decision hierarchy

Before an implementation PR changes the user experience, read in this order:

1. `01_PRODUCT_SPEC.md` — why the product exists and what is in scope;
2. `02_UX_RESEARCH_AND_FLOWS.md` — experience principles and end-to-end behaviour;
3. `02A_USER_CASE_CATALOG.md` — concrete scenarios the product must support;
4. `02B_INTERACTION_AND_STATE_SPEC.md` — state transitions and recovery rules;
5. `02C_STORYTELLING_AND_HISTORICAL_CONVERTER.md` — historical FX, money stories and temporal trust rules;
6. `03_UI_DESIGN_SYSTEM.md` — executive visual/component contract;
7. `03A_VISUAL_FOUNDATIONS.md` — tokens, hierarchy, typography, color, grid and visual language;
8. `03B_SCREEN_BLUEPRINTS.md` — screen composition and information density;
9. `03C1_COMPONENT_ANATOMY_AND_DIMENSIONS.md` — exact component anatomy, sizing and hierarchy;
10. `03C_COMPONENT_STATES_AND_MICROINTERACTIONS.md` — component state behavior;
11. `03D_RESPONSIVE_MOTION_ACCESSIBILITY.md` — adaptive/accessibility/motion QA.

A visually attractive implementation that violates the UX state model is not considered correct.

## Working agreement

Every non-trivial implementation PR should answer:

- What user problem does this solve?
- Which user-case IDs does it implement or change?
- Which UX state transitions does it affect?
- Which acceptance criteria does it satisfy?
- Which domain invariant can it affect?
- Does it change security, privacy, accessibility or data provenance?
- Which handbook section governs the decision?
- Are new abstractions justified by an actual boundary or regression risk?
- Does the change preserve web/mobile API compatibility where relevant?

If a PR changes an architectural decision, update the ADR log in the same PR.

If a PR changes a settled UX rule, update the relevant UX document and explain why.

## Product hierarchy

When trade-offs conflict, optimize in this order:

1. correctness and trust;
2. primary conversion task;
3. accessibility and recoverability;
4. clarity and maintainability;
5. performance;
6. cultural delight;
7. decorative novelty.

## Scope guardrail

This is **not** a trading platform, remittance product, banking product or real-time market terminal.

The product provides travel-oriented informational estimates. It must never imply:

- guaranteed executable exchange rates;
- regulated financial advice;
- exact merchant/card/ATM fees without authoritative provider data;
- universal prices within a country;
- cultural claims without provenance.

## Evidence rule

The documentation distinguishes:

- **settled product decisions**;
- **implementation choices**;
- **research hypotheses**.

Items marked as research questions should be tested through prototypes/usability work before they are treated as fixed behaviour.


## External data decision hierarchy

Before adding or changing a third-party API, read in this order:

1. `11_API_RESEARCH_AND_DATA_SOURCES.md` — whether the source belongs in the product at all;
2. `12_EXTERNAL_API_CONTRACTS.md` — how it is isolated, normalized, cached and tested;
3. `04_ARCHITECTURE.md` — where the adapter belongs and whether it may be request-path critical;
4. `05_DOMAIN_MODEL.md` — which normalized domain concept receives the data;
5. `07_QUALITY_SECURITY_ACCESSIBILITY.md` — outage, security and testing expectations;
6. `09_ADR_LOG.md` — durable provider/source decisions.

A new API is not accepted merely because it provides convenient JSON.


## Frontend decision hierarchy

Before adding/changing a web or mobile frontend dependency, read:

1. `13_FRONTEND_TECHNOLOGY_STRATEGY.md` — selected/rejected technologies and why;
2. `14_WEB_FRONTEND_ARCHITECTURE.md` — Django/HTMX/Vite/TypeScript ownership and implementation rules;
3. `15_MOBILE_FRONTEND_ARCHITECTURE.md` — Expo/React Native/API/offline state ownership;
4. `03_UI_DESIGN_SYSTEM.md` and detailed Quiet Atlas docs — required visual/interaction behavior;
5. `02B_INTERACTION_AND_STATE_SPEC.md` — state integrity and recovery rules;
6. `09_ADR_LOG.md` — durable frontend architecture decisions.

A frontend dependency is not accepted because it is popular, modern, or visually impressive.

It must solve a documented problem with lower total complexity than the native/platform/project-owned alternative.


## Backend decision hierarchy

Before implementing or changing backend behavior, read in this order:

1. 16_BACKEND_SYSTEM_DESIGN.md — system boundaries, synchronous Django strategy, transactions, data ownership and deployment shape;
2. 17_INFORMATION_FLOW_AND_REQUEST_LIFECYCLES.md — exact end-to-end information flow for current/historical conversion, context, mobile and imports;
3. 18_APPLICATION_SERVICES_AND_DOMAIN_ORCHESTRATION.md — use-case boundaries, domain purity and service responsibilities;
4. 19_DATA_CONSISTENCY_CACHING_AND_CONCURRENCY.md — PostgreSQL, cache, transaction, stale-data and concurrency rules;
5. 20_API_SECURITY_OBSERVABILITY_AND_OPERATIONS.md — public contract, auth/security, failures, health and operations;
6. 21_BACKEND_SCENARIO_CATALOG.md — concrete backend cases and regression coverage;
7. 22_DATA_IMPORT_JOBS_AND_MAINTENANCE.md — scheduled/import workflows and source maintenance;
8. 05_DOMAIN_MODEL.md and 12_EXTERNAL_API_CONTRACTS.md — persisted/domain/provider schemas;
9. 09_ADR_LOG.md — durable decisions.

Every backend implementation PR should list the relevant BE-* scenario IDs.

A backend abstraction is accepted only if it protects a real invariant, integration boundary, transaction, repeated query shape or measurable operational need.


## Media decision hierarchy

Before adding a sourced or generated image flow, read:

1. `23_MEDIA_AND_GENERATIVE_IMAGE_STRATEGY.md` — media classes, storage, AI policy, rights/provenance and selection rules;
2. `03_UI_DESIGN_SYSTEM.md` — visual hierarchy and media restraint;
3. `05_DOMAIN_MODEL.md` — MediaAsset metadata/provenance;
4. `22_DATA_IMPORT_JOBS_AND_MAINTENANCE.md` — ingestion/generation jobs;
5. `10_REFERENCES.md` — source/licensing/provider references.

A missing image is an acceptable state.

A misleading historical image is not.


## AI decision hierarchy

Before adding or changing AI behavior, read:

1. `24_AI_PRODUCT_STRATEGY.md` — allowed/rejected use cases and model routing;
2. `25_AI_INTEGRATION_ARCHITECTURE.md` — capability interfaces, provider boundary, structured outputs and persistence;
3. `26_AI_PROMPTS_EVALS_SAFETY_AND_COST.md` — prompt versions, eval gates, safety, privacy and spend controls;
4. `23_MEDIA_AND_GENERATIVE_IMAGE_STRATEGY.md` — image authenticity/storage policy;
5. `17_INFORMATION_FLOW_AND_REQUEST_LIFECYCLES.md` — deterministic source-of-truth flows;
6. `09_ADR_LOG.md` — durable decisions.

AI may transform trusted data into candidates.

AI may not become a new source of financial or historical truth.


## Static image implementation contract

Before adding or replacing release-owned imagery, read:

1. `27_STATIC_IMAGE_GENERATION_PLAN.md` — asset inventory, prompts, mapping, accessibility and authenticity rules;
2. `23_MEDIA_AND_GENERATIVE_IMAGE_STRATEGY.md` — sourced/generated media boundaries;
3. `03_UI_DESIGN_SYSTEM.md` — Quiet Atlas visual hierarchy.

The initial P0 pack lives under `static/images/quiet-atlas/` and is designed to work with zero runtime image-generation cost.
