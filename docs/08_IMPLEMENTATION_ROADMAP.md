# Roadmap

This roadmap is an active direction, not a sequence of frozen PR contracts.

Re-evaluate priorities as product value, code quality and deployment needs become clearer.

## Current baseline

The web product already includes:

- current and historical FX conversion;
- country/currency temporal modelling;
- historical trends and Then & Now;
- destination payment/everyday-value context;
- deterministic culture/story content;
- managed media and static fallbacks;
- optional AI explanation with deterministic fallback;
- browser-local favourites/recent conversions;
- account authentication and durable favourites;
- separately opt-in account recent history;
- browser accessibility/reflow quality gates.

## Now: strengthen the web product

Continue improving the existing experience based on real product value.

Likely work includes:

- tighter integration of country atmosphere/media into the main converter;
- simplification of UX where controls/content are duplicated;
- better empty/degraded states;
- product-level performance profiling;
- deployability and production configuration;
- better portfolio/demo clarity;
- additional source quality where enrichment is thin.

Treat these as outcome areas rather than mandatory implementation recipes.

## Next candidate: stable external/mobile API

A versioned API is a reasonable next capability if a native client or external consumer becomes active.

Before implementation, re-evaluate:

- whether DRF is still the best fit;
- schema/OpenAPI tooling;
- authentication needs;
- endpoint granularity;
- offline/stale semantics.

Do not build an API only to satisfy an old roadmap line.

## Later candidate: native mobile

A native client should reuse backend/domain meaning, not copy web templates or business rules.

Choose the current stable mobile stack when implementation starts. React Native/Expo remains a strong candidate, but versions/libraries are intentionally not frozen in advance.

## Later candidate: trips and budgets

Trip/budget workflows can be valuable after the core converter/context experience proves repeat use.

Potential outcomes:

- saved trip;
- destination/currency context;
- daily/total budget interpretation;
- cross-device ownership;
- offline-friendly access.

Keep this separate from basic conversion unless user evidence justifies merging the flows.

## Research: historical purchasing power

Historical FX answers “what did currencies exchange at?”

Historical purchasing power answers a different question and needs defensible methodology.

Before shipping, research:

- CPI/inflation datasets;
- PPP/price-level methodology;
- country coverage;
- base periods;
- licensing/provenance;
- how to explain uncertainty.

Do not present a prototype as precise historical purchasing power.

## Production hardening

As public usage grows, revisit:

- deployment platform;
- PostgreSQL backup/restore;
- shared cache only when justified;
- observability/alerts;
- provider incident handling;
- media/object storage;
- security headers;
- performance budgets derived from measurements.

## How to add roadmap work

Add an item when it has:

- a user/problem outcome;
- enough evidence to justify work;
- a rough dependency/risk picture.

Do not create a separate roadmap document for each initiative. Refine this file and use issues/PRs for implementation detail.
