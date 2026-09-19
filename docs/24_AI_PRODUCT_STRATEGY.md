# AI Product Strategy and Model Selection

Research date: **2026-09-19**.

This document defines **where AI belongs in Cultural Currency Converter, where it does not belong, and which model/provider tiers are selected**.

The central rule is:

> **AI may synthesize trusted product data. AI does not create financial or historical truth.**

The application remains fully useful when every AI provider is unavailable.

---

# 1. Executive decision

## Primary AI provider

**OpenAI API** is the initial primary provider.

Reasons:

- strong structured-output support through the Responses API;
- current GPT-5.6 model family provides clear cost/intelligence tiers;
- first-party image generation through GPT-Image-2.5;
- first-party text/image moderation;
- one provider can cover the project's initial text + image assist use cases;
- current SDK/API surface supports structured schemas and multimodal inputs.

This is an implementation choice, not a domain dependency.

The product domain never imports OpenAI model names.

## Secondary providers

Google Gemini and Anthropic Claude remain:

- benchmark candidates;
- future fallback candidates;
- not parallel production dependencies initially.

Do not pay operational complexity for three providers before one provider has demonstrated a real failure or quality limitation.

---

# 2. Why OpenAI is the best current fit

The project needs two different model families:

1. structured text intelligence;
2. image generation.

OpenAI currently provides both behind one platform.

Current model tiers relevant to this project:

| Capability | Selected initial model tier | Intended use |
|---|---|---|
| cheap structured text | GPT-5.6 Luna | classification, metadata suggestions, low-risk transformations |
| quality structured text | GPT-5.6 Terra | editorial draft, prompt composition, bounded explanation |
| rare quality/audit pass | GPT-5.6 Sol | evaluation/adjudication only when Terra is insufficient |
| draft image candidates | GPT-Image-2.5 Flare | quick candidate generation |
| final featured image | GPT-Image-2.5 Sunburst | high-quality approved candidate generation/edit |
| moderation | omni-moderation-latest | text/image safety classification |

Model names are configuration.

Application code uses capability names.

---

# 3. Why not GPT-6 Astra by default

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

# 4. Why Terra is the main text model

GPT-5.6 Terra is currently positioned as the balance between intelligence and cost.

That matches:

- story drafting from structured facts;
- image-prompt synthesis;
- editorial rewriting;
- concise contextual explanation;
- title/caption drafting.

These are not trillion-token or autonomous-agent tasks.

Terra is the default quality lane.

---

# 5. Why Luna exists in the routing table

Use Luna only for narrow, easy-to-evaluate tasks.

Examples:

- classify a candidate into a small enum;
- normalize a draft title;
- suggest tags;
- draft alt-text candidate from already structured visual metadata;
- detect whether a generated paragraph mentions a fact ID not supplied;
- prompt/style linting.

If a task needs nuanced historical writing, use Terra.

Do not route only by price.

---

# 6. Why Sol is not the default

Sol is reserved for:

- difficult evaluation disagreements;
- rare high-value editorial quality pass;
- benchmark comparison;
- complex prompt/template redesign.

It should not silently become the default because it is “better”.

A more expensive model requires measured improvement.

---

# 7. Image model routing

## GPT-Image-2.5 Flare

Use for:

- candidate previews;
- style exploration;
- multiple low-cost/fast composition attempts;
- non-featured illustrative variants.

## GPT-Image-2.5 Sunburst

Use for:

- final featured editorial illustration;
- high-value story cover;
- controlled image edit;
- difficult composition;
- image where precision/style adherence matters.

The workflow can generate 2–4 Flare candidates, select/rework the best concept, then optionally create one Sunburst final.

Do not generate Sunburst at every selector change.

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

If OpenAI is fully unavailable:

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

Concept:

```text
AI_TEXT_FAST_MODEL      = gpt-5.6-luna
AI_TEXT_QUALITY_MODEL   = gpt-5.6-terra
AI_TEXT_AUDIT_MODEL     = gpt-5.6-sol

AI_IMAGE_DRAFT_MODEL    = gpt-image-2.5-flare
AI_IMAGE_FINAL_MODEL    = gpt-image-2.5-sunburst

AI_MODERATION_MODEL     = omni-moderation-latest
```

Exact aliases/snapshots are deployment configuration and re-checked before implementation.

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

Recommended:

**No user-request-path AI.**

AI may be used before launch internally to:

- generate selected image candidates;
- draft selected story prose;
- draft alt/captions;
- assist editorial QA.

All published assets are reviewed/stored.

---

# 32. P1 AI scope

After media/story data model exists:

- admin “Draft with AI” action;
- admin “Generate image candidates” action;
- stored prompt/model metadata;
- moderation;
- eval suite;
- usage/cost logging.

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

- OpenAI primary provider;
- Responses API for structured text;
- GPT-5.6 Terra as default quality model;
- GPT-5.6 Luna for narrow cheap tasks;
- GPT-5.6 Sol for rare audit/eval escalation;
- GPT-Image-2.5 Flare for image candidates;
- GPT-Image-2.5 Sunburst for final high-value image generation/edit;
- omni-moderation-latest for moderation;
- provider-neutral capability interfaces;
- editorial/background AI first.

## Rejected initially

- AI-generated FX;
- AI truth/source selection;
- autonomous web research/publication;
- agentic tool loops;
- runtime image generation on selection;
- multi-provider complexity;
- AI as a required dependency.

The product should be impressive because AI is **well-bounded**, not because it is everywhere.
