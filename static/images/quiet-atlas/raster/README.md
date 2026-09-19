# Quiet Atlas AI Raster Candidates

This directory contains **review candidates**, not canonical product media.

The canonical zero-runtime-cost visual layer remains the release-owned SVG pack
under `static/images/quiet-atlas/`.

Raster candidates may be promoted only after visual review confirms that they:

- match the Quiet Atlas art direction;
- contain no unwanted readable text;
- contain no logos or accidental brand marks;
- do not introduce country stereotypes;
- do not imply fabricated historical evidence;
- improve a real product surface over the SVG fallback;
- remain lightweight after optimization.

## Current candidates

| File | Semantic role | Prompt source | Generator | Job | Status |
|---|---|---|---|---|---|
| `trust-rate-provenance-ai-v1.webp` | trust / provenance | IMG-23 | Z Image | `aa52c950-ee69-4c26-882b-c0a37d4aae63` | generated candidate |

## Optimization

The source generator result is never committed directly by default.

Current pipeline:

```text
generator PNG
→ auto-orient
→ resize to product-appropriate review size
→ strip metadata
→ WebP compression
→ Git binary blob
```

The first provenance candidate was normalized to:

```text
560 × 420 WebP
~6.7 KiB
```

This small file is sufficient for repository review and preview comparison. A
larger derivative can be produced deliberately if a production surface proves
it needs additional resolution.

## Promotion rule

A raster candidate does not replace an SVG merely because it looks more
photographic.

Promotion requires a concrete UI reason such as:

- stronger hero emotional signal;
- better country atmosphere;
- clearer editorial storytelling;
- superior social-preview quality.

If raster art does not clearly outperform the release-owned SVG, keep the SVG.

## Historical rule

AI-generated historical-looking media is always editorial illustration.

It must never be described as an archival photograph or historical evidence.

## Runtime rule

These files are generated ahead of time and stored.

No normal country/year selection triggers an image-generation API call.
