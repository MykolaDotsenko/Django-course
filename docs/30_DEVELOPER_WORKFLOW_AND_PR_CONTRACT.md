# Developer Workflow and Pull Request Contract

Status: **execution contract**

This document defines how implementation work moves from handbook intent to merged code.

The objective is to reduce context switching, review ambiguity and regression risk without adding ceremony that does not protect a real invariant.

---

# 1. Core workflow

Every non-trivial change follows:

```text
documented user problem / invariant
→ bounded PR scope
→ acceptance criteria
→ implementation
→ targeted tests
→ CI / browser QA where relevant
→ documentation/ADR update if behaviour changed
→ merge
```

Do not begin with “what code should we write?”

Begin with:

> Which documented behaviour, scenario or invariant is this PR implementing?

---

# 2. Definition of Ready

A non-trivial implementation PR is ready to start only when these are known:

- user problem or operational problem;
- relevant user-case IDs and/or BE-* scenarios;
- governing handbook sections;
- exact in-scope behaviour;
- explicit out-of-scope behaviour;
- acceptance criteria;
- failure/recovery states;
- data/provenance implications;
- accessibility implications;
- security/privacy implications;
- intended test layer;
- migration/import impact if persisted data changes.

A task is **not ready** when a developer must invent product behaviour while coding.

Research questions may be implemented as prototypes only when they are clearly labelled as research.

---

# 3. Definition of Done

A feature is done when all applicable items are true.

## Behaviour

- acceptance criteria pass;
- documented failure states are implemented;
- no hidden alternate business-truth path exists;
- source/destination, historical and stale semantics remain correct where relevant.

## Code quality

- smallest justified abstraction is used;
- no speculative repository/service/framework layer was added;
- naming reflects product/domain language;
- dead/debug code is removed;
- secrets and machine-local paths are absent.

## Tests

- appropriate unit/integration/browser coverage exists;
- provider/network behaviour uses deterministic fixtures/fakes in normal CI;
- regression test exists for any bug fixed;
- no skipped/flaky test is introduced without an explicit issue and reason.

## UX/accessibility

For user-facing work:

- keyboard flow works;
- loading/error/empty/stale states are represented;
- responsive behaviour is verified;
- accessibility semantics are preserved;
- visual change is checked against Quiet Atlas documentation.

## Operations

Where applicable:

- migrations are reviewed;
- configuration changes are documented;
- logging/metrics support failure diagnosis;
- rollback implications are understood.

## Documentation

Update the handbook in the same PR when a settled rule changes.

Update the ADR log when a durable architecture decision changes.

---

# 4. Branch and PR scope

Prefer one bounded vertical or infrastructural concern per PR.

Good:

```text
feat/country-currency-domain
feat/current-conversion
feat/historical-date-mode
fix/stale-pair-cache-key
docs/development-execution-system
```

Avoid PRs that combine:

- unrelated refactors;
- formatting across untouched modules;
- speculative abstractions;
- product behaviour plus unrelated tooling;
- several roadmap milestones.

A PR may be stacked when a clean dependency exists. Its base/head relationship must be explicit in the PR description.

---

# 5. PR description contract

Every non-trivial PR should state:

1. **Problem** — what user/engineering problem is solved?
2. **Scope** — what exactly changes?
3. **Out of scope** — what intentionally does not change?
4. **Handbook links** — which documents govern the work?
5. **Scenarios** — user-case / BE-* IDs where applicable.
6. **Acceptance criteria**.
7. **Tests run**.
8. **Data/config/migration impact**.
9. **Accessibility/security/privacy impact**.
10. **Screenshots** for meaningful UI changes.

The repository PR template operationalizes this contract.

---

# 6. Current Python development commands

The validated Django product shell and Python tooling live at the repository root.

Install application and development dependencies from `pyproject.toml`:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Run the core CI-equivalent quality gates:

```bash
ruff format --check apps config scripts manage.py
ruff check apps config scripts manage.py
python manage.py check
coverage erase
coverage run -m pytest -q
coverage report
python -m pip_audit --skip-editable
```

Optional local commit hooks:

```bash
pre-commit install
```

Ruff owns Python formatting and linting. Black/isort are intentionally not part of the toolchain.

Runtime configuration is explicit through process environment variables. The canonical template is `.env.example`; Django does not silently load arbitrary `.env` files. Normal CI runs as `APP_ENV=test` and requires no secret credentials.

PostgreSQL and the phase-1 observability baseline are implemented and covered by CI.

## Current frontend development commands

The web asset toolchain lives in `frontend/` and is pinned by `.nvmrc`, `package.json` and `package-lock.json`.

Install exactly the locked dependency graph and run the CI-equivalent gate:

```bash
cd frontend
npm ci --no-audit --no-fund
npm run quality
```

The aggregate `quality` script runs, in order:

```text
TypeScript strict typecheck
→ Biome lint/format check
→ Vite production build
```

The production build emits the Vite backend manifest under `static/build/.vite/manifest.json`. Generated build output and `node_modules/` are not committed.

Node is build/development tooling only. Django remains responsible for HTML, routing and application state; PR 2A does not introduce a client application framework or web business logic.

The repo-owned Vite bridge is now implemented. For local asset development, run the two processes independently:

```bash
# terminal 1
python manage.py runserver

# terminal 2
cd frontend
npm run dev
```

Outside local debug, build assets before rendering templates that load the Vite entry:

```bash
cd frontend
npm run build
```

Django then resolves `static/build/.vite/manifest.json` through `{% vite_asset "frontend/src/app.ts" %}`. Missing/malformed production manifests fail fast rather than silently serving stale or unhashed asset paths.

The next bounded product slice is PR 2C: Quiet Atlas semantic tokens, typography and global shell.

---

# 7. Change discipline

Before modifying a file, answer:

- Which responsibility does this file own?
- Is this the narrowest layer where the rule belongs?
- Is this business truth, presentation policy, provider normalization or transport behaviour?
- Can a pure function express the rule?
- Will another client need the same logic?

Do not move a rule into JavaScript merely because the UI uses it.

Do not move provider JSON shapes into domain/application code.

Do not put domain rules into templates/serializers/views.

---

# 8. Refactoring rule

Refactor when at least one is true:

- duplicated business truth exists;
- a boundary is unclear and causes bugs/tests to be difficult;
- complexity blocks the next documented slice;
- measurements show performance/reliability need;
- naming/structure materially obscures an invariant.

Do not refactor because a pattern is fashionable.

Large mechanical refactors should be separate from product behaviour whenever practical.

---

# 9. Bug-fix workflow

For a real bug:

```text
reproduce
→ identify violated invariant
→ add failing regression test
→ smallest fix
→ run related suite
→ run broader CI
→ update docs only if intended behaviour was unclear/wrong
```

Never “fix” a test by weakening the assertion unless the assertion itself is demonstrably wrong.

---

# 10. Review priorities

Review in this order:

1. correctness / financial semantics;
2. data provenance and temporal semantics;
3. authorization/security/privacy;
4. failure/recovery behaviour;
5. accessibility;
6. architecture ownership;
7. test quality;
8. performance;
9. code style;
10. visual polish.

A stylish implementation with incorrect semantics is not mergeable.

---

# 11. Merge rule

Merge only when:

- required CI is green;
- unresolved review comments are addressed;
- documentation/ADR impact is handled;
- migration/config risk is understood;
- stacked dependency assumptions are still valid;
- the PR remains reviewably scoped.

If scope has drifted substantially, split before merge instead of expanding the description around accidental work.
