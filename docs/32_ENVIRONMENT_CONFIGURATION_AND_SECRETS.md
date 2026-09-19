# Environment, Configuration and Secrets Contract

Status: **configuration contract**

This document defines how configuration differs by environment and how secrets enter the application.

The current legacy settings module contains development-only hardcoded values. Implementation PR 1 must replace that with the target configuration model described here.

---

# 1. Environments

The product recognizes these execution contexts:

- **local** — developer machine;
- **test** — deterministic automated tests/CI;
- **preview/staging** — deployed validation environment when introduced;
- **production** — public product runtime.

Do not infer environment solely from hostname.

Use explicit configuration.

---

# 2. Twelve-factor boundary

Configuration that changes between deployments belongs outside source code.

Examples:

- secret keys;
- database connection;
- allowed hosts;
- provider credentials;
- cache connection;
- storage credentials;
- feature flags;
- AI model/provider configuration.

Stable product/domain constants stay in code.

Do not convert every constant into an environment variable.

---

# 3. Secrets

Secrets must:

- enter through environment/approved deployment secret storage;
- never be committed;
- never be written to logs;
- never be sent to browser/mobile clients unless they are explicitly public client identifiers;
- be replaceable without code changes.

Examples when implemented:

```text
DJANGO_SECRET_KEY
DATABASE_URL credentials
object-storage credentials
GEMINI_API_KEY
future authenticated provider keys
```

---

# 4. Non-secret configuration

Examples:

```text
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
FRANKFURTER_BASE_URL
AI_PROVIDER
AI_TEXT_MODEL
AI_RUNTIME_EXPLANATION_ENABLED
AI_EDITORIAL_GENERATION_ENABLED
AI_IMAGE_GENERATION_ENABLED
AI_FALLBACK_MODE
```

A value being non-secret does not mean it should be user-controlled.

---

# 5. Startup validation

Production startup must fail fast for missing configuration required for correctness/security.

Examples:

- missing Django secret;
- malformed database URL;
- invalid allowed-host configuration;
- production DEBUG enabled;
- enabled capability missing required provider credential.

Optional dependencies must **not** become readiness requirements.

Example:

- AI explanation disabled → no Gemini key required;
- media enrichment disabled → no media-provider key required.

---

# 6. Feature flags

Flags are for deployment/safety boundaries, not permanent branching around unfinished architecture.

Good:

```text
AI_RUNTIME_EXPLANATION_ENABLED
AI_IMAGE_GENERATION_ENABLED
```

Avoid:

```text
USE_NEW_SERVICE_V2_TEMP_FINAL
USE_DIFFERENT_ROUNDING
IGNORE_SECURITY_CHECK
```

A flag must not allow two conflicting domain truths.

---

# 7. Test configuration

Tests must default to:

- no internet;
- fake provider adapters;
- deterministic cache;
- deterministic time where needed;
- disposable database;
- no real email/payment/AI side effects;
- predictable static/media storage.

CI secrets should not be necessary for the normal test suite.

---

# 8. Local development

Local setup should work with the minimum secrets possible.

Target developer experience after foundation:

```text
copy example environment
install dependencies
start PostgreSQL or documented local DB
migrate
load minimal development seed data
run server
```

Implementation PR 1 must provide the exact canonical commands and an example environment file once the final settings/package structure exists.

Do not publish an `.env.example` whose variables are not actually consumed by code.

---

# 9. Provider endpoints

Provider base URLs may be configurable for:

- contract-test servers;
- preview/testing;
- controlled migration.

Production defaults must point to the documented provider.

Changing an endpoint must not silently change domain semantics.

---

# 10. Logging configuration

Configuration may control:

- log level;
- structured log output;
- request ID integration.

Never enable payload logging that exposes:

- secrets;
- auth tokens;
- personal notes;
- unnecessary user identifiers;
- provider credentials.

---

# 11. Mobile configuration

The mobile client may receive only public configuration required to locate/use the API.

Private provider keys remain server-side.

Build-time/public mobile configuration must be explicitly separated from server secrets.

---

# 12. Production settings baseline

Production must eventually enforce:

- `DEBUG=False`;
- explicit allowed hosts;
- secure session/CSRF cookie policy;
- HTTPS/proxy settings;
- HSTS after HTTPS is verified;
- production database;
- static/media storage strategy;
- deterministic health/readiness behaviour.

Exact deployment-platform values belong in the release/deployment runbook, not in domain code.

---

# 13. Configuration change checklist

A PR introducing configuration must answer:

- Is it secret?
- Which environments need it?
- Is there a safe default?
- What happens when missing/malformed?
- Does enabling it add an external dependency?
- Does readiness change?
- Does it affect privacy/security?
- Does documentation/example configuration need updating?

---

# 14. Implemented foundation boundary

The foundation now consumes security-sensitive Django configuration through `config.environment.load_runtime_config()`.

Canonical variables implemented at this stage:

```text
APP_ENV
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DJANGO_SECRET_KEY
```

Rules:

- `APP_ENV` is explicit and limited to local/test/preview/production;
- local can start without a committed secret and receives an ephemeral process key;
- normal test/CI requires no secret credential;
- preview/production require an explicit secret and allowed hosts;
- preview/production reject `DEBUG=True`;
- preview/production reject wildcard hosts;
- malformed booleans, hosts or environment names fail fast;
- production session/CSRF cookies are marked secure;
- `.env.example` contains only variables the application actually consumes;
- arbitrary `.env` files are not silently loaded into production configuration.

Database configuration remains the responsibility of the following PostgreSQL foundation slice.
