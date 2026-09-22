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

The exchange layer owns bounded timeout/retry behaviour, normalization, attribution, requested/effective-date semantics, historical coverage and cache/stale behaviour.

A successful HTTP response is not sufficient; validate semantic payloads before use or caching.

## Country/currency metadata

REST Countries is currently an import/reference source rather than a normal page-request dependency.

Normalize country/currency data locally so the product can preserve stable identity, temporal relationships and controlled reconciliation during upstream changes.

## Editorial/cultural sources

Curated cultural, payment, typical-price and story content should keep enough provenance to explain source, observation/verification time, scope and confidence.

Wikidata and similar services are candidate/research sources rather than automatic runtime truth.

## Premium photography strategy

The product uses **managed realistic photography**, not release-owned cartoon country illustrations.

Preferred hierarchy:

```text
high-quality owned/licensed contemporary photo
→ high-quality sourced editorial photo
→ authentic archival/heritage media for historical surfaces
→ no image
```

“No image” is an intentional valid state. Do not fill a premium layout with weak stock, cartoon fallback art or synthetic-looking placeholders merely to occupy a media slot.

Country hero and country teaser selection is restricted to reviewed, non-generated `contemporary_photo` assets.

## Media pipeline

Managed external media can come from sources such as Wikimedia Commons, Europeana, institutions or manually curated licensed/owned photography.

Prefer:

```text
candidate/source
→ rights + provenance review
→ safe managed raster copy
→ normalization/derivatives
→ editorial approval
→ publish
→ local runtime selection
```

Normal page requests should not search the web or call an image-generation service.

## File formats

Managed media validation accepts JPEG, PNG and WebP and rejects SVG ingestion.

For photographic delivery:

- retain a high-quality managed source;
- generate appropriately sized derivatives;
- prefer modern compressed delivery such as WebP where supported by the current pipeline;
- preserve intrinsic dimensions and focal/composition information.

SVG remains suitable for interface icons and small vector marks; it is not used as large editorial country imagery.

## Media quality bar

Before publishing a destination image, check:

- realistic and contemporary when used as current country atmosphere;
- strong composition and sufficient resolution;
- natural, premium editorial treatment;
- no obvious stock cliché or country stereotype;
- no misleading logos, text or manipulated factual cues;
- rights/provenance are sufficient;
- useful alt text when the image carries meaning.

## Historical media

Historical surfaces prefer real archival photography, documents, currency objects and institutional/heritage imagery.

Temporal precision should be honest. A visually attractive but misleading historical image is worse than no image.

## AI role

AI is optional synthesis, not a source of FX rates, historical observations or published factual truth.

Current runtime behaviour remains server-side, explicit, structured, validated and AI-independent for the core conversion path.

The configured provider/model is an implementation choice and may change after quality, latency, cost and reliability evaluation.

## Generated imagery

Runtime image generation is disabled.

Generated imagery is not the default visual strategy. If used in the future, it should be an explicitly reviewed supporting asset where factual authenticity is not implied. It should not replace real destination photography or masquerade as archival evidence.

## AI availability and cost

AI should remain:

- explicitly configurable;
- bounded by timeout/attempts;
- server-side with no browser-exposed key;
- absent from normal live-provider CI;
- gracefully degradable.

## Security/privacy at external boundaries

Avoid sending unnecessary personal/user-owned data to external providers.

Never log credentials, bearer tokens or provider secrets.

Avoid holding database locks/transactions around external network calls unless there is a concrete transactional reason.

## Adding a new integration

Before adding one, answer:

- What user problem does it solve?
- Is runtime access necessary, or can data be imported/cached?
- What is the project-owned normalized contract?
- What happens when the provider fails or changes shape?
- What provenance/licensing constraints apply?
- What tests can run without live provider dependence?
- What data leaves our system?
