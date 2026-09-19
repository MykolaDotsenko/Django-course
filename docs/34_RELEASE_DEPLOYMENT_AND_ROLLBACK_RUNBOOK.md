# Release, Deployment and Rollback Runbook

Status: **platform-neutral operational contract**

The deployment platform is not yet fixed.

This runbook defines the sequence and safety properties every deployment implementation must preserve.

---

# 1. Release principle

A release must be:

- reproducible;
- observable;
- reversible where practical;
- safe under provider failure;
- explicit about migrations/configuration.

A successful build is not proof of a successful release.

---

# 2. Pre-release checklist

Before production deployment:

- target commit/PRs identified;
- CI green;
- migration drift clean;
- dependencies locked/reviewed;
- required environment variables present;
- secrets configured in deployment secret store;
- production `DEBUG=False`;
- allowed hosts/proxy/HTTPS settings correct;
- static build deterministic;
- database backup/recovery point available for risky data changes;
- known provider incidents checked when relevant;
- release notes identify migrations/config changes.

---

# 3. Build

The final target build should:

- install from lockfiles;
- build frontend assets deterministically;
- collect static assets;
- fail on missing required configuration that is build/startup critical;
- avoid live provider calls;
- avoid AI calls;
- avoid data imports as hidden build side effects.

---

# 4. Migration ordering

Classify release migrations:

## Safe/additive
Can normally run before or during deploy.

Examples:

- new nullable column;
- new table;
- compatible index where operationally safe.

## Coordinated
Require application compatibility planning.

Examples:

- non-null transition;
- field rename/removal;
- uniqueness added to existing dirty data;
- large backfill.

For coordinated migrations use expand/migrate/contract.

---

# 5. Deployment sequence

Generic sequence:

```text
1. validate configuration
2. create/verify recovery point when required
3. deploy compatible artifact
4. run migrations at defined safe point
5. start application
6. run readiness check
7. smoke critical flows
8. monitor errors/latency
9. mark release complete
```

Provider/AI availability is not part of core process liveness.

Readiness may require PostgreSQL/config, but should not fail because Frankfurter/Gemini is temporarily unavailable.

---

# 6. Smoke checks

After deploy verify:

- home/converter page returns expected response;
- static CSS/JS/media load;
- current conversion succeeds or degrades according to provider/cache policy;
- historical route behaves for a known deterministic case when shipped;
- health endpoints return correct liveness/readiness;
- admin/auth critical route if applicable;
- no obvious error spike in structured logs.

Do not perform destructive smoke actions.

---

# 7. Rollback decision

Rollback when a release causes:

- incorrect financial result;
- authorization/security regression;
- migration/data corruption risk;
- widespread 5xx/startup failure;
- broken primary conversion without documented degradation path;
- severe accessibility blocker on primary flow.

A non-critical provider outage alone is not a reason to roll back application code if fallback behaviour is correct.

---

# 8. Code rollback

If schema remains backward-compatible:

```text
deploy previous known-good artifact
→ verify readiness
→ smoke
→ monitor
```

Never assume database rollback is safe merely because code rollback is easy.

---

# 9. Database rollback

Prefer forward corrective migrations over reversing destructive production migrations.

Reverse only when:

- migration declares a correct reverse path;
- no incompatible new writes make reversal unsafe;
- impact is understood;
- recovery point exists when needed.

For irreversible corruption risk, restore from verified backup/recovery point according to the deployment platform runbook.

---

# 10. Feature disablement

Optional capabilities should support safe disablement where documented.

Examples:

- live AI explanation;
- editorial AI generation;
- optional media enrichment.

Do not add a feature flag that changes core FX truth.

---

# 11. Provider incident during release

If Frankfurter fails during/after release:

- confirm application health independently;
- verify cached/stale fallback semantics;
- expose clear user state;
- do not silently switch to an unreviewed provider;
- do not block rollback/health decisions on provider recovery.

---

# 12. Release observability

Every release should make it possible to correlate:

- deployed commit/version;
- timestamp;
- request IDs;
- error spike;
- provider failures;
- import-job failures;
- database/migration problems.

Exact metrics backend is deployment-specific and may be selected later.

---

# 13. Static/media release checks

Verify:

- collected static manifest includes required assets;
- no broken hashed references;
- media/storage configuration is correct;
- release-owned SVG/WebP assets serve with correct MIME/type;
- browser smoke has no broken critical images.

Missing decorative media should not break conversion.

---

# 14. Roll-forward

When rollback is unsafe due to schema/data evolution, prepare a minimal roll-forward fix.

The release decision should explicitly state:

- why rollback is unsafe;
- what invariant the corrective release restores;
- how it is tested;
- how data integrity is verified afterward.

---

# 15. Incident notes

For significant production incidents record:

- timeline;
- user impact;
- affected invariant;
- detection;
- root cause;
- mitigation;
- permanent fix;
- missing test/alert/runbook item.

The goal is system learning, not blame.

---

# 16. Platform-specific follow-up

When deployment hosting is chosen, add a short platform appendix covering:

- build/start command;
- secret storage;
- managed PostgreSQL;
- cache;
- static/media storage;
- scheduler;
- health-check configuration;
- backup/restore procedure;
- rollback command/process.

Do not fork the product architecture around deployment-platform convenience without an ADR.
