# Contributing

This repository is a production-minded portfolio rebuild of **Cultural Currency Converter**.

The engineering handbook is the source of truth:

- [docs/00_INDEX.md](docs/00_INDEX.md)

Before implementing a non-trivial change, identify the governing product/UX/architecture document and the acceptance criteria being implemented.

## Python setup

The Django product shell lives at the repository root.

Python support is intentionally bounded to the versions exercised in CI:

- Python 3.13
- Python 3.14

Install the application and development toolchain from the single project metadata source:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Optional local commit hooks:

```bash
pre-commit install
```

## Quality checks

Run the same core checks used by CI:

```bash
ruff format --check .
ruff check .
python manage.py check
coverage erase
coverage run -m pytest -q
coverage report
python -m pip_audit --skip-editable
```

For intentional local formatting/fixes:

```bash
ruff check --fix .
ruff format .
```

Ruff is the repository's Python formatter and linter. Do not reintroduce Black or isort unless a concrete unsupported requirement appears.

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
