# Data Migrations, Fixtures and Seeding Strategy

Status: **data-change contract**

This document defines how schema changes, data migrations, provider fixtures and development seed data are handled.

The goal is deterministic development and safe production evolution without turning the repository into a dump of external data.

---

# 1. Schema migration rule

Every model/schema change must include its Django migration in the same PR.

Before merge:

```bash
python manage.py makemigrations --check
python manage.py migrate
```

Once the target project shell exists, CI should enforce migration drift detection.

Never edit an already-applied shared migration to change history.

---

# 2. Migration review

Review migrations for:

- unintended column/table deletion;
- null/default behaviour;
- large table rewrites;
- uniqueness/constraint effects;
- index cost;
- reverse behaviour;
- deploy ordering.

A generated migration is code and must be reviewed.

---

# 3. Expand / migrate / contract

For risky production schema changes prefer:

```text
expand schema
→ deploy compatible code
→ backfill/migrate data
→ verify
→ contract old schema later
```

Avoid one deploy that simultaneously removes old data shape and requires every running process to use the new shape.

---

# 4. Data migrations

Use Django data migrations for small, deterministic transformations tied directly to schema history.

Good:

- normalize an existing enum/value;
- populate a new field from existing local columns;
- split a local field into deterministic components.

Do not use schema migrations to:

- fetch remote APIs;
- import large provider datasets;
- call AI;
- depend on wall-clock/network state.

External imports belong in management commands/import services.

---

# 5. Reversibility

Prefer reversible migrations.

When a migration cannot be safely reversed:

- make that explicit;
- explain why;
- document rollback strategy;
- take backup/verification precautions before production execution.

Do not write a fake reverse operation that corrupts data.

---

# 6. Provider fixtures

Provider fixtures are test assets, not canonical product content.

They should be:

- minimal;
- representative;
- deterministic;
- version/review-date annotated where useful;
- stripped of irrelevant fields;
- safe to commit.

Do not commit full upstream datasets merely to make tests convenient.

---

# 7. Development seed data

Development seed data exists to enable useful local flows quickly.

The future seed command should create a **small deterministic product slice**, for example:

- representative countries/currencies;
- current + historical relationships;
- small curated cultural/payment examples;
- representative story/media records;
- optional demo user only when accounts ship.

The seed command must be idempotent or clearly reset/recreate its owned data.

---

# 8. Seed data vs fixtures

Prefer a management command/service for relational development seed data when relationships/logic matter.

Use static fixture files mainly for:

- external provider contract examples;
- compact immutable test payloads.

Do not make production depend on test fixture loading.

---

# 9. Import data

External source ingestion follows:

```text
fetch
→ validate completeness/sanity
→ normalize
→ calculate diff
→ atomic apply where appropriate
→ record source/run metadata
```

Never hold a database transaction open while performing remote network I/O.

Incomplete remote snapshots must not wipe canonical local data.

---

# 10. Historical data

Historical country/currency and story data must preserve temporal precision.

Do not “simplify” imported history by:

- sharpening decade/year to exact date without evidence;
- replacing archived currency with current currency;
- applying current cultural/payment facts retroactively.

Migration/import code must preserve the same temporal semantics as request-path code.

---

# 11. Production backfills

Large backfills should be:

- resumable;
- observable;
- bounded in batch size;
- safe to re-run;
- separated from request traffic where necessary.

Do not hide a long-running production backfill inside app startup.

---

# 12. Delete/destructive operations

Destructive imports/migrations require stronger evidence than additive changes.

Before deletion:

- prove source snapshot completeness;
- define scope;
- support dry-run/diff when practical;
- log counts/identifiers;
- preserve rollback/backup strategy.

---

# 13. Test requirements for migrations/imports

Test:

- fresh database migration;
- relevant upgrade path for risky migrations;
- constraints after migration;
- idempotent seed/import behaviour;
- malformed/incomplete upstream input;
- duplicate input;
- no-data input;
- transaction failure/rollback;
- destructive-snapshot guard.

---

# 14. Ownership

Each dataset should have one authoritative write path.

Examples:

- country/currency reference data → import service;
- user favourite → application use case;
- AI editorial candidate → AI pipeline/review workflow;
- migration-owned transformed field → migration.

Do not let admin scripts, request handlers and migrations all mutate the same semantic data differently.
