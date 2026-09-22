# Screen-by-Screen Design Blueprints

This document specifies the intended composition and priority of every important product surface.

It is a design blueprint, not a pixel-locked mockup.

---

# 1. Global shell

## Desktop

```text
┌─────────────────────────────────────────────────────────────┐
│ Brand                  Convert  Explore  Saved      Actions │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                       page content                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Data sources · About · Privacy · Accessibility              │
└─────────────────────────────────────────────────────────────┘
```

Header goals:

- compact
- quiet
- no oversized marketing nav
- primary task remains obvious

Brand mark should not consume converter space.

## Mobile

```text
┌──────────────────────┐
│ Brand          menu  │
├──────────────────────┤
│ content              │
│                      │
├──────────────────────┤
│ optional bottom nav  │
└──────────────────────┘
```

Web P0 may avoid bottom navigation if only 2–3 destinations exist.

React Native can adopt native bottom navigation later.

---

# 2. Home / Convert — desktop

This is the signature screen.

Recommended structure:

```text
                 Convert money with context
      Understand the rate, local value and money culture.

┌────────────────────────────────────────────────────────────┐
│ Amount                                                     │
│ [ 100.00                                      ] EUR        │
│                                                            │
│ ┌──────────────────────┐    ⇄    ┌──────────────────────┐ │
│ │ FROM                 │         │ TO                   │ │
│ │ 🇫🇮 Finland          │         │ 🇯🇵 Japan            │ │
│ │ Euro · EUR           │         │ Japanese yen · JPY   │ │
│ └──────────────────────┘         └──────────────────────┘ │
│                                                            │
│ Rate date: Latest available                [ Convert ]      │
└────────────────────────────────────────────────────────────┘

                    100 EUR
                       ≈
                  17,450 JPY

           1 EUR = 174.50 JPY
     Reference rate · Effective 18 Sep 2026
              ECB via Frankfurter

         [ source details ] [ save pair ]

──────────────────────────────────────────────────────────────

What this amount roughly buys

[ Coffee ]       [ Casual meal ]       [ Transit ]

──────────────────────────────────────────────────────────────

Paying in Japan
Cards ...
Cash ...
Tipping ...

──────────────────────────────────────────────────────────────

Explore money & culture →
```

---

# 3. Home hero rule

Avoid a conventional SaaS marketing hero with:

- huge headline
- screenshot mockup
- 2 CTA buttons
- testimonial

The product itself is the hero.

Headline max:

> **Convert money with context.**

Supporting sentence max two lines.

Converter starts within first viewport on normal laptop.

---

# 4. Amount field design

Desktop:

- full-width within converter top area
- label above
- large numeric type
- currency code at trailing edge
- no decorative symbol inside if ambiguous

Candidate height:

- 60–64px desktop
- 56px mobile

Numeric font:

- 24–32px depending container

Error appears directly below.

---

# 5. From/To selector cards

These are interactive fields, not marketing cards.

Default:

- neutral surface
- thin border
- 12–16px radius
- clear label
- selected country/currency

Hover:

- border emphasis
- slight surface shift

Focus:

- explicit ring

Open:

- list/search panel

Do not use huge flag circles.

Suggested flag size:

- 24–32px

Country name visually primary when country context selected.

Currency name/code secondary.

---

# 6. Swap placement

Desktop:

Centered between selectors.

It must not look like a floating decorative icon.

Suggested:

- 44–48px hit target
- icon inside low-emphasis button
- visually aligned to selector centers

On mobile:

- vertical placement between cards
- optional 90° icon orientation
- still labelled accessibly as “Swap source and destination”

---

# 7. Rate-date control

Default state is compact.

```text
Rate date
Latest available ▾
```

Historical mode reveals date.

Do not show a permanent large calendar if most sessions are current conversion.

---

# 8. Convert button

Primary action.

Desktop:

- aligned trailing/right or full-row depending converter width
- 48–52px height

Mobile:

- full-width
- 52–56px height

Content:

> Convert

After successful enhancement, button may remain Convert rather than rename Update unless testing proves clearer.

No gradient required.

---

# 9. Result area

Result does not need a giant boxed card if whitespace can create hierarchy.

Recommended:

- centered or visually bridging From/To
- large amount
- smaller reference-rate line
- provenance directly below

Result typography carries the “premium” feel.

Example:

```text
100 EUR
≈ 17,450 JPY
```

or one line on wide screens.

---

# 10. Provenance design

Directly under result:

```text
Reference rate · Effective 18 Sep 2026
ECB via Frankfurter
```

Secondary control:

> Source details

This opens disclosure/popover/inline details.

Not tooltip-only.

---

# 11. Stale result

Same geometry as normal result.

Add clear status row:

```text
Cached reference rate
Effective 18 Sep 2026 · Last synced 19 Sep, 08:12
```

Use warning/info styling.

Do not replace the entire result with an alert box.

---

# 12. Local-value section

Heading:

> What this amount roughly buys

Subheading only if necessary:

> Tokyo estimates from sourced recent observations.

Desktop:

3 cards in one row.

Tablet:

2 + 1.

Mobile:

stack or horizontal-scroll only if horizontal interaction is clearly discoverable; stacking preferred for accessibility.

Card:

```text
Coffee
¥500–650 typical

≈ 26–34
for your converted amount

Tokyo · May 2026
```

Do not rely on large emoji.

A restrained icon may be used.

---

# 13. Payment-context section

Prefer structured rows to card grid.

```text
Paying in Japan

Cards        Common in urban areas
Cash         Useful for smaller businesses
ATMs         ...
Tipping      ...
```

This makes comparison/scanning faster.

Each row:

- label
- concise statement
- optional details disclosure

No decorative progress bars.

---

# 14. Cultural teaser

One calm editorial block after practical information.

```text
Explore money & culture

Why Japan uses the yen, how money etiquette works,
and the story behind its currency.

[ Explore Japan ]
```

Optional subtle imagery/pattern.

Not a giant image carousel.

---

# 15. Current historical entry

After result:

> See this rate in the past

or via the Rate date control.

Do not place a large historical chart on default first conversion.

Progressive disclosure is intentional.

---

# 16. Historical conversion screen

Same converter shell.

Difference:

```text
Rate date
Historical · 14 Jun 1998

100 FIM ≈ X USD

Historical reference
Requested 14 Jun 1998
Observation used 12 Jun 1998
```

Requested/effective date discrepancy receives clear hierarchy.

Do not hide behind source details.

---

# 17. Historical suggestion

Finland + 1998 + EUR:

Inline suggestion under country/currency field:

```text
Finland used the Finnish markka (FIM) on this date.

[ Use FIM ]   Keep EUR
```

Style:

- informational
- not error
- no red/yellow warning unless actual issue

---

# 18. Then & Now comparison

Desktop:

```text
┌──────────────────────┬──────────────────────┐
│ THEN                 │ LATEST REFERENCE     │
│ 15 Jun 2016          │ 18 Sep 2026          │
│                      │                      │
│ 100 EUR ≈ X USD      │ 100 EUR ≈ Y USD      │
│ 1 EUR = ...          │ 1 EUR = ...          │
└──────────────────────┴──────────────────────┘

The latest reference gives approximately ...
```

Mobile:

stack Then first, Latest second.

Use neutral comparison styling.

No green “winner” box.

---

# 19. Historical chart screen/section

Composition:

```text
EUR → USD

[1Y] [5Y] [10Y] [Custom]

             simple line chart

Selected: 15 Jun 2016 · ...
Latest:   18 Sep 2026 · ...

High ...
Low ...
```

Controls are segmented but not overly pill-heavy.

Below chart:

> View data table

Text summary always present.

---

# 20. Story entry

After a historical result:

```text
The story behind this rate
Finland was still using the markka on this date.

[ Read the story ]
```

Keep teaser factual.

No cliffhanger/clickbait.

---

# 21. Story page

Desktop composition:

```text
┌────────────── readable editorial column ──────────────┐
│ Back to conversion                                    │
│                                                      │
│ 15 June 1998                                         │
│ The story behind this rate                           │
│                                                      │
│ 100 FIM ≈ X USD                                      │
│ [source/effective date]                              │
│                                                      │
│ Currency era                                         │
│ ...                                                  │
│                                                      │
│ Timeline                                             │
│ ...                                                  │
│                                                      │
│ Then & now                                           │
│ ...                                                  │
│                                                      │
│ Historical moment                                    │
│ ...                                                  │
│                                                      │
│ Sources                                              │
└──────────────────────────────────────────────────────┘
```

Optional media can break the column at deliberate chapter boundaries.

---

# 22. Story chapter rhythm

Each chapter:

- eyebrow/category
- heading
- 1–3 short paragraphs
- optional data figure/media
- source affordance

Avoid 8 equal cards.

Story should feel editorial, not dashboard-like.

---

# 23. Currency timeline

Desktop:

horizontal only when labels fit.

Mobile:

vertical.

Selected date is prominent.

Milestones:

- start
- transition
- changeover
- retirement

Use neutral dots/rail.

Do not create a “roller coaster” animation.

---

# 24. Explore country page

Purpose:

- deeper culture
- currency history
- payment context
- current money facts

Possible structure:

```text
Japan
Japanese yen · JPY

short money-oriented intro

Money today
Currency history
Paying locally
Typical prices
Cultural context
Sources
```

This is not a generic travel guide.

Every section relates to money/culture.

---

# 25. Explore index

Simple searchable/browsable country grid/list.

Do not create 200 image-heavy cards.

Preferred:

- search
- recently explored
- region filters only if useful
- compact country rows/cards

---

# 26. Search overlay / picker

Currency-country search is a critical interaction.

Desktop:

- anchored large popover/dialog near trigger
- search field at top
- recent/relevant results
- virtualized only if needed

Mobile:

- full-screen sheet/page is acceptable
- search field remains visible
- cancel/back predictable

Result row:

```text
🇯🇵 Japan
Japanese yen · JPY
```

or:

```text
€ Euro · EUR
Used by multiple countries
```

---

# 27. Search states

## Empty query

Show:

- recent
- common/relevant
- not arbitrary top 20 alphabetical unless useful

## No result

> No matching country or currency.

Secondary:

> Search by country, currency name or code.

## Archived result

Clear tag:

> Historical currency

---

# 28. Saved page

Do not overdesign.

Rows/cards contain:

- pair
- country context
- latest converted example only if meaningful
- quick Convert
- remove

No dashboard charts by default.

---

# 29. Recent conversions

Timeline/list:

```text
Today
100 EUR → 17,450 JPY
Finland → Japan
Reference effective ...

Yesterday
...
```

User can clear history.

Keep bounded.

---

# 30. Account pages

Accounts are utilitarian.

No separate “brand redesign”.

Sign in:

- one-column form
- max 420–480px
- strong labels
- simple errors

After login, return user to prior conversion context.

---

# 31. Mobile home

Target one-hand sequence:

```text
Amount
From
Swap
To
Rate date
Convert

Result

Reference metadata

What this buys

Paying locally

Culture
```

The first result should appear quickly after the action without forcing long scroll.

---

# 32. Mobile sticky action

Do not make Convert permanently sticky unless usability testing shows value.

Sticky controls can obscure focused fields and violate focus visibility.

If used:

- only after form section begins scrolling out
- safe-area-aware
- hides/adjusts with keyboard
- never obscures errors

Default preference:

> non-sticky full-width Convert in flow.

---

# 33. React Native Convert screen

Native design can use platform conventions more strongly than web.

Structure:

- safe-area header
- amount field
- From/To cards
- Swap
- date
- primary button
- result
- expandable context

Use native sheets/search patterns instead of cloning desktop popovers.

---

# 34. Offline mobile state

Result persists.

Top-level compact status:

```text
Offline · cached reference
```

Detailed date under result.

Do not show a huge red offline banner unless an action is blocked.

---

# 35. Desktop empty first-load

Avoid a visually dead blank result space.

Use subtle supporting content:

```text
Understand more than the number.

• reference-rate source
• local value
• payment context
```

This content disappears/reorders after first successful conversion.

Do not show fake sample financial results that can be mistaken for user data.

---

# 36. Error screen hierarchy

Never navigate to a dedicated error page for ordinary conversion failures.

Inline:

```text
Reference rate unavailable

Your amount and selections are still here.
[ Retry ]
```

404/500 pages may use a simple branded shell.

---

# 37. Source details panel

Source transparency is a differentiator.

Contents:

```text
Rate source
Frankfurter v2

Contributing provider(s)
...

Effective date
...

Fetched
...

About reference rates
...
```

Use disclosure/sheet.

No tiny footnote modal.

---

# 38. Privacy/settings surface

Keep compact.

Controls:

- clear local history
- clear saved local pairs
- analytics preference if applicable
- theme if implemented
- language later

No unnecessary account settings dashboard.

---

# 39. Footer

Minimal:

- Data sources
- About
- Privacy
- Accessibility
- GitHub / project link if portfolio deployment

Do not repeat full navigation.

---

# 40. Page transitions

Web:

Prefer no global page-transition effect initially.

HTMX fragment transitions only where they clarify state.

React Native:

native navigation transitions.

Story navigation can use subtle continuity, but content appears promptly.

---

# 41. Screen density rule

On every screen ask:

> If I remove this element, does comprehension or task success get worse?

If not, remove it.

This is the principal defense against portfolio-demo overdesign.


---

# 42. Signature bilateral converter blueprint

The large-screen converter should make the source↔destination relationship visually unmistakable without turning the screen into two separate mini-sites.

Reference composition:

```text
┌─────────────────────────────────────────────────────────────┐
│ Convert money with context                                  │
│                                                             │
│ FROM                                  TO                    │
│ Finland                               Japan                 │
│ EUR                                   JPY                   │
│ subtle source atmosphere              richer destination    │
│                                                             │
│ €100.00              →               ¥17,450               │
│                                                             │
│ Reference rate · effective date · provider/source           │
└─────────────────────────────────────────────────────────────┘
```

Rules:

- one visual shell;
- two explicit contexts;
- one shared result hierarchy;
- no mandatory exact 50/50 split;
- no giant decorative image before the task;
- source/destination visuals remain optional enhancement.

The result should feel like a bridge between the contexts.

---

# 43. Compact Explore blueprint

After a successful result:

```text
What does ¥17,450 mean in Japan?

Everyday value
Payment context
Money & culture
```

These are first-level paths, not necessarily three large cards.

Preferred presentation:

- compact disclosures;
- concise linked rows;
- one small grouped section.

Avoid:

- 8–12 tile dashboards;
- unrelated cultural trivia;
- carousel-first interaction;
- media that pushes practical context down.

---

# 44. Mobile bilateral blueprint

Do not reproduce the desktop layout at narrow width.

Recommended interaction order:

```text
Amount

FROM
Finland · EUR

↓ swap

TO
Japan · JPY

Rate date
Convert

Converted result
Trust metadata
Everyday value
Payment context
Money & culture
```

Destination selection is an input precondition, so the result must not visually appear before the
destination control in the editing flow. The visual transition may be subtle, but source and
destination identity must remain clear.

On compact layouts, avoid repeating the same country and currency wording in both the context heading
and the picker trigger. Keep the country identity in the context heading and let the trigger emphasize
the selectable currency; its accessible name still states the complete current selection.

The mobile page is successful when the user perceives one journey through two contexts without
horizontal scrolling or duplicated controls.
