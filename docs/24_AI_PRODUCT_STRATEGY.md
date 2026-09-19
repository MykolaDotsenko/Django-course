# AI Product Strategy and Model Selection

Research date: **2026-09-19**.

This document defines **where AI belongs in Cultural Currency Converter, where it does not belong, and which model/provider tiers are selected**.

The central rule is:

> **AI may synthesize trusted product data. AI does not create financial or historical truth.**

The application remains fully useful when every AI provider is unavailable.

---

# 1. Executive decision

## Primary AI provider

**Google Gemini Developer API free tier** is the initial runtime AI provider for the portfolio demo.

Primary runtime model:

```text
gemini-3.1-flash-lite
```

Reasons:

- the current Gemini Developer API pricing page lists free-tier input and output for Gemini 3.1 Flash-Lite;
- it supports Structured Outputs;
- it is explicitly optimized for low-latency, cost-efficient lightweight/high-volume tasks;
- no paid runtime AI is required for the portfolio demo;
- our source-packet/validator architecture means the runtime task is intentionally narrow;
- the product already has a deterministic fallback, so free-tier quota exhaustion is harmless.

This is an implementation choice, not a domain dependency.

The product domain never imports Gemini model names.

## Secondary providers

OpenRouter's free tier is a possible development/emergency experiment, but it is **not** an automatic production fallback because its free router can select among changing free models.

OpenAI, Anthropic and paid Gemini tiers remain quality benchmark/upgrade candidates only.

Do not add multiple production SDKs for a portfolio demo.

---

# 2. Why Gemini free tier is the best portfolio fit

For this project the highest-ROI goal is:

```text
show real AI architecture
+ show one useful live AI interaction
+ pay €0 in normal demo usage
```

Gemini 3.1 Flash-Lite is sufficient for the live task because the model does not research facts. It receives a small verified structured packet and produces a bounded structured explanation.

Current demo routing:

| Capability | Selected approach | Runtime cost target |
|---|---|---:|
| live “Explain this” | Gemini 3.1 Flash-Lite free tier | €0 |
| tags/metadata assist | Gemini 3.1 Flash-Lite free tier or deterministic code | €0 |
| story content | deterministic + pre-generated/reviewed stored draft | €0 runtime |
| image generation | pre-generated/manual development workflow | €0 runtime |
| moderation of stored assets | editorial review / optional dev tooling | €0 runtime |

Model IDs remain configuration.

Application code uses capability names.

---

# 3. Paid-model policy

Paid models are **not part of the normal portfolio runtime**.

A paid OpenAI/Gemini/Anthropic model may be used manually during development only if:

- a one-off quality benchmark is useful;
- cost is consciously accepted;
- generated output is stored;
- no page request depends on it.

The public demo never silently escalates from free Gemini to a paid model.

---

# 3A. Historical note — why not use a premium model by default

The most capable model is not automatically the best product choice.

Our normal AI tasks are:

- bounded;
- schema-constrained;
- fed with curated facts;
- editorial rather than open-ended autonomous research.

Therefore the default quality model should optimize:

```text
sufficient intelligence
+ structured reliability
+ predictable cost
+ low enough latency
```

rather than maximum benchmark intelligence.

Use GPT-6 Astra only if evaluations prove a specific task materially benefits enough to justify cost.

No architecture assumes it.

---

# 4. Why Gemini 3.1 Flash-Lite is the main runtime text model

Gemini 3.1 Flash-Lite is currently positioned by Google as a low-latency, cost-efficient model for lightweight/high-volume tasks and supports Structured Outputs.

Our live task is deliberately narrow:

```text
verified Conversion/Context packet
→ short structured explanation
```

It does not need premium open-ended reasoning.

For the portfolio demo this gives a much better ROI than a paid “quality lane”.

---

# 5. One-model runtime policy

Use one live text model initially:

```text
gemini-3.1-flash-lite
```

Benefits:

- one SDK;
- one error model;
- one free quota;
- one eval target;
- less configuration.

If a task cannot meet quality gates on Flash-Lite, prefer deterministic/manual/pre-generated content before adding a paid runtime model.

---

# 6. No automatic premium escalation

Do not implement:

```text
Flash-Lite quota/quality issue
→ paid Gemini
→ OpenAI
→ Anthropic
```

automatically.

If free AI is unavailable or quota-limited:

```text
cached AI result
→ deterministic explanation
```

The demo stays free and predictable.

---

# 7. Image generation is offline/pre-generated

The public portfolio deployment performs **zero image-generation API calls**.

Why:

- current Gemini 3.1 Flash Image and Flash Lite Image pricing lists no API free tier;
- paid image generation adds no meaningful recruiter value when assets can be generated once;
- stored images are more stable for visual regression and demos.

Use:

1. sourced Wikimedia/Europeana media where factual;
2. a small set of pre-generated AI illustrations created manually during development;
3. Quiet Atlas CSS/SVG fallback.

Generated assets are reviewed and stored through MediaAsset.

The image-generation adapter remains documented as a future/optional development tool, but `AI_IMAGE_GENERATION_ENABLED=false` in the public demo.

---

# 8. AI is not a core runtime dependency

P0/P1 conversion path:

```text
amount
→ FX/domain
→ result
→ context/story from local sourced data
```

No AI call.

If Gemini live AI is unavailable or free quota is exhausted:

- conversion works;
- historical conversion works;
- charts work;
- local value works;
- payment guidance works;
- deterministic story works;
- existing stored media works.

Only editorial candidate creation is degraded.

---

# 9. AI use-case tiers

## Tier A — accepted editorial assist

High ROI, low runtime risk.

- story draft from sourced fact packet;
- title/subtitle suggestion;
- caption draft;
- alt-text draft;
- generated-image prompt composition;
- image generation candidate;
- categorization/tagging candidate;
- duplicate/similarity editorial assistance later.

All outputs are candidates.

## Tier B — accepted internal QA assist

- compare two prompt versions;
- flag unsupported draft claims;
- check tone/style;
- detect likely stereotypes/anachronistic wording;
- generate test cases/evaluation variants.

AI QA is not the sole approval control.

## Tier C — possible future user-facing assist

Only after product evidence.

- “Explain this comparison in plain language”;
- “Summarize what changed between then and now”;
- short contextual travel explanation.

Runtime user-facing AI must be:
- explicitly marked as generated explanation where relevant;
- grounded only in server-provided structured data;
- non-authoritative;
- independently removable without breaking core UX.

## Tier D — rejected

- generate exchange rates;
- decide historical effective date;
- estimate unverified local prices;
- decide whether a source is true;
- invent historical events;
- autonomously browse and publish;
- decide media licensing;
- financial advice;
- personalized transfer recommendation;
- autonomous trading interpretation;
- mutate user data without explicit deterministic application action.

---

# 10. AI does not select truth

For historical story:

Wrong:

```text
year + country
→ LLM
→ "tell me what happened"
→ publish
```

Correct:

```text
verified StoryFacts
+ CurrencyEra
+ RateObservation
+ source IDs
        ↓
StorySourcePacket
        ↓
LLM editorial transformation
        ↓
DraftCandidate
        ↓
validator/review
        ↓
publish
```

The source packet defines allowable facts.

---

# 11. Deterministic story remains canonical

The deterministic StoryComposer remains capable of producing a useful story without AI.

AI can improve:

- flow;
- transitions;
- readability;
- editorial tone.

AI cannot be required to make the story factually complete.

If AI draft fails validation:

```text
use deterministic story
```

not:

```text
block story page
```

---

# 12. AI does not perform retrieval by default

Do not enable provider web search in normal AI generation.

Reasons:

- our source pipeline already owns evidence;
- web retrieval would create a second uncontrolled provenance path;
- search results can change;
- source/licence/fact review becomes harder;
- model may blend sourced and unsourced knowledge.

If research assistance is later added for editors, it is a separate candidate-research workflow.

Nothing found by AI search auto-publishes.

---

# 13. AI model knowledge is never a source

Even if the model “knows”:

- a historical event;
- a currency transition;
- a banknote detail;
- a cultural convention;

the model cannot add that fact unless it appears in the approved source packet.

Model knowledge is used for language competence, not evidence.

---

# 14. No autonomous agent loop initially

Rejected P1 architecture:

```text
LLM
→ search tool
→ DB tool
→ media tool
→ generation tool
→ publish tool
```

Selected:

```text
application code prepares exact input
→ one bounded AI call
→ structured candidate
→ deterministic validation
→ human/editorial action
```

Benefits:

- lower cost;
- easier tests;
- easier provenance;
- fewer unsafe side effects;
- simpler timeout/failure model.

---

# 15. Human-in-the-loop matrix

| AI output | Human review required before publication? |
|---|---:|
| historical story prose | yes |
| historical AI image | yes |
| current culture editorial prose | yes initially |
| source metadata suggestion | yes |
| alt-text suggestion | yes initially for editorial media |
| internal tag suggestion | not necessarily |
| internal style lint result | no |
| runtime plain-language explanation | no if later approved + grounded schema/evals |
| financial/domain value | AI prohibited |

---

# 16. What AI can publish automatically later

Only low-risk outputs may eventually become auto-accepted after evaluation history.

Examples:

- internal tags;
- non-visible classifications;
- formatting transformations.

Published factual prose and historical imagery stay review-gated until there is compelling evidence otherwise.

---

# 17. Model routing is capability-based

Application asks for:

```text
NARRATIVE_DRAFT
ALT_TEXT_DRAFT
IMAGE_PROMPT
IMAGE_DRAFT
IMAGE_FINAL
MODERATION
QUALITY_AUDIT
```

It does not ask:

```text
call gpt-5.6-terra
```

A configuration layer maps capability → provider/model.

This allows model upgrades without changing domain code.

---

# 18. Initial routing map

Portfolio-demo configuration:

```text
AI_PROVIDER                     = google
AI_TEXT_MODEL                   = gemini-3.1-flash-lite

AI_RUNTIME_EXPLANATION_ENABLED  = true
AI_EDITORIAL_GENERATION_ENABLED = false
AI_IMAGE_GENERATION_ENABLED     = false

AI_FALLBACK_MODE                = deterministic
```

The exact free-tier quota is checked in Google AI Studio because Google documents that limits vary by model, project and account status.

No billing account is required by architecture.

---

# 19. Alias vs snapshot policy

Development may use stable aliases for convenience.

Production/editorial pipelines should prefer a pinned model snapshot when:

- provider exposes one;
- reproducibility matters;
- the snapshot has passed our eval set.

If a capability has no suitable snapshot:

- use alias;
- record exact returned/model identity where available;
- run eval suite before intentional model upgrade.

Do not silently change model on a published content regeneration job.

---

# 20. Model-upgrade rule

A model upgrade is not a dependency bump only.

Before changing a model:

1. run representative eval set;
2. compare factual-support score;
3. compare style score;
4. compare schema/refusal behavior;
5. compare cost;
6. compare latency;
7. inspect at least a sample of historical-image candidates;
8. update model routing ADR/config.

Only then promote.

---

# 21. Provider benchmark scorecard

Current architectural fit:

| Provider | Fit /100 | Strength | Main limitation for this product |
|---|---:|---|---|
| OpenAI | 98 | structured text + image + moderation in one platform | provider concentration |
| Google Gemini | 93 | structured multimodal + image generation | fast API/model lifecycle change |
| Anthropic Claude | 89 | excellent text/tool workflows | no equivalent first-party image-generation stack, requiring second provider |

This score is architecture fit, not a universal model-quality ranking.

---

# 22. Why not multi-provider production from day one

Multi-provider sounds resilient but adds:

- duplicate SDKs;
- duplicate error semantics;
- duplicate pricing tracking;
- different moderation behavior;
- different JSON-schema support;
- different prompt tuning;
- more eval combinations.

Initial reliability is better served by:

```text
one provider
+ provider abstraction
+ no runtime critical dependency
```

If provider outage occurs, core product still works.

---

# 23. Fallback policy

Editorial AI fallback:

```text
AI unavailable
→ no draft generated
→ editor can use deterministic content/manual writing
```

Image fallback:

```text
AI unavailable
→ sourced media
→ existing approved generated media
→ Quiet Atlas CSS/SVG fallback
```

Do not automatically send the same prompt to another vendor unless that provider has been explicitly benchmarked/approved.

---

# 24. Model context size is not an architecture goal

Do not send the whole database because a model accepts a large context.

Input packets are intentionally small.

Benefits:

- lower cost;
- lower hallucination surface;
- easier source attribution;
- easier evaluation;
- reduced privacy exposure.

Large context is a safety valve, not a product design target.

---

# 25. Reasoning effort

Use the lowest reasoning effort that passes evals.

Suggested starting points:

- tags/classification: none/low;
- alt text: low;
- story draft: low/medium;
- prompt composition: low/medium;
- audit/adjudication: medium/high.

Do not use max reasoning for normal editorial prose.

---

# 26. Output length

AI outputs are bounded.

Examples:

- title: <= 90 chars;
- caption: <= 240 chars;
- alt text: <= 250 chars;
- story chapter: configured max sentences/words;
- explanation: concise.

Schema and application validation enforce limits after generation.

The model is not trusted to obey only prose instructions.

---

# 27. No conversational memory for editorial tasks

Each editorial generation is self-contained.

Do not create long-lived AI conversations that gradually accumulate hidden state.

Input explicitly contains:

- prompt version;
- source packet;
- requested task;
- style contract.

This supports reproducibility.

---

# 28. No AI personal memory

The product does not send user history/preferences to an AI model to personalize financial explanations in P0/P1.

If personalized AI later exists:

- explicit product/privacy review;
- minimal necessary data;
- clear retention semantics.

---

# 29. User-facing AI disclosure

If future runtime AI explanation ships, users should be able to distinguish:

- sourced factual values;
- generated explanation.

Do not visually merge generated prose into provenance metadata.

---

# 30. AI failure must be local

AI failure states may affect:

- candidate generation;
- optional explanation.

They may not affect:

- conversion status;
- historical rate;
- source metadata;
- payment context;
- saved trips.

AI is a leaf dependency.

---

# 31. P0 launch AI scope

Recommended public demo:

- core converter/history: no AI;
- one explicit **“Explain this”** button may call Gemini 3.1 Flash-Lite free tier;
- result is cached by normalized packet hash;
- deterministic explanation is the fallback;
- no automatic AI call on page load/change;
- no image-generation API;
- stories/media are stored/pre-generated.

This provides visible AI integration without turning every page view into quota consumption.

---

# 32. P1 AI scope

Optional later portfolio polish:

- admin “Draft with AI” using the same Gemini free tier when quota allows;
- stored prompt/model metadata;
- eval suite;
- usage/quota logging.

Image generation remains offline/manual unless a genuinely free and stable API tier exists at implementation time.

Still no core runtime dependency.

---

# 33. P2 runtime experiment

Only if user research shows value:

> Explain this conversion/context

Input:

- exact ConversionResult;
- exact DestinationContext;
- exact source metadata;
- optional StoryFacts.

Output:

- bounded structured explanation.

No web search.
No tools.
No arbitrary model facts.

The feature can be A/B tested and removed independently.

---

# 34. AI success metric

AI is successful only when it reduces editorial effort or improves understanding **without reducing trust**.

Metrics can include:

- editor acceptance rate;
- average edits before publish;
- unsupported-claim rate;
- image candidate acceptance rate;
- cost per approved asset;
- explanation helpfulness;
- latency if runtime;
- fallback rate.

“Number of AI calls” is not a success metric.

---

# 35. Final policy

## Selected

- Google Gemini Developer API free tier as primary runtime AI;
- Gemini 3.1 Flash-Lite as the single live text model;
- structured JSON output / schema-constrained responses;
- one recruiter-visible live feature: “Explain this”;
- persistent cache/reuse by normalized packet hash;
- deterministic fallback on quota/provider failure;
- zero runtime image-generation calls;
- sourced + pre-generated stored images;
- provider-neutral capability interfaces;
- €0 normal-demo runtime target.

## Rejected initially

- AI-generated FX;
- AI truth/source selection;
- autonomous web research/publication;
- agentic tool loops;
- runtime image generation on selection;
- multi-provider complexity;
- AI as a required dependency.

The product should be impressive because AI is **well-bounded**, not because it is everywhere.
