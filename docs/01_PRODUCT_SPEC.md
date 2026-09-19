# Product Specification

## 1. Product statement

**Cultural Currency Converter** is a travel-money intelligence application that helps people convert currency and understand the local meaning of the converted amount.

Tagline:

> **Convert money. Understand local value. Discover culture.**

### 1.1 Signature product invariant

Cultural Currency Converter is not a conventional converter with cultural content attached underneath it.

The conversion itself connects two cultural contexts.

> **Source and destination may independently influence atmosphere and context, while arithmetic, controls, trust, accessibility and interaction mechanics remain stable.**

Supporting principle:

> **Utility first. Culture within the interaction. Deeper context on demand.**

On larger screens, source and destination should read as two related sides of one conversion workspace. On mobile, the same bilateral identity is preserved in a stacked task flow rather than by compressing a desktop split layout.

See [Original Concept Traceability and Signature Experience](29_ORIGINAL_CONCEPT_TRACEABILITY.md).

## 2. Problem

Conventional currency converters answer the arithmetic question but leave three practical questions unanswered:

1. What can this amount realistically buy at the destination?
2. How do people commonly pay there?
3. What local money customs should a visitor know?

The product closes that context gap without pretending that approximate local prices are universal facts.

## 3. Primary users

### Traveller
Needs a fast conversion and immediate local context before or during a trip.

### Expat / international student
Frequently compares home and destination currencies and benefits from saved pairs and recurring context.

### Digital nomad
Compares day-to-day spending across destinations.

### Shopper
Wants a rough home-currency interpretation of a foreign price.

### Family trip planner
Needs to translate a total budget into meaningful daily spending.

## 4. Jobs to be done

### Core job
> When I see or plan to spend money in another country, help me understand both the converted amount and its practical local value so I can make a better decision.

### Supporting jobs
- quickly swap source and destination;
- verify how fresh the rate is;
- convert using a specific historical date;
- discover archived currencies relevant to a country/date;
- understand which rate observation was actually used;
- understand whether cards or cash are commonly useful;
- see approximate common-item equivalents;
- explore the sourced story behind a currency/date;
- compare a historical reference rate with the latest reference rate when semantically valid;
- repeat frequent pairs;
- inspect historical context;
- prepare a trip budget.

## 5. Product loop

```text
Choose → Convert → Understand → Explore → Save → Return
```

## 6. P0 web scope

A P0 release is successful when an anonymous visitor can:

1. choose source country/currency;
2. choose destination country/currency;
3. enter a valid amount;
4. receive a Decimal-correct converted amount;
5. see rate, provider/source attribution and effective date/time;
6. swap the pair;
7. see an explicit loading/error/stale state;
8. see destination payment/cash/tipping context;
9. see a small set of sourced typical-price examples;
10. use the complete flow with keyboard and mobile viewport;
11. identify both source and destination cultural contexts in the converter itself on larger screens;
12. experience restrained, independent source/destination atmosphere without changes to control mechanics;
13. enter a compact Explore layer with at most three first-level paths: Everyday value, Payment context and Money & culture.

## 7. P1 scope

- historical FX converter with requested/effective-date distinction;
- archived currency discovery in historical mode;
- country/date historical-currency suggestions;
- deterministic sourced money-story layer;
- currency timelines and Then & now comparisons where valid;
- historical chart context;
- recent conversions;
- favourite pairs;
- optional account sync;
- richer cultural profile;
- shareable/bookmarkable current and historical conversion URLs;
- progressive enhancement polish;
- optional click-to-play currency/country pronunciation or short sourced cultural audio;
- sourced source↔destination money-culture comparisons where evidence quality supports them;
- saved cultural pairs that preserve both country and currency context.

## 8. Later scope

### Travel mode
Budget and per-day interpretation.

### Saved trips
Destination, dates, home currency and planned budget.

### Shopping mode
Foreign item price interpreted in home currency with clearly-labelled fee assumptions.

### Offline mobile
Use the last successful rate and cached destination context with explicit staleness.

### Historical purchasing power
A separate, later feature using explicit CPI/PPP/price-level methodology. It must not be inferred from FX rates.

### Rate alerts
Only after notification infrastructure and provider semantics are robust.

## 9. Explicit non-goals

P0 will not include:

- money transfer;
- account balances;
- payment execution;
- trading;
- crypto;
- crowdsourced unsourced prices;
- AI-generated FX rates;
- automatic financial advice;
- full itinerary planning;
- social network features;
- microservices.

## 10. Trust model

Every data point belongs to one of these classes:

### Authoritative
Examples: FX provider rate, ISO code.

Display with source and source timestamp/date.

### Curated factual
Examples: official currency history, capital, payment-network guidance.

Persist with source URL and verification date.

### Approximate contextual
Examples: typical coffee or local-transit price.

Display as an estimate and include location/date/source/confidence.

### Generated explanatory
AI may rewrite or summarize only when its factual inputs are already sourced. Generated content is not a source of truth.

## 11. Success metrics

Portfolio/demo metrics:

- P0 conversion completes in <= 3 primary interactions after defaults;
- no ambiguous stale/live state;
- WCAG 2.2 AA automated checks have no serious/critical violations;
- every displayed external financial datum has provenance;
- domain logic has high branch coverage;
- response path remains functional if JavaScript enhancement fails;
- no client-side framework is shipped on the Django web path.

Potential product metrics for a deployed version:

- conversion completion rate;
- swap usage;
- money-context expansion rate;
- saved-pair rate;
- repeat visits;
- error recovery rate.

## 12. Product differentiation

The differentiation is not “more exchange rates”.

It is:

```text
bilateral source ↔ destination context
+ trusted FX conversion
+ local purchasing context
+ payment customs
+ travel-oriented interpretation
+ cultural/currency context
```

The cultural layer should increase understanding, not compete with the conversion task.

The preferred experience is not:

```text
converter
→ result
→ culture added somewhere below
```

It is:

```text
source cultural context
          ↘
       conversion
          ↗
destination cultural context
          ↓
 local meaning / payment / story
```

Country atmosphere is therefore part of the interaction, while deeper cultural content remains progressive.


## 13. Storytelling layer

Storytelling is a product layer over sourced data, not a content-generation gimmick.

The storytelling system may explain:

- the converted amount in plain language;
- the currency era on the selected date;
- a country/currency transition;
- a valid Then & now rate comparison;
- a relevant sourced historical/cultural moment.

The product-facing entry point can be:

> **The story behind this rate**

Story quality rules:

- every factual claim is sourced;
- temporal relevance matters;
- missing context is omitted rather than invented;
- causal explanations require explicit source support;
- deterministic templates are the default;
- AI, if introduced later, may rewrite only validated sourced facts.

## 14. Historical converter

The historical converter answers:

> **What would this amount convert to using the available historical FX observation for a selected date?**

It does not answer historical purchasing power.

Required semantics:

- `requested_date` = the calendar date selected by the user;
- `effective_date` = the actual rate observation used;
- provider/source attribution remains visible;
- missing weekend/holiday observations are never silently presented as exact-date data;
- archived currencies are discoverable only where data/era context supports them;
- country/date may suggest a historical currency but never silently replace an explicit user choice;
- pair/date coverage is communicated accurately rather than implying universal history back to the provider's earliest date.

## 15. Temporal trust model

Historical experiences must keep these concepts separate:

```text
historical FX rate
≠ inflation
≠ purchasing power
≠ current local prices
≠ investment return
```

A historical conversion can be enriched by a sourced story, but the story must not alter the arithmetic result or imply unsupported economic causality.
