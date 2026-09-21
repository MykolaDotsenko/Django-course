
# Media, Historical Imagery and Generative Image Strategy

Research date: **2026-09-19**.

This document defines how Cultural Currency Converter uses images for country atmosphere, historical storytelling and country/year comparisons.

The core decision is intentionally hybrid:

> **Real sourced media for evidence. Generated media for illustration. Static/vector assets for product identity. No default on-demand AI generation when the user changes country/year.**

The visual system must remain valuable even when no image is available.

---

# 1. Executive decision

Use four media classes.

## A. Product-owned static assets

Examples:

- logo;
- icons;
- Quiet Atlas SVG patterns;
- empty-state illustrations if any;
- small decorative motifs.

Storage:

- version-controlled under static assets;
- built/deployed with Vite/Django staticfiles.

No runtime AI.

## B. Programmatic country atmosphere

Examples:

- country accent;
- gradients;
- map/grid motifs;
- archival texture;
- currency-era color cues.

Implementation:

- CSS variables;
- SVG;
- deterministic tokens.

This is the **default visual fallback for every country/year**.

No raster image is required.

## C. Real sourced editorial/historical media

Examples:

- historical banknote photo;
- archival street image;
- public-domain photograph;
- museum/heritage object;
- contemporary destination image.

Priority sources:

- Wikimedia Commons;
- Europeana;
- official institutions/archives where rights are clear.

These are used when the image is factual/editorial evidence.

## D. AI-generated illustration

Examples:

- abstract “money & culture” atmospheric illustration;
- editorial reconstruction of a historical era;
- non-factual visual bridge when no suitable archive image exists.

AI-generated media is:

- generated ahead of user requests by default;
- reviewed;
- stored like editorial media;
- clearly labelled when it could be mistaken for evidence.

It is **not** a historical source.

---

# 2. Why not generate on every selection

Rejected default flow:

```text
user selects Japan + 1985
→ image-generation API call
→ wait
→ image appears
```

Problems:

1. conversion becomes dependent on an unrelated AI provider;
2. user latency becomes unpredictable;
3. every country/date change can create a billable request;
4. generated output can vary for the same input;
5. historical hallucination risk increases;
6. moderation/provider outage can damage an otherwise working conversion;
7. mobile offline becomes worse;
8. visual cache/storage becomes harder to reason about;
9. rapid selector changes can trigger wasted generations;
10. recruiter signal shifts from careful domain design toward gimmick API usage.

Therefore runtime AI generation is not part of the core conversion request path.

---

# 3. Primary visual hierarchy

Image strategy follows product hierarchy.

```text
conversion
↓
provenance
↓
historical/current context
↓
visual enrichment
```

An image may enrich understanding.

An image may never be required to understand:

- the amount;
- rate;
- date;
- source;
- historical context;
- comparison.

No image is preferable to misleading image.

---

# 4. Country selection behavior

Changing source or destination country may change its own presentation context.

Source-side changes may affect:

- source country token/theme;
- optional source editorial/static atmosphere;
- source country/context label.

Destination-side changes may affect:

- destination country token/theme;
- flag where appropriate;
- payment/local context;
- purchasing context;
- optional destination editorial media.

Neither side may change FX arithmetic or control mechanics.

The destination remains the primary home for practical local-value/payment enrichment; bilateral source atmosphere does not require duplicating destination-context data.

Do **not** trigger image generation.

Example:

```text
Finland
→ cool neutral atmosphere
→ restrained Finnish country accent
→ curated image if available

Japan
→ same component architecture
→ Japanese country atmosphere tokens
→ curated image if available
```

The interface remains complete when no curated image exists.

---

# 5. Year selection behavior

Selecting a historical year changes:

- historical currency semantics;
- dates/timeline;
- story;
- optional historical media selection.

It does not trigger an AI render by default.

The system searches already-published media whose temporal scope matches the selected context.

---

# 6. Exact year does not require exact-year imagery

A dangerous design would imply:

> “You selected 1973, therefore this image depicts 1973.”

Unless the image itself is reliably dated, do not make that claim.

Media can be scoped by:

- exact date;
- exact year;
- bounded date range;
- currency era;
- broad editorial era.

Presentation makes the scope explicit.

Example:

> Helsinki, c. 1970s

rather than:

> Helsinki, 1973

when only decade-level dating is known.

---

# 7. Country/year media selection

Conceptual query:

```text
select_media(
  country,
  currency,
  target_date,
  role,
  aspect_ratio
)
```

Priority:

1. exact relevant real historical media;
2. real media with valid date range containing target date;
3. real media from relevant currency era;
4. approved AI-generated illustration matching the era;
5. current/neutral country illustration if semantically safe;
6. Quiet Atlas CSS/SVG atmosphere fallback.

Do not stretch a loosely related archival image merely to fill space.

---

# 8. Comparison mode

For Then & Now or country/year comparison, each side selects media independently.

Example:

```text
Finland · 1998
[real archival image if available]
Finnish markka context

Finland · 2026
[current sourced image if useful]
Euro context
```

If only one side has trustworthy media:

- show media on that side if layout remains balanced;
- or use neutral visual fallback on both.

Do not generate a fake matching historical photograph solely for symmetry.

---

# 9. Historical-evidence rule

Real archival/historical images can function as evidence only when the backend has:

- source;
- creator/institution where known;
- rights/licence statement;
- source record URL;
- temporal scope/date;
- editorial relevance;
- attribution.

AI imagery is never evidence.

---

# 10. AI reconstruction rule

If an AI image depicts a historical-looking scene, label it.

Preferred:

> AI-generated editorial illustration

or:

> Artistic reconstruction · AI-generated

If source facts informed it:

> Illustration based on sourced historical context; not an archival photograph.

Do not label it:

> Helsinki, 1920

in a way that implies documentary authenticity.

---

# 11. Generated-image use cases

Good AI-generation uses:

- abstract country/currency atmosphere;
- map-like editorial texture;
- quiet non-photoreal historical reconstruction;
- story section cover;
- empty state;
- social preview artwork.

Poor uses:

- “photograph of this exact event” without a source;
- banknote reproduction that could be mistaken for authentic security imagery;
- portraits of historical persons presented as documentary material;
- exact historical architecture presented as verified fact;
- every selector change.

---

# 12. Prefer illustration over fake photography

For historical AI output, preferred style direction is intentionally illustrative.

Examples:

- editorial gouache;
- restrained lithographic illustration;
- archival poster-inspired geometry;
- line-and-wash urban illustration;
- Quiet Atlas cartographic collage.

Avoid photorealism when factual ambiguity is high.

This reduces the chance that users interpret generation as a real archive photograph.

---

# 13. Quiet Atlas generated style

Generated assets should follow a consistent prompt/style contract.

Properties:

- calm;
- editorial;
- high negative space;
- no visual clutter;
- no text generated into the image;
- no floating currency symbols;
- no glossy crypto-fintech look;
- no stereotypical “national costume collage”;
- no saturated tourism-ad aesthetic;
- no stock-photo business people;
- no flags dominating composition.

Images support the information hierarchy rather than become the product.

---

# 14. Prompt template strategy

Prompts are templates, not arbitrary strings scattered through code.

Concept:

```text
media-prompt:v1

role
country
city optional
target date/era
currency context
verified visual facts
Quiet Atlas style
aspect ratio
negative constraints
```

Prompt templates are versioned.

Generated asset stores the template version.

---

# 15. Structured prompt inputs

Automatic generation accepts normalized values, not raw user prose.

Allowed inputs:

- ISO country;
- normalized city if editorially supported;
- year/date;
- currency code/era;
- curated historical visual facts;
- role;
- aspect ratio.

Do not concatenate arbitrary URL query text into the prompt.

This reduces:

- prompt injection;
- accidental offensive text;
- unsupported claims.

---

# 16. Fact grounding for generated historical illustration

Before generation, gather only verified context.

Example:

```text
country = Finland
year = 1998
currency = FIM
verified context:
- Finnish markka in use
- winter urban Helsinki visual context only if relevant
- architectural cues supported by curated source
```

Do not ask the model to invent:

- a specific political event;
- a specific shop price;
- a specific banknote design;
- a specific historical street scene

unless those facts are explicitly supplied and suitable.

---

# 17. Generated prompt must avoid causal claims

Image prompt cannot visually imply a specific event caused an exchange-rate movement unless editorial content supports that relationship.

The image-generation layer is presentation, not historical reasoning.

---

# 18. Provider abstraction

AI generation should sit behind an explicit backend adapter.

Concept:

```python
class ImageGenerator(Protocol):
    def generate(
        self,
        request: GeneratedImageRequest,
    ) -> GeneratedImageCandidate:
        ...
```

Potential providers can include:

- OpenAI image generation;
- Stability AI;
- Google Gemini image generation.

The product does not hard-code provider response JSON into MediaAsset.

---

# 19. Do not select provider by hype

Before production generation, benchmark providers against the actual Quiet Atlas prompt set.

Evaluation:

| Criterion | Weight |
|---|---:|
| visual quality/composition | 25 |
| country/context fidelity | 20 |
| style consistency | 15 |
| historical non-hallucination behavior | 10 |
| latency | 10 |
| cost | 8 |
| API/version stability | 5 |
| moderation/operational clarity | 4 |
| output/control features | 3 |

Target test set should include diverse countries/eras, not only Japan/Finland.

---

# 20. Current provider observations

## OpenAI

The official image-generation API supports generated images and moderation controls. OpenAI has documented per-image-equivalent pricing that varies significantly by image quality, so generating on every country/date interaction can become a real variable-cost surface.

Use only behind server-side provider adapter.

## Stability AI

The current Stability Platform exposes text-to-image/image-to-image services with credit-based pricing and multiple quality/speed tiers.

This makes it suitable for benchmarking cost-controlled editorial generation.

## Google

Google's image-generation model lineup has changed quickly in 2026, including deprecations/migrations across Imagen/Gemini image endpoints.

This is a strong reason for keeping provider identity behind our own adapter instead of embedding model names throughout product code.

---

# 21. Provider selection status

**No runtime image-generation provider is enabled in the public portfolio demo.**

Current Gemini image-generation API pricing lists no Free Tier for Gemini 3.1 Flash Image / Flash Lite Image, so runtime image generation would violate the €0 target.

Portfolio strategy:

- factual imagery → Wikimedia/Europeana/other rights-aware sources;
- AI illustrations → created manually/offline during development, reviewed, then stored;
- long tail → Quiet Atlas CSS/SVG fallback.

Google Gemini 3.1 Flash-Lite is selected only for free-tier live **text** explanation.

Image-provider adapters remain future/optional development tooling.

---

# 22. Default generation lifecycle

Recommended P1/P2 flow:

```text
editor/admin requests candidate
        ↓
build structured prompt
        ↓
ImageGenerator adapter
        ↓
provider moderation/generation
        ↓
candidate bytes
        ↓
local validation
        ↓
store unpublished media
        ↓
human review
        ↓
alt/caption/AI label
        ↓
publish
```

User request is never waiting for this process.

---

# 23. Command-line generation

Initial tooling can be a management command.

Example:

```text
python manage.py generate_media_candidate \
  --country FI \
  --year 1998 \
  --role story_cover \
  --dry-run
```

Command can output:

- normalized prompt;
- prompt version;
- provider/model;
- estimated/current provider config;
- generated candidate ID.

Do not auto-publish.

---

# 24. Admin generation

A later Django admin action can:

- create generation request;
- compare candidates;
- reject;
- approve;
- add alt/caption;
- publish.

This has more ROI than a user-facing “AI generate” button during core implementation.

---

# 25. On-demand generation — future only

A future optional user feature could be:

> Generate an artistic illustration for this country and year

This would be explicitly optional.

Flow:

```text
user requests illustration
→ existing cached generated asset?
   ├─ yes → return
   └─ no
      ↓
      enqueue generation
      ↓
      immediate nonblocking UI state
      ↓
      generate/moderate/store
      ↓
      publish/return candidate under policy
```

Core conversion remains complete while generation runs.

---

# 26. On-demand generation changes backend architecture

True runtime on-demand image generation would justify asynchronous job infrastructure because generation is:

- relatively slow;
- externally billable;
- retryable;
- not request-critical;
- potentially moderation-dependent.

This is one of the concrete scenarios that could justify introducing:

- Celery/RQ/Dramatiq;
- broker;
- job state;
- idempotency;
- quotas;
- cancellation.

Do not add that infrastructure until this feature is approved.

---

# 27. On-demand rate/cost protection

If runtime generation ever ships:

- authenticated users only or strict anonymous quota;
- generation key/idempotency;
- per-user/day quota;
- global spend ceiling;
- prompt/date normalization;
- cached result reuse;
- no generation on hover/change events;
- explicit user action.

One click may create one job.

Changing a select field does not.

---

# 28. Generation cache identity

Generated asset identity can include:

```text
prompt_schema_version
provider
model
style_version
country
currency
date/era
role
aspect_ratio
normalized fact-set hash
seed if provider supports deterministic seed
```

Do not cache only by:

```text
country + year
```

because prompt/model/style semantics can change.

---

# 29. Reproducibility

AI generation is not guaranteed deterministic across provider/model updates.

Store:

- provider;
- model;
- generated_at;
- prompt template version;
- final normalized prompt or prompt hash;
- seed if meaningful;
- moderation result/status;
- generation parameters;
- output content hash.

The published output file itself is authoritative for the product.

Do not regenerate silently whenever page loads.

---

# 30. Model upgrades

Changing image model does not force regeneration of all published media.

Existing approved images remain versioned assets.

Generate replacements deliberately.

This avoids visual drift and unexpected cost.

---

# 31. Static vs media storage

Use two distinct Django concepts.

## Static

Files tied to code release:

```text
static/
├── brand/
├── icons/
├── patterns/
└── illustrations/  # only truly release-owned assets
```

Managed by:

- Vite;
- Django staticfiles/collectstatic.

## Media

Content/editorial/generated assets:

```text
MEDIA storage
├── sourced/
├── generated/
└── derivatives/
```

Managed by Django Storage API.

Do not put thousands of country/year content images in Git.

---

# 32. Development media storage

Local development:

- FileSystemStorage / MEDIA_ROOT.

Fixtures may include a tiny legally safe test-media subset.

Do not clone the production media library into every developer checkout.

---

# 33. Production media storage

Use Django's storage abstraction.

Preferred production shape:

```text
Django
  ↓
Django Storage API
  ↓
S3-compatible object storage
  ↓
CDN/custom media domain when justified
```

The architecture remains vendor-neutral.

Possible providers include:

- Amazon S3;
- Cloudflare R2;
- Backblaze B2;
- other S3-compatible storage.

---

# 34. django-storages

If production uses S3-compatible object storage, `django-storages[s3]` is a pragmatic adapter.

Django's STORAGES setting keeps static/media backends separate.

Do not hard-code Amazon-specific SDK calls into media domain code.

---

# 35. Never store image bytes in PostgreSQL

Database stores metadata and storage key.

Object/file storage stores bytes.

Reasons:

- DB backup size;
- serving efficiency;
- CDN compatibility;
- image processing;
- lifecycle management.

---

# 36. MediaAsset domain model

Candidate:

```text
MediaAsset
- id
- kind
- role
- country nullable
- currency nullable
- city nullable
- valid_from nullable
- valid_to nullable
- date_precision
- title
- alt_text
- caption
- storage_file
- width
- height
- aspect_ratio
- focal_x nullable
- focal_y nullable
- content_hash
- source_kind
- source_name
- source_url
- external_id nullable
- creator nullable
- licence_id nullable
- licence_url nullable
- rights_statement nullable
- attribution_text nullable
- generated_by_ai
- ai_label
- generation_provider nullable
- generation_model nullable
- prompt_version nullable
- prompt_hash nullable
- generated_at nullable
- reviewed_at nullable
- published_at nullable
- status
```

Not all fields are required for every media kind.

---

# 37. Media kind

Candidate enum:

- brand_asset;
- contemporary_photo;
- archival_photo;
- artwork;
- heritage_object;
- map;
- generated_illustration;
- decorative_pattern.

Do not encode source and semantic kind into one enum.

Example:

```text
kind = archival_photo
source_kind = wikimedia_commons
```

---

# 38. Media role

Candidate:

- country_hero;
- country_teaser;
- story_cover;
- story_chapter;
- comparison_then;
- comparison_now;
- historical_timeline;
- social_preview;
- decorative_background.

One asset can be approved for more than one role only if layout/cropping supports it.

---

# 39. Temporal precision

Media date metadata needs precision.

Candidate:

```text
exact_day
month
year
decade
range
era
unknown
```

Do not convert “circa 1950s” into 1955.

Presentation derives appropriate human label.

---

# 40. Real-media provenance

For sourced media, preserve:

- canonical source record;
- original institution/creator;
- rights/licence;
- source retrieval date;
- source date/title;
- modification/derivative status.

Attribution should remain possible even if the external page later changes.

---

# 41. Wikimedia Commons strategy

Wikimedia Commons is a strong source for reusable media, but each file's licence conditions still matter.

The integration should retrieve metadata such as file information and licence/creator information where available.

Selected assets should generally be downloaded/mirrored into managed media storage when licence terms permit, rather than relying on hotlink availability.

Attribution remains linked to the original Commons file/source.

---

# 42. Europeana strategy

Europeana is valuable for cultural heritage search and detailed record/rights metadata.

Important distinction:

- Europeana metadata may have broad reuse terms;
- the underlying digital object has its own rights statement.

The media pipeline must evaluate the object's rights statement, not assume all discovered images are public domain.

---

# 43. No blind search-to-production pipeline

Rejected:

```text
user selects 1930
→ search Wikimedia
→ first image result displayed
```

Problems:

- weak relevance;
- ambiguous date;
- rights/attribution;
- unstable ordering;
- unsafe imagery;
- external latency.

Search APIs belong in ingestion/editorial tooling.

---

# 44. Mirroring vs hotlinking

Preferred default for approved reusable media:

```text
source
→ verify licence
→ download approved original/variant
→ store managed copy
→ preserve attribution/source link
```

Reasons:

- performance;
- availability;
- controlled optimization;
- stable dimensions;
- offline mobile caching;
- no hotlink breakage.

Only mirror when licence/terms permit it.

---

# 45. Derivatives

Generate optimized derivatives from an approved source.

Possible widths:

- 480;
- 768;
- 1200;
- 1600 when needed.

Formats:

- AVIF where tool/deployment support is reliable;
- WebP;
- JPEG/PNG fallback where necessary.

Do not force every source into every format if the marginal value is low.

---

# 46. Source original

Keep an approved source/master when legally/operationally useful.

Derivatives should be reproducible.

Do not repeatedly download the upstream original during page requests.

---

# 47. Image processing

Initial processing can use Pillow/libvips-backed tooling depending deployment simplicity.

Tasks:

- validate actual image type;
- dimension limit;
- orientation;
- resize;
- crop;
- encode;
- strip unnecessary metadata;
- content hash.

Avoid a large DAM/image-service dependency before needed.

---

# 48. EXIF/privacy

For sourced/generated editorial assets:

- preserve required provenance in database;
- strip irrelevant EXIF/GPS/private metadata from served derivatives unless editorially needed.

Do not rely on embedded EXIF as the only source attribution.

---

# 49. Focal point

Editorial image can store normalized focal point:

```text
focal_x 0..1
focal_y 0..1
```

Responsive crops use it.

This avoids manually making separate crops for every breakpoint.

---

# 50. Responsive rendering

Web:

- width/height attributes;
- responsive `srcset`;
- `sizes`;
- lazy loading below fold;
- correct fetch priority only for actual important above-fold image.

Mobile:

- appropriate CDN/storage variant;
- local caching where useful;
- never download full archival master for a small card.

---

# 51. Above-fold media rule

The converter remains the hero.

Do not place a heavy country photograph above it merely because images exist.

A country image can appear:

- adjacent to context;
- in story;
- as subtle background with strict contrast;
- below primary result.

Performance and trust outrank visual spectacle.

---

# 52. Image failure behavior

If image request fails:

- layout remains stable;
- alt text is not used as decorative duplicate;
- Quiet Atlas fallback surface appears;
- no conversion/context error state.

Visual enrichment failure is isolated.

---

# 53. Alt-text ownership

Alt text is editorial metadata, not generated blindly at request time.

For factual images:

- describe relevant visible information;
- avoid repeating caption;
- preserve context.

For decorative imagery:

- empty alt / accessibility-hidden.

For AI illustration:

- alt describes visual;
- separate visible label identifies it as AI where required by context.

---

# 54. Captions

Historical/editorial image caption may include:

- what;
- approximate date;
- source/institution;
- AI illustration label where applicable.

Licence/attribution can be exposed in Source details if too verbose for the immediate caption, while still meeting licence requirements.

---

# 55. Generated-image accessibility

Do not put “AI-generated” only in alt text.

If authenticity matters, it is visible to everyone.

Example:

```text
Artistic reconstruction
AI-generated illustration · not an archival photograph
```

---

# 56. Generated-image moderation

Generation provider safety/moderation is one layer.

We also apply product review.

Candidate statuses:

```text
generated
rejected
needs_review
approved
published
retired
```

Do not auto-publish generation response.

---

# 57. Content review

Review checks:

- no invented readable text;
- no fake official seal/banknote detail;
- no offensive stereotype;
- no anachronism obvious enough to mislead;
- no unintended famous-person resemblance;
- no malformed cultural/religious symbol;
- matches Quiet Atlas;
- label requirement correct.

---

# 58. Historical image review

Real historical media review additionally checks:

- date confidence;
- geography;
- relevance to money/story;
- source authenticity;
- licence/rights;
- caption accuracy.

A real old photo can still be wrong for the selected year/country.

---

# 59. Country stereotype policy

Do not represent countries only through clichés.

Avoid automatic prompts like:

- Japan → geisha + cherry blossom;
- Finland → sauna + reindeer;
- France → Eiffel Tower;
- India → Taj Mahal.

Country atmosphere should prioritize:

- money/history context;
- geography/urban cues;
- editorial relevance;
- subtle design abstraction.

---

# 60. Sensitive-history policy

For war, disaster, repression or trauma:

- prefer sourced archival/editorial media;
- AI reconstruction is generally avoided;
- no decorative generative dramatization;
- captions/source context are required.

Historical storytelling should not aestheticize suffering.

---

# 61. People/faces

Prefer archival/source media for real historical people.

Do not generate a likeness of a real historical person and present it as factual imagery.

If illustration is used:

- clearly identify as illustration;
- only when product/editorial value is real.

---

# 62. Currency/banknotes

Banknotes/coins can have copyright, reproduction and anti-counterfeiting considerations.

Use:

- sourced licensed/public-domain media;
- museum/central-bank guidance where applicable;
- stylized abstract currency motifs for generated visuals.

Do not ask an image model to produce a convincing exact banknote and then display it as reference.

---

# 63. Flags

Use trusted static/vector flag assets or a reliable normalized source.

Do not AI-generate flags.

Flags are factual symbols; hallucination is unnecessary risk.

---

# 64. Maps

Use real map data/cartographic assets for geographic meaning.

Do not AI-generate geographic maps where positional accuracy matters.

AI can create abstract map-like background textures only when clearly decorative.

---

# 65. Country visual fallback

Every country should look intentional even with zero media assets.

Fallback stack:

```text
country theme tokens
+ Quiet Atlas texture
+ currency typography
+ subtle geography/coordinate motif if sourced
```

This makes global coverage possible without generating 200+ country photographs.

---

# 66. Historical visual fallback

Every year should look intentional with zero archival media.

Fallback:

```text
archive-blue semantics
+ date typography
+ timeline
+ currency-era labels
+ Quiet Atlas archival pattern
```

Do not add fake paper/yellowed-photo clichés.

---

# 67. Coverage strategy

Do not aim for:

```text
all countries × all years
~~ hundreds of thousands of generated images
```

Instead prioritize:

1. top demo/portfolio countries;
2. historically interesting currency transitions;
3. story pages with high editorial value;
4. popular usage based on real traffic later.

The fallback design covers the long tail.

---

# 68. Suggested initial curated media set

For portfolio launch, a small strong set is enough.

Example candidates:

- Finland / FIM→EUR transition;
- Germany / DEM→EUR;
- Japan / JPY;
- UK / GBP;
- US / USD;
- one Nordic comparison;
- one pre-euro historical story.

Each can have:

- one contemporary real image or abstract visual;
- one archival sourced media item where useful;
- optionally one AI editorial illustration.

Quality beats breadth.

---

# 69. Social preview images

OpenGraph/social images are a good AI/pre-generation use case.

Generate once per featured story/page.

Store/publish as normal media.

Do not call AI when a crawler requests the page.

---

# 70. Build/release-owned generated art

If we generate a small timeless visual such as:

- product cover;
- empty-state art;
- generic Quiet Atlas illustration;

and it changes only with releases, it may live in static.

Country/year/story images remain content media.

---

# 71. Storage lifecycle

Media state lifecycle:

```text
candidate
→ reviewed
→ approved
→ published
→ retired
```

Retired asset:

- removed from future selection;
- may remain stored for attribution/audit until deletion policy allows cleanup.

---

# 72. Orphan cleanup

Do not immediately delete bytes when a DB row changes.

A maintenance command can identify:

- unreferenced derivatives;
- rejected generation candidates older than threshold;
- retired unused assets;
- duplicate content hashes.

Dry run before deletion.

---

# 73. Content hashes

Compute SHA-256 or equivalent content hash for approved bytes.

Use for:

- duplicate detection;
- immutable naming;
- cache-busting;
- integrity checks.

Do not use original filename as identity.

---

# 74. Media URLs

Prefer immutable/versioned URLs.

Example shape:

```text
/media/generated/sha256-prefix/asset.webp
```

Replace an image by publishing a new asset, not mutating bytes behind the same immutable URL.

---

# 75. CDN

CDN is optional initially.

Object storage + CDN becomes useful for:

- global image latency;
- large cultural media;
- mobile delivery;
- cache headers.

Media architecture must not require CDN-specific application code.

---

# 76. Cache headers

Published immutable derivative:

```text
Cache-Control: public, max-age=31536000, immutable
```

only when URL is content/version hashed.

Metadata/page HTML uses normal application cache semantics.

---

# 77. Deletion and CDN

If licence/rights require removing an asset:

- mark unpublished;
- delete/origin block as required;
- purge CDN if present;
- remove from selection;
- preserve non-public audit metadata only where appropriate.

Long immutable cache policy must have a purge path for rights incidents.

---

# 78. Media API contract

Mobile/web presentation can receive normalized media metadata.

Example:

```json
{
  "kind": "archival_photo",
  "url": "...",
  "width": 1200,
  "height": 800,
  "alt": "...",
  "caption": "Helsinki, c. 1970s",
  "provenance": {
    "source": "Wikimedia Commons",
    "source_url": "...",
    "creator": "...",
    "licence": "CC BY-SA 4.0"
  },
  "ai_generated": false
}
```

For AI:

```json
{
  "kind": "generated_illustration",
  "ai_generated": true,
  "authenticity_label": "AI-generated editorial illustration"
}
```

---

# 79. Mobile offline media

Do not cache every historical image automatically.

Cache:

- currently viewed story media;
- explicit saved trip/story where useful;
- bounded recent media.

Metadata/source attribution should remain cached with the image.

If offline image is missing, text/story still works.

---

# 80. No AI provider in mobile/web client

Image generation keys are server-only.

Browser/mobile never call:

- OpenAI;
- Stability;
- Google image-generation endpoint

directly.

Benefits:

- no key leakage;
- centralized quotas;
- consistent prompt policy;
- moderation;
- reusable cache;
- provider portability.

---

# 81. Provider outage

Editorial generation provider outage:

- generation job fails/retries according to command/task policy;
- existing published media remains;
- user conversion unaffected.

This provider is never a readiness dependency.

---

# 82. Cost accounting

If AI generation is enabled, record operational metadata:

- provider;
- model;
- generated count;
- success/failure;
- optional provider cost/usage metadata where available.

Do not put cost logic into MediaAsset domain rules.

A monthly spend ceiling is deployment configuration.

---

# 83. Why runtime generation is expensive at scale

Even low per-image cost compounds quickly if every user interaction generates.

Example shape:

```text
1,000 sessions
× 8 country/year changes
= 8,000 generations
```

At only a few cents each, this is already meaningful recurring spend for a feature that does not improve FX correctness.

Pre-generation turns that into:

```text
one generation
→ many views
```

which has much higher ROI.

---

# 84. Visual consistency advantage of pre-generation

Runtime generation can return a different composition/model behavior after provider upgrades.

Approved stored media gives:

- stable screenshots;
- stable recruiter demo;
- consistent visual art direction;
- repeatable visual regression tests.

This is especially valuable for a portfolio product.

---

# 85. Testing

Test:

- media selection priority;
- temporal filtering;
- real vs generated labeling;
- unpublished assets excluded;
- expired/licence-blocked assets excluded;
- missing media fallback;
- aspect-ratio selection;
- source attribution presence;
- generated media requires AI metadata;
- user request never triggers generation in core flow.

---

# 86. Security testing

Test:

- malicious SVG not blindly served/uploaded;
- fake MIME extension;
- oversized image;
- decompression-bomb protection;
- unsafe source URL scheme;
- provider key never returned;
- generation prompt uses normalized structured values;
- remote image URL is not arbitrary user-controlled SSRF input.

---

# 87. Image upload validation

Editorial upload/import validates:

- actual content type;
- supported raster/vector type;
- dimensions;
- byte size;
- decode success.

SVG requires stricter treatment because it can contain active content.

Preferred:

- repository-owned trusted SVG for static;
- rasterize/sanitize third-party SVG before public media if needed.

---

# 88. Availability behavior

Image availability is never tied to conversion status.

Possible independent media states:

```text
available
loading
unavailable
rights_blocked
fallback
```

These states do not become:

```text
conversion_error
```

---

# 89. Performance budget

Initial media targets:

- zero mandatory photographic bytes before conversion/result interaction;
- no large hero download on first view;
- responsive derivative rather than original;
- explicit dimensions to avoid layout shift;
- lazy load story/context images.

Exact byte budgets are measured during implementation rather than invented in documentation.

---

# 90. Design acceptance rule

A media-rich screen fails design review if:

- the image is more visually dominant than the conversion/result without product reason;
- historical AI looks like an archival fact;
- source/licence is unavailable;
- image causes primary task layout shift;
- contrast depends on the particular image;
- missing image breaks composition;
- country imagery relies on stereotypes.

---

# 91. Recommended final architecture

```text
                           ┌─────────────────────┐
                           │ static brand assets │
                           │ SVG/CSS/Vite        │
                           └──────────┬──────────┘
                                      │
                                      ▼
Browser / Mobile ← Django media metadata/selectors
                         ▲
                         │
                   PostgreSQL
                   MediaAsset
                         │
                  storage key
                         ▼
               managed object storage
                 / CDN optional
                  ▲             ▲
                  │             │
         sourced media      generated media
        Wikimedia/Europeana   AI provider
                  │             │
                  └──── editorial/review ────┘
```

Normal user request reads only published/local media metadata and stored assets.

No generation/search API is in the core request path.

---

# 92. Final policy

For the initial product:

## We WILL

- keep UI/brand assets static;
- use programmatic country/year fallback visuals;
- curate real archival images from rights-aware sources;
- store approved media in managed media storage;
- optionally generate selected Quiet Atlas illustrations ahead of time;
- visibly identify AI reconstruction;
- keep provenance/rights in the database;
- use image-generation adapters only in editorial tooling.

## We WILL NOT

- generate a new image every time country/year changes;
- show AI output as historical evidence;
- call image APIs directly from frontend/mobile;
- hotlink arbitrary search results;
- commit a huge media library into Git;
- make image providers a health/runtime dependency;
- auto-publish generated media.

## Future option

On-demand user-triggered artistic generation can be reconsidered later as an explicit asynchronous feature with quotas, caching and job infrastructure.


# 101. Implemented static social/responsive derivatives

Following real desktop/tablet/mobile browser QA, the project now includes a small release-owned derivative set:

- portrait home hero;
- portrait Then & Now comparison;
- home OpenGraph visual;
- Then & Now OpenGraph visual;
- local-value OpenGraph visual.

These are derived from already approved Quiet Atlas concepts rather than generated for arbitrary user-selected country/year combinations.

They remain under `static/images/quiet-atlas/` because they change with releases, have no content-management lifecycle, and create no runtime image-generation cost.

This does not change the core rule:

> Country/year editorial media remains stored/curated content, not on-demand AI output.


---

# 84. Implemented PR7A managed-media boundary

The roadmap PR7A milestone is now implemented as a dedicated Django app:

\`\`\`text
apps/media/
├── models.py
├── services.py
├── presentation.py
├── validation.py
├── sources/
│   ├── wikimedia.py
│   └── europeana.py
└── management/commands/
    ├── ingest_media_candidates.py
    ├── attach_media_file.py
    └── build_media_derivative.py
\`\`\`

The persisted \`MediaAsset\` owns metadata and storage identity, not binary image bytes. Managed bytes are written through Django's \`default_storage\` / \`FileField\` abstraction. Local development uses \`MEDIA_ROOT\`; a production deployment can replace the configured Django storage backend without changing media-domain code.

## 84.1 Publication lifecycle

The executable lifecycle is:

\`\`\`text
candidate / needs_review
→ explicit approval
→ approved
→ explicit publish
→ published
→ optional retirement
\`\`\`

Rejected unpublished candidates are explicit state as well.

Important enforcement:

- Django admin exposes controlled transition actions rather than editable publication/status fields;
- managed binary fields/status/timestamps are read-only in admin;
- ingestion never auto-publishes;
- responsive derivative creation never auto-publishes;
- approved/published bytes are immutable in place;
- replacement means publishing a new content-hashed asset.

## 84.2 Binary validation and privacy boundary

Managed media currently accepts only decoded single-frame:

- JPEG;
- PNG;
- WebP.

Before storage the pipeline:

1. bounds the input byte size;
2. rejects third-party SVG;
3. decodes/verifies the raster;
4. bounds dimensions and total pixel count;
5. verifies filename extension against decoded format;
6. applies EXIF orientation;
7. re-encodes the raster without original metadata;
8. computes SHA-256 over the sanitized bytes;
9. stores under a content-hash-derived immutable key.

This means untrusted EXIF/GPS/application metadata is not propagated into the served managed asset.

Third-party SVG remains rejected rather than served unsanitized. Release-owned reviewed Quiet Atlas SVG files continue to use Django staticfiles and are a different trust class.

## 84.3 Provenance and publication gates

A sourced asset cannot be published without:

- a managed storage file;
- SHA-256 identity;
- intrinsic dimensions;
- non-decorative alt text;
- explicit editorial review;
- canonical HTTPS source URL;
- source/institution metadata;
- licence or rights statement;
- attribution text.

Historical sourced assets require explicit temporal precision/scope.

AI-generated illustration metadata is supported for pre-generated reviewed assets, but runtime generation is not part of PR7A. A generated asset cannot publish without:

- \`generated_by_ai=true\`;
- generated-illustration kind/source semantics;
- a visible label that explicitly identifies it as AI-generated;
- provider/model;
- prompt version;
- valid SHA-256 prompt hash;
- temporal precision when used in a historical role.

The visible authenticity label is carried through the normalized \`ImageViewModel\` and shared media template; it is not hidden only in alt text.

## 84.4 Selection and request-path isolation

User-facing selection reads only local \`PUBLISHED\` rows.

Selection considers:

- semantic country/currency specificity;
- sourced/AI authenticity class;
- temporal precision for historical requests;
- requested aspect-ratio preference;
- publication recency as a deterministic tie-breaker.

For historical context, temporally relevant sourced media outranks AI illustration. A dated AI illustration may outrank an undated neutral asset rather than allowing a present-day/temporally-unknown image to masquerade as historical evidence.

When no managed asset qualifies, presentation falls back to the existing release-owned Quiet Atlas registry.

The selector performs no:

- Wikimedia request;
- Europeana request;
- AI/image-generation request;
- hot archive search.

## 84.5 Editorial ingestion commands

Metadata candidate discovery is request-independent:

\`\`\`bash
python manage.py ingest_media_candidates \
  --source wikimedia \
  --query "Finland markka 1998" \
  --role historical_timeline \
  --kind archival_photo \
  --country FI
\`\`\`

Europeana candidate search additionally requires the server-side \`EUROPEANA_API_KEY\`.

Candidate ingestion stores normalized review metadata only. A reviewed local raster can then be validated/sanitized and attached:

\`\`\`bash
python manage.py attach_media_file --asset-id 123 --path ./candidate.jpg
\`\`\`

Reviewed managed media can receive an explicitly requested responsive derivative:

\`\`\`bash
python manage.py build_media_derivative --asset-id 123 --width 768
\`\`\`

The derivative is WebP, content-hashed and remains review-gated.

## 84.6 Intentionally deferred

PR7A does not select:

- an S3 vendor/package before a deployment platform exists;
- a runtime ImageGenerator provider;
- automatic external binary mirroring;
- AI generation from country/year selector changes;
- auto-publishing;
- media CDN-specific application code.

Those boundaries remain separate so media trust does not depend on provider novelty or deployment convenience.
