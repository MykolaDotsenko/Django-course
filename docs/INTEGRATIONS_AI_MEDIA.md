# Integrations, AI and Media

This document describes the main external trust boundaries. Exact provider versions, endpoints and configuration live in code and environment settings.

## Integration principle

External data should enter the product through a small project-owned boundary:

```text
external response
→ transport/validation
→ normalized project-owned value
→ application/domain use
```

Do not spread provider-specific payload shapes through views, templates or domain models.

## Runtime FX

Frankfurter is the current runtime FX provider.

The exchange layer is responsible for:

- bounded timeout/retry behaviour;
- normalization;
- attribution/provenance;
- requested/effective-date semantics;
- current/historical coverage handling;
- safe caching and stale semantics.

A provider response is not trustworthy merely because the HTTP status is 200. Validate the semantic payload before using or caching it.

Provider choice can change later if another source provides better coverage/reliability while preserving the normalized domain contract.

## Country/currency metadata

REST Countries is currently used as an import/reference source rather than a normal page-request dependency.

Country/currency data should be normalized into local models so the product can:

- preserve stable identity;
- represent temporal relationships;
- reconcile upstream changes deliberately;
- remain usable during source outages.

Imports should be repeatable and non-destructive by default when upstream drift is ambiguous.

## Editorial/cultural sources

Curated cultural, payment, typical-price and story content should keep enough source metadata to explain:

- where the claim came from;
- when it was observed/verified;
- what geographic/temporal scope it has;
- how much confidence the UI should imply.

Wikidata and similar sources are suitable for candidate ingestion/research, not automatic runtime truth.

## Media sources

Managed external media can come from sources such as Wikimedia Commons or Europeana when rights/provenance are sufficient.

Prefer a pipeline like:

```text
candidate metadata
→ review
→ safe local/managed copy
→ validation/derivatives
→ publish
→ runtime selection
```

Avoid hotlink/search dependencies in the primary conversion request path.

## Quiet Atlas static media

The repository includes release-owned Quiet Atlas SVG assets under:

`static/images/quiet-atlas/`

They provide deterministic visual fallbacks for:

- country atmosphere;
- historical context;
- everyday-value/story cards;
- provenance/trust surfaces;
- social/preview assets.

Use the existing registry/selectors instead of scattering asset filenames through templates.

Static fallbacks may be replaced or supplemented by better managed media without changing the product contract.

## AI role

AI is an optional synthesis capability, not a source of financial or historical truth.

Current runtime behaviour:

- server-side Google Gemini integration;
- explicit user-triggered explanation;
- bounded trusted input packet;
- structured output;
- application-side validation;
- persistent/deterministic fallback;
- core conversion remains AI-independent.

The currently configured model (`gemini-3.1-flash-lite`) is a configuration choice. Change it only after checking quality, latency, cost and failure behaviour; the documentation does not treat a model name as permanent architecture.

## AI input/output discipline

Prefer:

```text
trusted deterministic facts
→ small typed packet
→ model
→ structured candidate
→ semantic validation
→ display/review
```

Do not ask the model to invent missing rates, dates, provenance or historical causality.

For user-facing factual text, retain the ability to map claims back to trusted source material.

## AI availability and cost

AI should have:

- explicit enable/disable configuration;
- bounded timeout/attempts;
- no browser-exposed provider key;
- no normal CI dependence on live provider calls;
- graceful fallback on quota/provider failure.

A future provider/model may be adopted if it improves the capability without weakening privacy, trust or reliability.

## Generated imagery

Runtime image generation is currently disabled.

If generated imagery is added later:

- use it as illustration rather than archival evidence;
- store/review it before publication for factual/historical surfaces;
- label it appropriately when authenticity could be misunderstood;
- keep deterministic fallbacks.

## Security/privacy at external boundaries

Avoid sending unnecessary personal/user-owned data to external providers.

Never log credentials, bearer tokens or provider secrets.

Network calls should generally happen outside database transactions that hold locks or await durable writes.

## Adding a new integration

Before adding one, answer:

- What user problem does it solve?
- Is runtime access necessary, or can data be imported/cached?
- What is the normalized project-owned contract?
- What happens when the provider fails or changes shape?
- What provenance/licensing constraints apply?
- What tests can run without live provider dependence?
- What data leaves our system?

If those answers are unclear, keep the integration experimental until they are.
