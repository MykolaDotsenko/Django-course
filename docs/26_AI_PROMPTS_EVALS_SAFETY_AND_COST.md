# AI Prompting, Evaluation, Safety and Cost Governance

This document defines how AI behavior is tested, promoted, monitored and paid for.

The core rule is:

> **A prompt/model pair is production code. It changes only through evaluation, review and versioned rollout.**

---

# 1. Prompt as versioned code

Every production prompt has:

- capability;
- prompt version;
- schema version;
- style version where relevant;
- owner/domain;
- representative eval set;
- change history.

Example:

```text
culture.narrative:v3
media.image_prompt:v2
media.alt_text:v1
```

Do not edit a production prompt in an admin text box without source control/versioning.

---

# 2. Prompt anatomy

Recommended text prompt sections:

1. role/capability;
2. non-negotiable truth rules;
3. task;
4. output schema;
5. style constraints;
6. forbidden behavior;
7. structured source packet.

Avoid a giant generic system prompt shared by every capability.

Capability-specific prompts are easier to evaluate.

---

# 3. Stable prompt prefix

Keep reusable instructions stable and place variable data later.

Benefits:

- easier review;
- easier diff;
- potential prompt caching;
- less accidental behavior drift.

Do not optimize prompt structure for caching at the cost of clarity.

---

# 4. Prompt length discipline

Do not repeat the same instruction in five ways.

Prompt should be the smallest text that reliably preserves:

- source grounding;
- schema;
- tone;
- safety boundaries.

Long prompts are not automatically safer.

---

# 5. Fact packet quality precedes model quality

A stronger model cannot fix bad source packets reliably.

Evaluation must distinguish:

- packet/data bug;
- prompt bug;
- model bug;
- validator bug.

If source facts are incomplete, fix source data rather than asking the model to “use its knowledge”.

---

# 6. Structured output validation

Structured Outputs guarantees shape, not truth.

Post-generation validators must verify:

- all referenced fact IDs exist;
- values/enums are expected;
- text lengths;
- source IDs;
- temporal/currency constraints;
- forbidden claim patterns;
- no unknown URLs;
- no HTML when plain text expected.

Failed semantic validation means candidate rejection.

---

# 7. Narrative factual-support score

For each factual clause in generated draft:

```text
supported by supplied fact(s)
or
unsupported
```

Target for publishable candidate:

> **100% factual claims supported by the supplied packet.**

If the model adds a plausible but unsupplied fact, that is a failure.

---

# 8. Causality evaluation

Historical prose often overstates causality.

Bad:

> The currency fell because event X happened.

Allowed only if a supplied source explicitly supports that causal relationship.

Otherwise use neutral chronology:

> During the same period, event X occurred.

Eval set must include tempting correlation examples.

---

# 9. Temporal precision evaluation

Test model with:

- exact day;
- year-only fact;
- decade;
- approximate “circa”;
- range;
- unknown.

Model must not sharpen precision.

Example failure:

```text
source: "during the 1970s"
output: "in 1975"
```

---

# 10. Currency-lifecycle evaluation

Test:

- retired currency;
- euro transition;
- parallel/accounting transition periods;
- current vs historical status;
- unavailable provider coverage.

AI must not convert lifecycle metadata into unsupported rate claims.

---

# 11. Stereotype evaluation

Country prompts/drafts are tested for stereotypical shortcuts.

Examples:

- Finland → sauna/reindeer when unrelated;
- Japan → geisha/cherry blossom when unrelated;
- France → Eiffel Tower when unrelated.

The model can use a cultural detail only when the supplied context makes it relevant.

---

# 12. Sensitive-history evaluation

Use cases involving:

- war;
- disaster;
- persecution;
- colonial violence;
- political repression.

AI output should be:

- sober;
- source-grounded;
- non-sensational;
- free of decorative fictionalization.

For imagery, prefer no AI reconstruction.

---

# 13. Alt-text evaluation

Test:

- decorative image;
- archival photo;
- currency artifact;
- generated illustration;
- image with visible text;
- uncertain content.

Failures include:

- invented visible objects;
- repeating caption word-for-word;
- unnecessary “image of” prefix;
- omitted relevant content;
- hiding AI authenticity in alt rather than visible UI.

---

# 14. Image prompt evaluation

Evaluate prompt composer for:

- factual constraints preserved;
- no new historical details;
- no stereotypes;
- no generated text in image;
- style consistency;
- correct aspect ratio/role;
- forbidden-elements included.

Prompt quality can be evaluated before paying for image generation.

---

# 15. Image candidate evaluation

Human/eval rubric:

| Criterion | Weight |
|---|---:|
| factual/context fidelity | 25 |
| no misleading historical detail | 20 |
| Quiet Atlas style | 15 |
| composition/usefulness | 15 |
| stereotype avoidance | 10 |
| visual defects/text artifacts | 10 |
| accessibility/crop suitability | 5 |

A beautiful but historically misleading image fails regardless of total aesthetic score.

---

# 16. Model routing evals

For the portfolio demo, the production comparison is deliberately simple:

```text
Gemini 3.1 Flash-Lite
vs
deterministic fallback
```

Optional development benchmarking may compare:

- Gemini 3.8 Flash free tier;
- OpenRouter free models;
- paid models manually.

Do not add a paid runtime model unless free-tier quality demonstrably fails a recruiter-visible requirement.

---

# 17. Golden eval dataset

Create a versioned local eval set with representative cases.

Suggested first set:

- Finland/FIM 1998;
- Finland euro transition;
- Germany/DEM transition;
- Japan current JPY;
- UK/GBP historical example;
- USD cross-country current example;
- weekend historical rate;
- archived currency;
- sparse source packet;
- conflicting/ambiguous source candidate;
- sensitive historical context;
- no-image fallback;
- stereotype bait;
- prompt-injection-like source text.

The dataset uses licensed/synthetic/small test fixtures where necessary.

---

# 18. Eval case structure

Concept:

```text
EvalCase
- id
- capability
- input_packet
- expected_invariants
- prohibited_claims
- expected_fact_ids
- style expectations
- notes
```

Do not hard-code one exact natural-language answer when multiple good answers exist.

---

# 19. Deterministic assertions

Automatable:

- JSON schema valid;
- no unknown fact IDs;
- no forbidden currencies/dates;
- bounded lengths;
- no URL not in source set;
- no HTML;
- required label;
- all expected structural fields.

These run in CI against stored model outputs or controlled eval runs.

---

# 20. Model-based evaluation

An AI judge may help score style/semantic quality.

But do not use one model's score as sole promotion gate.

Use:

- deterministic validators;
- human sample;
- model-based scoring as supplementary.

For critical factual support, deterministic source mapping dominates.

---

# 21. Human evaluation

Before promoting a model/prompt change:

- inspect representative outputs;
- inspect all failures;
- inspect sensitive cases;
- inspect several image candidates.

Small curated eval sets have higher ROI than a huge unreviewed synthetic benchmark.

---

# 22. Promotion thresholds

Example text-generation thresholds:

- schema success: 100%;
- unknown fact IDs: 0%;
- unsupported factual claim rate: 0% on critical eval;
- temporal-precision violations: 0;
- prohibited causal inference: 0;
- human tone acceptance: >=95%;
- cost/latency within capability budget.

Thresholds can tighten with maturity.

---

# 23. Regression policy

A new model can improve average style but still fail promotion if it introduces one critical trust regression.

Examples:

- invents exact date;
- drops AI image label;
- adds unsupported causal claim.

Trust metrics are hard gates.

---

# 24. Eval recording

Record for each evaluation run:

- eval dataset version;
- capability;
- provider/model;
- prompt version;
- schema version;
- reasoning effort;
- output;
- deterministic results;
- human/model scores;
- token/image usage;
- estimated cost;
- latency.

This allows historical comparison.

---

# 25. No live-model call in normal CI

Normal CI:

- validates prompts/schemas;
- tests adapters with fixtures;
- runs validators against stored outputs.

Live AI eval:

- explicit command;
- scheduled/manual;
- model-upgrade PR;
- controlled cost.

A provider outage does not block unrelated PRs.

---

# 26. Live eval command

Candidate:

```text
python manage.py run_ai_eval \
  --capability narrative_draft \
  --model gpt-5.6-terra \
  --dataset core-v1
```

Outputs:

- score summary;
- failures;
- usage;
- estimated cost;
- comparison to baseline.

No automatic model promotion.

---

# 27. Prompt diff review

PR changing prompt should show:

- old/new prompt version;
- reason;
- eval result;
- example changed outputs;
- cost/latency impact.

A prompt-only change can be behaviorally larger than a Python refactor.

---

# 28. Safety layers

Safety is layered:

```text
input policy
→ structured bounded prompt
→ provider safeguards
→ product moderation
→ semantic validator
→ editorial review
→ publication constraints
```

No one layer is treated as perfect.

---

# 29. Moderation is not factual validation

Moderation answers safety/content categories.

It does not answer:

- is this year correct?
- is this photo really Helsinki?
- is this licence valid?
- did event X cause the rate move?

Keep safety and truth validation separate.

---

# 30. Prompt-injection evaluation

Test source text containing:

- “ignore previous instructions”;
- fake JSON;
- model/provider instructions;
- embedded URLs;
- fake fact IDs.

Expected:

- treated as source text/data;
- no behavior change;
- no tool call because none exists;
- unsupported instruction not surfaced in output.

---

# 31. Output injection / HTML

Generated prose is plain text structured fields.

Django autoescaping remains enabled.

Do not ask AI to emit trusted HTML.

If rich editorial formatting is later needed:

- use a constrained semantic structure;
- render HTML ourselves.

---

# 32. Model refusal behavior

A refusal is a normal typed outcome.

Application behavior:

- log;
- mark candidate blocked/refused;
- do not retry repeatedly;
- show editor actionable status.

A refusal never becomes an empty published field.

---

# 33. Safety false positives

If a historical topic is blocked despite legitimate editorial intent:

- editor can use manual writing/sourced media;
- do not bypass provider safety through prompt obfuscation;
- evaluate another approved model/provider only through governance.

Core product remains unaffected.

---

# 34. Cost model

Portfolio target:

> **€0/month normal AI runtime cost.**

Track:

- free-tier live calls;
- persistent-cache hits;
- provider 429/quota exhaustion;
- deterministic fallbacks;
- any accidental paid configuration.

A paid model is off by default and must never be reached automatically.

---

# 35. Current free-tier anchor

At research date, Google's Gemini Developer API pricing lists **Gemini 3.1 Flash-Lite input and output as free of charge on the Free Tier**.

Google also documents that free-tier usage limits vary by model/project/account and should be checked in AI Studio.

Therefore architecture relies on:

- quota-aware failure handling;
- cache;
- deterministic fallback;

not on a promised fixed number of requests per day.

---

# 36. Cost-per-approved-artifact

More meaningful than cost per call:

```text
total generation/evaluation cost
÷
number of approved useful outputs
```

For image generation:

- 10 cheap rejected candidates may cost more than one strong final generation.

Measure acceptance rate.

---

# 37. Default portfolio budget strategy

Default production policy:

- live text: Gemini 3.1 Flash-Lite Free Tier only;
- stories: deterministic/pre-generated stored content;
- image candidates: generated manually/offline during development;
- final images: stored assets;
- no background mass generation;
- no paid API key required.

Budget target remains €0.

If a developer intentionally benchmarks a paid model, that is a one-off development expense, not product runtime.

---

# 38. Quota ceilings

Because default runtime is free-tier only, configure:

- application daily live-call ceiling;
- per-session/IP guard where needed;
- maximum retries = 0 or one tightly bounded retry;
- persistent cache before provider call.

When application or provider quota is exhausted:

- stop live AI calls;
- serve cached/deterministic output;
- core product stays available.

No paid overflow.

---

# 39. No paid escalation

Do not implement:

```text
Gemini free quota exhausted
→ paid Gemini
→ OpenAI
→ another paid provider
```

Selected behavior:

```text
Gemini free unavailable
→ cached output
→ deterministic fallback
```

This guarantees predictable demo cost.

---

# 40. Token budgets

Each text capability defines:

- max source facts;
- max input size;
- max output tokens;
- reasoning effort.

Reject/trim at application layer using semantic rules.

Do not rely only on model context maximum.

---

# 41. Source packet truncation

Never truncate factual packet blindly by character count.

If packet too large:

- rank facts deterministically by relevance;
- split story;
- ask editor;
- create chapters from subsets.

Dropping a critical source fact silently can change meaning.

---

# 42. Provider prompt caching

Use provider prompt caching only when repeated stable prefixes make it valuable.

Measure:

- cached tokens;
- cost savings;
- latency savings.

Do not redesign source packets solely to chase cache hits.

---

# 43. Image cost control

Public demo:

```text
runtime image-generation cost = €0
```

Controls:

- image API disabled in production;
- pre-generate a small curated set during development;
- reuse stored MediaAsset;
- sourced archive media preferred;
- no auto-regenerate on deploy;
- no generation on page view/selector change.

---

# 44. Image generation policy

No production image-model tier is selected because current relevant Gemini image-generation API pricing lists no Free Tier.

Development can use whichever manually available tool/provider gives the best one-off result.

The final application only sees reviewed stored media.

---

# 45. Storage cost

Published image bytes and derivatives have storage/CDN cost.

Avoid storing:

- all rejected variations indefinitely;
- unnecessary 4K masters;
- duplicate hashes.

Candidate retention policy can delete old rejected images after review window.

---

# 46. AI usage in development

Developers should have:

- fake AI provider by default;
- optional real provider via env key;
- commands for one controlled live call.

App startup does not require AI credentials unless an explicitly enabled AI feature needs them.

---

# 47. Production feature flags

AI capabilities have explicit enabled state.

Example:

```text
AI_NARRATIVE_DRAFT_ENABLED=true
AI_IMAGE_GENERATION_ENABLED=false
AI_RUNTIME_EXPLANATION_ENABLED=false
```

Disabled capability returns a defined unavailable state.

---

# 48. Fail-open vs fail-closed

Editorial assist:

- fail open to manual/deterministic workflow.

Moderation before AI-generated media publication:

- fail closed; do not publish if required moderation/review cannot complete.

Core FX:

- unrelated to AI.

---

# 49. Privacy data minimization

Do not send:

- auth tokens;
- email;
- name;
- exact street address;
- private notes;
- unrelated analytics;
- full account history.

Send only fields needed for the AI capability.

---

# 50. Free-tier provider data use

Google currently marks Gemini Developer API Free Tier content as used to improve Google products.

Therefore the live demo AI payload contains only non-sensitive/public product data.

Before sending any personal/private data:

- disable free-tier AI for that feature;
- reassess paid/data-control options;
- update privacy documentation.

The current design needs no personal data.

---

# 51. Sensitive user data

No current AI capability needs sensitive personal data.

Therefore P0/P1 policy:

> Do not send sensitive/personal profile data to AI.

If future use requires it, that is a separate privacy/security decision and ADR.

---

# 52. Observability dashboards

Useful aggregate views:

- live calls by capability;
- cache hit rate;
- free-tier 429/quota exhaustion;
- deterministic fallback rate;
- p50/p95 latency;
- schema/semantic validation failures;
- any non-zero paid spend alert.

For this demo, zero-cost compliance is itself an operational metric.

Avoid dashboards containing full prompt/user content by default.

---

# 53. Alerting

Potential alerts:

- spend exceeds threshold;
- provider error rate spike;
- structured-output validation spike;
- refusal spike;
- image generation suddenly much slower;
- model alias behavior changes;
- unsupported-claim eval regression.

No need for enterprise alerting platform initially.

---

# 54. Model-deprecation response

When provider deprecates a model:

1. identify capabilities using it;
2. benchmark replacement;
3. run eval dataset;
4. update config;
5. preserve old published outputs;
6. update references/ADR;
7. remove old model only after rollout.

Do not mass-regenerate content because a model was retired.

---

# 55. Multi-provider fallback threshold

For the portfolio demo, prefer **no second production provider**.

Add one only when one of these occurs:

- unacceptable sustained outage risk for a user-facing AI feature;
- cost difference materially changes economics;
- primary provider repeatedly fails a quality category;
- regulatory/data-residency need;
- specific capability is clearly stronger elsewhere.

Until then abstraction is enough.

---

# 56. Fine-tuning

No fine-tuning initially.

Reasons:

- prompt + structured source packet should solve current tasks;
- small editorial volume;
- changing product style;
- strong base models.

Consider only when:
- stable high-volume repeated task;
- eval set exists;
- prompt improvements plateau;
- measurable quality/cost benefit.

---

# 57. RAG/vector database

No vector database initially.

We already know the relevant structured facts by:

- country;
- currency;
- date;
- story category.

SQL/domain queries provide precise retrieval.

Do not add embeddings just because the product uses AI.

Vector search becomes justified only when editors/users need semantic retrieval across a genuinely large unstructured corpus.

---

# 58. Embeddings

Potential future use:

- near-duplicate editorial fact detection;
- semantic media/story search.

Not required for P0/P1.

Do not embed every row preemptively.

---

# 59. Agent framework

No LangChain/LlamaIndex/agent framework initially.

Reasons:

- no agent loop;
- few bounded calls;
- direct provider SDK is clearer;
- fewer abstractions;
- better observability.

Adopt a framework only if repeated orchestration complexity materially exceeds direct code.

---

# 60. AI scorecard

Before calling AI architecture production-ready:

| Area | Target |
|---|---:|
| core-product AI independence | 100/100 |
| provenance/grounding | 100/100 |
| structured output | 99/100 |
| hallucination containment | 99/100 |
| provider isolation | 98/100 |
| privacy minimization | 99/100 |
| cost control | 98/100 |
| evaluation discipline | 98/100 |
| observability | 97/100 |
| operational simplicity | 99/100 |

A flashy AI feature does not compensate for a grounding failure.

---

# 61. Release checklist

Before first AI-enabled production feature:

- capability interface exists;
- provider adapter tests green;
- prompt versioned;
- schema versioned;
- representative eval set;
- thresholds documented;
- privacy payload reviewed;
- cost budget configured;
- timeout/retry configured;
- moderation policy defined;
- deterministic fallback exists;
- AI key server-only;
- AI disabled does not break core app;
- manual/live smoke completed.

---

# 62. Final governance principle

The model is replaceable.

The product contract is not.

We should be able to switch:

```text
GPT-5.6 Terra
→ future OpenAI model
→ approved Gemini/Claude equivalent
```

without changing:

- what facts are allowed;
- what output schema means;
- what must be reviewed;
- what counts as a valid historical statement;
- what users can trust.


# 63. Zero-cost recruiter-demo scorecard

The selected architecture is successful when:

| Goal | Target |
|---|---:|
| monthly AI runtime bill in normal demo use | €0 |
| paid provider automatic calls | 0 |
| runtime image-generation calls | 0 |
| AI calls before explicit user action | 0 |
| repeated identical explanation cache reuse | ~100% after first success |
| core feature availability after AI quota exhaustion | 100% |
| live AI architecture visible to recruiter | yes |

A portfolio project does not gain extra engineering value from spending money on invisible model quality that the use case does not require.
