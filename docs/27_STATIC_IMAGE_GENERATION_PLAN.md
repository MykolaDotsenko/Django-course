# Static Image Generation Plan

Status: **P0 image pack generated and committed**

Research/design baseline: **Quiet Atlas**

The portfolio demo does not require runtime image generation. Release-owned visuals are stored as static SVG assets and can later be supplemented by reviewed sourced/AI media through the MediaAsset pipeline.

---

# 1. Goals

The first image pack must:

- make the demo visually intentional before any media API exists;
- cost €0 at runtime;
- load fast;
- scale sharply on retina/mobile displays;
- avoid licensing ambiguity;
- avoid fake historical evidence;
- preserve a consistent Quiet Atlas art direction;
- remain useful if every AI provider is disabled.

---

# 2. Current implementation

The current pack contains **19 static SVG illustrations** under:

- 14 P0 assets;
- 5 focused P1 expansion assets.

All are stored under:

```text
static/images/quiet-atlas/
```

These SVGs are release-owned design assets rather than factual archive media.

They contain:

- no external image URLs;
- no generated readable text;
- no brand logos;
- no runtime network dependencies;
- no historical claims embedded in pixels.

Historical illustrations use abstract currency forms rather than fake exact banknote reproductions.

---

# 3. Visual language

All assets follow the same visual system:

- Quiet Atlas calm editorial style;
- restrained Nordic palette;
- soft gradients;
- shallow atmospheric depth;
- rounded practical objects;
- subtle paper/grain texture;
- no glossy crypto-fintech aesthetic;
- no national flags as the primary visual cue;
- no text baked into images;
- no decorative complexity that competes with conversion data.

Core colors:

```text
canvas   #F6F7F3
ink      #14211D
brand    #0B6B61
history  #345E7D
sage     #8FA99A
sand     #DCCCAD
paper    #ECE4D3
rust     #A5664E
gold     #C29B61
```

---

# 4. Asset inventory

| ID | Asset | Role | Format | Status |
|---|---|---|---|---|
| IMG-01 | hero-home-global-value-v1.svg | home hero | 16:9 SVG | generated |
| IMG-02 | fallback-local-value-generic-v1.svg | local-value fallback | 4:3 SVG | generated |
| IMG-03 | fallback-history-generic-v1.svg | history fallback | 4:3 SVG | generated |
| IMG-04 | countries-finland-local-value-v1.svg | Finland context | 4:3 SVG | generated |
| IMG-05 | countries-japan-local-value-v1.svg | Japan context | 4:3 SVG | generated |
| IMG-06 | countries-usa-local-value-v1.svg | USA context | 4:3 SVG | generated |
| IMG-07 | countries-uk-local-value-v1.svg | UK context | 4:3 SVG | generated |
| IMG-08 | countries-france-local-value-v1.svg | France context | 4:3 SVG | generated |
| IMG-09 | countries-italy-local-value-v1.svg | Italy context | 4:3 SVG | generated |
| IMG-10 | countries-thailand-local-value-v1.svg | Thailand context | 4:3 SVG | generated |
| IMG-11 | countries-turkey-local-value-v1.svg | Turkey context | 4:3 SVG | generated |
| IMG-12 | history-euro-transition-2002-v1.svg | euro transition story | 4:3 SVG | generated |
| IMG-13 | history-finland-markka-1998-v1.svg | Finland markka story | 4:3 SVG | generated |
| IMG-14 | fallback-payment-culture-v1.svg | payment guidance fallback | 4:3 SVG | generated |
| IMG-15 | countries-germany-local-value-v1.svg | Germany context | 4:3 SVG | generated |
| IMG-16 | countries-spain-local-value-v1.svg | Spain context | 4:3 SVG | generated |
| IMG-17 | story-market-basket-value-v1.svg | purchasing-power story | 4:3 SVG | generated |
| IMG-18 | story-cafe-affordability-v1.svg | café affordability story | 4:3 SVG | generated |
| IMG-19 | story-street-food-affordability-v1.svg | street-food affordability story | 4:3 SVG | generated |

---

# 5. Shared AI art-direction prompt

If we later create raster/AI alternatives, every prompt starts from this style contract:

```text
Create a calm premium editorial illustration for a modern currency and
cost-of-living app. Quiet Atlas style. Realistic but gently stylized,
soft natural lighting, subtle texture, elegant composition, restrained
premium color palette, visually trustworthy, clean frame and generous
negative space. No text, no typography, no labels, no watermark, no
visible brand logos, no glossy fintech aesthetic, no fantasy, no
collage layout, no stereotypical tourism poster.
```

AI output is always a candidate, not an automatically published asset.

---

# 6. Per-asset prompts

## IMG-01 — Home hero

File:

```text
static/images/quiet-atlas/hero-home-global-value-v1.svg
```

Prompt:

```text
Create one coherent premium travel-finance scene showing the idea that
the same amount of money has different local meaning around the world.
A thoughtful traveler sits at a refined table with a folded map, subtle
generic coins, coffee and simple food. Beyond the table, blend understated
Northern European and East Asian urban cues around a calm waterfront.
Keep the traveler and city atmosphere to the right/middle and leave
useful quiet space for interface copy. No national flags or text.
```

UI use:

- home hero;
- portfolio/social fallback;
- empty marketing state.

---

## IMG-02 — Generic local value

File:

```text
fallback-local-value-generic-v1.svg
```

Prompt:

```text
Show a calm international everyday-spending scene: coffee, a simple
meal, public-transport payment context, a small grocery bag and a few
generic coins. It should communicate “what your money buys locally”
without depending on one country. Practical, trustworthy and compact
enough for a context card.
```

---

## IMG-03 — Generic historical converter

File:

```text
fallback-history-generic-v1.svg
```

Prompt:

```text
Show an elegant archival research table with abstract historical money
forms, a ledger, timeline cues and a magnifier in a quiet museum/archive
atmosphere. Use archive-blue and warm paper colors. Do not reproduce a
real banknote or pretend this is a documentary photograph.
```

---

## IMG-04 — Finland local value

File:

```text
countries-finland-local-value-v1.svg
```

Prompt:

```text
Show practical everyday Finland through restrained Nordic city design:
clean urban architecture, subtle tram cues, coffee, a cinnamon-bun-like
pastry, a generic contactless payment card and coins. Cool natural
daylight. Distinctly Finnish without relying on snow, sauna, reindeer,
flags or postcard tourism.
```

---

## IMG-05 — Japan local value

File:

```text
countries-japan-local-value-v1.svg
```

Prompt:

```text
Show everyday Japanese urban spending: a simple ramen or teishoku-style
meal, calm modern street/building forms, a generic transit/payment card
and small everyday goods. Refined and practical rather than touristy.
Avoid geisha, anime styling, excessive neon, flags or exaggerated
cherry-blossom imagery.
```

---

## IMG-06 — USA local value

File:

```text
countries-usa-local-value-v1.svg
```

Prompt:

```text
Show everyday urban spending in the United States: a neighborhood café
or diner table with coffee and a simple meal, generic contactless
payment context and a restrained city skyline. Focus on normal daily
expenses rather than luxury, road-trip or landmark tourism.
```

---

## IMG-07 — UK local value

File:

```text
countries-uk-local-value-v1.svg
```

Prompt:

```text
Show everyday UK spending through a calm commuter/café context with
coffee, bakery food, a generic contactless payment card and understated
urban architecture. A restrained clock-tower silhouette may establish
place, but the composition should remain practical rather than royal or
tourist themed.
```

---

## IMG-08 — France local value

File:

```text
countries-france-local-value-v1.svg
```

Prompt:

```text
Show normal French daily spending: a quiet café/bakery setting with
coffee and pastry, restrained urban façades and practical market
context. Keep it elegant but ordinary, not luxury fashion or tourism.
Any Paris cue should remain secondary to the everyday-value story.
```

---

## IMG-09 — Italy local value

File:

```text
countries-italy-local-value-v1.svg
```

Prompt:

```text
Show everyday Italian spending with an espresso/casual meal context,
warm compact urban architecture and a generic payment card. Focus on
daily local life rather than a theatrical vacation postcard.
```

---

## IMG-10 — Thailand local value

File:

```text
countries-thailand-local-value-v1.svg
```

Prompt:

```text
Show an everyday Thai market or street-food spending context with a
simple local meal, small market bag, warm natural light and restrained
urban forms. Communicate affordability and daily life without party
tourism or exoticized imagery.
```

---

## IMG-11 — Turkey local value

File:

```text
countries-turkey-local-value-v1.svg
```

Prompt:

```text
Show everyday Turkish spending through tea/coffee, bakery or market
context with a calm waterfront/urban silhouette and generic payment
objects. The scene should feel welcoming and practical without
orientalist decoration or excessive landmark emphasis.
```

---

## IMG-12 — Euro transition

File:

```text
history-euro-transition-2002-v1.svg
```

Prompt:

```text
Create an editorial historical illustration about a currency transition
around the introduction of euro cash: two abstract eras of paper money
and coins connected by a clear visual transition/timeline. Do not
reproduce exact historical banknotes, printed denominations or official
security designs. Educational and calm, not documentary evidence.
```

---

## IMG-13 — Finland markka era

File:

```text
history-finland-markka-1998-v1.svg
```

Prompt:

```text
Create a late-1990s Finnish everyday-money editorial scene with Nordic
urban architecture, a tram-like transport cue, generic pre-euro paper
money, coins, a period-inspired calculator/mobile-device shape and
coffee. Do not reproduce an exact Finnish markka banknote. Make the
historical era legible without pretending to be an archival photograph.
```

---

## IMG-14 — Payment culture

File:

```text
fallback-payment-culture-v1.svg
```

Prompt:

```text
Show a modern everyday payment scene using a generic contactless card,
phone, a few coins, coffee and a simple café context. No bank/payment
brand marks. The illustration must work internationally as a fallback
for cash/card/mobile-payment guidance.
```

---

## IMG-15 — Germany local value

File:

```text
countries-germany-local-value-v1.svg
```

Prompt:

```text
Show everyday German spending through a calm bakery/café and public-
transport context: coffee, bakery food, a generic contactless payment
card and understated Central European urban architecture. Focus on
practical local life and affordability, not festival or landmark
tourism.
```

---

## IMG-16 — Spain local value

File:

```text
countries-spain-local-value-v1.svg
```

Prompt:

```text
Show normal Spanish everyday spending in a warm but restrained café/
market setting: coffee, a simple casual meal, generic payment context
and compact Mediterranean urban architecture. Emphasize ordinary local
value, not resort or holiday imagery.
```

---

## IMG-17 — Market basket value

File:

```text
story-market-basket-value-v1.svg
```

Prompt:

```text
Create a premium editorial purchasing-power illustration centered on
one everyday grocery basket with produce, pantry staples, a generic
payment card and a few coins. The image should visually support the
question “what can this amount buy here?” without showing prices,
currency symbols or text.
```

---

## IMG-18 — Café affordability

File:

```text
story-cafe-affordability-v1.svg
```

Prompt:

```text
Show a calm café affordability story using coffee, pastry, generic
coins/payment context and understated urban surroundings. Make the
composition useful for explaining equivalent everyday purchases rather
than depicting a luxury café or lifestyle advertisement.
```

---

## IMG-19 — Street-food affordability

File:

```text
story-street-food-affordability-v1.svg
```

Prompt:

```text
Show a culturally neutral, respectful everyday street-food market scene
with two simple meal options, a generic payment card, market bag and
warm practical atmosphere. The image should communicate affordable
daily food choices without exoticizing a specific culture.
```

---

# 7. Accessibility contract

The SVG files are decorative presentation assets by default and therefore contain no embedded text.

When used as decorative background/card atmosphere:

```html
<img src="..." alt="">
```

When an image becomes meaningful editorial content, the surrounding application owns a contextual alt description rather than baking language into the asset.

Do not infer historical facts from the illustration itself.

---

# 8. Rendering rules

Web implementation should:

- provide explicit width/height or aspect ratio;
- preserve the SVG viewBox;
- avoid layout shift;
- lazy-load below-fold cards;
- not put the hero image ahead of critical conversion HTML;
- allow CSS background fallback if SVG fails.

The assets are suitable for direct SVG serving. Raster derivatives should only be created if deployment/social platforms require them.

---

# 9. Historical authenticity

The two historical assets are **editorial illustrations**.

They deliberately use abstract money forms and should never be captioned as:

> photograph of the actual currency in 1998

or equivalent.

If real historical evidence is needed, use sourced media through the MediaAsset pipeline documented in `23_MEDIA_AND_GENERATIVE_IMAGE_STRATEGY.md`.

---

# 10. Next image batch

The focused P1 expansion is now complete.

Do **not** add more decorative static country cards until the 19 current assets
are wired into real layouts and inspected in desktop/mobile screenshots.

The next media work should be higher-value and evidence-based:

- one rights-cleared real historical image/object for the Finland markka story;
- one rights-cleared real historical image/object for the euro transition story;
- raster social/OG derivative only if the deployment surface requires it;
- replace any static illustration that proves visually redundant in real UI.

The goal is not a large gallery. The goal is maximum explanatory value per asset.

---

# 11. Definition of done

The static P0 + focused P1 pack is done when:

- all 19 assets exist in the repository;
- each maps to a concrete component/screen;
- no asset contains baked text;
- no asset makes unsupported historical claims;
- the hero works at desktop/mobile crops;
- country cards remain visually coherent as a set;
- missing-media fallback still works;
- accessibility behavior is documented;
- screenshots confirm the visuals improve the product rather than merely decorate it.
