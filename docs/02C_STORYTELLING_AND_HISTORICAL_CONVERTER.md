# Storytelling and Historical Converter

This document defines the **storytelling layer** and the **historical FX converter**.

The goal is to make exchange-rate data memorable and culturally meaningful without turning financial reference data into entertainment, speculation or invented causal narratives.

---

# 1. Product idea

A normal converter answers:

> 100 EUR ≈ X JPY today.

The historical experience can answer:

> What would 100 Finnish markka have converted to on 15 June 1998?

and then explain:

- which rate observation was actually available;
- what currency era the user is looking at;
- what changed between then and now;
- what relevant, sourced currency/cultural context belongs to that moment.

The storytelling principle is:

> **Numbers first. Meaning second. Story third.**

A story can enrich a correct conversion.

It can never replace, alter or obscure the underlying data.

---

# 2. Product-facing concept

Internal term:

> Storytelling layer

Preferred user-facing language:

- **The story behind this rate**
- **Money story**
- **Currency timeline**
- **Then & now**
- **Explore this moment**

Avoid making the core financial tool feel gimmicky with labels such as:

- Magic time machine
- Fortune teller
- What if you invested
- You would have won/lost

The tone should remain curious, intelligent and trustworthy.

---

# 3. Experience model

The historical journey has five narrative beats:

```text
1. The amount
   ↓
2. The rate on that date
   ↓
3. The currency era
   ↓
4. What changed since then
   ↓
5. The cultural/historical context
```

Not every conversion needs all five.

Missing or weakly sourced context is omitted rather than replaced with filler.

---

# 4. Entry points

Historical conversion should feel like an extension of the main converter, not a separate unrelated application.

## 4.1 Primary converter control

Default:

```text
Rate date
● Latest available
○ Historical date
```

When Historical date is selected:

```text
[ 15 Jun 1998 ]
```

The main fields remain:

- Amount;
- From;
- To;
- optional source/destination country context.

This preserves the user's mental model.

## 4.2 Secondary entry point

After a normal conversion:

> **See this pair in the past**

This can open/focus the historical-date control.

## 4.3 Currency/country pages

A currency timeline may offer:

> Convert using this historical currency

Example:

> Finnish markka (FIM) · 1972–2002

---

# 5. Historical converter scope

The first historical converter answers only:

> **What would this amount convert to using a published historical FX observation?**

It does **not** automatically answer:

> What was this amount's inflation-adjusted purchasing power?

Those are separate questions.

---

# 6. Historical FX vs historical purchasing power

This distinction is a trust invariant.

## Historical FX conversion

Example:

> On 15 June 1998, 100 FIM ≈ X USD using the published reference observation.

Inputs:

- amount;
- base currency;
- quote currency;
- requested date.

Output:

- historical rate;
- converted amount;
- actual rate observation/effective date;
- provider/source;
- data granularity.

## Historical purchasing power

Different question:

> What could 100 FIM buy in Finland in 1998 compared with today?

This requires:

- CPI/inflation series;
- price-level data;
- country-specific methodology;
- explicit base periods;
- potentially category-level historical prices.

It belongs to a later product phase.

### UI rule

Never attach today's `What this buys` cards to a 1998 historical conversion as if they describe 1998.

If current purchasing context is shown, label it explicitly:

> **Current destination context — not historical purchasing power**

Default preference: omit current price cards from historical mode unless the user requests current context.

---

# 7. Historical data capability

The initial provider, Frankfurter v2, supports:

- specific historical dates;
- date ranges;
- time series;
- legacy/archived currencies;
- provider attribution.

Its dataset includes active and archived currencies and spans some provider series back to 1948.

This makes the historical converter a genuine product capability rather than a chart over recent rates.

---

# 8. Currency eras

A core storytelling feature is understanding which currency belonged to a country at a point in time.

Examples:

```text
Finland
FIM → EUR

Germany
DEM → EUR

Austria
ATS → EUR

Spain
ESP → EUR
```

The app should be able to answer:

> Which supported currency was relevant to this country on the selected date?

This is a **suggestion**, not an automatic rewrite of user intent.

---

# 9. Historical country → currency suggestion

Scenario:

- country: Finland;
- date: 15 Jun 1998;
- user currently has EUR selected.

If the product has a sourced CountryCurrency relationship that says FIM was the relevant currency then, show:

> Finland used the Finnish markka (FIM) on this date.

Action:

> **Use FIM**

Secondary:

> Keep EUR

Do not silently change EUR to FIM.

Why:

- user may intentionally be researching EUR's early accounting-era history;
- currency adoption can have legal/accounting/cash transition nuances;
- automatic replacement would destroy explicit intent.

---

# 10. Archived currencies in selection

Default current converter search should prioritize active currencies.

When Historical date mode is active:

- archived currencies valid near the selected date become discoverable;
- search can return FIM, DEM, ATS, ESP, etc.;
- options expose active date/coverage context.

Example result:

```text
Finnish markka · FIM
Historical · provider data 1972–2002
```

Do not clutter the default current-currency picker with every archived code.

---

# 11. Requested date vs observation date

Historical financial datasets do not guarantee an observation on every calendar day.

The system must distinguish:

```text
Requested date
15 Jun 1998

Rate observation
15 Jun 1998
```

or:

```text
Requested date
14 Jun 1998 (Sunday)

Rate observation used
12 Jun 1998
```

The requested date is user intent.

The effective/observation date is the actual data point.

They must never be conflated.

---

# 12. Non-business days and missing observations

## Daily series

When the selected date has no observation because of weekend/holiday:

Preferred behaviour:

1. search backward for the most recent available observation;
2. use it only within a documented safe window;
3. show the actual observation date prominently.

Initial policy candidate:

> For daily series, use the latest available observation on or before the requested date within 7 calendar days.

This is an implementation hypothesis to validate against provider semantics.

## Monthly/low-frequency historical series

Some archived/provider datasets may have monthly or otherwise lower-frequency observations.

Do not manufacture daily precision.

Display:

> Monthly historical observation

with the relevant period/date.

The provider adapter should expose observation granularity when known.

---

# 13. Historical result hierarchy

Example:

```text
15 Jun 1998

100 FIM ≈ 18.40 USD

Historical reference rate
1 FIM = 0.1840 USD

Observation effective 15 Jun 1998
Source: [provider]
```

If fallback date used:

```text
You selected 14 Jun 1998.
No observation was published for that date.

Using the previous available reference observation:
12 Jun 1998
```

Never hide the fallback in fine print.

---

# 14. Date validation

Reject:

- future dates;
- dates before both currencies/provider coverage;
- malformed dates.

Allow:

- dates within historical coverage;
- today only through the normal latest/current pathway unless provider semantics justify historical-date lookup.

If a requested date predates available pair coverage:

> Historical data for this pair starts on [date].

Offer:

- earliest available date;
- another currency;
- provider/source details where helpful.

---

# 15. Pair coverage

Historical availability is the intersection of:

- base currency existence/coverage;
- quote currency existence/coverage;
- selected provider coverage;
- cross-rate capability.

The UI should not pretend that “Frankfurter goes back to 1948” means every currency pair has daily data back to 1948.

Coverage should be discovered and communicated per query/currency/provider.

---

# 16. Then & now

For currency pairs that exist both on the historical date and today, offer a concise comparison.

Example:

```text
Then
15 Jun 2016
100 EUR ≈ X USD

Latest reference
18 Sep 2026
100 EUR ≈ Y USD
```

Then summarize the **rate difference**, not investment outcome.

Good:

> The USD amount per 100 EUR is about 8% higher in the latest reference rate than in the selected 2016 observation.

Bad:

> You would have made 8%.

Bad:

> The euro is 8% better now.

The comparison must define direction clearly.

---

# 17. Archived-currency “Then & now”

An archived currency cannot always be meaningfully converted using a present-day market rate.

Example:

FIM today.

Do not fabricate a “current FIM market rate”.

Instead show a **currency transition story**:

```text
1998
Finnish markka · FIM

2002
Euro cash changeover

Today
Finland uses EUR
```

If an official fixed conversion relationship exists and is curated from an authoritative source, it may be shown as a historical transition fact, clearly distinct from a current market rate.

---

# 18. Storytelling system

Stories are assembled from structured, sourced facts.

They are not generated by an LLM from scratch.

Conceptually:

```text
Conversion result
      │
      ├── currency era
      ├── rate comparison
      ├── country/currency transition
      ├── sourced historical moment
      └── curated cultural context
              ↓
         Story composer
              ↓
        Story chapters
```

The composer chooses relevant chapters and leaves out missing ones.

---

# 19. Story chapters

## Chapter A — The number

Mandatory.

Example:

> On 15 June 1998, 100 Finnish markka converted to approximately X US dollars using the available historical reference observation.

This restates trusted data in readable language.

## Chapter B — The currency era

Shown when relevant.

Example:

> Finland was still using the Finnish markka. The euro had not yet replaced markka cash.

Exact chronology must be sourced.

## Chapter C — Then & now

Shown only if comparison is semantically valid.

Example:

> For the same EUR/USD pair, today's reference conversion differs by approximately X%.

No investment framing.

## Chapter D — Currency transition

For archived currencies / monetary reforms.

Examples:

- FIM → EUR;
- DEM → EUR;
- old/new lira;
- redenominations.

## Chapter E — Historical/cultural moment

Optional, curated.

Example structure:

> **Around this time**
>
> [short sourced contextual fact]

Requirements:

- temporal relevance;
- reliable source;
- no fake causality;
- no sensationalism;
- no unrelated trivia just to fill space.

## Chapter F — Explore

Links to:

- currency timeline;
- country money culture;
- historical chart;
- source details.

---

# 20. Story relevance rules

A story chapter should exist only when it helps answer one of:

1. What does this number mean?
2. Why is this currency/date interesting?
3. What changed?
4. What monetary/cultural era am I looking at?

Do not include a fact merely because it is true.

Storytelling quality is about relevance, not volume.

---

# 21. Causality rule

Historical FX moves can have many causes.

The product must not write:

> The currency fell because event X happened.

unless a reliable source directly supports that causal explanation.

Preferred neutral language:

> The rate moved from X to Y over this period.

A sourced historical note can be shown beside the data without implying causation.

---

# 22. Story tone

Desired:

- concise;
- curious;
- human;
- calm;
- factual;
- culturally respectful.

Avoid:

- clickbait;
- nationalism;
- stereotypes;
- financial hype;
- dramatic “currency crashed” language without a source;
- moral judgement.

---

# 23. Deterministic storytelling first

P0/P1 storytelling should use deterministic templates.

Example template:

```text
On {requested_date}, {amount} {base_name}
was approximately {result} {quote_name}
using the {effective_date} reference observation.
```

Benefits:

- testable;
- translatable;
- reproducible;
- source-aligned;
- no hallucination risk.

---

# 24. AI storytelling later

AI may later improve prose **only over a bounded sourced fact set**.

Safe flow:

```text
structured sourced facts
        ↓
validated story context
        ↓
optional AI rewrite
        ↓
claim/source validation
        ↓
display
```

AI must never invent:

- rates;
- currency dates;
- transition facts;
- historical causes;
- prices;
- economic events.

The deterministic version remains fallback/source of truth.

---

# 25. Story provenance

Every chapter should be able to expose provenance.

Example:

```text
Rate
Frankfurter / Bundesbank
Observation 15 Jun 1998

Currency transition
Bank of Finland / ECB
Verified [date]

Historical moment
[source]
Published/verified [date]
```

A story is not exempt from the trust model because it is written conversationally.

---

# 26. Historical Story UI

Recommended structure:

```text
Historical conversion
────────────────────────
15 Jun 1998

100 FIM
≈
X USD

Historical reference rate
[effective date · source]

[ The story behind this rate ↓ ]

Chapter 1 — Your money on this date
Chapter 2 — Finland's currency then
Chapter 3 — From markka to euro
Chapter 4 — Explore the timeline
```

Story is progressive disclosure.

The conversion remains readable without opening the story.

---

# 27. Timeline UI

Currency page / Story can expose a horizontal/vertical timeline.

Example:

```text
1972 ───────── 1998 ───────── 1999 ───── 2002 ───── Today
 FIM data        selected       EUR era     cash        EUR
 begins          date           begins*     changeover
```

The exact euro-transition wording must account for sourced legal/accounting/cash milestones rather than oversimplify.

Mobile should use a vertical timeline if horizontal scrolling reduces comprehension.

---

# 28. Historical chart integration

A historical conversion date can become the highlighted point on the rate chart.

Example:

- selected historical point;
- latest point;
- high/low for chosen period.

The chart and the converter must use the same normalized rate semantics.

No separate calculation logic.

---

# 29. Quick historical presets

Useful secondary actions:

- 1 year ago;
- 5 years ago;
- 10 years ago;
- custom date.

For archived currencies:

- first available;
- last available;
- notable transition dates may be offered only if curated/sourced.

Presets should not crowd the default converter.

---

# 30. Historical deep links

Candidate URL:

```text
/?amount=100&from=FIM&to=USD&date=1998-06-15&from_country=FI
```

The URL captures requested date.

The result separately shows actual observation/effective date.

This makes stories reproducible/shareable.

---

# 31. Shareable money stories

Later enhancement:

> Share this money story

Potential outputs:

- canonical URL;
- social preview card;
- compact image card.

A share card should include:

- amount;
- pair;
- requested date;
- observation date if different;
- source attribution;
- product name.

Do not put unsourced narrative claims into preview images.

---

# 32. Current vs historical context separation

Historical mode changes some sections.

## Keep

- historical conversion;
- source;
- currency timeline;
- historical rate chart;
- sourced story.

## Hide by default

- current typical prices;
- current card/cash guidance.

## Optional

Provide a clearly separate CTA:

> See today's travel context for Japan

This prevents temporal mixing.

---

# 33. Historical payment/culture data

If later we acquire time-bounded historical cultural/payment facts, the model can support them.

Until then:

- do not backdate current customs;
- do not say “cards were commonly accepted in 1998” using a 2026 source;
- do not infer historical practice from current practice.

---

# 34. StoryMoment model concept

A structured historical/cultural event may be represented as:

```text
StoryMoment
- countries[]
- currencies[]
- category
- title
- summary
- start_date
- end_date?
- source_name
- source_url
- source_published_at?
- verified_at
- relevance_weight
- is_published
```

Potential categories:

- currency_introduction;
- currency_retirement;
- redenomination;
- monetary_union;
- cash_changeover;
- central_bank;
- cultural_money_fact;
- sourced_economic_context.

This is a candidate model; final normalization should be reviewed with domain architecture.

---

# 35. Currency transition model

Existing `CountryCurrency.valid_from/valid_to` may be sufficient for basic era lookup.

If transition complexity grows, add explicit transition metadata rather than overloading generic facts.

Potential concept:

```text
CurrencyTransition
- country
- from_currency
- to_currency
- transition_type
- announced_date?
- accounting_start?
- legal_tender_start?
- cash_changeover_date?
- legacy_end_date?
- fixed_conversion_rate?
- source
```

Do not implement all fields merely because they are imaginable.

Start from supported stories and authoritative data.

---

# 36. Historical quote value object

Extend normalized rate semantics conceptually:

```text
RateQuote
- base_currency
- quote_currency
- rate
- requested_date?
- effective_date
- fetched_at
- provider
- provider_sources[]
- observation_granularity
- historical
- stale
```

For latest reference quotes:

`requested_date = null`.

For historical:

`requested_date = user selected date`.

---

# 37. Historical caching

Historical observations are strong cache candidates.

Policy:

- historical normalized rate → long-lived/immutable-style cache;
- provider metadata → long-lived with version/freshness policy;
- story facts → database-backed editorial cache as needed.

If a provider later corrects historical data, cache invalidation must remain possible.

“Long-lived” does not mean impossible to refresh.

---

# 38. Historical API shape

Existing quote endpoint can accept optional date.

Request:

```json
{
  "amount": "100.00",
  "base": "FIM",
  "quote": "USD",
  "date": "1998-06-15",
  "source_country": "FI"
}
```

Response concept:

```json
{
  "amount": "100.00",
  "base": "FIM",
  "quote": "USD",
  "result": "...",
  "rate": "...",
  "historical": true,
  "requested_date": "1998-06-15",
  "effective_date": "1998-06-15",
  "observation_granularity": "daily",
  "provider": "...",
  "sources": ["..."]
}
```

If fallback observation:

```json
{
  "requested_date": "1998-06-14",
  "effective_date": "1998-06-12",
  "used_previous_observation": true
}
```

Machine-readable distinction is mandatory for mobile and web parity.

---

# 39. Historical converter states

Add:

```text
historical-ready
historical-loading
historical-success-exact
historical-success-previous-observation
historical-out-of-coverage
historical-pair-unavailable
historical-archived-currency-suggested
story-loading
story-ready
story-partial
story-unavailable
```

Story failure never invalidates the historical conversion.

---

# 40. Historical user cases

### H1 — Exact historical date

> Convert 100 EUR to USD using 15 June 2016.

### H2 — Weekend historical date

> Convert using Sunday, when no daily observation exists.

Expected:

- use/display previous valid observation only under defined policy;
- show requested/effective dates separately.

### H3 — Archived currency

> Convert 100 FIM to USD in 1998.

### H4 — Country currency mismatch

> Finland + 1998 + EUR.

Expected:

- suggest FIM;
- do not silently replace EUR.

### H5 — Out of coverage

> Ask for pair/date before data exists.

Expected:

- explain coverage;
- offer earliest supported point.

### H6 — Then & now

> Compare a historical EUR/USD result with latest reference rate.

### H7 — Story

> Explain the currency era around a historical conversion.

### H8 — Historical buying power question

User asks:

> What could this buy then?

Expected:

- explain that FX conversion alone cannot answer;
- only show historical purchasing-power data when separately supported.

---

# 41. Story quality scoring

A story should be evaluated on:

- factual correctness;
- provenance completeness;
- temporal relevance;
- clarity;
- narrative relevance;
- cultural sensitivity;
- no causal overreach;
- no financial hype;
- accessibility;
- concise reading time.

A shorter sourced story scores higher than a longer speculative one.

---

# 42. Story accessibility

Narrative structure uses semantic headings.

Timeline does not rely on visual position alone.

Historical chart has text/table equivalent.

Dates are written in accessible human-readable form.

Dynamic story loading does not dump an entire long narrative into a live region.

Only the historical conversion result is announced automatically.

---

# 43. Mobile historical experience

Mobile entry:

```text
Rate date
Latest available  >
```

Tap:

```text
Latest available
Historical date
[Date picker]
```

After result:

```text
100 FIM
≈ X USD

Historical reference
15 Jun 1998

[See the story]
```

Story is a vertical sequence, optimized for reading and interruption/resume.

---

# 44. Performance

Historical conversion should not require downloading a whole time series.

For a single date:

- fetch/query one normalized historical quote.

Load time series only when the user opens:

- chart;
- trend;
- Then & now detail requiring range context.

Story facts come from local curated storage where possible.

---

# 45. Privacy

Historical conversion has no special personal-data requirement.

Shareable historical URLs contain:

- amount;
- pair;
- date;
- optional country context.

Do not include:

- account identifiers;
- private trip notes;
- personal labels.

---

# 46. Analytics questions

Useful product questions:

- What percentage of users try historical conversion?
- Which quick-date presets are used?
- How often are archived currencies selected?
- Do users open The story behind this rate?
- Which story chapters hold attention?
- Do people confuse historical FX with purchasing power?
- How often does country/date trigger an archived-currency suggestion?
- Are fallback observation dates understood?

Do not use engagement metrics to justify adding low-quality trivia.

---

# 47. Usability tests

## Test A — Finland 1998

> You want to know what 100 Finnish markka were worth in US dollars in June 1998.

Observe:

- can user discover historical mode?
- can they find FIM?
- do they understand requested vs effective date?

## Test B — Weekend

> Select a Sunday.

Ask:

> Which day's rate did the app actually use?

Success requires the participant to answer correctly.

## Test C — EUR-era mismatch

> Select Finland, 1998, and EUR.

Observe whether the FIM suggestion is understandable without feeling like an error.

## Test D — Historical purchasing power

Ask:

> Does this tell you what 100 markka could buy in 1998?

Correct comprehension:

> No — it shows FX conversion; buying power is a different dataset.

## Test E — Story causality

Show a rate movement plus historical event.

Ask:

> Is the app claiming this event caused the rate move?

Correct answer should be no unless explicitly sourced.

---

# 48. P1 acceptance criteria

The historical/story experience is ready only when:

- exact-date historical conversion uses Decimal and normalized provider data;
- requested date and effective observation date are distinct fields;
- non-observation fallback is explicit;
- no future date is accepted;
- pair/date coverage errors are informative;
- archived currencies can be discovered in historical mode;
- country/date can suggest a historical currency without forcing it;
- same underlying historical quote powers web/API/story;
- current local-price cards do not masquerade as historical prices;
- Then & now never uses investment-return language;
- archived currencies do not receive fabricated current market rates;
- story chapters are sourced and deterministic by default;
- missing story context produces no filler;
- historical conversion works even when story data is unavailable;
- chart and story remain progressive enrichment;
- deep links reproduce requested historical state;
- accessibility tests cover historical date selection/result.

---

# 49. Anti-patterns

Do not:

- call a past FX conversion “what your money was worth” without clarifying FX context;
- apply current coffee/hotel prices to a historical conversion;
- infer historical prices from FX rates;
- invent exact rates for dates with no observation;
- hide effective-date fallback;
- pretend every pair has data back to 1948;
- silently replace selected EUR with FIM/DEM/etc.;
- calculate a fake current market rate for retired currencies;
- claim a historical event caused a rate movement without a source;
- use AI as a historical fact generator;
- turn the story into an SEO trivia dump;
- overwhelm current-conversion users with historical controls by default.

---

# 50. Future: historical purchasing power

This deserves a separate product specification when implemented.

Potential source classes:

- official national CPI;
- World Bank indicator data;
- OECD price/PPP data;
- curated historical price datasets.

The methodology must answer:

- country;
- index;
- base year;
- date granularity;
- inflation formula;
- whether comparison is domestic purchasing power or cross-country price level.

Until that methodology exists, the product explicitly says:

> Historical exchange-rate conversion does not measure inflation or purchasing power.
