# Contributing

The repository is optimized for small, evidence-driven changes and AI-assisted development.

Start with:

- [docs/00_INDEX.md](docs/00_INDEX.md)
- [docs/AI_DEVELOPMENT_GUIDE.md](docs/AI_DEVELOPMENT_GUIDE.md)

Then read only the canonical document(s) relevant to the task.

## Before coding

1. Understand the user/problem outcome.
2. Inspect the current implementation and nearby tests.
3. Check relevant docs for product intent/invariants.
4. Choose the smallest coherent change.
5. If an old documented approach is now worse, improve it and update the relevant doc.

Do not preserve accidental complexity merely because it is documented.

## Python setup

```bash
python -m pip install -e ".[dev]"
python manage.py migrate
```

Optional reference/demo data:

```bash
python manage.py seed_reference_data
python manage.py seed_story_data
python manage.py seed_destination_context
```

## Frontend setup

```bash
cd frontend
npm ci
npm run dev
```

## Quality checks

Python/Django:

```bash
ruff format --check apps config scripts manage.py
ruff check apps config scripts manage.py
djlint templates --check
python manage.py check
python manage.py makemigrations --check --dry-run
coverage run -m pytest -q
coverage report
```

Frontend:

```bash
cd frontend
npm run quality
```

Use browser QA when the change affects important interactions, accessibility, reflow or frontend runtime behaviour.

## Pull requests

Keep a PR coherent rather than artificially tiny.

A useful PR explains:

- the problem/outcome;
- the main implementation choice;
- meaningful risks or trade-offs;
- test evidence;
- any migration/config impact;
- documentation updates when product/architecture meaning changed.

Screenshots are useful for visible UI changes but are not a substitute for interaction/accessibility checks.

## Architecture changes

For a durable project-wide architectural decision, update:

- `docs/04_ARCHITECTURE.md`;
- `docs/09_ADR_LOG.md` when the reasoning should survive future refactors.

Routine implementation detail does not need an ADR.

## External services / AI / media

Read [docs/INTEGRATIONS_AI_MEDIA.md](docs/INTEGRATIONS_AI_MEDIA.md).

Prefer provider isolation, local normalization, graceful failure and deterministic tests.

## Documentation

Prefer editing an existing canonical document over creating a new one.

Delete stale guidance rather than leaving multiple “current” versions.

Documentation should explain stable meaning and reasoning; exact dependency versions and implementation details belong in config/code when possible.
