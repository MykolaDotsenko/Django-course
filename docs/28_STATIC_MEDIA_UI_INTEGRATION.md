# Static Media UI Integration Architecture

Status: **accepted implementation contract**

Research/design baseline: **Quiet Atlas**

This document converts the static-image work into an implementation architecture for Django SSR/HTMX.

The goal is not merely to display illustrations.

The goal is to make media:

- centralized;
- replaceable;
- accessible;
- performance-safe;
- compatible with sourced MediaAsset records;
- testable;
- free from hardcoded template paths.

---

# 1. Core finding

The UI should never decide image paths itself.

Selected architecture:

```text
domain/application context
        ↓
media selector
        ↓
asset registry
        ↓
normalized ImageViewModel
        ↓
shared template component
        ↓
HTML
```

This prevents:

- duplicated static paths;
- template-specific fallback logic;
- inconsistent accessibility behavior;
- future pain when static art is replaced by sourced MediaAsset content.

---

# 2. Why not hardcode images in templates

Rejected:

```django
<img src="{% static 'images/quiet-atlas/countries-finland-local-value-v1.svg' %}">
```

repeated across templates.

Problems:

- presentation decisions spread across HTML;
- fallbacks duplicated;
- path changes require multi-file edits;
- templates learn country/story mapping;
- switching to database-backed media becomes expensive.

Selected rule:

> Templates receive a normalized media object, not an asset key/path decision.

---

# 3. Suggested package structure

```text
apps/
└── presentation/
    ├── media_assets.py
    ├── media_selectors.py
    ├── media_view_models.py
    └── home_presenter.py

templates/
└── components/
    └── media/
        ├── image_frame.html
        ├── hero_visual.html
        ├── country_card.html
        ├── story_card.html
        └── explainer_card.html

static/
└── images/
    └── quiet-atlas/
        └── *.svg
```

If the final app layout uses another presentation package, preserve the responsibilities even if exact paths differ.

---

# 4. Asset registry

Use one typed registry for release-owned visuals.

Concept:

```python
from dataclasses import dataclass
from typing import Literal

AssetKind = Literal[
    "hero",
    "fallback",
    "country",
    "story",
    "history",
    "trust",
]

@dataclass(frozen=True, slots=True)
class StaticMediaAsset:
    key: str
    path: str
    ratio: str
    kind: AssetKind
    decorative: bool = True
    alt: str = ""
    label: str = ""
```

The registry describes assets.

It does not contain business logic.

---

# 5. Registry keys

Recommended semantic keys:

```text
hero_home_global_value

fallback_local_value
fallback_history
fallback_payment_culture

country_finland
country_japan
country_usa
country_uk
country_france
country_italy
country_thailand
country_turkey
country_germany
country_spain

story_market_basket
story_cafe_affordability
story_street_food_affordability
story_transit_affordability
story_budget_hotel_affordability

history_euro_transition
history_finland_markka_1998
history_then_now

trust_rate_provenance
```

Keys are stable product semantics.

Filenames may evolve independently.

---

# 6. Country selector

Country mapping belongs in one selector.

```python
COUNTRY_MEDIA_KEYS = {
    "FI": "country_finland",
    "JP": "country_japan",
    "US": "country_usa",
    "GB": "country_uk",
    "FR": "country_france",
    "IT": "country_italy",
    "TH": "country_thailand",
    "TR": "country_turkey",
    "DE": "country_germany",
    "ES": "country_spain",
}

DEFAULT_COUNTRY_MEDIA_KEY = "fallback_local_value"
```

Unknown country:

```text
country-specific static art unavailable
→ fallback_local_value
```

Do not throw an application error.

---

# 7. Story selector

Suggested mapping:

```python
STORY_MEDIA_KEYS = {
    "market_basket": "story_market_basket",
    "cafe_affordability": "story_cafe_affordability",
    "street_food_affordability": "story_street_food_affordability",
    "transit_affordability": "story_transit_affordability",
    "budget_hotel_affordability": "story_budget_hotel_affordability",
    "euro_transition": "history_euro_transition",
    "finland_markka_1998": "history_finland_markka_1998",
    "then_now": "history_then_now",
}
```

Unknown story:

```text
fallback_history
```

---

# 8. Why four new assets were required

The first 19-image pack covered:

- hero;
- country context;
- generic local value;
- generic history;
- payment guidance;
- food/market value stories.

Four high-ROI gaps remained.

## 8.1 Then & Now comparison

File:

```text
history-then-now-comparison-v1.svg
```

Needed because the historical converter has a distinct comparison state:

```text
selected historical value
vs
current value
```

A generic archive illustration does not communicate the two-era structure clearly enough.

## 8.2 Transit affordability

File:

```text
story-transit-affordability-v1.svg
```

Needed because public transport is one of the most intuitive purchasing-power equivalents and appears naturally in destination context.

## 8.3 Budget-hotel affordability

File:

```text
story-budget-hotel-affordability-v1.svg
```

Needed because accommodation is a materially different spending category from food/coffee/transport.

It expands local-value storytelling without adding another decorative country image.

## 8.4 Rate/source provenance

File:

```text
trust-rate-provenance-v1.svg
```

Needed because trust is a primary product differentiator.

Use for:

- source/provenance explainer;
- “Why trust this rate?” section;
- stale/source metadata education;
- trust-focused onboarding.

The asset communicates inspection + verification rather than financial hype.

---

# 9. Current static pack

After this expansion:

```text
23 SVG assets total
```

Composition:

- 1 hero;
- 3 generic fallbacks;
- 10 country/context assets;
- 2 historical era assets;
- 1 Then & Now asset;
- 5 purchasing-power story assets;
- 1 trust/provenance asset.

This is now enough for the planned first product surfaces.

Do not add more static images until screenshot-based UI review proves a real gap.

---

# 10. ImageViewModel

Templates should not receive raw registry objects.

Normalize them.

Concept:

```python
@dataclass(frozen=True, slots=True)
class ImageViewModel:
    src: str
    ratio: str
    alt: str
    decorative: bool
    kind: str
    label: str
```

Builder:

```python
def build_static_image_vm(asset: StaticMediaAsset) -> ImageViewModel:
    return ImageViewModel(
        src=static(asset.path),
        ratio=asset.ratio,
        alt=asset.alt,
        decorative=asset.decorative,
        kind=asset.kind,
        label=asset.label,
    )
```

Future MediaAsset can produce the same view model.

---

# 11. Future MediaAsset compatibility

The template layer must not know whether an image came from:

- static SVG;
- Wikimedia/Europeana sourced media;
- reviewed AI illustration;
- object storage;
- CDN.

Future adapter:

```text
StaticMediaAsset ─┐
                  ├→ ImageViewModel → templates
MediaAsset DB ────┘
```

This keeps the first implementation simple while preserving migration path.

---

# 12. Base image component

Recommended template:

```django
<div
  class="overflow-hidden rounded-[28px] border border-black/5 bg-white/60 shadow-sm"
  style="aspect-ratio: {{ image.ratio }}"
>
  <img
    src="{{ image.src }}"
    alt="{{ image.alt }}"
    {% if image.decorative %}aria-hidden="true"{% endif %}
    class="h-full w-full object-cover"
    loading="{{ loading|default:'lazy' }}"
    decoding="async"
  >
</div>
```

Centralize:

- radius;
- border;
- shadow;
- loading behavior;
- object-fit.

---

# 13. Home hero mapping

Use:

```text
hero_home_global_value
```

Rules:

- desktop: visual adjacent to primary converter;
- mobile: below primary copy/form;
- only one media asset may be eager-loaded;
- conversion form and H1 remain understandable without the image.

Do not make the hero an opaque full-screen background behind form fields.

---

# 14. Local-value explainer mapping

Generic local-value section:

```text
fallback_local_value
```

Specific destination:

```text
country selector
→ country_* asset
```

Purchasing-power cards:

```text
market → story_market_basket
café → story_cafe_affordability
street food → story_street_food_affordability
transit → story_transit_affordability
budget accommodation → story_budget_hotel_affordability
```

Not every category needs an image simultaneously.

Use media to create hierarchy, not a gallery.

---

# 15. Historical converter mapping

Historical landing/empty state:

```text
fallback_history
```

Specific Finland markka story:

```text
history_finland_markka_1998
```

Euro transition:

```text
history_euro_transition
```

Then & Now result:

```text
history_then_now
```

Historical static illustrations must display as:

> Illustrative visual

when context could otherwise imply archival authenticity.

---

# 16. Trust/source mapping

Use:

```text
trust_rate_provenance
```

for a compact explainer such as:

- provider;
- observation/effective date;
- fetched-at time;
- stale/fresh meaning;
- source attribution.

Do not place it next to every rate result.

Recommended use:

- expandable trust section;
- product explainer;
- onboarding/tutorial;
- empty/source education state.

---

# 17. Payment culture mapping

Use:

```text
fallback_payment_culture
```

only when there is meaningful payment guidance.

Do not use an image merely because a card has empty space.

---

# 18. Home page image budget

Recommended home screen maximum before interaction:

- 1 hero;
- 3 explainer images at most;
- 3–6 featured country cards;
- story images below fold.

Do not render all 23 assets on the landing page.

---

# 19. Mobile image budget

On mobile:

- hero after primary action;
- one-column cards;
- image height bounded by aspect ratio;
- avoid consecutive image-heavy cards without text rhythm;
- lazy-load below first viewport.

The converter must remain visible without scrolling through decorative content first.

---

# 20. Accessibility

Default static illustrations are decorative.

Use:

```html
alt=""
aria-hidden="true"
```

where surrounding text communicates the same concept.

If a sourced historical image later carries factual information:

- provide contextual alt;
- visible caption/source;
- do not mark decorative.

AI authenticity labels belong in visible UI metadata, not alt text alone.

---

# 21. Performance

SVG advantages:

- scalable;
- small;
- no responsive raster variants required;
- deterministic;
- no external media host.

Rules:

- do not inline every SVG into HTML;
- serve through static URL;
- explicit aspect ratio;
- hero only may be eager;
- below-fold media lazy;
- no JS image loader required.

---

# 22. HTMX behavior

HTMX fragment responses should not trigger image-selection side effects.

The selector is a pure function over presentation context.

Example:

```text
country changes
→ backend returns updated result/context fragment
→ same selector chooses image
→ browser loads static URL if not cached
```

No AI generation.
No media import.
No write.

---

# 23. Testing

## Registry tests

Assert:

- every key is unique;
- every path exists;
- ratio belongs to approved set;
- decorative assets have empty alt by default.

## Selector tests

Assert:

- known country → expected key;
- unknown country → fallback;
- known story → expected key;
- unknown story → history fallback.

## Template tests

Assert:

- decorative image has empty alt;
- hero loading behavior;
- source URL comes from view model;
- no raw static path mapping in page template.

## Static-file integrity

For all current SVGs:

- starts with SVG root;
- has viewBox;
- no script;
- no external href;
- no embedded raster image;
- no embedded text element.

---

# 24. Screenshot matrix

After implementation, render:

## Desktop

1. home hero;
2. converter success + country context;
3. local-value story group;
4. historical Then & Now;
5. trust/source explainer;
6. country grid;
7. story grid.

## Mobile

8. home hero;
9. converter success;
10. local-value story;
11. historical Then & Now;
12. country/story card stack.

Review at minimum:

- 390px;
- 768px;
- 1440px.

---

# 25. Visual QA questions

For every screen:

1. Does the image clarify hierarchy?
2. Would the page remain fully useful without it?
3. Is the image competing with the converted amount?
4. Is the country visual stereotypical?
5. Could a historical illustration be mistaken for evidence?
6. Is the same concept repeated visually too many times?
7. Does the mobile page become image-heavy?
8. Does this asset earn its bytes and vertical space?

If not, remove it.

---

# 26. Recommended implementation PR sequence

## PR A — media presentation foundation

Add:

- typed asset registry;
- country/story selectors;
- ImageViewModel;
- tests.

No UI redesign yet.

## PR B — reusable media components

Add:

- image frame;
- hero visual;
- country card;
- story card;
- explainer card.

## PR C — home + converter integration

Wire:

- hero;
- fallback/local-value;
- country context;
- trust section;
- payment context.

## PR D — historical integration

Wire:

- generic history;
- Then & Now;
- markka/euro stories.

## PR E — screenshot and pruning pass

Render desktop/mobile.

Remove or replace any static asset that does not improve comprehension.

---

# 27. Anti-patterns

Do not:

- put country → filename maps in templates;
- create one template per asset;
- add JS to choose static images;
- use inline SVG everywhere;
- use alt text for SEO stuffing;
- render every image on one page;
- make historical art look like archival evidence;
- fetch AI images at runtime;
- add more images before screenshot QA.

---

# 28. Definition of done

Static-media UI integration is complete when:

- one typed registry owns release asset metadata;
- selector functions own country/story mapping;
- templates receive normalized ImageViewModel;
- no page template hardcodes specific Quiet Atlas file paths;
- all current 23 assets pass integrity tests;
- fallback behavior is tested;
- desktop/mobile screenshot matrix has been reviewed;
- image count has been pruned based on actual UI value;
- architecture can later accept database-backed MediaAsset without rewriting templates.

---

# 29. Final finding

The optimal portfolio signal is not “many generated images”.

It is:

> **a small, coherent asset system with typed selection, graceful fallbacks, historical honesty, zero runtime cost, and a clean path to real sourced media later.**

That is the architecture this document standardizes.


# 30. Foundation implementation status

The first implementation slice lives in the transitional Django shell at:

```text
django-blog/apps/common/presentation/
├── media_assets.py
├── media_selectors.py
└── media_view_models.py
```

This location is intentionally outside the legacy `apps.post` feature.

The module contains no blog/domain dependency and can move unchanged into the rebuilt project shell.

The implementation also configures:

```text
STATICFILES_DIRS = [BASE_DIR.parent / "static"]
```

so the repository-root Quiet Atlas pack is discoverable by the current Django staticfiles system.

Tests cover:

- all 23 registry entries;
- unique/static paths;
- approved aspect ratios;
- decorative accessibility defaults;
- registry immutability;
- country normalization/fallback;
- story normalization/fallback;
- named hero/payment/provenance selectors;
- ImageViewModel static URL generation;
- explicit meaningful-alt promotion;
- Django staticfiles discovery for every registered asset.

Normal command from `django-blog/`:

```text
pytest
```

The project pyproject now provides the Django settings/testpaths needed by pytest-django.


# 31. Reusable template component implementation

The second implementation slice introduces exactly two project-level templates:

```text
django-blog/templates/components/media/
├── image_frame.html
└── media_card.html
```

This deliberately avoids separate country/story/explainer card templates while their structure is still identical.

## image_frame.html

Owns:

- intrinsic width/height;
- aspect-ratio wrapper;
- lazy/eager loading;
- async decoding;
- optional fetchpriority;
- decorative `aria-hidden`;
- optional semantic figcaption;
- one stable media CSS hook.

## media_card.html

Owns:

- shared image frame;
- optional eyebrow;
- title;
- optional href;
- summary;
- optional badge.

Country/story/explainer presenters vary data, not duplicated markup.

The typed Python contract is:

```text
MediaCardViewModel
- image: ImageViewModel
- title
- summary
- href
- eyebrow
- badge
```

## Intrinsic dimensions

StaticMediaAsset now stores physical SVG dimensions.

Current contract:

- hero: 1600×900;
- all card/history/trust assets: 1200×900.

The dimensions flow into ImageViewModel and then HTML `width`/`height` attributes to strengthen layout stability.

## Project-level template discovery

The transitional Django settings now include:

```text
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]
```

so shared presentation components do not need to live inside the legacy blog app.

## Component tests

Template tests assert:

- decorative image defaults to lazy + async loading;
- decorative image uses empty alt and aria-hidden;
- intrinsic dimensions render;
- hero can opt into eager/high fetch priority;
- meaningful image is not hidden from the accessibility tree;
- optional figcaption renders semantically;
- media card renders typed optional fields and link;
- missing href renders a non-link title.

This keeps accessibility/performance behavior centralized instead of retested independently in every future page.


# 32. DEBUG visual QA preview

A dedicated preview surface now exists at:

```text
/_design/media/
```

It is registered only when:

```text
DEBUG = True
```

Purpose:

- inspect the real registry/selectors/view models/templates together;
- review image density before product-page wiring;
- compare desktop/tablet/mobile layouts;
- verify historical illustration labels;
- verify trust/provenance placement;
- test eager vs lazy loading behavior.

The preview is not a product page and must not become a production route.

## Preview coverage

The page renders:

- home hero;
- three explainer cards;
- all ten initial destination visuals;
- five purchasing-power story categories;
- Then & Now;
- Finland markka era;
- euro transition;
- trust/source block.

The page intentionally renders more media than a real product screen because its job is QA, not production information density.

## Preview styling

The route uses:

```text
static/css/quiet-atlas-preview.css
```

This stylesheet is **preview-only**.

It exists so media composition can be evaluated before the planned Tailwind/Vite implementation.

Do not evolve it into a second production CSS system.

When Tailwind ships:

- production pages use the design-system utility/components;
- this preview can either migrate to those components or remain a small isolated QA harness.

## Preview tests

Tests assert:

- route renders;
- correct template;
- expected section/card counts;
- key scenarios are visible;
- hero uses eager/high fetch priority;
- card media remains lazy by default.

This gives one end-to-end presentation test across the static-media stack.


# 33. Automated browser screenshot QA

Responsive visual QA is automated through Playwright.

Workflow:

```text
.github/workflows/media-preview-screenshots.yml
```

Capture script:

```text
django-blog/scripts/capture_media_preview.py
```

## Viewports

The workflow renders the DEBUG media preview at:

- desktop: 1440 × 1200;
- tablet: 768 × 1024;
- mobile: 390 × 844.

Each capture is full-page.

## Browser integrity checks

Before saving a screenshot, the Playwright script asserts:

- expected preview H1;
- exactly 23 rendered images;
- every image completed with non-zero natural width;
- no page-level horizontal overflow;
- no browser console errors;
- HTTP response is successful.

A visually broken asset therefore fails QA instead of merely producing a misleading screenshot.

## Artifact

Successful runs upload:

```text
quiet-atlas-media-preview
```

containing:

```text
desktop-1440.png
tablet-768.png
mobile-390.png
```

Artifacts are retained for 14 days.

The workflow is intentionally scoped to media/template/preview-related changes and can also be run manually.

## Tooling

Current reviewed implementation uses:

- Python 3.13;
- Playwright Python 1.63.0;
- Chromium;
- actions/checkout v7;
- actions/setup-python v7;
- actions/upload-artifact v7.

Production does not depend on Playwright. It is QA tooling only.


# 34. Responsive and social derivative implementation

Browser screenshot QA validated the original 23 semantic content assets and exposed two additional delivery surfaces that justify dedicated compositions:

- narrow mobile hero/history presentation;
- 1200×630 social/OpenGraph previews.

Five release-owned derivatives were therefore added without expanding country/story semantics:

```text
hero-home-global-value-mobile-v1.svg
history-then-now-mobile-v1.svg
og-home-global-value-v1.svg
og-history-then-now-v1.svg
og-local-value-v1.svg
```

The registry now contains **28 assets**:

- 23 canonical semantic assets;
- 2 responsive portrait derivatives;
- 3 social/OpenGraph derivatives.

## Selection contract

Dedicated selectors own these variants:

```text
select_home_hero_mobile_media()
select_history_then_now_mobile_media()
select_home_og_media()
select_history_og_media()
select_local_value_og_media()
```

Page templates should not guess filenames or dimensions.

## Responsive images

The two portrait derivatives are 960×1200 / 4:5.

They are intended for responsive source selection when a narrow viewport materially benefits from a different composition.

Do not render/download desktop and portrait hero assets simultaneously without browser-level source selection.

Recommended future production markup:

```html
<picture>
  <source media="(max-width: 640px)" srcset="...mobile...">
  <img src="...desktop..." ...>
</picture>
```

The server/presenter still owns which approved semantic variant is available.

## Social images

The three OpenGraph derivatives are 1200×630 and intentionally contain no baked text.

This keeps:

- title/copy in metadata rather than pixels;
- localization independent from artwork;
- the image reusable across page titles;
- visual authenticity rules identical to in-product artwork.

These are release-owned visuals, so they may live in static.

## QA

The DEBUG media preview renders all 28 registered assets.

Playwright now validates all 28 at:

- 1440px;
- 768px;
- 390px.

The original content-pack constraint remains:

> Delivery-format derivatives are allowed only for concrete rendering surfaces; they are not permission to create more decorative country cards.


---

# 35. Managed MediaAsset integration implemented

The original static-media architecture remains the deterministic fallback and is now joined by the roadmap PR7A managed-media path.

Current presentation flow:

\`\`\`text
domain/application context
        ↓
apps.media.services.select_published_media()
        ↓
published managed MediaAsset?
        ├── yes → managed storage URL + provenance/authenticity metadata
        └── no  → Quiet Atlas static selector
                         ↓
               normalized ImageViewModel
                         ↓
               shared media template
\`\`\`

The shared \`ImageViewModel\` now supports both release-owned static assets and managed assets with optional:

- caption;
- attribution text;
- canonical source URL;
- visible authenticity label.

Templates still do not know database-selection rules, external provider schemas or static filenames.

The managed selector is deliberately read-only and local. External archive search remains a management-command/editorial concern, so rendering a page never creates a Wikimedia/Europeana/AI dependency.
