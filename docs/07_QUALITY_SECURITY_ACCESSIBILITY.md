# Engineering Quality, Security and Accessibility

This document describes the practical quality baseline. CI/config files are the executable source for exact versions, thresholds and commands.

## Development principle

Use the smallest set of checks that gives confidence for the change, then run broader checks before merging when risk warrants it.

Do not add process for its own sake.

## Python/Django checks

The current CI runs checks equivalent to:

```bash
ruff format --check apps config scripts manage.py
ruff check apps config scripts manage.py
djlint templates --check
python manage.py check
python manage.py makemigrations --check --dry-run
coverage run -m pytest -q
coverage report
python -m pip_audit --skip-editable
```

The coverage threshold is configured in `pyproject.toml`; treat that file as authoritative.

PostgreSQL also has a dedicated CI job because SQLite alone cannot validate all persistence/concurrency behaviour.

## Frontend checks

```bash
cd frontend
npm ci
npm run typecheck
npm run check
npm run build
```

Browser QA uses Playwright and axe. Chromium carries the broadest gate; Firefox/WebKit provide smoke coverage.

Use browser tests for high-value interaction behaviour, not every CSS detail.

## Testing priorities

Prefer tests that protect:

- financial/domain semantics;
- historical date semantics;
- ownership/privacy boundaries;
- external-provider normalization and failure handling;
- important form/HTMX flows;
- accessibility behaviour;
- migrations/constraints where data can be corrupted;
- regressions that have actually occurred.

Avoid duplicating the implementation structure in tests when no user/domain risk is protected.

## Security baseline

Keep:

- secrets server-side and out of version control;
- CSRF protection on state-changing browser requests;
- secure cookie/settings behaviour in production;
- strict host/config validation;
- sanitized external URLs/media;
- redaction for credential-bearing logs;
- dependency audits.

Do not weaken Django defaults without a concrete reason and test.

## Privacy and ownership

User-owned database rows should be queried/mutated through the authenticated owner boundary.

Cross-device recent history is opt-in. Disabling future recording should not unexpectedly delete existing history unless the user explicitly chooses deletion.

Anonymous browser state should be described as local browser storage, not account sync.

## Accessibility baseline

Target WCAG 2.2 AA behaviour for the product experience.

Important practical checks include:

- keyboard-only operation;
- visible focus;
- correct labels/descriptions/errors;
- sensible heading/landmark structure;
- no colour-only meaning;
- reflow/zoom resilience;
- reduced-motion support;
- meaningful live announcements without duplicate noise;
- usable touch targets.

Automated axe checks are useful but do not replace interaction testing.

## Configuration

Runtime configuration is validated in `config/environment.py`, `config/database.py` and `config/ai.py`.

Use `.env.example` as the practical inventory of supported environment variables.

Avoid duplicating exact default values in documentation when the code is clearer and already tested.

## Database changes

For schema/data changes:

1. make the smallest migration that preserves data;
2. use constraints when an invariant belongs in the database;
3. test risky backfills/destructive changes;
4. prefer additive/expand-first changes when rollback compatibility matters;
5. do not hide destructive operations inside unrelated migrations.

For imports/seeds, favour idempotent behaviour and explicit provenance.

## Release/rollback thinking

Before a release, consider:

- migrations;
- configuration/secrets;
- static build;
- provider dependencies;
- smoke paths;
- rollback/roll-forward options.

Prefer roll-forward for simple defects once migrations/data are already in use. Do not assume database rollback is safe.

## Performance

Performance work should be evidence-driven.

Watch:

- avoidable provider calls;
- N+1 ORM patterns;
- oversized frontend bundles;
- unnecessary eager chart/media code;
- large images;
- slow request-path enrichment.

Use profiling/measurements before introducing caches or infrastructure.

## Documentation quality

A change should update documentation when it changes stable product meaning, architecture ownership or an external contract.

Do not require documentation edits for every refactor.

## Merge confidence

Pull requests have an always-present `Required merge quality` status. It classifies changed paths, runs the applicable Python/PostgreSQL/frontend/Chromium lanes and fails unless every applicable lane succeeds. This status is designed to be the single required branch-protection check so documentation-only pull requests still receive a deterministic merge result instead of waiting on path-filtered workflows that never start.

The broader Python 3.14 and Firefox/WebKit workflows remain valuable compatibility evidence in addition to that minimum protected merge gate.

A change is generally ready when:

- the user/problem outcome is satisfied;
- relevant tests pass;
- failure/security/privacy/accessibility risks are covered proportionally;
- migrations/config changes are explicit;
- docs remain aligned where the project meaning changed.
