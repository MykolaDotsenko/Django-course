# Engineering Handbook Index

This handbook is the single source of truth for the Cultural Currency Converter rebuild.

## Documents

1. [Product specification](01_PRODUCT_SPEC.md)
2. [UX research and user flows](02_UX_RESEARCH_AND_FLOWS.md)
3. [UI design system](03_UI_DESIGN_SYSTEM.md)
4. [Architecture](04_ARCHITECTURE.md)
5. [Domain model](05_DOMAIN_MODEL.md)
6. [Mobile and API](06_MOBILE_AND_API.md)
7. [Quality, security and accessibility](07_QUALITY_SECURITY_ACCESSIBILITY.md)
8. [Implementation roadmap](08_IMPLEMENTATION_ROADMAP.md)
9. [Architecture decision log](09_ADR_LOG.md)
10. [Official references](10_REFERENCES.md)

## Working agreement

Every non-trivial implementation PR should answer:

- What user problem does this solve?
- Which acceptance criteria does it satisfy?
- Which domain invariant can it affect?
- Does it change security, privacy, accessibility or data provenance?
- Which handbook section governs the decision?
- Are new abstractions justified by an actual boundary or regression risk?
- Does the change preserve web/mobile API compatibility where relevant?

If a PR changes an architectural decision, update the ADR log in the same PR.

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
