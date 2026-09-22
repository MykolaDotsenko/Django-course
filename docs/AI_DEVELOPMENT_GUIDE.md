# AI-Assisted Development Guide

This project is developed with heavy AI assistance. The goal is not to make the documentation more restrictive; it is to give AI enough high-quality context to make good engineering decisions and improve the product safely.

## Core principle

Treat documentation as **maintained intent**, not immutable law.

Before preserving an existing pattern, ask whether it still serves the product. If a better architecture, UX or implementation is justified by evidence, improve the implementation and update the relevant canonical document.

## Context package for a task

For a normal task, an AI should read only what is relevant:

1. `README.md`;
2. `docs/00_INDEX.md`;
3. this guide;
4. one or two domain-specific canonical documents;
5. the current implementation and nearby tests.

Do not load the whole documentation set by default. A smaller, relevant context window usually produces better decisions.

## Workflow

### 1. Understand the user outcome

Describe the user/problem outcome in one or two sentences.

Avoid starting from a preferred implementation.

### 2. Inspect the current implementation

Read:

- relevant views/forms/services/models;
- templates and frontend code for UI work;
- migrations/schema for persisted behaviour;
- tests and CI around the affected area.

Code and tests reveal current behaviour more reliably than an old planning paragraph.

### 3. Check the relevant documentation

Use documentation to understand:

- product intent;
- important constraints;
- architecture boundaries;
- why a non-obvious decision exists.

If the document is stale, do not work around it. Correct it.

### 4. Design the smallest coherent improvement

Prefer a change that:

- solves the real problem;
- has a clear ownership boundary;
- removes duplication rather than adding another layer;
- keeps failure behaviour explicit;
- remains testable.

Do not add abstractions, dependencies, new documentation files or infrastructure merely because they are considered “best practice” in isolation.

### 5. Challenge existing choices

It is acceptable to replace a documented approach when:

- requirements changed;
- the old approach creates UX or maintenance problems;
- a simpler solution now exists;
- measured evidence contradicts the old assumption;
- the project has outgrown a temporary choice.

When doing so, update the affected canonical document and, for a durable architectural decision, the ADR log.

### 6. Implement with tests

Tests should protect meaningful behaviour and regression risks.

Prefer testing:

- financial/domain semantics;
- ownership/privacy boundaries;
- provider normalization/failure behaviour;
- important user flows;
- accessibility behaviour;
- previously observed regressions.

Avoid tests that only mirror implementation structure without protecting behaviour.

### 7. Verify

Run the smallest relevant quality set first, then broader checks when the change warrants it.

Use the commands in `07_QUALITY_SECURITY_ACCESSIBILITY.md` and the CI workflows as the current executable reference.

### 8. Update documentation proportionally

Update docs when the change affects:

- product behaviour;
- user flow;
- a domain invariant;
- architecture ownership;
- an external integration;
- a durable engineering decision;
- the active roadmap.

Do not update docs for mechanical refactors that do not change those things.

## How to interpret wording

- **Invariant / safety requirement:** treat as strong unless the underlying requirement itself changes.
- **Current architecture:** describes the implementation now; it can evolve.
- **Preference/default:** follow it unless a better option is justified.
- **Roadmap:** direction, not a contract.
- **Historical note:** context only.

## Documentation anti-patterns

Avoid reintroducing:

- separate documents for each PR or milestone;
- giant user-case/scenario catalogs that repeat tests;
- exact technology matrices years before implementation;
- duplicated UX rules in product, design and architecture docs;
- “locked”, “final”, “never change” wording for normal engineering choices;
- long rejected-technology lists;
- instructions that force AI to consult ten documents before editing one component.

## Definition of a good AI-assisted change

A strong change leaves the project easier to understand than before:

- one clear implementation path;
- fewer duplicated concepts;
- tests covering the real risk;
- documentation still aligned with code;
- no unnecessary new framework or abstraction;
- explicit reasoning where trade-offs were meaningful.
