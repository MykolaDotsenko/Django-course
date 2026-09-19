# Test Strategy and Requirement Traceability

Status: **quality execution contract**

This document converts product/backend scenarios into a predictable test system.

The goal is not maximum test count.

The goal is:

> **fast feedback for pure rules, strong boundary tests for integration risk, and a small browser suite for user-critical flows.**

---

# 1. Traceability model

Every meaningful test should protect at least one of:

- product acceptance criterion;
- UX state transition;
- domain invariant;
- BE-* backend scenario;
- security/accessibility requirement;
- previously observed regression.

For non-trivial features, the PR description should identify the governing IDs/doc sections.

Do not invent duplicate requirement IDs in test code when existing user-case / BE-* IDs already describe the behaviour.

---

# 2. Test layers

## Layer A — pure domain/unit tests

Use for:

- Decimal FX calculation;
- rounding;
- date/temporal rules;
- country/currency validity;
- stale semantics;
- cache-key semantics;
- price-equivalent calculations;
- story selection/composition rules;
- media selection rules.

Properties:

- no database when not required;
- no network;
- milliseconds;
- exhaustive edge cases.

## Layer B — application/use-case tests

Use for orchestration:

- provider call + domain normalization;
- cache/fallback decisions;
- transaction boundaries;
- persistence of user-owned state;
- import validation/apply behaviour.

External providers are faked at their adapter boundary.

## Layer C — Django integration tests

Use for:

- ORM constraints;
- migrations where needed;
- forms/views;
- authorization;
- HTMX partial/full responses;
- cache integration;
- static/template wiring;
- management commands.

## Layer D — provider contract tests

Use representative stored payloads.

Validate:

- expected payload shape;
- malformed/partial payload rejection;
- normalization;
- source/effective-date metadata;
- upstream error mapping.

Normal CI makes **zero live provider calls**.

## Layer E — browser E2E

Use Playwright for the small set of high-value flows:

- first conversion;
- swap;
- invalid amount;
- stale/provider recovery;
- bilateral desktop layout;
- mobile stacked flow;
- historical exact/fallback date;
- keyboard flow;
- favourites/history when shipped.

Do not recreate all domain edge cases in the browser.

## Layer F — accessibility QA

Automated:

- axe scans on important states;
- semantic/template assertions where useful.

Manual:

- keyboard-only flow;
- focus order after HTMX swaps;
- screen-reader-oriented review;
- zoom/reflow;
- reduced motion.

Automated checks do not prove WCAG conformance.

---

# 3. Test naming

Test names should describe behaviour, not implementation.

Good:

```python
test_weekend_request_reports_effective_observation_date()
test_unknown_country_uses_local_value_media_fallback()
test_user_cannot_delete_another_users_favourite()
```

Avoid:

```python
test_service_method()
test_model_works()
test_view_2()
```

---

# 4. Given / When / Then discipline

Complex tests should read as:

```text
Given: known state/provider payload
When: use case/action runs
Then: observable contract/invariant holds
```

Avoid asserting private implementation details unless the detail itself is the documented contract.

---

# 5. Provider fixtures

Provider fixtures represent boundary examples, not a mirror of the upstream API.

Rules:

- small;
- deterministic;
- human-reviewable;
- no secrets;
- no giant raw dumps;
- include valid + malformed + missing-field cases;
- preserve enough metadata to verify source/effective-date semantics.

Record the upstream API/version and review date in the adapter documentation/tests where useful.

---

# 6. Database test data

Prefer explicit builders/helpers over large global database fixtures.

Test setup should reveal the facts relevant to the scenario.

Good:

```python
country = make_country(code="FI")
currency = make_currency(code="EUR")
link_country_currency(country, currency, valid_from=...)
```

Avoid opaque seed datasets where a test passes because unrelated records happen to exist.

Do not add a third-party factory framework until repeated setup complexity justifies it.

---

# 7. Time-dependent tests

Never depend on the developer/CI wall clock for business semantics.

Inject or freeze time at the relevant boundary.

Always test:

- timezone-aware timestamps;
- date boundaries;
- weekend/holiday observation fallback;
- cache freshness vs physical retention;
- historical requested date vs effective date.

---

# 8. Money tests

Financial tests must use `Decimal`.

Include:

- very small amount;
- normal amount;
- configured maximum;
- excessive precision;
- zero/negative rejection where required;
- same-currency path;
- rate inversion only where explicitly supported;
- rounding at currency-display boundary.

Never assert financial truth using binary float arithmetic.

---

# 9. Regression-test rule

Every confirmed bug should add a regression test at the **lowest layer that reproduces the invariant failure**.

Examples:

- wrong calculation → domain test;
- ownership bypass → Django/API authorization test;
- stale response race → browser/integration test;
- malformed provider accepted → adapter contract test.

Do not default every regression to E2E.

---

# 10. CI lanes

## Fast lane

Expected on every implementation PR:

```text
Django/system checks
lint/format
type checks when configured
unit/application/integration tests
migration drift check
```

## Browser lane

Run separately for UI/high-risk paths:

```text
Playwright smoke
responsive screenshots where relevant
axe critical states
```

## External smoke lane

Manual/scheduled only:

- real provider health smoke;
- live AI eval;
- deployment smoke.

Failures in live external smoke must not make deterministic unit tests flaky.

---

# 11. Coverage

Coverage is a diagnostic, not a target to game.

Prioritize:

- financial/domain branches;
- failure/fallback branches;
- permissions;
- historical temporal cases;
- provider validation;
- migrations/import safety.

A high line percentage with missing invariants is weak coverage.

Introduce a numeric CI threshold only after the target project shell and baseline suite are stable.

---

# 12. Flaky-test policy

A flaky test is a defect.

Do not:

- add arbitrary sleeps;
- retry indefinitely;
- mark flaky tests skipped without ownership.

Instead identify:

- unawaited async/browser state;
- wall-clock dependency;
- shared mutable fixture;
- network dependency;
- race condition;
- nondeterministic ordering.

Temporary quarantine requires a tracked issue and explicit reason.

---

# 13. Traceability checklist per PR

For each acceptance criterion, reviewers should be able to answer:

- Which test protects it?
- At what layer?
- Is the test deterministic?
- Is failure meaningful?
- Is the same invariant redundantly reimplemented in another layer?

Where the answer is “no test”, explain why the criterion is validated manually.

---

# 14. Test data authenticity

Test fixtures may be synthetic, but they must not teach incorrect domain semantics.

Historical/cultural provider fixtures should clearly separate:

- invented test identifiers/amounts;
- real sourced facts;
- illustrative media.

Do not accidentally turn a synthetic fixture into user-facing canonical content.

---

# 15. Definition of a healthy suite

The suite is healthy when:

- fast tests dominate count;
- browser tests protect only high-value journeys;
- no normal test requires internet;
- providers are isolated by fixtures/fakes;
- failures point toward a specific invariant;
- developers can run the relevant subset quickly;
- full CI remains predictable enough to trust.
