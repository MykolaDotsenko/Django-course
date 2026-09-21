
# Data Import, Scheduled Jobs and Maintenance Architecture

This document defines how slowly changing external/reference data enters the system without becoming a runtime dependency.

---

# 1. Job philosophy

Scheduled/background work must be:

- explicit;
- idempotent;
- observable;
- retryable at the scheduler level;
- independent from web requests;
- safe when external sources fail.

Initial implementation uses Django management commands plus the deployment platform scheduler.

No Celery is required initially.

---

# 2. Why management commands first

Django management commands are sufficient for:

- weekly country metadata refresh;
- cultural candidate ingestion;
- media metadata refresh;
- future monthly HICP/CPI import;
- future annual PPP import;
- cache rebuild/invalidation utilities.

Benefits:

- easy local execution;
- easy testing;
- no broker;
- no worker fleet;
- simple scheduler integration.

---

# 3. Thin command rule

Command handle() should:

1. parse CLI options;
2. call reusable application/import service;
3. print structured human summary;
4. map failure to CommandError/exit status.

It should not contain the import algorithm itself.

---

# 4. Standard command options

Where useful:

~~~text
--dry-run
--source
--country
--since
--force
--limit
--verbosity
~~~

Do not add generic options that no source uses.

---

# 5. Dry-run

Important imports should support dry-run when practical.

Dry-run reports:

- fetched;
- normalized;
- insert count;
- update count;
- unchanged;
- delete/unpublish candidates;
- validation failures.

No durable mutation.

---

# 6. Country metadata sync

Command:

~~~text
manage.py sync_country_metadata
~~~

Flow:

~~~text
fetch
→ validate complete snapshot
→ normalize
→ diff
→ dry-run output OR atomic apply
→ summary
~~~

Never delete all missing rows merely because source response is incomplete.

---

# 7. Completeness guard

For known bounded datasets, define sanity checks.

Examples:

- minimum expected country count;
- required ISO codes present;
- no duplicate ISO code;
- expected fields parseable.

A suspicious source shrink is a failure requiring review.

---

# 8. Country upsert

Use stable ISO code identity.

Update only owned normalized fields.

Do not overwrite editorial/internal fields from external source.

Examples external-owned:

- current name;
- capital;
- region;
- languages where selected.

Examples internal-owned:

- featured;
- custom theme;
- editorial notes.

---

# 9. Country-currency history

Historical CountryCurrency data needs stronger sources than current REST Countries metadata.

Do not infer all historical validity ranges from a current-country API.

Historical rows are curated/imported from authoritative historical sources with explicit provenance.

---

# 10. Wikidata candidate import

Possible command:

~~~text
manage.py ingest_wikidata_story_candidates --currency FIM
~~~

Output creates/reports unpublished candidates.

No auto-publish.

---

# 11. Candidate deduplication

Stable external identity:

- entity QID;
- property/event identity;
- source URL/date.

Duplicate candidate imports update/merge metadata rather than multiply records.

---

# 12. Europeana/media import

Command/service should preserve:

- external record ID;
- provider/institution;
- canonical record URL;
- rights URI;
- creator;
- media URL;
- retrieval timestamp.

No rights URI/license → not publishable automatically.

---

# 13. Media binary strategy

Do not automatically mirror every external binary into repository.

Initial options:

- store canonical external media reference if terms/reliability allow;
- or download selected approved assets into managed media storage.

Decision is per source/licence.

Repository should not become an unreviewed cultural-asset dump.

---

# 14. Statistical jobs — future

Potential commands:

~~~text
sync_eurostat_hicp
sync_eurostat_ppp
sync_oecd_ppp
sync_world_bank_cpi
~~~

Each command maps one explicit dataset/methodology family.

Avoid:

~~~text
sync_all_statistics
~~~

until there is a clear orchestration need.

---

# 15. Statistical staging

For large/revisable datasets:

~~~text
fetch source version
  ↓
normalize into staging/run scope
  ↓
validate completeness
  ↓
publish/activate snapshot
~~~

Old active snapshot remains until new snapshot is complete.

---

# 16. Import run metadata

A lightweight ImportRun model may be introduced when scheduled imports become important.

Candidate fields:

~~~text
source
job_name
started_at
finished_at
status
source_version
fetched_count
inserted_count
updated_count
unchanged_count
rejected_count
error_code
metadata JSON
~~~

Do not create it before there are multiple recurring jobs if logs alone are sufficient.

---

# 17. Import status values

~~~text
running
success
failed
partial
dry_run
~~~

Prefer failed over silently partial for small canonical snapshots.

Partial is justified for a large source where explicitly designed.

---

# 18. Network outside transaction

Always:

~~~text
fetch remote
validate
normalize
↓
transaction starts
write
commit
~~~

Never hold a transaction open while waiting for remote HTTP.

---

# 19. Small snapshot atomicity

For a small country metadata snapshot:

- apply as one transaction where practical.

If any critical write fails:

- rollback snapshot apply;
- previous state remains.

---

# 20. Large dataset atomicity

For large statistical data:

- staging/versioned import;
- chunk writes;
- activate only after complete validation.

One massive transaction may be worse operationally.

---

# 21. Upsert semantics

Prefer explicit unique keys.

Examples:

~~~text
Country: iso2
Currency: code
StatisticalObservation:
  source + dataset + indicator + geography + period + category + unit
~~~

Do not use display name as identity.

---

# 22. Unchanged rows

Avoid updating unchanged rows only to refresh updated_at unless re-verification timestamp intentionally changes.

This:

- reduces writes;
- preserves meaningful change history;
- simplifies cache invalidation.

---

# 23. Deletions from source

External absence does not automatically mean delete.

Possible meanings:

- source bug;
- temporary filtering;
- renamed code;
- retired item.

Use source-specific deletion policy:

- mark inactive;
- unpublish;
- require confirmation;
- hard delete only when safe.

---

# 24. Source revision

If source changes a value:

- validate;
- update source-owned field;
- record retrieval/version metadata;
- invalidate affected derived caches after commit.

For trust-sensitive historical facts, editorial re-verification may be required before public update.

---

# 25. Job overlap

Initial scheduler should avoid overlapping same job.

If platform scheduler cannot guarantee:

- use a DB lock row/advisory mechanism;
- or command-level run lock.

Second run exits cleanly with “already running”.

Do not let two full imports race.

---

# 26. Job retry

One command invocation uses bounded HTTP retry.

If whole job fails:

- exits non-zero;
- scheduler may retry later.

Avoid 30-minute internal infinite retry loops.

---

# 27. Backoff

For import HTTP:

- exponential backoff;
- jitter;
- Retry-After where available;
- maximum attempts.

User request path has a much smaller retry budget than scheduled imports.

---

# 28. Timeout

Import timeouts may be longer than user-facing FX timeouts but are still finite.

Each source defines:

- connect timeout;
- read timeout;
- total retry budget.

---

# 29. API quota awareness

Import frequency reflects source quota/update cadence.

REST Countries:

- slow-changing;
- weekly/manual likely enough.

HICP:

- release-driven/monthly.

PPP:

- annual/release-driven.

Do not poll annual data daily.

---

# 30. Credentials

Scheduled job credentials are server/deployment secrets.

Commands fail clearly when required source credential is missing.

Do not silently skip an enabled source and report success.

---

# 31. Command output

Use self.stdout/self.stderr via Django command API.

Summary example:

~~~text
Source: REST Countries
Fetched: 250
Validated: 250
Inserted: 0
Updated: 3
Unchanged: 247
Rejected: 0
Duration: 1.8s
~~~

No secrets.

---

# 32. Machine-readable logs

In production scheduler logs, emit structured run events in addition to human command summary if logging config supports it.

Useful event names:

~~~text
import.started
import.completed
import.failed
import.snapshot_rejected
~~~

---

# 33. Alert threshold

Initial product need not integrate PagerDuty.

Operational visibility can be:

- platform failed-job notification;
- GitHub/CI failure if scheduled there;
- log alert later.

The important property is failure is visible.

---

# 34. Cache invalidation after import

Only after successful DB commit:

- invalidate affected local caches.

Use transaction.on_commit.

Failed import leaves old cache consistent with old DB state.

---

# 35. Search index

No external search engine initially.

Country/currency search uses PostgreSQL.

If imported data changes:

- normal DB query sees new rows after commit;
- no search-index synchronization problem.

---

# 36. Management maintenance commands

Potential useful commands:

~~~text
warm_fx_cache
invalidate_fx_cache
rebuild_story_cache
verify_source_links
list_stale_editorial_content
check_price_freshness
~~~

Only implement those proven useful.

Do not fill repository with speculative maintenance scripts.

---

# 37. Source-link verification

A future scheduled maintenance job can verify:

- HTTP reachability;
- redirects;
- dead source links.

It must not automatically unpublish on one transient network failure.

Use status/history/review policy.

---

# 38. Editorial freshness review

Command/report:

~~~text
list content where verified_at < threshold
~~~

Human/editorial workflow decides whether content is still valid.

Different categories have different review periods.

---

# 39. TypicalPrice freshness

Price records may have source-specific expiry/aging policy.

Maintenance can report:

- current;
- aging;
- stale/suppress.

Do not update price values automatically from unrelated sources.

---

# 40. Frankfurter cache warm

Optional.

At low traffic, not required.

If useful, warm top pairs:

~~~text
EUR/USD
EUR/JPY
EUR/GBP
...
~~~

But provider request budget/terms must be respected.

User request correctness cannot depend on warm cache.

---

# 41. Historical prefetch

Do not prefetch huge historical datasets without evidence.

Historical queries are cache-friendly after first access.

Time-series can be fetched on demand.

---

# 42. Database maintenance

Rely primarily on managed PostgreSQL/platform for:

- vacuum/autovacuum;
- backups;
- monitoring.

Application should not schedule custom VACUUM jobs casually.

---

# 43. Data verification command

Potential:

~~~text
manage.py verify_domain_invariants
~~~

Could check:

- duplicate lifecycle overlaps;
- published content without source;
- impossible TypicalPrice ranges;
- archived currencies marked current;
- broken media-rights metadata.

Many invariants should be DB constraints first; command catches cross-row/complex cases.

---

# 44. Lifecycle overlap verification

CountryCurrency ranges can accidentally overlap.

If DB exclusion constraint is not introduced, maintenance/import validation checks:

~~~text
same country
same usage role
overlapping validity intervals
~~~

Historical transitions must remain coherent.

---

# 45. Dry-run deployment workflow

Before a risky import:

~~~text
production-like environment
→ dry run
→ review diff
→ real apply
~~~

This is especially valuable for metadata schema/provider changes.

---

# 46. Import fixture testing

Normal CI uses stored small provider fixtures.

Tests cover:

- expected payload;
- missing required field;
- duplicate ID;
- malformed date;
- partial response;
- source rename.

CI does not depend on live external APIs.

---

# 47. Live smoke checks

Optional scheduled/manual source smoke test:

- fetch minimal endpoint;
- validate contract.

Do not make every PR CI fail because an external provider is temporarily down.

---

# 48. Backfill jobs

Large data backfill should not be a request or model save side effect.

Use explicit management command.

Backfill can support:

- chunk size;
- resume cursor;
- dry run;
- progress.

Only add complexity if dataset size requires it.

---

# 49. Resume semantics

For large future jobs:

- persist cursor/run state;
- restart safely;
- idempotent upsert.

For current small metadata imports, restart whole job is simpler.

---

# 50. Job cancellation

Scheduler/process termination should leave:

- small atomic apply rolled back;
- staging job unpublished;
- previous active data intact.

Design writes around interruption.

---

# 51. Import security

External payload is untrusted.

Do not:

- eval;
- deserialize unsafe objects;
- render upstream HTML;
- trust MIME/URL blindly.

Normalize plain structured fields.

---

# 52. Import data size

Enforce reasonable response/body limits.

A source returning an unexpected 2GB payload is operational failure, not a valid import.

---

# 53. Source redirects

HTTP adapter follows only safe policy.

If canonical endpoint unexpectedly redirects to another host:

- inspect/allow intentionally;
- do not blindly follow arbitrary chains when credentials could leak.

---

# 54. Scheduler ownership

Choose one canonical scheduler per environment.

Avoid running the same recurring import from:

- GitHub Actions;
- platform cron;
- local server cron

simultaneously.

Document where production jobs run.

---

# 55. When Celery becomes justified

Introduce queue/broker only if at least one real workload requires:

- user-visible asynchronous job status;
- high-volume retryable jobs;
- scheduled notifications/rate alerts;
- distributed workers;
- long-running exports/imports that exceed simple scheduler model.

Then document:

- broker;
- retry semantics;
- idempotency;
- dead-letter/failure policy.

Until then, Celery is unnecessary operational surface.

---

# 56. Job acceptance criteria

A scheduled/import job is production-ready when:

- it is callable through a management command;
- core logic is reusable/testable outside command;
- it is idempotent;
- network occurs outside write transaction;
- invalid source cannot wipe valid local data;
- dry-run exists for risky snapshot changes where useful;
- credentials are server-only;
- run has structured summary;
- failure is non-zero/visible;
- cache invalidation occurs after commit;
- concurrent overlap is safe/prevented when necessary.


# Media and image jobs

## 57. Sourced-media ingestion

Implemented command:

```text
manage.py ingest_media_candidates \
  --source wikimedia \
  --query "Finland markka 1998" \
  --role historical_timeline \
  --kind archival_photo \
  --country FI
```

Europeana uses the same command with `--source europeana` and a server-side `EUROPEANA_API_KEY`.

The command does not download or publish the first search result. It stores normalized review metadata only.

Implemented review flow:

```text
search fixed reviewed source
→ normalize candidate metadata
→ unpublished needs_review MediaAsset
→ human rights/date/relevance review
→ attach reviewed local raster through attach_media_file
→ decode / sanitize / SHA-256 / Django Storage
→ explicit approve action
→ explicit publish action
```

This deliberately keeps binary acquisition/review separate from search-result discovery rather than turning arbitrary remote URLs into a media proxy.

## 58. AI media generation command

Initial generated media is editorial/build-time.

Example:

```text
manage.py generate_media_candidate \
  --country FI \
  --year 1998 \
  --role story_cover
```

The command:

- builds normalized prompt from structured data;
- calls one configured ImageGenerator adapter;
- records provider/model/prompt metadata;
- validates output;
- stores unpublished candidate;
- never auto-publishes.

## 59. No generation from selector changes

Country/year selection is not a scheduled/background generation trigger.

A user may select the same combination many times with zero AI generation cost.

Published stored asset selection is read-only.

## 60. Media derivatives

The implemented `build_media_derivative` command/service creates an explicitly requested responsive WebP width from reviewed managed source media. It re-encodes the derivative, computes a content hash, records `derivative_of` / `variant_width`, and leaves the derivative unpublished for review.

AVIF, focal-point-aware cropping and multi-width batch generation remain later optimizations that require a concrete delivery need.

Do not regenerate derivatives on every web request.

## 61. Media-rights maintenance

Potential report:

```text
manage.py audit_media_rights
```

Checks:

- missing licence;
- dead canonical source;
- missing attribution;
- retired/blocked rights status;
- AI illustration missing required label.

A transient dead source URL alone does not automatically delete the asset.

## 62. Orphan cleanup

Potential:

```text
manage.py clean_orphan_media --dry-run
```

Candidates:

- rejected AI candidates older than retention threshold;
- unreferenced derivatives;
- duplicate hashes;
- retired unused assets.

Deletion defaults to dry-run/review.

## 63. Future user on-demand generation

If approved later, do **not** implement through a long-running management command invoked from a request.

That feature becomes a real asynchronous workload with:

- queued job;
- job state;
- idempotency;
- quota;
- cancellation/timeout;
- spend limits.

At that point a task queue may finally be justified.


---

# 64. Story candidate ingestion

PR8 implements targeted Wikidata discovery as an editorial command, not a runtime research service.

Example command:

python manage.py ingest_story_candidate --item Q4916 --category monetary_union --country FI --currency EUR --start-date 1999-01-01 --end-date 1999-01-01 --date-precision exact_day

Properties:

- the input entity must be an explicit QID;
- the provider endpoint is fixed to the versioned Wikibase REST API;
- response size and timeout are bounded;
- an explicit Wikimedia-compatible User-Agent is sent;
- the result is always an unpublished needs_review candidate;
- reviewed/approved/published/retired rows are protected from upstream overwrite;
- --dry-run rolls all local writes back;
- no fuzzy search or broad SPARQL query is part of the product request path.

The deterministic portfolio slice can be seeded after country/currency reference data:

python manage.py seed_reference_data
python manage.py seed_story_data

The reviewed demo story seed uses official European Commission and Bank of Japan sources. Seeded rows pass the same approve/publish service gates as editor-created content rather than bypassing the lifecycle.
