# Quiet Atlas Static Image Pack

This directory contains release-owned static illustrations for Cultural Currency Converter.

## Rules

- SVG only for the initial pack.
- No runtime AI generation.
- No external image dependencies.
- No text embedded in the artwork.
- Country visuals are atmospheric, not evidence.
- Historical visuals are editorial illustrations, not archival photographs.
- Use real sourced media through the MediaAsset pipeline when factual visual evidence matters.

## Files

### Hero

- `hero-home-global-value-v1.svg`

### Generic fallbacks

- `fallback-local-value-generic-v1.svg`
- `fallback-history-generic-v1.svg`
- `fallback-payment-culture-v1.svg`

### Country context

- `countries-finland-local-value-v1.svg`
- `countries-japan-local-value-v1.svg`
- `countries-usa-local-value-v1.svg`
- `countries-uk-local-value-v1.svg`
- `countries-france-local-value-v1.svg`
- `countries-italy-local-value-v1.svg`
- `countries-thailand-local-value-v1.svg`
- `countries-turkey-local-value-v1.svg`

### Historical editorial illustrations

- `history-euro-transition-2002-v1.svg`
- `history-finland-markka-1998-v1.svg`

### P1 expansion

- `countries-germany-local-value-v1.svg`
- `countries-spain-local-value-v1.svg`
- `story-market-basket-value-v1.svg`
- `story-cafe-affordability-v1.svg`
- `story-street-food-affordability-v1.svg`

### UI coverage expansion

- `history-then-now-comparison-v1.svg`
- `story-transit-affordability-v1.svg`
- `story-budget-hotel-affordability-v1.svg`
- `trust-rate-provenance-v1.svg`

### Responsive / social derivatives

- `hero-home-global-value-mobile-v1.svg`
- `history-then-now-mobile-v1.svg`
- `og-home-global-value-v1.svg`
- `og-history-then-now-v1.svg`
- `og-local-value-v1.svg`

Total current pack: **28 SVG assets**.

Full prompt, usage and authenticity documentation:

- `docs/27_STATIC_IMAGE_GENERATION_PLAN.md`


## Selection architecture

Do not hardcode these file paths directly across page templates.

Use the presentation registry/selectors documented in:

- `docs/28_STATIC_MEDIA_UI_INTEGRATION.md`

The original 23-asset content pack remains capped. The 5 additional files are responsive/social derivatives added only after real desktop/mobile screenshot QA identified concrete delivery surfaces.
