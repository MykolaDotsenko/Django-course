# Product Specification

## 1. Product statement

**Cultural Currency Converter** is a travel-money intelligence application that helps people convert currency and understand the local meaning of the converted amount.

Tagline:

> **Convert money. Understand local value. Discover culture.**

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
- understand whether cards or cash are commonly useful;
- see approximate common-item equivalents;
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
10. use the complete flow with keyboard and mobile viewport.

## 7. P1 scope

- recent conversions;
- favourite pairs;
- optional account sync;
- richer cultural profile;
- historical rate context;
- shareable/bookmarkable conversion URL;
- progressive enhancement polish.

## 8. Later scope

### Travel mode
Budget and per-day interpretation.

### Saved trips
Destination, dates, home currency and planned budget.

### Shopping mode
Foreign item price interpreted in home currency with clearly-labelled fee assumptions.

### Offline mobile
Use the last successful rate and cached destination context with explicit staleness.

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
FX conversion
+ local purchasing context
+ payment customs
+ travel-oriented interpretation
+ cultural/currency context
```

The cultural layer should increase understanding, not compete with the conversion task.
