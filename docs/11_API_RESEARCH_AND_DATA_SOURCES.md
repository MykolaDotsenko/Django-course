# API Research and Data-Source Strategy

This document records the external APIs and data sources evaluated for Cultural Currency Converter.

The goal is not to maximize the number of integrations. The goal is to select the **smallest set of trustworthy, replaceable and economically sensible sources** that support the product's core promises.

Research date: **2026-09-19**.

---

# 1. Decision summary

## Selected / planned

| Data domain | Source | Role | Runtime critical? | Score |
|---|---|---|---:|---:|
| Current + historical FX | Frankfurter v2 | Primary FX provider | Yes | 98/100 |
| Official euro reference verification | ECB Data Portal / SDMX | Verification / future pinned provider adapter | No | 91/100 |
| Country metadata | REST Countries v5 | Import/enrichment only | No | 84/100 |
| Currency/provider metadata | Frankfurter v2 | Currency coverage + archived currencies | Yes for historical discovery | 97/100 |
| Structured cultural facts | Wikidata stable APIs | Editorial ingestion/discovery | No | 91/100 |
| Cultural media | Wikimedia Commons APIs | Optional media metadata/assets | No | 84/100 |
| European cultural heritage | Europeana Search/Record/IIIF | Optional enrichment | No | 88/100 |
| EU inflation / PPP | Eurostat API | Future purchasing-power/statistical layer | No | 96/100 |
| OECD price levels / PPP | OECD SDMX API | Future purchasing-power layer | No | 94/100 |
| Global CPI / PPP | World Bank Indicators API | Future global statistical layer | No | 92/100 |

## Evaluated but not selected as default

| Source | Why not default | Score |
|---|---|---:|
| Numbeo Data API | Excellent price coverage but expensive for a portfolio project and crowdsourced | 72/100 |
| REST Countries Currencies API for FX | Additional key/quota dependency; weaker fit than Frankfurter for provenance/history | 58/100 |
| Wikidata SPARQL Query Service at request time | Powerful but current responsiveness/timeout risk makes it unsuitable for critical runtime paths | 60/100 |
| Generic “travel tips / tipping APIs” | No sufficiently authoritative universal source identified | 40/100 |

The architecture deliberately allows a source to be replaced without changing product/domain semantics.

---

# 2. Data-source philosophy

External data belongs to one of four operational classes.

## Class A — runtime source of truth

Used during a user-facing request when fresh/selected-date data is required.

Current selection:

- Frankfurter v2 for FX.

Requirements:

- strict timeout;
- response validation;
- normalized domain model;
- cache;
- explicit stale/error semantics;
- provenance.

## Class B — scheduled/imported reference data

Fetched occasionally and persisted locally.

Examples:

- country metadata;
- statistical price-level data.

Requirements:

- import command/job;
- source version/fetch timestamp;
- idempotent upsert;
- app keeps working when source is unavailable.

## Class C — editorial enrichment

Used by an admin/import workflow to discover candidate cultural facts/media.

Examples:

- Wikidata;
- Wikimedia Commons;
- Europeana.

Requirements:

- never publish blindly;
- preserve source/licence metadata;
- human/curation step where claims are trust-sensitive.

## Class D — research-only candidate

Evaluated but not shipped until cost/methodology is justified.

Example:

- Numbeo.

---

# 3. FX provider — Frankfurter v2

## Decision

**Selected as primary P0/P1 FX provider.**

Score: **98/100**

## Why it fits

Frankfurter currently documents:

- 98 central banks and official sources;
- 206 tracked currencies/codes;
- 166 active currencies;
- 40 archived currencies;
- coverage reaching back to 1948 for some series;
- current/latest rates;
- exact historical dates;
- time series;
- weekly/monthly grouping;
- provider filtering;
- provider attribution;
- CSV and NDJSON;
- no API key;
- open-source self-hosting.

This is unusually well aligned with the product because we need both:

- ordinary travel conversion;
- serious historical/archived-currency support.

## Important API routes

### Single pair

```text
GET /v2/rate/{base}/{quote}
```

Historical:

```text
GET /v2/rate/{base}/{quote}?date=YYYY-MM-DD
```

### Rate rows

```text
GET /v2/rates
GET /v2/rates?base=EUR&quotes=JPY,USD
GET /v2/rates?date=1998-06-15
GET /v2/rates?from=2016-01-01&to=2026-01-01
GET /v2/rates?group=month
```

### Attribution

```text
GET /v2/rates?expand=providers
```

### Pin provider

```text
GET /v2/rates?providers=ecb
GET /v2/providers/ecb/rates
```

### Currencies

```text
GET /v2/currencies
GET /v2/currencies?scope=all
GET /v2/currency/{code}
```

### Providers

```text
GET /v2/providers
GET /v2/providers/{provider}
```

## No conversion endpoint

Frankfurter intentionally exposes the rate, not a converted amount.

That is desirable.

Our domain performs:

```text
Decimal(amount) × Decimal(rate)
```

with our own:

- validation;
- precision;
- target minor-unit rounding;
- auditability.

The upstream provider never owns our financial arithmetic.

## Rate semantics

Frankfurter returns mid-market/reference-style rates.

Its default v2 feed blends official/institutional providers.

Important documented detail:

- almost all providers are daily;
- HMRC is monthly;
- U.S. Treasury is quarterly;
- non-daily providers do not enter the default blend.

This is why the UI says:

> Reference rate

rather than:

> Real-time trading rate

## Default provider policy

### General travel conversion

Use:

> **Frankfurter blended v2 rate**

Reasons:

- broad coverage;
- central/official inputs;
- outlier-aware blend;
- consistent general-purpose product semantics.

Store/display attribution when available.

### Explicit official-provider mode

The architecture permits a future request to pin a provider.

Examples:

- ECB;
- NBP;
- BBK.

This can support:

- source-specific historical stories;
- compliance-oriented exploration;
- reproducible official-series analysis.

The consumer product does not expose a provider selector in P0.

## Historical policy

For historical conversions:

1. send selected date to provider adapter;
2. normalize actual returned observation date;
3. preserve requested date separately;
4. never invent a missing observation;
5. expose provider/provider set;
6. expose frequency/granularity when relevant.

## Then & now policy

Then & now comparisons must use compatible semantics.

Preferred:

- same Frankfurter blend policy at both dates;

or:

- same pinned provider where available.

If provider composition differs materially, attribution remains visible and the app must not pretend the underlying institutional series is identical.

## Public API operational risk

No published API key is required.

A fixed public request quota was not identified in the official docs reviewed.

That **does not mean unlimited/SLA-backed service**.

Treat the public API as best effort:

- cache aggressively;
- time out;
- no unbounded retries;
- degrade to explicit cached/stale state;
- keep self-host option.

## Self-hosting

Frankfurter is open source and MIT licensed.

Official deployment documentation includes Docker.

Production escape hatch:

```text
public Frankfurter
      ↓
provider adapter contract
      ↓
self-hosted Frankfurter
```

The product does not need to change its domain/API contract.

Some upstream provider connectors require their own optional credentials when self-hosting; these remain infrastructure secrets.

## Failure strategy

Do **not** silently switch to a completely different commercial FX API.

Preferred order:

```text
fresh normalized cache
↓
Frankfurter request
↓
safe same-pair stale cache
↓
explicit unavailable state
```

Production may point the same adapter at a self-hosted Frankfurter deployment.

## Cache strategy

### Latest blended quote

Short-lived cache.

Initial implementation hypothesis:

- cache around provider publication cadence;
- permit longer stale fallback with explicit label.

Do not freeze exact TTL before observing deployment behaviour.

### Historical exact quote

Very long-lived cache.

Historical observations can still be corrected upstream, so cache must be invalidatable/versioned.

### Time series

Cache by:

- base;
- quote;
- range;
- grouping;
- provider policy.

## Security

No public API key.

Still:

- outbound URL is fixed/configured, not user-controlled;
- query values are validated codes/dates;
- strict timeout;
- bounded response size;
- parse schema before use.

---

# 4. Direct ECB Data Portal / SDMX API

## Decision

**Selected as authoritative reference/verification source, not the P0 general runtime provider.**

Score: **91/100**

## Strengths

ECB exposes official statistical data through an SDMX 2.1 REST service.

The EXR dataset provides exchange-rate data and metadata with dimensions such as:

- frequency;
- currency;
- denominator currency;
- exchange-rate type;
- series variation.

It is the direct authoritative source for ECB euro reference rates.

## Why it is not the general primary provider

Compared with Frankfurter:

- naturally euro-centric;
- smaller set of direct reference currencies;
- historical product coverage is narrower for our global/legacy-currency use case;
- SDMX is more verbose/complex for routine pair conversion.

Frankfurter already supports an ECB-pinned provider route.

Therefore adding direct ECB to the P0 request path would duplicate logic without enough user value.

## Planned uses

- contract/reference verification;
- troubleshooting suspicious ECB-sourced results;
- future `EcbFxProvider` adapter if a concrete need appears;
- methodology/source links in provenance UI.

## Failover rule

Direct ECB must not become a silent failover for a Frankfurter blended rate.

That would change rate semantics.

If explicitly used, UI/domain attribution changes accordingly.

---

# 5. Country metadata — REST Countries v5

## Decision

**Selected for import/enrichment only, not as a runtime dependency.**

Score: **84/100**

## Useful fields

Potentially useful normalized inputs include:

- country name;
- official name;
- ISO codes;
- capital;
- currencies;
- languages;
- borders;
- regions;
- flag asset URLs;
- basic geography.

We will import only fields our domain actually owns.

## Current operational model

The current REST Countries documentation states:

- bearer-token authentication;
- Free plan: 1,000 requests/month;
- paid tiers above that;
- throughput ceiling: 20 requests per 10 seconds;
- static fields reviewed against ISO/UN sources weekly;
- selected dynamic fields update more often.

This is different from older versions of REST Countries that many tutorials describe as an unauthenticated free endpoint.

Implementation must follow current v5 documentation.

## Why import-only

Country metadata changes slowly.

Bad design:

```text
every page request
→ REST Countries
→ user waits
```

Good design:

```text
management command / scheduled refresh
→ REST Countries
→ validate
→ normalize
→ PostgreSQL
→ application reads local DB
```

Benefits:

- quota almost irrelevant;
- app survives provider outage;
- predictable latency;
- data review possible.

## Terms/licensing guardrail

REST Countries' current terms allow using API responses in a product but restrict redistribution/resale of the dataset.

Therefore:

- do not commit a full raw API export to the public repository;
- do not mirror/repackage the raw dataset;
- persist only product-required normalized fields;
- retain source metadata;
- review terms again before deployment/import automation.

## Flags

The provider currently exposes a flag CDN without an API key.

We do **not** make flag CDN availability critical to conversion.

Flags remain decorative/supportive.

The UI must still work if a flag image fails.

## What REST Countries does not own for us

Do not use it as authority for:

- historical country-currency transitions;
- historical legal-tender milestones;
- FX rates;
- payment customs;
- story causality.

Those need dedicated/sourced models.

---

# 6. Canonical country/currency identity policy

External APIs are not the canonical identity layer.

Our domain stores stable identifiers:

```text
Country.iso2
Country.iso3
Currency.code
```

External records map into those identifiers.

This prevents provider naming differences from leaking through the codebase.

Examples:

```text
"Türkiye"
"Turkey"

"Czechia"
"Czech Republic"
```

are presentation/source concerns.

The stable code is the join boundary.

---

# 7. Wikidata stable APIs

## Decision

**Selected for editorial discovery/import of structured cultural and currency facts.**

Score: **91/100**

Not selected for critical runtime rendering.

## Why it fits

Wikidata provides:

- global structured entities;
- multilingual labels/descriptions;
- dates;
- relationships;
- external IDs;
- references/qualifiers;
- CC0 structured data.

Stable interfaces include:

- Wikibase Web API;
- Wikibase REST API;
- Special:EntityData / linked-data interface.

## Preferred access pattern

Use targeted entity access.

Example conceptually:

```text
currency QID
country QID
specific event QID
→ fetch structured entity
→ validate selected properties
→ store curated candidate
```

Avoid broad live graph queries in the user-facing request path.

## Why not runtime SPARQL

Wikidata Query Service is extraordinarily useful for research but current 2026 guidance/performance observations show heavy queries can be slow or timeout.

Therefore:

- SPARQL = research/import tooling;
- not = “render user page now” dependency.

## Licensing

Wikidata structured data is CC0.

We should still preserve useful source attribution and references because product trust matters even where attribution is not legally required.

## Trust guardrail

Wikidata is collaborative.

A Wikidata value is not automatically editorially approved.

For important historical claims:

- inspect references;
- prefer primary/authoritative linked sources where possible;
- store `verified_at`;
- human-review before publish.

---

# 8. Wikimedia Commons APIs

## Decision

**Selected as optional global cultural-media source.**

Score: **84/100**

## Role

Potential uses:

- currency-note/coin imagery where rights permit;
- cultural landmarks;
- historical public-domain images;
- country/currency page illustrations.

## Runtime policy

Prefer editorial ingestion/storage of metadata.

Do not execute a broad Commons search every time a user opens a conversion result.

## 2026 API limits

Wikimedia introduced/enforced cross-project API rate limiting in 2026.

Official best practices include:

- meaningful User-Agent with contact information;
- low concurrency;
- respect `Retry-After`;
- back off on 429/503.

Documentation currently recommends keeping concurrency to 3 or fewer for automated clients.

## Licensing

This is the main complexity.

Wikimedia Commons files do **not** all share one simple media licence.

Each file can have its own:

- CC licence;
- public-domain status;
- author;
- attribution requirement;
- share-alike requirement.

Therefore a media record must persist:

```text
source page
author/creator
license identifier
license URL
attribution text
original file URL
retrieved_at
```

Never copy an image URL alone and discard its licence metadata.

---

# 9. Europeana APIs

## Decision

**Optional P1/P2 source for curated European cultural heritage.**

Score: **88/100**

## Strengths

Europeana aggregates cultural heritage from thousands of European institutions.

Relevant APIs:

- Search API;
- Record API;
- IIIF APIs.

Potential product value:

- historical banknote/coin context;
- artworks;
- archive material;
- culturally relevant historical objects;
- richer European currency-transition stories.

## Authentication

Current API access requires an API key.

Europeana distinguishes:

- personal keys for exploration/testing;
- project keys for services/operational use.

The key should stay server-side.

## Operational policy

Because this is enrichment:

- no critical user flow depends on Europeana;
- fetch during editorial/import process;
- persist canonical record URL + rights metadata;
- use IIIF only where rights/record metadata support it.

## Licensing

Rights can vary per cultural object.

Do not treat “Europeana result” as a universal reuse licence.

Store and enforce per-record rights/licence metadata.

---

# 10. “What this buys” — source decision

This is the hardest data domain in the product.

A useful result needs actual item-level prices such as:

- coffee;
- inexpensive meal;
- transit ticket.

No single free authoritative global API was identified that provides high-quality current item prices worldwide with strong provenance and portfolio-friendly licensing.

Therefore P0 strategy is:

> **curated price observations with source/date/location metadata**

not:

> call an unknown global cost-of-living API live.

---

# 11. Numbeo Data API

## Decision

**Evaluated, not selected for default P0/P1.**

Score: **72/100**

## Technical fit

Numbeo is actually a strong feature fit.

Its API currently exposes:

- city current prices;
- country current prices;
- roughly 60 everyday items;
- low/average/high values;
- number of data points/contributors;
- historical city prices;
- historical country prices;
- monthly historical country prices;
- cost-of-living indices.

This could directly power “What this buys”.

## Why not selected

### Cost

Current Basic API:

- USD 260/month;
- max 200,000 queries/month.

That is poor ROI for an open portfolio project.

### Data nature

The data is crowdsourced.

Numbeo itself exposes contributor/data-point counts and notes spam-detection considerations for raw records.

For a trust-oriented product, crowdsourced data must be visibly classified differently from official statistics.

### Licence dependency

Commercial usage requires the relevant paid/API licence.

This creates a deployment/business dependency that is unnecessary at this stage.

## Future option

Keep a conceptual price-provider adapter.

If later:

- product earns revenue;
- a sponsor supplies a licence;
- price coverage becomes strategically important;

then `NumbeoPriceProvider` can be evaluated.

It must still expose:

- city/country scope;
- update month/year;
- data point count;
- low/average/high;
- source class = crowdsourced.

---

# 12. Current local prices — P0 strategy

Use a curated `TypicalPrice` model.

Preferred source hierarchy:

1. official local provider/operator price where category permits;
2. official statistical price/PPP source where methodology matches;
3. reputable commercial/crowdsourced dataset with explicit licence;
4. otherwise no item.

Examples:

### Transit

Prefer official transport operator fare.

### Museum ticket

Prefer official museum/attraction price if we intentionally support that category.

### Coffee / casual meal

Harder to source authoritatively.

Use carefully curated/reviewed estimates only with:

- city;
- range;
- source;
- observed date;
- confidence/source class.

Do not fake global consistency.

---

# 13. Eurostat API

## Decision

**Selected for future EU purchasing-power / inflation analysis.**

Score: **96/100**

## API characteristics

Eurostat provides free programmatic access through REST/statistics and SDMX APIs.

The official documentation states datasets are refreshed when new data/structural changes are available, with regular update windows.

Useful product datasets include:

### HICP

```text
prc_hicp_midx
```

Monthly Harmonised Index of Consumer Prices.

Use case:

- inflation/time purchasing-power research for European countries.

### PPP / price levels

```text
prc_ppp_ind
prc_ppp_ind_1
```

Use case:

- cross-country price-level comparisons;
- analytical categories;
- purchasing-power research.

## Important methodological rule

PPP/price-level indices are not a substitute for CPI time-series inflation.

Eurostat itself warns that price-level indices are for relative cross-country price levels and are not the correct measure of domestic price change through time.

Therefore:

```text
cross-country relative price level
→ PPP / PLI

within-country inflation through time
→ HICP/CPI
```

## Operational model

Not runtime per conversion.

Use scheduled/statistical import:

```text
Eurostat API
→ dataset adapter
→ normalized StatisticalObservation
→ PostgreSQL
→ calculation service
```

Cache/update based on dataset frequency, not web-request traffic.

## Scope

Eurostat is strongest for Europe.

It cannot be the only global statistical source.

---

# 14. OECD SDMX API

## Decision

**Selected future source for OECD/partner-country PPP and price-level data.**

Score: **94/100**

## Characteristics

OECD Data Explorer exposes an SDMX API.

It is:

- free;
- structured;
- official;
- metadata-rich;
- rate-limited/responsible-use oriented.

Useful dataset family:

```text
DSD_PPP@DF_PPP_CPL
```

for PPP detailed results / price-level indices.

The current detailed dataset includes analytical categories aligned with updated COICOP classifications.

## Why useful

Compared with only Eurostat:

- broader OECD-country coverage;
- useful category-level price-level comparisons;
- consistent official statistical methodology.

## Complexity

SDMX datasets are structurally richer than a simple JSON REST endpoint.

Implementation requires:

- dataflow/structure awareness;
- dimension mapping;
- versioned dataset identifiers;
- careful category semantics.

This belongs in a dedicated statistical adapter, not generic “HTTP util” code.

## Runtime policy

Periodic import only.

No page request waits for OECD.

---

# 15. World Bank Indicators API

## Decision

**Selected future global statistical source.**

Score: **92/100**

## Characteristics

World Bank Indicators API v2:

- no API key required;
- nearly 16,000 time-series indicators;
- broad country coverage;
- many series with decades of history.

Relevant indicators include:

### CPI index

```text
FP.CPI.TOTL
```

### Consumer inflation annual %

```text
FP.CPI.TOTL.ZG
```

### PPP conversion factor

```text
PA.NUS.PPP
```

### Price level ratio

```text
PA.NUS.PPPC.RF
```

## Licensing

Many World Bank open datasets are CC BY 4.0, but dataset/indicator metadata can include third-party restrictions.

Therefore the adapter/import process must preserve:

- dataset;
- indicator;
- source attribution;
- licence/terms reference where required.

Do not assume every World Bank-hosted value has identical reuse terms.

## Request limits

The API requires reasonable use.

The World Bank SDMX guidance imposes data-point limits for large calls.

Our use case needs narrow country/indicator/year ranges, so this is not a practical constraint if queries are designed correctly.

## Role

Use as:

- global CPI baseline;
- PPP/price-level fallback/complement;
- research source where Eurostat/OECD do not cover destination.

Not as:

- current coffee/meal price API;
- FX provider.

---

# 16. Statistical-source precedence

For future purchasing-power work, source selection depends on the question.

## EU domestic inflation

Prefer:

1. Eurostat HICP;
2. national statistical office if needed;
3. World Bank CPI for fallback/comparability.

## OECD cross-country price levels

Prefer:

1. Eurostat PPP for EU/participating European countries where appropriate;
2. OECD PPP/PLI;
3. World Bank PPP/price-level indicators for global extension.

## Global domestic inflation

Prefer:

1. World Bank/IMF-derived CPI series;
2. country-specific official source when methodology demands.

No one API is universally “best”.

---

# 17. Payment customs / tipping / card usage

## Decision

**No universal runtime API selected.**

This is intentional.

The risk of a convenient but weakly sourced API is higher than the value it provides.

## Planned source model

Use curated `CulturalProfile` fields backed by source URLs.

Preferred evidence hierarchy:

1. central bank;
2. government travel/consumer authority;
3. official tourism authority;
4. payment network/public institutional guidance;
5. reputable secondary reference only when primary source is unavailable.

Store:

- statement;
- geography scope;
- source;
- verified date;
- confidence/source class.

## Why not scrape travel blogs

Because claims such as:

- “cash is essential”;
- “cards are accepted everywhere”;
- “tip 15%”;

can quickly become wrong and may vary by region/context.

---

# 18. Cultural text and storytelling sources

The story system needs factual building blocks, not scraped prose.

Preferred flow:

```text
Wikidata / official source / Europeana
→ candidate structured fact
→ editorial verification
→ StoryMoment
→ deterministic StoryChapter
```

Do not persist copyrighted article paragraphs as story content.

Store our own concise factual summary plus provenance.

---

# 19. Cultural images

Source priority:

1. public-domain/clearly licensed Wikimedia Commons;
2. Europeana records with suitable rights;
3. own/generated decorative imagery only where it does not misrepresent historical facts.

Every external media asset needs a `MediaAttribution` record or equivalent.

Concept:

```text
MediaAttribution
- source_name
- source_url
- creator
- licence_id
- licence_url
- attribution_text
- retrieved_at
```

---

# 20. API keys and secrets

## Server-side only

Potential secrets:

- REST Countries bearer key;
- Europeana project/personal key;
- optional future commercial-data keys;
- optional self-hosted Frankfurter upstream-provider credentials.

Never:

- commit;
- expose in HTML;
- expose in React Native bundle;
- put secret query keys into shareable URLs.

## No-key APIs

Still route server-side where:

- normalization;
- caching;
- source policy;
- observability

are business logic.

Mobile should call our Django API, not third-party FX/statistical APIs directly.

---

# 21. Request-path matrix

| Source | Browser direct? | Django runtime? | Scheduled/import? |
|---|---:|---:|---:|
| Frankfurter | No | Yes | Optional warm/preload |
| ECB | No | Usually no | Verification/import |
| REST Countries | No | No | Yes |
| Wikidata | No | No | Yes |
| Wikimedia Commons | No | No | Yes |
| Europeana | No | No | Yes |
| Eurostat | No | No | Yes |
| OECD | No | No | Yes |
| World Bank | No | No | Yes |
| Numbeo | No | Not selected | Not selected |

This keeps the user-facing request path small and predictable.

---

# 22. Refresh policy

Initial policy:

| Data | Refresh model |
|---|---|
| Latest FX | provider cadence + short cache |
| Historical FX | long-lived cache, refreshable |
| Frankfurter currency/provider catalog | daily/weekly refresh |
| Country metadata | weekly/manual import |
| Cultural facts | editorial review / verification schedule |
| Wikimedia/Europeana media metadata | import-time + licence recheck when needed |
| HICP/CPI | monthly/after official release |
| PPP/PLI | annual/release-driven |
| TypicalPrice | source-specific freshness policy |
| Payment customs | manual review cadence |

Do not poll annual statistical datasets every hour.

---

# 23. External dependency resilience

A request-path dependency must have a graceful degradation story.

## Frankfurter down

- use safe same-pair cached quote;
- mark cached/stale;
- retry option;
- otherwise explicit unavailable.

## REST Countries down

No user impact because local DB is already populated.

## Wikidata/Commons/Europeana down

No user impact because published content is local/curated.

## Statistical APIs down

No user impact because last imported official observations remain available with observation/retrieval metadata.

This is the preferred architecture.

---

# 24. Provider-change policy

Never swap data providers merely because another endpoint responded.

Provider switching is a product/data decision.

If an adapter changes:

- source classification may change;
- methodology may change;
- coverage may change;
- attribution changes;
- test fixtures must change;
- historical comparison semantics may change.

A provider change requires:

- ADR update;
- contract tests;
- provenance review;
- migration/compatibility plan when persisted data is affected.

---

# 25. Data quality classes

Normalize source trust into explicit classes.

Possible enum:

```text
official
institutional_aggregate
open_structured
curated_editorial
commercial_crowdsourced
unknown
```

Examples:

- ECB = official;
- Frankfurter blend = institutional_aggregate;
- Wikidata = open_structured;
- manually verified payment statement = curated_editorial;
- Numbeo = commercial_crowdsourced.

UI does not necessarily expose enum names, but domain policy can use them.

---

# 26. API evaluation rubric

Each source is assessed against:

- authority/provenance — 20;
- coverage — 15;
- historical depth — 10;
- data model fit — 10;
- licence/reuse clarity — 10;
- cost/ROI — 10;
- operational reliability — 10;
- integration complexity — 5;
- replaceability — 5;
- portfolio/engineering value — 5.

Total: 100.

## Scores

### Frankfurter v2 — 98/100

Exceptional fit for current + historical + archived currencies with inspectable institutional provenance and self-host escape hatch.

### Eurostat — 96/100

Best fit for EU HICP/PPP methodology; not global.

### OECD SDMX — 94/100

Strong official price-level/PPP data, somewhat more complex integration.

### World Bank Indicators — 92/100

Excellent global statistical coverage and no auth; indicator methodology/licensing still must be checked.

### ECB direct — 91/100

Maximum authority for ECB series, narrower/general-purpose fit than Frankfurter.

### Wikidata stable APIs — 91/100

Excellent open structured discovery/ingestion; requires editorial verification.

### Europeana — 88/100

High-quality heritage source, mainly European and key/rights workflow adds complexity.

### Wikimedia Commons — 84/100

Huge global media collection; per-file licence handling is mandatory.

### REST Countries v5 — 84/100

Convenient country metadata, but current key/quota/terms mean it should not be a runtime dependency.

### Numbeo — 72/100

Excellent feature coverage; price and crowdsourced trust model are poor P0 ROI.

---

# 27. Final selected stack

## P0/P1 runtime

```text
Frankfurter v2
        ↓
Django FX adapter
        ↓
normalized RateQuote
        ↓
cache
        ↓
web + mobile API
```

## Reference/import

```text
REST Countries
Wikidata
Wikimedia Commons
Europeana (optional)
        ↓
management/editorial ingestion
        ↓
validated local models
```

## Statistical future layer

```text
Eurostat
OECD SDMX
World Bank Indicators
        ↓
statistical adapters
        ↓
normalized observations
        ↓
purchasing-power methodology
```

## Explicitly not selected

```text
random free FX APIs
runtime SPARQL
scraped travel blogs
unsourced cost-of-living endpoints
Numbeo as mandatory dependency
```

---

# 28. Implementation rule

Before implementing any external source:

1. re-check current official documentation;
2. re-check current authentication/pricing/licence;
3. capture representative fixtures;
4. define normalized output contract;
5. define timeout/retry/cache behaviour;
6. define source/provenance fields;
7. write contract tests;
8. define outage behaviour;
9. ensure raw provider schema does not leak into templates/API clients.

External APIs are infrastructure.

The product domain must remain understandable without knowing their JSON shape.
