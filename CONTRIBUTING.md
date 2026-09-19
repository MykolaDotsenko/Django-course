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

Local development works without committed secrets. The default execution context is `local`.

To make configuration explicit, copy the tracked template and export it through your shell or IDE:

```bash
cp .env.example .env
set -a
. ./.env
set +a
```

Django does not silently parse arbitrary `.env` files; deployment configuration always enters through the process environment. A local `DJANGO_SECRET_KEY` is optional, while preview/production require an explicit strong key and allowed hosts.

### Database

Local/test use SQLite when `DATABASE_URL` is empty. Preview/production require PostgreSQL, and CI runs the full test suite against PostgreSQL 18.6.

To run the same PostgreSQL baseline locally:

```bash
docker run --rm --name quiet-atlas-postgres \
  -e POSTGRES_DB=cultural_currency \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  postgres:18.6-alpine

export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5432/cultural_currency
python manage.py migrate
pytest -q
```

The database settings keep Django autocommit enabled and explicitly disable global `ATOMIC_REQUESTS`. External network calls must never be placed inside intentional write transactions.

Optional local commit hooks:

```bash
pre-commit install
```

## Quality checks

Run the same core checks used by CI:

```bash
ruff format --check apps config scripts manage.py
ruff check apps config scripts manage.py
python manage.py check
python manage.py makemigrations --check --dry-run
coverage erase
coverage run -m pytest -q
coverage report
python -m pip_audit --skip-editable
```

For intentional local formatting/fixes:

```bash
ruff check --fix apps config scripts manage.py
ruff format apps config scripts manage.py
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
