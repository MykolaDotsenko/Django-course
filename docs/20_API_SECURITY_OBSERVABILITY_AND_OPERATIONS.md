
# API, Security, Observability and Operations

This document defines production-facing backend behavior: API contract, security boundaries, structured failures, health, observability and operational recovery.

---

# 1. API philosophy

The mobile API exists to expose stable product use cases.

It does not expose the database schema.

Good:

~~~text
POST /api/v1/conversions/quote/
GET  /api/v1/countries/
GET  /api/v1/currencies/
GET  /api/v1/destinations/{iso2}/context/
~~~

Avoid:

~~~text
/api/v1/countrycurrency/
/api/v1/storymoment/
/api/v1/typicalprice/
~~~

unless those model-shaped resources become genuine public concepts.

---

# 2. API versioning

Use URL namespace:

~~~text
/api/v1/
~~~

The version is part of the public client contract.

Breaking response/request changes require:

- backwards-compatible extension;
- or explicit v2.

Do not use a query parameter for core version selection.

---

# 3. OpenAPI source of truth

Use drf-spectacular.

Reasons:

- DRF built-in OpenAPI generation is deprecated;
- DRF documentation recommends drf-spectacular;
- mobile types are generated from schema.

CI:

~~~text
generate schema
→ validate schema
→ generate mobile types
→ assert clean diff
~~~

The schema is a deliverable, not incidental documentation.

---

# 4. API serializer strategy

Request serializer:

- parses transport;
- validates field syntax;
- creates command.

Application service:

- owns semantic behavior.

Response serializer:

- serializes result object.

Avoid ModelSerializer for calculation endpoints when no persisted model corresponds to the result.

---

# 5. Decimal API representation

Money/rates are strings.

Example:

~~~json
{
  "amount": "100.00",
  "rate": "174.500000",
  "result": "17450"
}
~~~

Do not send binary float as canonical money.

---

# 6. Dates and timestamps

Date-only:

~~~text
YYYY-MM-DD
~~~

Use for:

- requested_date;
- effective_date.

Timestamp:

- ISO 8601;
- timezone-aware UTC.

Use for:

- fetched_at;
- updated_at;
- verified_at.

---

# 7. Stable error codes

Candidate catalog:

~~~text
validation_error
authentication_required
permission_denied
not_found
conflict
unsupported_currency
unsupported_pair
historical_out_of_coverage
historical_observation_unavailable
rate_unavailable
source_data_invalid
throttled
server_error
~~~

Add code only when client behavior differs meaningfully.

---

# 8. Error envelope

~~~json
{
  "code": "rate_unavailable",
  "detail": "The reference rate is temporarily unavailable.",
  "retryable": true,
  "fields": {},
  "request_id": "01..."
}
~~~

Rules:

- stable code;
- human-readable detail;
- retryable explicit where useful;
- field errors structured;
- request_id always available on API failure.

---

# 9. Validation errors

Example:

~~~json
{
  "code": "validation_error",
  "detail": "Check the highlighted fields.",
  "retryable": false,
  "fields": {
    "amount": [
      "Enter zero or a positive amount."
    ]
  },
  "request_id": "..."
}
~~~

Do not expose Django/Python exception strings directly.

---

# 10. 4xx vs 5xx ownership

4xx:

- client input;
- auth;
- ownership;
- known conflict;
- unsupported semantic request.

5xx/503:

- unexpected server failure;
- DB unavailable;
- transient provider unavailable when no safe stale result exists.

Provider timeout with usable stale quote can still return 200 with status=stale.

---

# 11. Quote endpoint semantics

Quote is computational and repeatable.

Use POST because:

- structured body;
- amount/date/context can grow;
- avoids awkward URL exposure/length;
- not because it mutates server state.

Do not create durable history as hidden side effect.

---

# 12. GET reference endpoints

Countries/currencies:

- public;
- bounded;
- local DB;
- cache validators appropriate.

Potential:

~~~text
ETag
Last-Modified
Cache-Control: public, max-age=...
~~~

Only after behavior is tested with versioning/deployment.

---

# 13. Authentication

Basic conversion remains anonymous.

Authentication is introduced for:

- cross-device favourites;
- trips;
- account preferences.

Exact mobile auth mechanism is deferred until implementation research.

Non-negotiable properties:

- revocable;
- short-lived exposure where possible;
- secure storage on mobile;
- ownership enforced server-side.

Do not invent custom crypto/auth protocol.

---

# 14. Session vs token boundary

Web uses normal Django session auth for PR12A account features. Mutating web requests remain
CSRF-protected, logout is POST-only, account-owned favourite queries are always scoped by
`request.user`, and cross-user delete attempts resolve without exposing another user's object.

Native app will use an explicit API auth method.

Do not send browser session cookie assumptions into mobile architecture.

Shared user identity does not mean shared transport mechanism.

---

# 15. CSRF

Web unsafe requests:

- Django CSRF mandatory;
- HTMX sends token.

Mobile token API:

- does not disable browser CSRF globally;
- has separate authentication semantics.

Never mark broad views csrf_exempt merely for convenience.

---

# 16. CORS

Same-origin web needs no broad CORS.

Native apps are not constrained like browser cross-origin JS.

Keep CORS disabled/restrictive until a real browser-origin API consumer exists.

---

# 17. Security headers

Production target:

- HSTS after HTTPS verified;
- secure cookies;
- HttpOnly where appropriate;
- SameSite policy;
- X-Content-Type-Options;
- frame-ancestor/clickjacking protection;
- Referrer-Policy;
- Content-Security-Policy;
- Permissions-Policy as appropriate.

Do not copy a giant header set without testing required product behavior.

---

# 18. CSP

Target CSP-friendly architecture.

No required:

- inline onclick;
- arbitrary inline scripts;
- third-party CDN scripts;
- eval-like application code.

HTMX hardening can be tested with script/eval processing disabled where compatible.

Source/media domains are explicitly allowlisted.

---

# 19. HTML escaping

Django autoescape stays enabled.

External/editorial text is plain text/structured markup.

Do not mark upstream content safe.

If rich text is ever allowed:

- sanitize with an explicit trusted policy;
- constrain allowed elements;
- test XSS payloads.

---

# 20. URL security

Provider adapters have fixed/configured base URLs.

User-provided source/provenance URLs are links only.

Do not server-fetch arbitrary user URL.

This prevents SSRF class issues.

---

# 21. External HTTP security

Provider client:

- HTTPS only;
- bounded timeout;
- response size sanity;
- no redirects to arbitrary hosts unless deliberately allowed;
- validated content type/schema;
- secrets redacted.

---

# 22. Secret handling

Secrets come from deployment environment/secret manager.

Never:

- commit;
- log;
- expose to Vite;
- expose to Expo;
- include in browser HTML.

Configuration validation fails fast in production.

---

# 23. SQL injection

Use Django ORM/bound SQL parameters.

If raw SQL is needed:

- parameterized only;
- documented query;
- test.

Local Expo SQLite uses parameter binding too.

---

# 24. Object authorization

Query user resources with owner scope.

Example concept:

~~~text
Trip.objects.filter(user=actor).get(id=...)
~~~

Do not:

~~~text
Trip.objects.get(id=...)
then check later in template
~~~

Authorization should fail before presentation.

---

# 25. Mass assignment

DRF serializers explicitly list writable fields.

Do not expose:

- user/owner;
- verification fields;
- publication fields;
- source trust class;

as arbitrary client writable fields.

---

# 26. Admin security

Django admin:

- staff only;
- least privilege;
- source verification fields restricted appropriately;
- publication actions logged where useful.

Do not expose admin publicly without normal production security controls.

---

# 27. Brute force / abuse

DRF throttling can reduce accidental/low-grade abuse.

DRF itself documents that throttling is not a security/DDoS mechanism and may be fuzzy under concurrency.

For meaningful public abuse:

- edge/platform rate limit;
- bot/WAF controls if needed;
- endpoint-specific cost limits.

---

# 28. Expensive endpoint protection

Potentially expensive:

- large history range;
- story search;
- bulk sync;
- authenticated exports.

Protect with:

- maximum range/page size;
- request validation;
- scoped throttles;
- server-side grouping/downsampling.

Do not accept unbounded parameters.

---

# 29. Request ID middleware

At request start:

1. inspect incoming X-Request-ID if allowed;
2. validate max length/format;
3. generate otherwise;
4. bind to log context;
5. return response header.

Use UUID/ULID-like opaque ID.

Implemented request-ID acceptance contract:

- header: `X-Request-ID`;
- accepted length: 1–64 characters;
- accepted characters: ASCII letters/digits plus `.`, `_` and `-`;
- first character must be alphanumeric;
- absent/invalid/oversized values are replaced with a server-generated UUID4;
- the final ID is returned in `X-Request-ID` and bound to structured logs.

Do not put user data into request ID.

---

# 30. Structured log schema

Suggested fields:

~~~text
timestamp
level
environment
service
request_id
route
method
status_code
duration_ms
actor_id optional
error_code optional
provider optional
cache_status optional
db_query_count optional debug/perf
~~~

Use consistent field names.

---

# 31. Privacy in logs

Do not log by default:

- access tokens;
- passwords;
- full authorization headers;
- raw user request bodies;
- private notes;
- exact personal trip content.

For conversion amounts, decide analytics/logging policy explicitly.

Operational debugging usually needs pair/date/status more than amount.

The structured JSON formatter is the final logging safety boundary: event text, string-valued
structured fields and formatted exception tracebacks are sanitized for credential-bearing URLs,
Bearer tokens, API keys/tokens, client secrets and passwords before serialization. Call sites still
must avoid logging raw request bodies or authorization headers; formatter redaction is defense in
depth, not permission to log sensitive data.

---

# 32. Provider observability

Record:

- provider;
- operation latest/historical/series;
- duration;
- status class;
- timeout;
- normalized invalid payload;
- fallback used.

Never log provider secret.

---

# 33. Cache observability

Useful statuses:

~~~text
fresh_hit
miss
stale_hit
set_failed
get_failed
bypass
~~~

Track by cache domain:

- quote;
- series;
- context/story later.

---

# 34. Import observability

Every import run logs:

- source;
- dataset/type;
- started;
- completed;
- fetched count;
- accepted count;
- inserted;
- updated;
- unchanged;
- rejected;
- duration;
- failure class.

This is more useful than print("done").

---

# 35. Error logging levels

Expected user/domain failure:

- usually info/warning;
- no stack trace.

Provider transient:

- warning;
- stack/transport detail server-side as useful.

Unexpected exception:

- error/exception;
- stack trace;
- request ID.

Do not make validation errors look like production incidents.

---

# 36. Health endpoints

Liveness:

~~~text
GET /health/live/
~~~

No dependency checks.

Readiness:

~~~text
GET /health/ready/
~~~

Check:

- settings loaded;
- DB reachable.

Optional cache check only if deployment declares cache required.

No external provider check.

Implemented health responses deliberately expose only generic state. Database exception strings, credentials and host details are not returned to clients.

The access-log baseline records `request.path`, not the full URL, and never records request bodies by default.

---

# 37. Startup checks

Production startup/deploy should fail before traffic if:

- secret key missing;
- invalid allowed hosts;
- DB config missing;
- required API secret missing for enabled import feature;
- build manifest missing where required.

Optional features can remain disabled when their config is absent if explicitly designed that way.

---

# 38. Django system checks

Add custom system checks only for configuration invariants that cannot be reliably covered by settings parsing.

Example:

- incompatible enabled provider setting.

Avoid a custom check framework.

---

# 39. Metrics

Phase 1 can derive metrics from logs/platform.

Core SLO-like signals:

- request error rate;
- p50/p95 quote latency;
- provider timeout rate;
- stale fallback ratio;
- readiness failures;
- DB latency;
- import failure rate.

Do not define unrealistic enterprise SLOs before deployment data exists.

---

# 40. OpenTelemetry

Optional phase 2.

If adopted:

- instrument Django requests;
- HTTP provider call;
- PostgreSQL;
- cache if useful.

Use infrastructure integration.

Do not add tracing calls to pure domain arithmetic.

---

# 41. Performance monitoring

Measure:

- server timing;
- query count;
- slow queries;
- provider time;
- cache effect.

Use Django Debug Toolbar locally if helpful, not in production.

Profiling comes before speculative optimization.

---

# 42. N+1 detection

Critical pages should have query-count expectations/tests where regression risk exists:

- destination context;
- story page;
- saved trips.

Do not assert brittle query count for every trivial view.

---

# 43. Backups

Production PostgreSQL needs platform backup/restore strategy.

Minimum:

- automated backups;
- restore process understood/tested;
- migration rollback/forward-fix awareness.

Cache needs no backup.

---

# 44. Disaster recovery

Priority:

1. restore PostgreSQL;
2. redeploy code/static assets;
3. warm/import replaceable reference data if needed;
4. cache rebuilds naturally.

External imported data can be re-synced.

User-owned data cannot be casually reconstructed, so backups matter.

---

# 45. Deployment strategy

Portfolio-scale baseline:

- one Django service;
- one PostgreSQL;
- optional managed cache;
- static asset serving/CDN;
- platform scheduler.

No Kubernetes requirement.

---

# 46. Static files

Vite outputs static assets.

Django collectstatic/deployment handles:

- fingerprinted build;
- icons/fonts;
- admin static.

Static failure should be detectable at deployment.

---

# 47. Database connection management

Use deployment-appropriate connection settings.

Do not crank CONN_MAX_AGE blindly.

Monitor:

- worker count;
- database connection limit;
- pooling behavior.

If a pooler is introduced, document transaction/session semantics.

---

# 48. Timeouts

Timeout hierarchy should be coherent.

Example intent:

~~~text
provider connect/read timeout
<
Django request timeout
<
reverse-proxy/platform timeout
~~~

The inner operation should fail first and allow controlled fallback.

---

# 49. Graceful shutdown

Web workers should finish/abort requests according to server/platform behavior.

No critical import job should rely on in-process web background thread.

Scheduled commands are separate processes.

---

# 50. Scheduled job failure

A failed import:

- exits non-zero;
- logs run summary;
- preserves previous published data;
- becomes operationally visible.

It does not retry forever inside one invocation.

Scheduler can retry with bounded policy.

---

# 51. API backwards compatibility

Compatible:

- add optional response field;
- add new endpoint;
- broaden enum carefully if client handles unknowns.

Potentially breaking:

- rename field;
- change Decimal string to number;
- change date semantics;
- remove status;
- change error code meaning.

Schema diff belongs in API PR review.

---

# 52. Enum evolution

Mobile may see a newer server enum value.

Generated types help catch build-time changes, but older deployed mobile clients still exist.

For externally evolving enums:

- consider unknown-safe client mapping;
- avoid changing meaning of existing values.

---

# 53. Mobile compatibility window

Server should support currently supported released mobile versions for a documented window once app is public.

Do not deploy breaking v1 behavior because latest app version is already in development.

---

# 54. Data export/privacy

If account data export ships:

- authenticate strongly;
- scope only user's data;
- do not include secrets/internal source credentials;
- generate synchronously only if bounded;
- otherwise later background job architecture may be justified.

---

# 55. Account deletion

Deletion flow should define:

- server-owned personal data;
- favourites;
- trips;
- history;
- auth credentials;
- local-device data guidance.

Deletion completion must not depend on optional external provider availability.

---

# 56. Dependency vulnerability checks

CI should include Python and npm dependency security checks appropriate to tooling.

Do not blindly auto-fix major dependency versions.

Security update still passes functional/contract tests.

---

# 57. Provider incident playbook

If Frankfurter is failing:

1. verify provider errors/latency;
2. inspect stale fallback ratio;
3. confirm no wrong-pair cache issue;
4. consider self-hosted endpoint if preconfigured/tested;
5. communicate degraded reference freshness if public product needs status messaging.

Do not silently switch to a different rate methodology.

---

# 58. Data-source incident playbook

If imported cultural/statistical source becomes wrong/licensing changes:

1. unpublish affected content/media;
2. preserve evidence/source metadata internally as policy allows;
3. invalidate derived cache;
4. correct/reimport;
5. verify before republish.

Conversion remains available.

---

# 59. Migration incident

If schema migration fails:

- stop rollout;
- do not run reference imports;
- inspect migration state;
- restore/forward-fix based on deployment strategy.

Do not manually alter production schema without a corresponding migration record.

---

# 60. Operational acceptance criteria

Production backend is ready when:

- health endpoints behave correctly;
- request IDs appear in logs/API errors;
- provider/cache/DB failures have distinct logs;
- no secrets appear in logs;
- OpenAPI is generated/validated;
- API errors are stable;
- quote timeout fits within request timeout;
- failed imports preserve old data;
- backup/restore story exists;
- optional external providers are not readiness dependencies;
- security headers/CSP pass functional tests.


---

# 61. Execution runbook cross-references

This document defines backend operational semantics.

Use these execution-level runbooks for implementation/release work:

- environment/configuration/secrets: `32_ENVIRONMENT_CONFIGURATION_AND_SECRETS.md`;
- migrations/fixtures/seeding: `33_DATA_MIGRATIONS_FIXTURES_AND_SEEDING.md`;
- release/deploy/rollback: `34_RELEASE_DEPLOYMENT_AND_ROLLBACK_RUNBOOK.md`;
- performance/profiling: `36_PERFORMANCE_BUDGETS_AND_PROFILING.md`.

These documents do not replace the health, incident, security or provider semantics here; they operationalize them.
