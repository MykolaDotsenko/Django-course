
# Data Consistency, Caching and Concurrency

This document defines consistency guarantees for PostgreSQL, cache, provider data and concurrent user actions.

The central rule is:

> Correctness must never depend on a cache race, timing accident or optimistic assumption about a remote provider.

---

# 1. Consistency model by data class

## Financial reference data

Source:

- normalized provider observation.

Consistency goal:

- correct pair;
- correct provider policy;
- correct requested/effective dates;
- explicit freshness.

A slightly stale but correctly labelled quote can be acceptable.

A fresh-looking wrong quote is never acceptable.

## Curated product data

Source:

- PostgreSQL.

Consistency goal:

- transactional durable state;
- provenance;
- publication rules.

## User-owned state

Source:

- PostgreSQL after account sync exists.

Consistency goal:

- ownership;
- atomic writes where needed;
- conflict behavior.

## Anonymous local state

Source:

- browser/mobile local storage.

Consistency goal:

- convenience only;
- failure must not affect conversion correctness.

---

# 2. PostgreSQL is durable authority

PostgreSQL owns durable application truth.

Cache may accelerate reads.

Cache may never be the only copy of:

- StoryMoment;
- TypicalPrice;
- Trip;
- FavouritePair;
- account preferences;
- imported canonical country metadata.

---

# 3. Autocommit default

Keep Django autocommit enabled.

Most read operations need no explicit transaction.

Examples:

- country lookup;
- quote cache read;
- story query;
- destination context read.

This keeps transactions short.

---

# 4. No global ATOMIC_REQUESTS

Do not enable ATOMIC_REQUESTS globally.

Reasons:

- unnecessary transaction for read-only views;
- provider call could accidentally happen inside request transaction;
- longer DB resource/lock duration;
- implicit boundaries reduce clarity.

Use explicit atomic blocks for specific commands.

---

# 5. Transaction boundary rule

The transaction starts immediately before the first durable write that must be atomic and ends immediately after the last related write.

Good:

~~~text
validate
fetch external data
calculate
↓
BEGIN
write A
write B
COMMIT
↓
post-commit cache invalidation
~~~

Bad:

~~~text
BEGIN
call provider
wait
calculate
write
COMMIT
~~~

---

# 6. Expected atomic use cases

Likely:

- create Trip + initial budget items;
- multi-row favourite import/merge;
- editorial publication spanning related records;
- future account deletion cascade requiring explicit workflow.

Not needed:

- current conversion;
- historical quote;
- normal context read;
- single favourite get_or_create where DB uniqueness is sufficient.

---

# 7. on_commit rule

Any side effect that must observe committed DB state runs after commit.

Examples:

- invalidate context cache;
- invalidate story cache;
- enqueue future notification task;
- emit integration event later.

If transaction rolls back, callback must not run.

---

# 8. IntegrityError handling

Catch database integrity errors outside the relevant atomic block.

Do not catch and continue querying inside a broken transaction.

Map known constraint violation to:

- idempotent existing object;
- Conflict;
- validation-like result,

depending on use case.

---

# 9. Database constraints first

Use constraints for invariants that must survive concurrent requests.

Examples:

~~~text
Currency.code unique
Country.iso2 unique
FavouritePair unique per user/pair/context
TypicalPrice.low > 0
TypicalPrice.high >= low
~~~

Application pre-checks alone are race-prone.

---

# 10. Favourite concurrency

Two requests simultaneously saving same favourite:

~~~text
Request A → get/create
Request B → get/create
        ↓
DB unique constraint
~~~

At most one row persists.

The loser resolves to the existing row.

No pessimistic lock.

---

# 11. Trip concurrency

Cross-device mutable aggregate can use optimistic concurrency when feature ships.

Model candidate:

~~~text
Trip.version integer
~~~

Update:

~~~text
WHERE id = ? AND version = current_version
~~~

Success:

- increment version.

Failure:

- 409 Conflict;
- return/reload current state.

This avoids silent last-writer-wins.

---

# 12. When to use select_for_update

Only when:

- optimistic conflict is unsuitable;
- update depends on reading then mutating a row atomically;
- concurrent writers must serialize.

Potential future example:

- consuming a strict limited resource.

It is probably not necessary for initial Cultural Currency Converter workflows.

Use PostgreSQL behavior intentionally and test with TransactionTestCase when locks matter.

---

# 13. Avoid broad row locks

If select_for_update is used:

- select only needed rows;
- use of=("self",) or equivalent when appropriate;
- keep transaction short;
- never call remote API while locked.

Avoid lock escalation through unnecessary select_related joins.

---

# 14. Isolation level

Use PostgreSQL/Django normal default isolation unless a demonstrated anomaly requires change.

Do not globally enable SERIALIZABLE.

Application invariants are protected through:

- constraints;
- atomic writes;
- explicit conflict handling.

A stronger isolation level adds retry/operational complexity.

---

# 15. Cache architecture

Separate:

- semantic freshness;
- physical cache retention.

A quote may remain physically cached longer than it is considered fresh.

Example:

~~~text
freshness threshold: provider/update-policy based
physical retention: much longer for stale fallback
~~~

This enables explicit stale-success.

---

# 16. Quote cache record

Cache normalized structured object:

~~~text
CachedRateQuote
- base
- quote
- rate
- provider_policy
- providers
- effective_date
- fetched_at
- granularity
~~~

Fresh/stale is preferably derived against current time/policy, not trusted as an old stored boolean.

---

# 17. Current quote cache keys

Versioned semantic key:

~~~text
fx:v1:latest:{policy}:{provider-or-blend}:{base}:{quote}
~~~

Examples:

~~~text
fx:v1:latest:blend:all:EUR:JPY
fx:v1:latest:pinned:ecb:EUR:USD
~~~

Cache namespace version changes when semantics change.

---

# 18. Historical quote cache keys

~~~text
fx:v1:historical:{policy}:{provider}:{base}:{quote}:{effective-date}
~~~

Requested date may differ from effective date.

Also store/request a mapping where needed:

~~~text
historical-resolution:{pair}:{requested-date}
→ effective-date
~~~

Only if it improves provider lookup.

Do not lose requested/effective distinction.

---

# 19. Historical cache retention

Historical observations can have long retention.

But they are not mathematically immutable because upstream data may be corrected.

Therefore:

- long TTL;
- versioned key;
- explicit invalidation/rebuild command;
- provider/source metadata retained.

---

# 20. Time-series cache key

~~~text
fxseries:v1:{policy}:{provider}:{base}:{quote}:{from}:{to}:{group}
~~~

Grouping is semantic.

A monthly series cannot reuse a daily-series key.

---

# 21. Freshness classification

Centralize freshness policy.

Concept:

~~~text
classify_quote_freshness(
    quote,
    now,
    policy
) -> fresh | stale | too_old
~~~

Do not scatter TTL comparisons through views/templates.

---

# 22. Stale fallback maximum

Stale fallback should have an upper safety horizon.

Do not show a year-old current FX quote merely because it exists in cache.

The exact horizon is provider/product policy and should be configurable/tested.

Historical observations have different freshness semantics.

---

# 23. Provider cadence awareness

Reference-rate freshness is not “seconds since fetch” only.

Consider:

- daily publication;
- weekends;
- holidays;
- lower-frequency providers.

A quote fetched Saturday can still reflect Friday's valid effective observation without being “bad”.

UI exposes effective date.

---

# 24. Cache backend failure

Correctness must survive:

- cache get failure;
- cache set failure;
- cache eviction;
- restart.

Behavior:

- fall through to DB/provider;
- log cache failure;
- do not corrupt result.

Cache set failure after successful provider response does not invalidate that response.

---

# 25. Cache stampede

Initial traffic is expected to be low.

Do not add distributed locking preemptively.

Accept that two cold requests may fetch same provider quote concurrently.

When metrics prove stampede cost:

- shared cache lock/add pattern;
- request coalescing;
- Redis lock;

can be considered.

Correctness does not depend on single-flight.

---

# 26. LocMemCache limitation

Local-memory cache is acceptable for development.

It is per-process.

Therefore it cannot provide:

- cross-worker cache coherence;
- distributed locks;
- global throttle accuracy.

Do not assume otherwise in production architecture.

---

# 27. Production cache choice

Keep Django cache abstraction.

Possible production backends:

- Redis;
- Memcached;
- platform-managed equivalent.

Choose based on deployment.

Application code never imports Redis client for normal cache semantics.

---

# 28. Culture/context cache

Cache only when profiling shows value.

Potential key:

~~~text
context:v1:{country}:{city-or-national}:{language}
~~~

Invalidated after editorial publication/update.

Because source data is PostgreSQL-local, correctness does not require a cache.

---

# 29. Story cache

Candidate:

~~~text
story:v1:{country}:{currency}:{requested-date}:{language}
~~~

But cache only after composition cost/traffic justifies it.

Story composition should initially be cheap enough from indexed DB data.

---

# 30. User-specific caching

Be conservative.

Do not public-cache authenticated HTML/API responses.

Avoid cache keys that accidentally omit user identity.

For P0/P1, user-owned data can simply read PostgreSQL.

---

# 31. HTTP cache vs application cache

They are different.

Application cache:

- normalized quote;
- series;
- derived context.

HTTP caching:

- whole response validators/TTL.

Do not conflate them.

---

# 32. Good HTTP-cache candidates

Public slowly changing GET resources:

- currencies metadata;
- countries metadata;
- public story/country pages;
- static cultural context.

Use:

- ETag;
- Last-Modified;
- Cache-Control policy.

---

# 33. Poor HTTP-cache candidates

- authenticated user resources;
- mutation responses;
- amount-specific conversion POST;
- error pages containing user/request-specific state.

Use internal quote cache instead.

---

# 34. HTMX response caching

If same URL returns:

- full document for normal request;
- fragment for HX-Request,

response must vary by HX-Request.

Otherwise a shared/downstream cache can deliver fragment HTML as full page.

---

# 35. Cache invalidation patterns

Prefer namespace/version + targeted delete.

Avoid cache.clear() in application logic.

Examples:

~~~text
publish payment context
→ invalidate context keys for country

change StoryMoment
→ invalidate story keys for affected country/currency/date range if cached
~~~

When targeted invalidation becomes too complex, short TTL can be safer.

---

# 36. Import consistency

Never stream remote records directly into canonical DB one by one before knowing whether the source response is valid enough.

Preferred small-dataset flow:

~~~text
fetch full
validate full
normalize full
diff
atomic apply
~~~

For very large future datasets:

- chunk/staging strategy;
- run metadata;
- publish completed snapshot only after validation.

---

# 37. Partial import failure

Small dataset:

- rollback whole apply transaction.

Large statistical dataset:

- each dataset/version can import to staging;
- failed run remains unpublished;
- prior active snapshot stays active.

Do not leave mixed old/new source versions presented as one coherent dataset without explicit policy.

---

# 38. Source snapshot identity

Imported data should preserve enough metadata to answer:

- source;
- retrieved_at;
- source version/date if provided;
- import run/dataset ID when useful.

This aids correction/debugging.

---

# 39. Import idempotency

Run twice with same source snapshot:

- no duplicates;
- same canonical state;
- predictable updated_at policy.

Do not update every row timestamp if values did not change unless metadata intentionally records re-verification.

---

# 40. Import concurrency

Prevent two scheduled runs of the same import from racing if that could corrupt/double work.

Initial simple options:

- scheduler guarantees non-overlap;
- database advisory/lock row if needed;
- command-level lock.

Do not introduce distributed task orchestration solely for this.

---

# 41. Publication consistency

Editorial records can have:

~~~text
draft
published
unpublished
~~~

Public queries filter published state.

A multi-record publication workflow uses a transaction if users must see either old or new coherent set.

---

# 42. Media rights consistency

If rights metadata is removed/invalidated:

- media becomes unpublished;
- story may remain with text;
- cached media/context invalidated.

Do not keep displaying a cached asset after rights state changes.

---

# 43. Deletion consistency

User account deletion:

- define transactional deletion of owned server state;
- after commit, clear relevant caches;
- client may separately clear local state.

No partially deleted account visible as normal active user.

---

# 44. Privacy and cache

Do not cache private response bodies in shared cache without explicit user-key isolation.

Do not include auth tokens or private notes in cache keys/logs.

---

# 45. Mobile offline consistency

SQLite snapshot must include semantic identity:

- base;
- quote;
- requested date;
- effective date;
- source/policy;
- fetched time.

The UI does not reconstruct those fields from current controls.

---

# 46. Mobile write synchronization

Future server-owned favourites/trips:

- local pending mutation may be optimistic only when safe;
- server response remains canonical;
- conflict behavior explicit.

Do not overwrite server state from a stale local snapshot blindly.

---

# 47. Local schema migrations

Expo SQLite schema migrations must preserve:

- cached quote identity;
- favourites;
- user-created trip drafts.

Do not clear cache/data merely because app version changes unless data is truly disposable and policy says so.

---

# 48. Clock skew

Server timestamps are canonical for:

- fetched_at;
- server updated_at;
- cache semantic freshness returned to mobile.

Do not trust device clock for deciding whether a server quote is authoritative.

Device clock may affect UI display but not source truth.

---

# 49. Duplicate provider responses

Same quote fetched concurrently can be written to cache multiple times.

Safe because cache content is semantically identical or latest validated response.

If provider effective dates differ around publication boundary, each response carries its own effective/fetched metadata.

The later cache write is acceptable under latest policy if validated.

---

# 50. Provider correction race

If explicit historical invalidation/refetch occurs:

- new provider observation gets new cache value/version;
- no DB durable financial history is overwritten unless that history is intentionally persisted.

Persistent trip projections retain the exact quote metadata they originally used.

---

# 51. Derived-data consistency

Derived values such as:

- purchase-equivalent count;
- Then & Now percentage;
- story selection;

should be recomputable from source rows/results.

Avoid storing them unless performance/audit requirements justify persistence.

Store primary source values and provenance.

---

# 52. Query consistency within request

For multi-read context pages where strict snapshot consistency is not critical, normal PostgreSQL read committed behavior is sufficient.

Do not wrap an entire story page in a transaction merely to freeze all reads.

If publication workflow ensures coherent published records, ordinary queries are enough.

---

# 53. Soft deletes

Avoid generic soft-delete framework.

Use explicit publication/unpublication for editorial content.

Use real delete for user-owned data when privacy/product semantics expect deletion.

Soft delete creates query/filter complexity and accidental data exposure.

---

# 54. Race-condition test strategy

Test at DB level when concurrency matters.

Examples:

- duplicate favourite;
- optimistic Trip version conflict;
- import overlap lock if implemented;
- select_for_update path if ever used.

SQLite is insufficient for PostgreSQL locking semantics.

Run these tests against PostgreSQL.

---

# 55. Cache test strategy

Test:

- miss → provider;
- fresh hit → no provider;
- provider fails → valid stale;
- provider fails → too-old stale rejected;
- wrong pair not reused;
- different provider policy not reused;
- cache exception still permits correct path;
- historical key keeps date semantics.

---

# 56. Consistency acceptance criteria

Architecture is acceptable when:

- no user-visible correctness depends on cache persistence;
- transactions contain no network calls;
- durable invariants have DB constraints;
- concurrent duplicate favourites remain one row;
- stale FX has exact semantic identity and bounded age;
- requested/effective dates survive every layer;
- publication writes invalidate cache after commit;
- failed imports preserve last valid local data;
- mobile cached data carries source/effective/fetched metadata;
- PostgreSQL-specific concurrency behavior is tested on PostgreSQL.
