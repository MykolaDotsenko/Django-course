
# Backend Scenario Catalog

This catalog enumerates backend scenarios that implementation and testing must consider.

Priority:
- P0 = core correctness / trust / security
- P1 = expected production behavior
- P2 = later feature / hardening
- R = research-dependent

---

# A. Current conversion

## BE-001 — Valid current conversion
Priority: P0

Input:
- valid positive amount;
- supported base/quote.

Expected:
- normalized quote;
- Decimal result;
- effective date/source;
- fresh status.

## BE-002 — Same-currency conversion
Priority: P0

Expected:
- exact rate 1;
- no provider call;
- context still available.

## BE-003 — Zero amount
Priority: P0

Expected:
- accepted if product rule allows zero;
- result zero;
- provider call may be skipped if policy can return metadata separately, otherwise quote may still be needed for provenance.

Implementation must choose and test one behavior.

## BE-004 — Negative amount
Priority: P0

Expected:
- validation failure before provider call.

## BE-005 — Very large amount
Priority: P0

Expected:
- bounded validation;
- no overflow;
- no provider call when rejected.

## BE-006 — Excess decimal precision
Priority: P0

Expected:
- explicit validation/normalization policy;
- no float conversion.

## BE-007 — Decimal comma parsed by form layer
Priority: P0

Expected:
- normalized Decimal command;
- domain never sees locale string.

## BE-008 — Unsupported currency code
Priority: P0

Expected:
- typed unsupported error;
- no provider request when locally known.

## BE-009 — Invalid currency syntax
Priority: P0

Expected:
- transport validation error.

## BE-010 — Currency exists but provider has no current rate
Priority: P0

Expected:
- UnsupportedPair/RateUnavailable;
- no fabricated cross-rate unless provider/domain explicitly supports it.

---

# B. Cache/provider

## BE-011 — Fresh quote cache hit
Priority: P0

Expected:
- no provider call.

## BE-012 — Cache miss + provider success
Priority: P0

Expected:
- normalize;
- cache;
- convert.

## BE-013 — Provider timeout + safe stale quote
Priority: P0

Expected:
- stale success;
- source/effective/fetched time preserved.

## BE-014 — Provider timeout + no stale quote
Priority: P0

Expected:
- 503/application unavailable state.

## BE-015 — Provider timeout + stale quote too old
Priority: P0

Expected:
- reject stale;
- unavailable.

## BE-016 — Provider HTTP 500
Priority: P0

Expected:
- same fallback path as transient provider failure.

## BE-017 — Provider HTTP 429
Priority: P1

Expected:
- bounded retry only if latency policy permits;
- otherwise stale/unavailable.

## BE-018 — Provider 200 malformed JSON
Priority: P0

Expected:
- SourceDataInvalid;
- stale fallback.

## BE-019 — Provider 200 wrong pair
Priority: P0

Expected:
- reject payload;
- never display.

## BE-020 — Provider zero/negative rate
Priority: P0

Expected:
- reject as invalid source data.

## BE-021 — Cache get raises
Priority: P1

Expected:
- log;
- continue provider path.

## BE-022 — Cache set raises after provider success
Priority: P1

Expected:
- current user still receives valid provider result;
- log cache failure.

## BE-023 — Wrong-pair stale cache exists
Priority: P0

Expected:
- ignored by semantic key.

## BE-024 — Blend cache exists but request is pinned provider
Priority: P0

Expected:
- cache miss; policies never mix.

## BE-025 — Concurrent cold requests for same pair
Priority: P1

Expected:
- duplicate provider calls acceptable initially;
- both results correct;
- no cache corruption.

## BE-026 — Provider publishes new observation between concurrent calls
Priority: P1

Expected:
- each response remains internally coherent;
- cache ends with a valid latest observation.

---

# C. Historical conversion

## BE-027 — Exact historical observation
Priority: P0

Expected:
- requested == effective;
- historical=true.

## BE-028 — Weekend requested date
Priority: P0

Expected:
- previous allowed observation;
- requested/effective both returned.

## BE-029 — Holiday gap within policy
Priority: P0

Expected:
- previous observation allowed and explicit.

## BE-030 — Gap exceeds fallback policy
Priority: P0

Expected:
- historical observation unavailable.

## BE-031 — Future historical date
Priority: P0

Expected:
- validation error before provider call.

## BE-032 — Date before currency lifecycle
Priority: P0

Expected:
- out-of-coverage/suggestion where possible.

## BE-033 — Date after retired currency lifecycle
Priority: P0

Expected:
- out-of-coverage or transition context;
- no current fake quote.

## BE-034 — Provider history starts later than currency existence
Priority: P0

Expected:
- provider coverage governs available quote;
- lifecycle and provider coverage remain distinct.

## BE-035 — Monthly historical series
Priority: P0

Expected:
- granularity=monthly;
- no day-level claim.

## BE-036 — Quarterly provider series
Priority: P1

Expected:
- granularity visible;
- not mixed into daily semantics.

## BE-037 — Historical cache hit
Priority: P0

Expected:
- no provider call;
- observation semantics preserved.

## BE-038 — Historical provider correction
Priority: P1

Expected:
- invalidation/refetch can replace cache;
- persisted old trip projections retain their original quote metadata.

## BE-039 — Finland 1998 + explicit EUR
Priority: P1

Expected:
- suggest FIM;
- do not mutate EUR.

## BE-040 — Archived FIM selected in historical mode
Priority: P1

Expected:
- allowed within supported dates.

## BE-041 — Archived FIM selected in latest mode
Priority: P0

Expected:
- reject current-market interpretation;
- provide historical/transition guidance.

---

# D. Series/chart

## BE-042 — Valid 1Y series
Priority: P1

Expected:
- bounded provider query;
- normalized observations.

## BE-043 — Huge unbounded range
Priority: P0

Expected:
- validation/bounded range.

## BE-044 — Range reversed
Priority: P0

Expected:
- validation error.

## BE-045 — Series includes missing dates
Priority: P1

Expected:
- gaps preserved/normalized;
- no invented daily values.

## BE-046 — Monthly grouping
Priority: P1

Expected:
- cache key contains grouping;
- UI receives granularity.

## BE-047 — Selected date not exact series point
Priority: P0

Expected:
- chart uses historical effective observation semantics.

## BE-048 — Series provider fails
Priority: P1

Expected:
- series stale cache if safe;
- conversion result remains unaffected.

---

# E. Destination context

## BE-049 — Full published context
Priority: P1

Expected:
- payment + prices + provenance.

## BE-050 — Payment context only
Priority: P1

Expected:
- partial context, no fake price cards.

## BE-051 — Prices only
Priority: P1

Expected:
- render available data.

## BE-052 — No context
Priority: P1

Expected:
- explicit empty state;
- conversion unaffected.

## BE-053 — Expired/too-old price data
Priority: P1

Expected:
- suppressed or clearly aging according to policy.

## BE-054 — City price requested, only national data exists
Priority: P1

Expected:
- explicit national scope;
- no city claim.

## BE-055 — City price presented as national
Priority: P0 regression

Expected:
- impossible through scope model/tests.

## BE-056 — Low > high price range
Priority: P0

Expected:
- DB constraint/admin validation rejects.

## BE-057 — Zero/negative price
Priority: P0

Expected:
- reject.

## BE-058 — Converted amount below one item
Priority: P1

Expected:
- structured below-one result.

---

# F. Storytelling

## BE-059 — Full story
Priority: P1

Expected:
- deterministic chapters from sourced facts.

## BE-060 — No StoryMoment
Priority: P1

Expected:
- shorter story; no filler.

## BE-061 — Unpublished StoryMoment
Priority: P0

Expected:
- excluded.

## BE-062 — StoryMoment outside date range
Priority: P0

Expected:
- excluded.

## BE-063 — StoryMoment lacks required provenance
Priority: P0

Expected:
- cannot publish / excluded.

## BE-064 — Historical event near rate movement
Priority: P0

Expected:
- no causal statement unless source explicitly supports causality.

## BE-065 — Then & Now same compatible pair
Priority: P1

Expected:
- directional percentage.

## BE-066 — Then & Now archived currency with no current market
Priority: P0

Expected:
- no fake comparison.

## BE-067 — Story composition fails unexpectedly
Priority: P0

Expected:
- conversion remains successful;
- story unavailable;
- error logged.

## BE-068 — Media licence incomplete
Priority: P0

Expected:
- media not published/displayed.

---

# G. Web/HTMX

## BE-069 — Full page current conversion
Priority: P0

Expected:
- full document.

## BE-070 — HTMX current conversion
Priority: P0

Expected:
- equivalent domain result;
- fragment only.

## BE-071 — Full and HTMX same URL cached
Priority: P0

Expected:
- Vary HX-Request prevents representation mix.

## BE-072 — Rapid request A/B
Priority: P0

Expected:
- obsolete A cannot overwrite B state.

## BE-073 — HTMX validation error
Priority: P0

Expected:
- preserve input;
- field errors;
- no provider call for invalid amount.

## BE-074 — HTMX network failure
Priority: P1

Expected:
- previous safe result remains correctly labelled;
- retry possible.

## BE-075 — JavaScript disabled
Priority: P0

Expected:
- full-submit conversion works.

## BE-076 — Deep link invalid currency
Priority: P0

Expected:
- clean validation/fallback; no 500.

---

# H. Mobile API/offline

## BE-077 — Mobile online current quote
Priority: P0

Expected:
- same application result as web.

## BE-078 — Mobile historical quote
Priority: P0

Expected:
- requested/effective date fields.

## BE-079 — Mobile offline exact cache hit
Priority: P0

Expected:
- cached/offline state.

## BE-080 — Mobile offline wrong pair available
Priority: P0

Expected:
- ignored.

## BE-081 — Mobile offline no matching cache
Priority: P0

Expected:
- OfflineUnavailable.

## BE-082 — Reconnect refresh success
Priority: P1

Expected:
- cached stays visible until authoritative replacement.

## BE-083 — Reconnect refresh failure
Priority: P1

Expected:
- keep cached.

## BE-084 — Device clock wrong
Priority: P1

Expected:
- server fetched/effective metadata governs trust.

## BE-085 — Mobile API receives new optional field
Priority: P1

Expected:
- older client remains compatible.

## BE-086 — Mobile sees unknown future enum
Priority: P1

Expected:
- safe fallback/unknown mapping where enum is extensible.

---

# I. Authentication/ownership

## BE-087 — Anonymous quote
Priority: P0

Expected:
- allowed.

## BE-088 — Anonymous tries authenticated favourite endpoint
Priority: P1

Expected:
- 401.

## BE-089 — User saves favourite
Priority: P1

Expected:
- durable row.

## BE-090 — Duplicate favourite request concurrently
Priority: P1

Expected:
- one row.

## BE-091 — User reads another user's trip ID
Priority: P0 security

Expected:
- 404/forbidden policy without leakage.

## BE-092 — User updates another user's trip
Priority: P0 security

Expected:
- denied.

## BE-093 — User deletes another user's favourite
Priority: P0 security

Expected:
- denied/not found.

## BE-094 — Sign-in local favourite merge
Priority: P1

Expected:
- union/deduplication.

## BE-095 — Malformed local sync payload
Priority: P0

Expected:
- reject bounded validation;
- no partial unexpected rows.

---

# J. Trip concurrency

## BE-096 — Create trip + items success
Priority: P2

Expected:
- one transaction.

## BE-097 — Item creation fails
Priority: P2

Expected:
- whole create transaction rolls back.

## BE-098 — Quote required for trip projection
Priority: P2

Expected:
- provider call before DB transaction.

## BE-099 — Concurrent update matching version
Priority: P2

Expected:
- one success/version increment.

## BE-100 — Concurrent stale update
Priority: P2

Expected:
- 409 Conflict.

---

# K. Import jobs

## BE-101 — REST Countries import success
Priority: P1

Expected:
- validate full snapshot;
- atomic apply.

## BE-102 — REST Countries timeout
Priority: P1

Expected:
- zero canonical changes.

## BE-103 — Source returns suspiciously fewer countries
Priority: P0

Expected:
- reject snapshot unless explicitly approved.

## BE-104 — Same import run twice
Priority: P1

Expected:
- idempotent canonical state.

## BE-105 — Two imports overlap
Priority: P1

Expected:
- scheduler/lock prevents harmful race.

## BE-106 — Import contains one malformed critical record
Priority: P1

Expected:
- according to source policy, reject whole small snapshot rather than silently publish partial canonical data.

## BE-107 — Statistical staging import fails halfway
Priority: P2/R

Expected:
- active prior snapshot remains.

## BE-108 — Import succeeds but cache invalidation fails
Priority: P1

Expected:
- DB state committed;
- log;
- bounded stale cache until TTL/manual invalidation.

---

# L. Database/transaction

## BE-109 — IntegrityError inside atomic
Priority: P0

Expected:
- exception exits atomic;
- rollback;
- no queries attempted in broken block.

## BE-110 — on_commit after success
Priority: P1

Expected:
- callback runs.

## BE-111 — on_commit after rollback
Priority: P0

Expected:
- callback discarded.

## BE-112 — select_for_update used outside transaction
Priority: P0 if introduced

Expected:
- PostgreSQL test catches invalid usage.

## BE-113 — DB outage
Priority: P0 operations

Expected:
- readiness fails;
- DB-backed requests fail safely.

## BE-114 — migration and code incompatible
Priority: P0 deploy

Expected:
- deployment check/rollout catches before normal traffic when possible.

---

# M. Security

## BE-115 — CSRF missing on web mutation
Priority: P0

Expected:
- rejected.

## BE-116 — Arbitrary provider URL supplied by user
Priority: P0

Expected:
- no path exists to use it for server fetch.

## BE-117 — Malicious HTML in editorial/import field
Priority: P0

Expected:
- escaped/sanitized according to field policy.

## BE-118 — SQL injection string in search
Priority: P0

Expected:
- ORM parameterization; treated as text.

## BE-119 — Oversized history range
Priority: P0

Expected:
- bounded validation.

## BE-120 — DRF throttle race
Priority: P1

Expected:
- correctness/security does not depend on exact throttle count.

## BE-121 — Token leaked in logs
Priority: P0 regression

Expected:
- logging redaction tests/policy prevent;
- centralized structured formatter sanitizes event text and exception tracebacks;
- credential-bearing URLs, Bearer tokens and named API/token/password secrets are redacted.

## BE-122 — Source URL uses javascript scheme
Priority: P0

Expected:
- not rendered as trusted external link.

---

# N. Observability/operations

## BE-123 — Provider timeout
Priority: P0

Expected log fields:
- request_id;
- provider;
- operation;
- duration;
- normalized error;
- fallback result.

## BE-124 — User reports request ID
Priority: P1

Expected:
- operator can find corresponding structured log.

## BE-125 — Liveness during Frankfurter outage
Priority: P0

Expected:
- healthy 200.

## BE-126 — Readiness during Frankfurter outage
Priority: P0

Expected:
- healthy if DB/config okay.

## BE-127 — Readiness during DB outage
Priority: P0

Expected:
- 503.

## BE-128 — Import failure
Priority: P1

Expected:
- non-zero exit + structured run summary.

## BE-129 — Cache outage
Priority: P1

Expected:
- service remains correct if provider/DB available.

## BE-130 — Missing required production secret
Priority: P0

Expected:
- fail fast at startup/deploy.

---

# O. API compatibility

## BE-131 — Add optional response field
Priority: P1

Expected:
- v1 remains compatible.

## BE-132 — Rename required response field
Priority: P0 review

Expected:
- considered breaking; do not silently ship.

## BE-133 — Change Decimal string to JSON number
Priority: P0 review

Expected:
- breaking semantic change; reject for v1.

## BE-134 — Change error-code meaning
Priority: P0 review

Expected:
- reject/bump contract.

## BE-135 — OpenAPI generation changes
Priority: P1

Expected:
- CI generated mobile types/diff exposes change.

---

# P. Privacy/data lifecycle

## BE-136 — User clears server history
Priority: P2

Expected:
- owned records deleted;
- cache invalidation if relevant.

## BE-137 — User deletes account
Priority: P2

Expected:
- defined owned-data deletion;
- no dependency on external API.

## BE-138 — Anonymous local history
Priority: P1

Expected:
- never uploaded without explicit sync behavior.

## BE-139 — Logging private trip notes
Priority: P0 regression

Expected:
- prohibited.

---

# Q. Performance

## BE-140 — Destination context N+1
Priority: P1 regression

Expected:
- optimized queryset/query-count test where useful.

## BE-141 — Story page many related facts
Priority: P1

Expected:
- bounded/prefetched reads.

## BE-142 — History chart massive raw data
Priority: P1

Expected:
- server grouping/downsampling.

## BE-143 — Cache miss storm
Priority: P2

Expected:
- correctness intact; metrics guide later coalescing.

## BE-144 — Long transaction
Priority: P0 regression

Expected:
- architecture review rejects provider/network work inside transaction.

---

# R. Future purchasing-power research

## BE-145 — CPI source available
Priority: R

Expected:
- explicit dataset/unit/base-period semantics.

## BE-146 — PPP used as inflation replacement
Priority: P0 methodology regression

Expected:
- rejected.

## BE-147 — Statistical source revised value
Priority: R

Expected:
- new import version/revision metadata; derived values recalculate.

## BE-148 — Geography unavailable
Priority: R

Expected:
- no invented fallback methodology.

---

# Scenario implementation rule

A backend PR references the scenario IDs it implements.

Critical P0 scenarios should become automated tests where technically meaningful.

Not every scenario needs a separate test function; parameterization and layered tests are preferred.

The catalog is a coverage contract, not a mandate for 148 duplicated test cases.


# S. Media and generated imagery

## BE-149 — Country has approved sourced media
Priority: P1

Expected:
- media selector returns published asset;
- source/licence metadata preserved.

## BE-150 — Country has no image
Priority: P0

Expected:
- Quiet Atlas programmatic fallback;
- conversion/context remains complete.

## BE-151 — Historical exact-year archival image
Priority: P1

Expected:
- exact temporal precision exposed;
- attribution available.

## BE-152 — Historical media dated only to decade
Priority: P0 trust

Expected:
- presented as approximate decade/era;
- no invented exact year.

## BE-153 — AI historical illustration available
Priority: P1

Expected:
- generated illustration may be selected below real sourced priority;
- visible AI/authenticity label.

## BE-154 — AI illustration missing label metadata
Priority: P0 trust

Expected:
- cannot publish/use where authenticity could be confused.

## BE-155 — User changes country/year rapidly
Priority: P0

Expected:
- zero image-generation API calls;
- stored media/fallback selection only.

## BE-156 — Wikimedia search unavailable
Priority: P1

Expected:
- editorial import fails;
- existing published media unaffected;
- user request unaffected.

## BE-157 — Europeana media rights unclear
Priority: P0

Expected:
- candidate remains unpublished/rejected.

## BE-158 — Sourced image disappears upstream
Priority: P1

Expected:
- managed approved copy continues if licence permits;
- source audit flags issue;
- no silent provenance removal.

## BE-159 — Generated provider unavailable
Priority: P1

Expected:
- editorial generation job fails/retries according to job policy;
- product readiness/conversion unaffected.

## BE-160 — Generated output contains misleading text/banknote detail
Priority: P0 editorial

Expected:
- review rejects candidate.

## BE-161 — Malicious/invalid image bytes
Priority: P0 security

Expected:
- decoding/type/size validation rejects;
- not publicly served.

## BE-162 — Third-party SVG contains active content
Priority: P0 security

Expected:
- sanitize/rasterize/reject according to implementation policy.

## BE-163 — Media image fails to load
Priority: P1

Expected:
- stable layout + programmatic fallback;
- no conversion error.

## BE-164 — AI provider/model changes
Priority: P1

Expected:
- existing published assets do not silently regenerate;
- new candidates record new provider/model/prompt version.

## BE-165 — Duplicate sourced/generated bytes
Priority: P1

Expected:
- content hash allows duplicate detection/reuse/review.

## BE-166 — Future user-triggered generation duplicate request
Priority: P2

Expected:
- semantic/idempotency key prevents duplicate billable jobs when feature exists.


# T. AI integration and governance

## BE-167 — AI disabled globally
Priority: P0

Expected:
- conversion/history/context/story fallback works;
- no Gemini key required for core app.

## BE-168 — Narrative draft from valid source packet
Priority: P1

Expected:
- Structured Output parses;
- all factual chapters reference supplied fact IDs;
- candidate remains unpublished.

## BE-169 — Narrative returns unknown fact ID
Priority: P0 trust

Expected:
- semantic validation rejects candidate.

## BE-170 — Narrative adds plausible unsupplied fact
Priority: P0 trust

Expected:
- eval/review detects unsupported claim;
- cannot publish as accepted AI draft.

## BE-171 — Model sharpens approximate date
Priority: P0 trust

Expected:
- temporal-precision validator/eval rejects.

## BE-172 — Model asserts causal FX explanation without sourced causality
Priority: P0 trust

Expected:
- reject/flag candidate.

## BE-173 — Source text contains prompt injection instructions
Priority: P0 security

Expected:
- treated as data;
- no tool/action exists;
- generation contract remains unchanged.

## BE-174 — Gemini timeout during live explanation
Priority: P1

Expected:
- normalized timeout;
- cached/deterministic fallback is returned;
- no core product failure.

## BE-175 — Gemini free-tier quota / 429
Priority: P1

Expected:
- no paid escalation;
- cached/deterministic fallback.

## BE-176 — Gemini refusal
Priority: P1

Expected:
- typed refusal state;
- no empty publication;
- no repeated bypass attempts.

## BE-177 — AI structured output schema succeeds but semantics are wrong
Priority: P0

Expected:
- post-schema semantic validation can still reject.

## BE-178 — AI provider unavailable at app startup
Priority: P0 operations

Expected:
- app startup/readiness succeeds when AI is optional/disabled;
- AI capability reports unavailable only when used.

## BE-179 — Missing Gemini key while AI feature enabled
Priority: P0 config

Expected:
- capability/config check fails clearly;
- no secret fallback in code.

## BE-180 — AI call attempted inside DB transaction
Priority: P0 regression

Expected:
- architecture/test/review rejects.

## BE-181 — CI without provider key
Priority: P0

Expected:
- full normal test suite passes with fake adapter;
- zero live billable calls.

## BE-182 — Model routing changes Gemini Flash-Lite → another model
Priority: P1 governance

Expected:
- eval comparison required before promotion.

## BE-183 — Prompt changes without version bump
Priority: P0 governance

Expected:
- review/test convention rejects.

## BE-184 — Generated candidate exceeds length
Priority: P1

Expected:
- deterministic validator rejects/truncates only according to explicit policy; no silent publish.

## BE-185 — Generated output includes unknown URL
Priority: P0 security/trust

Expected:
- reject; only supplied source references are allowed.

## BE-186 — Public demo requests runtime image generation
Priority: P0 cost regression

Expected:
- disabled by configuration;
- stored/sourced media or Quiet Atlas fallback used.

## BE-187 — Development creates a pre-generated AI image
Priority: P1

Expected:
- candidate is reviewed and stored as MediaAsset;
- production page never regenerates it.

## BE-188 — Image-generation provider refusal
Priority: P1

Expected:
- no automatic prompt-obfuscation bypass;
- manual/sourced fallback.

## BE-189 — Moderation flags image
Priority: P0

Expected:
- candidate cannot auto-publish.

## BE-190 — Moderation passes historically false image
Priority: P0 trust

Expected:
- historical/editorial review still required; moderation is not truth validation.

## BE-191 — AI monthly budget ceiling reached
Priority: P1 operations

Expected:
- optional generation disabled;
- core product remains healthy.

## BE-192 — AI cost metadata unavailable
Priority: P2

Expected:
- operation may complete if otherwise valid;
- observability records missing usage;
- no domain failure.

## BE-193 — Duplicate AI job exact same input
Priority: P1

Expected:
- semantic idempotency/reuse policy prevents accidental duplicate billable request unless variant requested.

## BE-194 — Editor intentionally requests another variant
Priority: P1

Expected:
- new variant explicitly generated and separately tracked.

## BE-195 — Source fact corrected after AI story approved
Priority: P0 trust

Expected:
- affected draft/published derived content is flagged needs-review according to source-packet dependency policy.

## BE-196 — Provider model deprecated
Priority: P1 operations

Expected:
- benchmark replacement through eval pipeline;
- existing published content remains unchanged.

## BE-197 — Runtime explanation feature disabled
Priority: P0

Expected:
- no effect on converter; deterministic UI remains complete.

## BE-198 — Future runtime explanation receives private trip notes unexpectedly
Priority: P0 privacy regression

Expected:
- prohibited by payload builder/tests.

## BE-199 — AI capability attempts web-search tool
Priority: P0 architecture regression

Expected:
- no tool configured in P1 path; impossible by adapter contract.

## BE-200 — AI capability attempts autonomous publish/write
Priority: P0 security regression

Expected:
- no action tool/authority exists; publication remains deterministic application action.


---

# V. Authenticated recent-history privacy and ownership

## BE-201 — Sign in with browser-local recent history
Priority: P0 privacy

Expected:
- no recent-history upload occurs merely because authentication succeeded;
- browser-local recents remain local.

## BE-202 — Enable account recent history
Priority: P0 privacy

Expected:
- preference is off by default;
- explicit authenticated POST enables future account recording;
- pre-existing browser-local recents are not imported automatically.

## BE-203 — Duplicate/concurrent recent conversion
Priority: P0 regression

Expected:
- semantic duplicate intent resolves to one account row;
- concurrent writes cannot create duplicate rows;
- newest result metadata wins.

## BE-204 — Account recent-history retention bound
Priority: P1 privacy/operations

Expected:
- at most 50 account-owned recent conversions remain;
- oldest rows are trimmed deterministically.

## BE-205 — User deletes another user's recent conversion ID
Priority: P0 security

Expected:
- 404/forbidden policy without existence leakage;
- target row remains unchanged.

## BE-206 — Account-history persistence failure
Priority: P0 reliability/privacy

Expected:
- successful FX conversion remains valid;
- persistence failure is logged without sensitive payload;
- web recent state falls back to browser-local storage rather than losing the result.
