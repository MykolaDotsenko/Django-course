# Engineering Handbook Index

This handbook is the single source of truth for the Cultural Currency Converter rebuild.

## Documents

1. [Product specification](01_PRODUCT_SPEC.md)
2. [UX research and experience blueprint](02_UX_RESEARCH_AND_FLOWS.md)
   - [User case catalog](02A_USER_CASE_CATALOG.md)
   - [Interaction and state specification](02B_INTERACTION_AND_STATE_SPEC.md)
   - [Storytelling and historical converter](02C_STORYTELLING_AND_HISTORICAL_CONVERTER.md)
3. [UI design system](03_UI_DESIGN_SYSTEM.md)
4. [Architecture](04_ARCHITECTURE.md)
5. [Domain model](05_DOMAIN_MODEL.md)
6. [Mobile and API](06_MOBILE_AND_API.md)
7. [Quality, security and accessibility](07_QUALITY_SECURITY_ACCESSIBILITY.md)
8. [Implementation roadmap](08_IMPLEMENTATION_ROADMAP.md)
9. [Architecture decision log](09_ADR_LOG.md)
10. [Official references](10_REFERENCES.md)
11. [API research and data-source strategy](11_API_RESEARCH_AND_DATA_SOURCES.md)
12. [External API integration contracts](12_EXTERNAL_API_CONTRACTS.md)

## UX decision hierarchy

Before an implementation PR changes the user experience, read in this order:

1. `01_PRODUCT_SPEC.md` — why the product exists and what is in scope;
2. `02_UX_RESEARCH_AND_FLOWS.md` — experience principles and end-to-end behaviour;
3. `02A_USER_CASE_CATALOG.md` — concrete scenarios the product must support;
4. `02B_INTERACTION_AND_STATE_SPEC.md` — state transitions and recovery rules;
5. `02C_STORYTELLING_AND_HISTORICAL_CONVERTER.md` — historical FX, money stories and temporal trust rules;
6. `03_UI_DESIGN_SYSTEM.md` — visual/component implementation constraints.

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
