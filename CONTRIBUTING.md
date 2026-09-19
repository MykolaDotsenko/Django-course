# Contributing

This repository is a production-minded portfolio rebuild of **Cultural Currency Converter**.

The engineering handbook is the source of truth:

- [docs/00_INDEX.md](docs/00_INDEX.md)

Before implementing a non-trivial change, identify the governing product/UX/architecture document and the acceptance criteria being implemented.

## Current implementation setup

The Django product shell lives at the repository root.

Validated checks currently mirror CI:

```bash
python -m pip install \
  "Django>=5.2.1,<6.0.0" \
  "pytest==8.3.5" \
  "pytest-django==4.11.1" \
  "ruff==0.11.10"

python manage.py check
ruff check apps/common
pytest -q
```

Dependency consolidation, environment-driven settings, PostgreSQL integration and runtime observability are intentionally delivered in the next bounded foundation PRs rather than hidden inside this structural migration.

## Before coding

Read:

1. [Developer workflow and PR contract](docs/30_DEVELOPER_WORKFLOW_AND_PR_CONTRACT.md)
2. [Test strategy and traceability](docs/31_TEST_STRATEGY_AND_TRACEABILITY.md)
3. the domain/UX/backend/frontend documents relevant to the change.

## Pull requests

Keep PRs bounded.

Every non-trivial PR should explain:

- problem;
- scope / out of scope;
- handbook references;
- scenario IDs where applicable;
- acceptance criteria;
- tests;
- migration/config implications;
- security/privacy/accessibility implications;
- screenshots for meaningful UI changes.

Use the repository PR template.

## Architecture changes

If a durable architecture decision changes, update [docs/09_ADR_LOG.md](docs/09_ADR_LOG.md) in the same PR.

## External services

Normal CI must not depend on live third-party APIs.

Provider integration tests use deterministic fixtures/fakes.

Live smoke/eval flows are separate and explicit.

## Product rule

Do not optimize decorative novelty over correctness, trust, accessibility or the primary conversion task.
