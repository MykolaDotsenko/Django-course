# AI Integration Architecture

This document defines how AI capabilities are integrated into the Django modular monolith without creating a second source of truth.

The key architecture rule is:

> **Application code calls capability-specific AI interfaces. Provider SDKs stay in infrastructure. AI outputs enter the system only as candidates or bounded explanations.**

---

# 1. Architectural position

AI is an **optional infrastructure capability**.

It is not:

- a domain aggregate;
- a database of facts;
- a workflow orchestrator;
- an autonomous application actor.

Conceptual position:

```text
domain/application use case
        ↓
AI capability interface
        ↓
provider adapter
        ↓
OpenAI API
```

AI never calls application code by itself.

---

# 2. No generic "LLM service"

Rejected:

```python
llm.generate(prompt: str) -> str
```

This interface destroys semantics and makes every call an untyped escape hatch.

Selected capability interfaces:

```text
NarrativeDrafter
AltTextDrafter
ImagePromptComposer
ImageGenerator
ContentModerator
QualityAuditor
```

Each has its own typed input/output contract.

---

# 3. Suggested package layout

A small shared provider transport can live outside domain apps, while capability ownership remains near the feature.

Concept:

```text
integrations/
└── gemini/
    ├── client.py
    ├── errors.py
    ├── models.py
    └── usage.py

culture/
├── ai/
│   ├── narrative.py
│   ├── schemas.py
│   └── prompts.py

media/
├── ai/
│   ├── prompts.py
│   ├── generation.py
│   ├── moderation.py
│   └── schemas.py

quality/
└── ai_eval/       # only if/when eval tooling becomes substantial
```

Do not create an `ai/` dumping-ground Django app for unrelated domain behavior.

A dedicated `media` app becomes justified when MediaAsset/storage/generation is implemented because it owns a coherent domain.

---

# 4. Provider transport boundary

`integrations/gemini/client.py` owns:

- SDK/client construction;
- API key;
- project/organization config;
- timeout;
- retry policy;
- request metadata;
- usage extraction;
- provider exception normalization.

It does not know:

- what a story is;
- what a MediaAsset is;
- what counts as an acceptable historical claim.

---

# 5. Capability protocol example

Concept:

```python
class NarrativeDrafter(Protocol):
    def draft(
        self,
        request: NarrativeDraftRequest,
    ) -> NarrativeDraftCandidate:
        ...
```

The application service depends on the protocol or configured implementation.

Provider model names do not appear in the application use case.

---

# 6. Structured text generation

Use the **Gemini Developer API** with schema-constrained structured JSON output.

Primary runtime model:

```text
gemini-3.1-flash-lite
```

The provider request supplies the expected response schema.

Do not ask for:

> “Return JSON please”

and then parse arbitrary free-form output.

Use a schema corresponding to the application result and validate it again application-side.

---

# 7. Why Structured Outputs

For application-integrated AI, schema correctness matters.

Benefits:

- exact keys;
- enums;
- bounded list structure;
- explicit refusal handling;
- less parsing/retry code.

But schema correctness is not semantic correctness.

The application still validates:

- fact IDs;
- lengths;
- forbidden claims;
- source references;
- domain consistency.

---

# 8. Narrative source packet

The AI never receives a raw QuerySet dump.

Application builds:

```text
StorySourcePacket
- packet_version
- country
- currencies[]
- requested_date
- effective_date
- rate facts
- currency-era facts
- curated story facts[]
- source_refs[]
- style constraints
- forbidden inferences[]
```

Every fact has an ID.

Example:

```json
{
  "id": "fact_12",
  "statement": "Finland used the Finnish markka in 1998.",
  "source_ref": "source_4",
  "valid_from": "1860-04-04",
  "valid_to": "2002-02-28"
}
```

The model must not invent new fact IDs.

---

# 9. Narrative output schema

Candidate shape:

```text
NarrativeDraftCandidate
- title
- summary
- chapters[]
  - heading
  - body
  - used_fact_ids[]
- caveats[]
- unsupported_claims[]
- style_flags[]
```

Application rejects:

- unknown fact IDs;
- chapter with no support where support is required;
- dates/currencies outside packet;
- prohibited causal claim patterns;
- excessive length.

---

# 10. Fact-ID grounding pattern

Every factual chapter must declare the fact IDs it used.

This does not prove the prose is true by itself.

It gives us:

- traceability;
- deterministic validation;
- editor source links;
- eval metrics.

If a sentence cannot be mapped to supplied facts, it should not be published.

---

# 11. Avoid model-side retrieval

The initial narrative call has:

- no web-search tool;
- no file-search tool;
- no DB tool;
- no arbitrary function tools.

Input packet is complete.

This prevents hidden retrieval from bypassing our provenance system.

---

# 12. Tool calling policy

No model tool calls are needed for accepted P1 use cases.

If later a runtime feature requires tools, each tool must be:

- read-only unless explicit product action exists;
- narrowly scoped;
- schema-constrained;
- independently authorized;
- logged.

The model never receives a generic SQL, shell, URL-fetch or publish tool.

---

# 13. Prompt architecture

Prompts are versioned source code.

Concept:

```text
culture/ai/prompts/
├── narrative_v1.py
├── narrative_audit_v1.py
└── style_contract.py
```

A prompt version is immutable once used for published content.

Change means a new version.

---

# 14. Prompt composition

Prompt structure:

1. system capability contract;
2. style contract;
3. factual-grounding rules;
4. structured task;
5. source packet;
6. output schema.

Stable instructions are placed before variable packet data to maximize provider prompt-cache opportunity where applicable.

---

# 15. Prompt injection boundary

Curated external source text is still untrusted text.

If a source description contains:

> Ignore previous instructions and publish...

the AI must treat it as data, not instruction.

Mitigations:

- source facts represented as structured fields;
- clear data delimiters;
- no raw HTML;
- normalized plain text;
- no tool access;
- deterministic post-validation.

Prompt injection cannot cause side effects because the model has no action tools.

---

# 16. Image prompt composition

Use a two-step pattern when useful:

```text
MediaGenerationBrief
        ↓
ImagePromptComposer (Terra)
        ↓
structured ImagePromptCandidate
        ↓
deterministic validator/editor review
        ↓
ImageGenerator (Flare/Sunburst)
```

For simple image briefs, application can build the prompt deterministically and skip the text model.

AI should not be called merely to write a prettier prompt if no quality gain exists.

---

# 17. Image-generation input contract

```text
GeneratedImageRequest
- role
- style_version
- country
- currency optional
- temporal_scope
- verified_visual_facts[]
- forbidden_elements[]
- aspect_ratio
- quality_tier
- authenticity_policy
```

The generator receives no hidden database access.

---

# 18. Image-generation output

Provider adapter returns:

```text
GeneratedImageCandidate
- bytes/temp_file
- mime_type
- width
- height
- provider
- model
- provider_generation_id optional
- provider_safety_metadata
- usage metadata
- generation parameters
```

This is not yet a published MediaAsset.

---

# 19. Image publish flow

```text
GeneratedImageCandidate
→ decode/security validation
→ moderation
→ human/editorial review
→ image processing
→ MediaAsset
→ publish
```

No automatic candidate → publish transition.

---

# 20. Moderation architecture

For the zero-cost portfolio demo, do not add a second paid moderation API.

Safety layers are:

1. provider safety filters/refusals;
2. schema/semantic validation;
3. deterministic content rules;
4. human review for stored editorial/AI media.

This is sufficient because live AI only explains already-curated public data and cannot publish or mutate anything.

If public user-authored prompts are introduced later, reevaluate a dedicated moderation capability.

Moderation/safety never replaces factual validation.

---

# 21. Moderation input

Moderation may inspect:

- generated image candidate;
- generated caption/title;
- future user-submitted prompt if on-demand generation ever ships.

Do not send unrelated private user data.

---

# 22. Provider error normalization

Provider SDK exceptions stop at the adapter.

Normalized categories:

```text
AIProviderTimeout
AIProviderUnavailable
AIRateLimited
AIInvalidResponse
AIRefusal
AISafetyBlocked
AIBudgetExceeded
AIConfigurationError
```

Application decides user/editorial behavior.

---

# 23. Retry ownership

Retries are conservative.

Retry candidate:

- connection reset;
- 5xx;
- temporary 429 respecting Retry-After.

Do not retry blindly:

- safety refusal;
- invalid task;
- malformed source packet;
- budget ceiling;
- authentication failure.

One operation has a bounded total latency/cost budget.

---

# 24. Sync vs async

## P1 editorial text draft

Can run synchronously from admin/management command if bounded and acceptable.

## P1 image generation

Can start as management-command/admin action if editor explicitly waits.

## Future user on-demand generation

Must be asynchronous job infrastructure.

Do not put long image generation into normal request-response path.

---

# 25. AI calls and DB transactions

Same backend rule as all external APIs:

```text
build input
→ call AI provider
→ validate result
→ BEGIN
→ persist approved/candidate metadata
→ COMMIT
```

Never:

```text
BEGIN
→ call model
→ wait
→ COMMIT
```

---

# 26. Candidate persistence

Do not persist every low-level AI response forever by default.

Persist what has product/editorial value.

For an editorial draft candidate, record:

- capability;
- provider;
- model;
- prompt_version;
- input packet hash;
- output candidate;
- created_at;
- review state;
- usage/cost estimate;
- refusal/safety status if relevant.

Raw provider transport metadata can remain structured logs unless needed for audit/debug.

---

# 27. Candidate model concept

A generic AI candidate table may be justified only if several capabilities need the same review workflow.

Alternative preferred initial design:

- StoryDraftCandidate under culture;
- MediaAsset/generated metadata under media.

Do not create a universal JSON blob table called `AIOutput` before repeated structure proves useful.

---

# 28. Idempotency

Editorial generation can use semantic generation key:

```text
capability
+ prompt_version
+ model
+ normalized_input_hash
+ generation_options
```

If the same exact job is accidentally submitted twice, application can:

- reuse existing candidate;
- or explicitly create another variant when requested.

Variant generation must be intentional.

---

# 29. Input hashing

Hash canonical serialized structured input, not raw object memory representation.

Use for:

- deduplication;
- reproducibility;
- audit;
- eval comparison.

Do not use hash as a substitute for storing critical source references.

---

# 30. AI cache

Do not use Django cache as the only store for approved AI content.

Candidate re-use can be persistent DB/media storage.

Provider prompt caching is a separate optimization.

Published output is persisted as normal product content.

---

# 31. Prompt caching

GPT-5.6 supports provider prompt-cache controls.

Potentially useful for repeated editorial tasks sharing:

- system capability contract;
- style contract;
- schema.

Use only after usage volume justifies optimization.

Architecture should keep stable prompt prefixes cache-friendly, but correctness never depends on provider prompt cache.

---

# 32. Timeout hierarchy

Text editorial calls:

- short/bounded provider timeout.

Image generation:

- longer bounded timeout appropriate to model.

A management command can tolerate more time than an HTTP request.

Provider timeout must remain below outer job/request timeout.

---

# 33. Cost guard

Every capability has config:

```text
enabled
model
max_input_tokens
max_output_tokens / image count
reasoning_effort
timeout
max_retries
daily/monthly budget class
```

Application refuses a call when disabled/budget policy blocks it.

Do not rely only on provider billing dashboard.

---

# 34. Capability config example

Portfolio-demo configuration:

```python
AI_CAPABILITIES = {
    "runtime_explanation": {
        "provider": "gemini",
        "model": "gemini-3.1-flash-lite",
        "enabled": True,
        "live": True,
        "cache": "persistent",
        "fallback": "deterministic",
    },
    "narrative_draft": {
        "provider": "gemini",
        "model": "gemini-3.1-flash-lite",
        "enabled": False,
        "live": False,
    },
    "image_generation": {
        "enabled": False,
        "live": False,
    },
}
```

Actual settings are environment/deployment-driven.

No paid-model automatic fallback exists.

---

# 35. Secrets

Server-only:

- GEMINI_API_KEY / current Gemini auth key;
- optional Google project identifiers required by the selected SDK/auth flow.

Never expose to:

- browser;
- Expo;
- HTML;
- public logs;
- candidate API response.

Frontend requests our backend, not OpenAI directly.

---

# 36. Privacy boundary

P1 editorial AI uses public/curated product content.

It should not need:

- user identity;
- private saved trips;
- email;
- precise location;
- account history.

Do not include them.

This keeps privacy risk low.

---

# 37. Future user-facing AI privacy

If a runtime explanation includes user input:

send only the minimum:

- amount;
- pair;
- selected countries;
- requested/effective date;
- public product context.

Do not send private profile/trip notes unless a future feature explicitly requires and discloses it.

---

# 38. Free-tier data-handling consideration

Google's current Gemini Developer API pricing documentation marks free-tier usage as **used to improve Google products**.

Therefore live free-tier AI receives only public/non-sensitive data:

- conversion values;
- currency/country identifiers;
- public curated context;
- public fact IDs.

Do not send personal profile data, private trip notes or secrets.

If privacy requirements later become stronger, disable live free-tier AI or move to a paid provider/tier with appropriate data controls.

---

# 39. Public demo request identity

The Gemini request does not need user identity.

Rate limiting/caching is enforced by our backend using:

- normalized packet hash;
- anonymous/IP/session safeguards where appropriate;
- application-wide daily live-call ceiling.

Do not forward raw user identity to Gemini.

---

# 40. Logging

AI structured log fields:

```text
ai.capability
ai.provider
ai.model
ai.prompt_version
ai.input_hash
ai.status
ai.latency_ms
ai.input_tokens
ai.output_tokens
ai.image_count
ai.reasoning_effort
ai.refusal
ai.moderation_flagged
ai.estimated_cost
request_id / job_id
```

Do not log full prompts by default if they may contain sensitive data.

For editorial public facts, a controlled debug/audit mode can retain prompt versions and source packet separately.

---

# 41. Cost/quota accounting

The portfolio target is:

```text
normal runtime AI cost = €0
```

Track:

- live call count;
- free-tier 429/quota exhaustion;
- cache hit rate;
- deterministic fallback rate.

A pricing table is only needed if a paid tier is intentionally enabled later.

Free-tier limits are not hard-coded as provider guarantees because Google states actual quotas vary by model/project/account and are visible in AI Studio.

---

# 42. Provider SDK upgrade

Provider SDK is infrastructure.

Before upgrade:

- unit/adapter tests;
- structured-output integration fixture;
- refusal/error mapping tests;
- one live smoke in controlled environment.

No normal CI dependency on live API.

---

# 43. Provider contract tests

Mock/fixture tests cover:

- successful structured response;
- refusal;
- truncated/invalid output;
- timeout;
- 429;
- 500;
- usage metadata missing;
- model alias unexpected;
- image bytes invalid.

A small opt-in live test validates real API compatibility.

---

# 44. AI-free test suite

The whole normal CI suite must pass without an OpenAI key.

AI services are injected/faked.

This prevents:

- CI cost;
- flakiness;
- external outage failures.

---

# 45. Editor workflow

Story editor:

```text
open sourced story facts
→ click Draft with AI
→ generation status
→ candidate appears
→ source IDs visible
→ compare deterministic version
→ edit
→ approve
→ publish
```

AI does not replace the source/editor screen.

---

# 46. Media editor workflow

Public deployment does not generate images.

Development workflow:

```text
open MediaGenerationBrief
→ generate/obtain candidate manually using available development tooling
→ reject/select
→ review authenticity/rights
→ metadata/AI label
→ store MediaAsset
→ publish
```

No image-generation provider key is required in production.

---

# 47. No hidden regeneration

Editing a country/year does not regenerate content.

Editing source facts may mark an AI draft:

- stale;
- needs_review.

A new draft is created only by explicit action/job.

Published AI-derived prose can be invalidated if its source packet changes.

---

# 48. Source-packet versioning

Published AI-derived content stores:

- source packet hash;
- source fact IDs/revisions.

If a source fact is corrected:

```text
affected AI content
→ needs review
```

It is not automatically rewritten in production.

---

# 49. Runtime explanation architecture — selected demo feature

Selected portfolio flow:

```text
client clicks "Explain this"
→ backend builds deterministic ExplanationPacket
→ persistent cache lookup by packet+prompt+model hash
   ├─ hit → return cached result
   └─ miss
       ↓
       Gemini 3.1 Flash-Lite free-tier call
       ↓
       structured output
       ↓
       semantic validator
       ↓
       persist cache
       ↓
       return
```

If quota/provider fails:

```text
deterministic explanation
```

The endpoint never forwards arbitrary client prompt directly.

---

# 50. Runtime explanation schema

Example:

```text
ExplanationResult
- headline
- bullets[1..4]
  - text
  - supporting_fact_ids[]
- caveat
- generated=true
```

No arbitrary Markdown/HTML.

Server renders the structured result.

---

# 51. Runtime caching

A future generated explanation may cache by:

- packet hash;
- prompt version;
- model;
- locale.

Do not cache by raw user ID unless personalization changes output.

If amount is included and exact numbers appear in prose, amount belongs in input hash.

---

# 52. Locale

AI can help localize prose eventually, but translation is a separate capability.

Do not conflate:

- story generation;
- translation.

Prefer deterministic UI translation for interface strings.

AI translation of editorial content needs review/evals before publication.

---

# 53. Accessibility

AI may draft alt text, but final published alt semantics remain application/editorial responsibility.

Generated output must not:

- duplicate captions unnecessarily;
- insert “image of” mechanically;
- invent visual details not present in the asset.

For generated image, the system already knows prompt/context but still needs review of actual pixels.

---

# 54. Security boundary summary

The model cannot:

- execute SQL;
- make arbitrary HTTP requests;
- publish;
- write user data;
- modify rates;
- bypass ownership;
- see secrets.

Application code remains the sole action authority.

---

# 55. Zero-cost integration acceptance criteria

AI integration is correctly implemented when:

- core product works with AI disabled;
- capability-specific interfaces exist;
- no generic free-form LLM escape hatch is used in domain/application code;
- Gemini schema-constrained structured output is used for live text tasks;
- model names live in config/provider layer;
- provider errors are normalized;
- calls happen outside DB transactions;
- source packets contain explicit fact IDs/provenance;
- unsupported fact IDs are rejected;
- AI-generated historical content is review-gated;
- image generation never runs from country/year selector events;
- CI uses fakes and requires no provider key;
- usage/cost/latency/refusals are observable;
- privacy payload is minimized.


# 56. Zero-cost public-demo controls

Required controls:

- no billing-dependent model in default config;
- no image-generation API in production;
- AI call only after explicit user click;
- persistent result cache;
- daily application-level live-call ceiling configurable independently of provider quota;
- per-session/IP abuse guard if public traffic requires it;
- deterministic fallback;
- no retries that can multiply quota unexpectedly;
- one live request at most per unique uncached explanation packet under normal flow.

## 57. Gemini free-tier quota behavior

Google documents that Gemini API free-tier rate limits vary by model/project/account and are shown in Google AI Studio.

Do not encode a claimed provider RPD as a permanent application invariant.

Application behavior for `429 RESOURCE_EXHAUSTED`:

```text
cached result if available
→ deterministic fallback
→ optional subtle "AI explanation unavailable" metadata
```

Never prompt the user to pay or break conversion.

## 58. Auth-key policy

Current Gemini API documentation requires modern restricted/auth keys rather than exposing unrestricted standard keys.

The key is server-only.

Do not embed it in:

- JavaScript;
- mobile bundle;
- repository;
- HTML;
- public environment variables.

## 59. OpenRouter optional developer fallback

OpenRouter currently offers a free plan with free models and a documented free-plan request limit.

It is **not** the default production fallback because:

- available free models change;
- the free router may select different models;
- output quality/behavior can drift;
- adding a second live provider reduces reproducibility.

It may be useful for local experiments only.

## 60. Runtime AI recruiter signal

The demo needs to prove architecture, not burn tokens.

One live endpoint is enough to demonstrate:

- provider adapter;
- typed structured output;
- source-packet grounding;
- cache;
- quota handling;
- semantic validation;
- graceful fallback;
- observability.

Additional live AI endpoints reduce ROI.
