# UX Research and User Experience Blueprint

This document defines the intended end-to-end experience of Cultural Currency Converter before visual implementation begins.

The goal is not to produce a feature inventory. It is to define **what the user is trying to accomplish, what they need to understand at each moment, what the system should do automatically, and where the product must deliberately stay out of the way**.

Companion specifications:

- [User Case Catalog](02A_USER_CASE_CATALOG.md)
- [Interaction and State Specification](02B_INTERACTION_AND_STATE_SPEC.md)
- [Storytelling and Historical Converter](02C_STORYTELLING_AND_HISTORICAL_CONVERTER.md)
- [UI Design System](03_UI_DESIGN_SYSTEM.md)

---

## 1. Experience north star

> **In a few seconds, a person should understand what an amount of money becomes, how trustworthy that number is, and what it roughly means at the destination.**

The experience hierarchy is:

```text
1. Convert
2. Trust
3. Understand local value
4. Prepare to pay
5. Explore cultural context
6. Save useful context
```

The product fails if culture, animations, account prompts, charts or monetization make step 1 slower or less obvious.

---

## 2. Core UX principles

### 2.1 Utility first, context second, culture third

The converter is the product's front door.

Cultural content is differentiation, not a tax on conversion.

### 2.2 Trust must be visible

A financial-looking number without provenance is not enough.

Every conversion result must make it easy to answer:

- Which currencies are being compared?
- What rate was used?
- When is that rate effective?
- Which provider/source supplied it?
- Is it current reference data or cached/stale data?
- Is this a market/reference rate rather than a guaranteed transaction rate?

### 2.3 Never imply real-time data when the provider is not real-time

The initial Frankfurter provider aggregates mostly daily official/reference rates.

Therefore the product uses language such as:

- **Reference rate**
- **Effective 18 Sep 2026**
- **Source: ECB / contributing providers**
- **Last fetched ...**

Avoid:

- Live rate
- Real-time rate
- Rate right now

unless a future provider contract genuinely supports that claim.

### 2.4 Progressive enhancement, not progressive obstruction

The base HTML form must work.

HTMX improves:

- speed;
- partial updates;
- validation feedback;
- saved state;
- contextual enrichment.

It must not create a second, incompatible interaction model.

### 2.5 Preserve user work

On validation errors, provider errors or enrichment failures:

- keep entered amount;
- keep selected pair;
- keep same-pair last successful result when safe;
- do not reset the page;
- do not move focus unexpectedly.

### 2.6 Explicit uncertainty beats fake precision

Typical prices, card acceptance and cultural practices vary.

Use:

- ranges;
- scope labels;
- observation dates;
- source labels;
- confidence where useful.

Never present a city observation as a universal country fact.

### 2.7 One clear primary action per moment

The user should never have to choose between:

- Convert;
- Explore culture;
- Create account;
- Track rate;
- Start trip;

before seeing a basic result.

### 2.8 Familiar controls before clever controls

Native or well-understood form behaviour is preferred.

A custom control is justified only when it materially improves a long-list task and can match keyboard, screen-reader and touch expectations.

---

## 3. User priority model

Not all personas receive equal product weight.

### Tier 1 — Traveller in the moment

Context:

- in a shop;
- airport;
- station;
- restaurant;
- hotel;
- walking;
- weak network;
- one-handed mobile use.

Primary need:

> “What is this amount in my money, and is it expensive?”

Design consequence:

- conversion result must be immediate;
- minimal typing;
- large touch targets;
- easy swap;
- cached mobile state later;
- cultural exploration stays below the fold.

### Tier 1 — Traveller planning a trip

Context:

- desktop or tablet;
- comparing destinations;
- planning budget;
- researching payment norms.

Primary need:

> “What will my budget feel like there?”

Design consequence:

- local purchasing context;
- payment customs;
- historical context;
- later trip budget.

### Tier 2 — Expat / international student

Primary need:

> “I keep comparing these same currencies and countries.”

Design consequence:

- remembered pairs;
- favourites;
- recent history;
- optional account sync.

### Tier 2 — Digital nomad

Primary need:

> “How does ordinary spending compare between places?”

Design consequence:

- fast destination switching;
- transparent city scope;
- later cross-destination context.

### Tier 2 — Cross-border shopper

Primary need:

> “What does this foreign price roughly mean in my home currency?”

Design consequence:

- fast currency-only conversion;
- shareable URLs;
- later fee assumptions.

### Tier 3 — Currency/culture explorer

Primary need:

> “Teach me about money and culture.”

Design consequence:

- currency history;
- cultural cards;
- historical rates;
- discovery pathways.

This user must not dominate the converter UX.

---

## 4. Contexts of use

UX decisions must be tested against these contexts.

### C1 — Desktop planning

- large viewport;
- good connection;
- longer attention;
- comparison and exploration.

### C2 — Mobile in transit

- one hand;
- glare;
- distraction;
- unstable connection;
- short session;
- touch imprecision.

### C3 — At point of purchase

- user already knows the foreign price;
- wants home-currency interpretation immediately;
- cultural content is secondary.

### C4 — Low connectivity / offline mobile

- no assumption of fresh network data;
- cached result may still have value;
- timestamp and stale status become primary trust UI.

### C5 — Assistive technology

- keyboard;
- screen reader;
- zoom;
- voice input;
- switch/alternative pointer.

### C6 — Locale mismatch

The device locale may not match:

- nationality;
- current location;
- home currency;
- destination;
- preferred number format.

Do not infer too much from locale.

---

## 5. Information architecture

### Web P0

Primary navigation should remain minimal:

```text
Convert
Explore
Saved   [only when feature exists]
About / Sources
```

Do not create navigation entries for features that are not shipped.

### Mobile long-term

```text
Convert
Explore
Trips
Saved
```

P0 mobile may intentionally contain fewer tabs.

### Converter page information order

```text
1. Conversion form
2. Converted amount
3. Rate + effective date + source
4. Local purchasing context
5. Payment guidance
6. Cultural context
7. Historical rate context
8. Save/share actions
```

The order is based on decision value, not on content richness.

---

## 6. First-run experience

### 6.1 No forced onboarding

Do not show:

- welcome carousel;
- tutorial modal;
- sign-up wall;
- location permission request.

The interface should teach itself through clear labels.

### 6.2 Defaults

Priority:

1. use the user's last explicit pair if available locally;
2. otherwise offer a conservative source-currency suggestion from locale;
3. leave destination unselected unless a reliable explicit previous choice exists.

Do not use precise geolocation merely to choose a currency.

A person travelling in Japan may still want EUR as their source.

### 6.3 First screen

The user should immediately see:

- amount;
- From;
- To;
- primary Convert button;
- one sentence explaining the differentiator.

Suggested supporting line:

> Convert a currency, then see what the amount roughly means at your destination.

---

## 7. Conversion interaction model

### 7.1 First conversion is explicit

The first conversion uses an explicit **Convert** action.

Benefits:

- works without JavaScript;
- reduces network calls while the form is incomplete;
- gives a predictable accessibility model;
- prevents surprising updates while the user is selecting countries.

### 7.2 After a successful first conversion

HTMX may progressively enhance subsequent edits.

Recommended behaviour:

- amount changes: debounce approximately 400–500 ms after a valid value;
- currency/country selection changes: update after committed selection;
- Swap: immediate;
- invalid edits: do not fire provider requests.

The exact debounce value should be usability-tested rather than treated as architecture.

### 7.3 Submit button remains available

Even with live enhancement, keep a visible Convert/Update action.

It provides:

- clear user control;
- keyboard predictability;
- no-JS fallback;
- recovery if an automatic update was interrupted.

---

## 8. Amount-entry UX

### 8.1 Visible label

Use a persistent label such as:

> Amount

Do not use placeholder text as the only label.

### 8.2 Mobile keyboard

Use an input mode that encourages decimal numeric entry without assuming a locale-specific keyboard implementation.

### 8.3 Parsing philosophy

Do not silently reinterpret ambiguous amounts.

P0 should:

- accept plain integers;
- accept a single decimal point or comma when unambiguous;
- allow leading/trailing whitespace;
- reject letters and currency symbols in the amount field;
- reject negative values;
- set a documented upper bound;
- preserve the user's input on error.

Avoid supporting arbitrary thousands separators until locale-aware parsing is explicitly designed.

Example guidance on ambiguous input:

> Enter the amount without thousands separators, for example 1234.56 or 1234,56.

### 8.4 Zero

Decision:

- zero is valid arithmetic but has little product value;
- accept it only if doing so simplifies predictable input behaviour;
- contextual equivalents should return zero rather than errors.

This can be revisited after testing.

### 8.5 Precision

Users may enter more decimals than a currency displays.

Do not mutate the input unexpectedly while typing.

Normalize only after successful conversion/display.

---

## 9. Country and currency selection

This is the most distinctive interaction problem in the product.

### 9.1 Currency is required for conversion; country is contextual

A conversion mathematically requires:

- base currency;
- quote currency.

A cultural interpretation additionally benefits from:

- source country, optional;
- destination country, strongly preferred.

The domain and UI must not pretend these are the same thing.

### 9.2 Search by what users know

The selection experience should support queries such as:

- Japan
- JPY
- yen
- Euro
- EUR
- Finland

### 9.3 Proposed selection model

A search result can represent either:

```text
Japan
Japanese yen · JPY
```

or a currency-only choice:

```text
Euro · EUR
Used by multiple countries
```

If a shared currency is chosen and cultural context is requested, prompt for a country without blocking the conversion.

### 9.4 Shared-currency example

User selects:

```text
EUR → EUR
Finland → Italy
```

The monetary conversion is 1:1.

The product still has value because:

- purchasing context changes;
- payment/tipping conventions may change;
- cultural context changes.

The UI should say:

> Same currency — compare local value and money customs.

Do not show a confusing “conversion error”.

### 9.5 Search-result content

Each result should prioritize:

1. country/currency name;
2. code;
3. secondary context.

Flags are supplementary, never the identifier.

### 9.6 Long-list accessibility

Do not ship an inaccessible custom autocomplete for visual polish.

Until a robust searchable combobox is ready, a simpler accessible selector is preferable.

---

## 10. Swap behaviour

Swap exchanges the full selected context:

- source currency ↔ destination currency;
- source country ↔ destination country when present.

Amount remains the source amount.

Why:

A user asking:

> 100 EUR in JPY?

and then tapping Swap most predictably asks:

> 100 JPY in EUR?

Do not automatically use the previous converted amount as the new source amount unless user testing strongly supports that behaviour.

Swap must:

- have a text accessible name;
- not be icon-only to assistive technology;
- not move keyboard focus;
- announce only the updated result, not the whole form.

---

## 11. Result hierarchy

The success state should read in this order.

### 11.1 Primary result

```text
100 EUR ≈ 17,450 JPY
```

Use approximation language because:

- reference rates are not guaranteed transaction rates;
- final card/cash exchange may differ.

### 11.2 Reference rate

```text
1 EUR = 174.50 JPY
```

Optional inverse:

```text
1 JPY = 0.00573 EUR
```

Do not make both equally visually dominant.

### 11.3 Data trust

Example:

```text
Reference rate effective 18 Sep 2026
Source: ECB via Frankfurter
Fetched 19 Sep 2026, 12:40
```

Separate:

- rate effective time/date;
- app fetch time.

### 11.4 Transaction disclaimer

Compact wording:

> Reference exchange rate for information. Your bank, card or cash provider may use a different rate or add fees.

This belongs near rate metadata, not hidden in a legal footer.

---

## 12. Local purchasing context

Section title:

> What this amount roughly buys

Prefer concrete, relatable categories.

Potential categories:

- coffee;
- casual meal;
- local public transport;
- grocery basket item;
- budget hotel only when source quality is good.

### 12.1 Calculation

If the converted amount is 17,450 JPY and a coffee observation is 500–650 JPY, show a range such as:

> roughly 26–34 coffees

Do not round to a falsely exact “35 coffees”.

### 12.2 Metadata

Expandable provenance includes:

- Tokyo;
- observed May 2026;
- source;
- range/typical value;
- confidence/classification.

### 12.3 Missing context

Say:

> Local price context is not available for this destination yet.

Do not fall back to an invented global average.

---

## 13. Payment guidance

Order by immediate traveller value:

1. card acceptance;
2. cash usefulness;
3. ATM practical note;
4. tipping norm;
5. DCC / conversion warning;
6. special local considerations.

### Copy rules

Good:

> Cards are commonly accepted in cities; carrying some cash is still useful for smaller businesses.

Bad:

> Japan is a cash country.

Use qualified, sourced statements.

---

## 14. Cultural exploration

Cultural content should reward curiosity after the practical task is complete.

### Entry points

- “Explore money & culture”
- currency-history disclosure;
- destination profile.

### Categories

- currency history;
- language;
- money etiquette;
- food;
- traditions;
- notable places;
- local context relevant to travellers.

### Progressive disclosure

P0 page should show only a small teaser.

Long content belongs in:

- expandable sections;
- dedicated country page;
- later Explore destination.

Do not bury the converter under editorial content.

---

## 15. Historical rate UX

Historical charts answer:

> How unusual is today's reference rate compared with recent history?

They do **not** answer:

> Should I trade now?

### Display

Include:

- selected period;
- current/end rate;
- high;
- low;
- average when meaningful;
- simple change summary.

### Accessibility

Charts must have equivalent textual/table information.

### Default period

Do not overload P0.

Historical UX belongs after the core contextual product works reliably.

---

## 16. Favourites and recents

### Anonymous users

Prefer local persistence initially.

Favourites store:

- currency pair;
- optional country contexts.

Recent history should be:

- bounded;
- easy to clear;
- not silently sent to the server.

### Signed-in users

Later enable cross-device sync.

### UX rule

Saving must never be required to convert.

---

## 17. Shareable state and URLs

A useful conversion should be bookmarkable/shareable.

Candidate query model:

```text
/?amount=100&from=EUR&to=JPY&from_country=FI&to_country=JP
```

Rules:

- URL parameters are untrusted input;
- invalid/unsupported values fall back gracefully;
- no personal data in URL;
- loading a deep link produces the same result hierarchy as manual entry.

---

## 18. Accounts

Accounts are convenience, not access control for the public converter.

Do not ask users to register until there is a clear value proposition such as:

- sync favourites;
- sync trips;
- retain history across devices.

Account prompts occur after value is demonstrated.

Never interrupt the first conversion with a sign-up modal.

---

## 19. Trip/budget UX

Later flow:

```text
Destination
↓
Dates
↓
Home currency
↓
Total budget
↓
Per-day interpretation
↓
Optional category allocation
```

The trip feature should reuse conversion/context components instead of creating a second financial mental model.

Avoid pretending the app can produce an exact “required budget” for a person.

---

## 20. Mobile-native UX

The React Native app optimizes for repeated, on-the-go use.

### P0 mobile screen

```text
[Amount]
[From]

        ⇅

[To]

[Converted result]
[Reference rate · effective date]

What this buys
Payment tips
```

### One-handed use

Frequent actions belong in comfortable reach:

- amount;
- pair controls;
- swap;
- saved pair access.

### Touch targets

Use platform-native comfortable hit areas rather than merely meeting web minimums.

### Native feedback

Custom pressable controls need visible pressed states.

Haptics can be considered for explicit actions such as Save or Swap, but are not required and must never be the only feedback.

---

## 21. Offline and stale UX

Offline usability is a mobile differentiator.

### Same pair cached

Show:

```text
17,450 JPY
Cached reference rate
Effective 18 Sep 2026
Last synced 19 Sep, 08:12
Offline
```

### Different pair requested while offline

Never reuse the prior result.

Show:

> This pair is not available offline yet.

with a path back to available saved/cached pairs.

### Stale data visual treatment

Use:

- explicit text;
- status badge/icon;
- timestamp.

Never colour alone.

---

## 22. Loading behaviour

### First conversion

Show progress near the result area, not a full-screen loader.

### Updating amount

Retain the previous result visually while marking the result region as updating if necessary.

Avoid flashing skeletons on every keystroke.

### Enrichment

Purchasing/culture sections load independently.

Failure of enrichment must not turn the whole page into an error.

---

## 23. Error and recovery design

Every error answers:

1. What happened?
2. What data, if any, is still trustworthy?
3. What can I do next?

### Example — provider unavailable, same pair cached

> The reference rate could not be refreshed. Showing the last successful EUR → JPY rate effective 18 Sep 2026.

Actions:

- Retry;
- keep using cached result.

### Example — unsupported pair

> A reference rate is not available for X → Y.

Actions:

- choose another currency.

### Example — malformed amount

> Enter an amount such as 1234.56 or 1234,56, without thousands separators.

Focus remains on the field after submission.

---

## 24. Empty states

### No destination

> Choose a destination currency or country to convert.

### Conversion exists, no cultural country

> Choose a destination country to see local prices and money customs.

### No price context

> Local price context is not available for this destination yet.

### No favourites

> Save a currency pair you use often for faster access next time.

Empty states explain the next useful action; they do not advertise unrelated features.

---

## 25. Localization and internationalization

The product is international by definition.

Even if the first UI language is English, architecture and copy must avoid assumptions that make localization expensive later.

### Requirements

- currency names and country names can be localized later;
- amount input supports decimal comma scenarios;
- displayed numbers use user-facing locale formatting;
- internal API/domain values remain canonical;
- dates use clear formats;
- UTC/source dates are not silently converted in misleading ways;
- text expansion must not break layouts;
- RTL must not be made impossible by directional CSS assumptions.

### Currency symbols

Always keep the code available.

`$` alone is ambiguous.

Prefer:

> USD 100

or:

> $100 USD

depending on locale/presentation context.

---

## 26. Accessibility UX requirements

Baseline: WCAG 2.2 AA.

### Labels

Every input has a persistent visible label.

### Error association

Error text is programmatically associated with the field.

### Focus

- no focus theft after normal HTMX updates;
- focused control is not obscured;
- visible focus indicator is strong;
- modal/drawer focus behaviour is correct if such patterns are introduced.

### Targets

Web pointer targets meet WCAG 2.2 minimum sizing/spacing.

Product design should usually exceed the minimum for touch-heavy controls.

### Live regions

Announce only essential result changes.

Good:

> 100 euros is approximately 17,450 Japanese yen. Reference rate effective 18 September.

Do not announce the full context section after each amount change.

### Zoom/reflow

Core conversion works without horizontal scrolling at 320 CSS px equivalent layouts and under high zoom/reflow conditions.

---

## 27. Privacy UX

### Anonymous conversion

No account required.

### History

If recent history is stored locally:

- disclose it in a concise settings/help context;
- allow Clear history;
- do not imply cloud sync.

### Analytics

Do not log raw sensitive user-entered notes or trip content.

Product analytics should answer behavioural questions with the minimum data necessary.

---

## 28. Interruption and resume

Real travel use is interruption-heavy.

The app should preserve:

- current amount;
- selected pair;
- expanded context where reasonable.

Mobile should restore the last useful state after backgrounding unless the state is security-sensitive.

A refreshed browser page should remain useful through URL state/local preferences rather than depending entirely on ephemeral client memory.

---

## 29. Performance as UX

Targets are experience targets, not benchmark theatre.

Important outcomes:

- HTML shell appears quickly;
- form is usable before enrichment completes;
- conversion update does not shift the page dramatically;
- country selectors do not freeze on large datasets;
- cultural media is lazy;
- images do not block the result.

---

## 30. Competitive benchmark observations

Current mainstream converters such as Wise and Xe strongly prioritize:

- amount;
- From;
- To;
- converted result;
- exchange-rate context;
- rate tracking/history.

That validates keeping conversion as the primary visual task.

Our differentiator should therefore appear **immediately after the trusted result**, not before it:

```text
Conversion
↓
Reference-rate trust
↓
Local value
↓
Payment context
↓
Culture
```

Do not imitate transfer/marketing CTAs from commercial competitors; this product has a different job.

---

## 31. Product analytics questions

Do not instrument everything.

Measure only what helps answer a product decision.

### Early questions

- Do users complete a conversion?
- Do they use country context or only currency?
- Is Swap used frequently?
- Do people open local-value context?
- Do they open provenance details?
- Where do validation failures happen?
- How often does provider failure lead to successful retry?
- Are favourites used enough to justify accounts?
- Which contextual categories are actually useful?

Analytics never replace qualitative usability testing.

---

## 32. Usability-test scenarios

Before polishing the UI, test these tasks with representative people.

### Test 1 — quick travel conversion

> You are in Tokyo. A meal costs 3,800 JPY. You normally think in EUR. Find roughly what it costs and whether this is around a typical casual-meal range.

### Test 2 — shared currency

> You are travelling from Finland to Italy. Both use EUR. Find useful differences the app can still tell you.

### Test 3 — stale data

> Your connection becomes unreliable. Decide whether the number shown can still be trusted and how old it is.

### Test 4 — unfamiliar currency

> Convert 500 PLN to Japanese yen without knowing the currency names in English.

### Test 5 — keyboard only

Complete the primary conversion without a pointing device.

### Test 6 — screen-reader-oriented review

Verify that amount, pair, result, source status and errors are understandable without visual layout.

Success is not measured by “the participant eventually succeeded”; note hesitation, misinterpretation and unnecessary steps.

---

## 33. P0 UX acceptance criteria

A P0 experience is ready only when:

- a first-time user can identify the main task without onboarding;
- conversion works with JavaScript disabled;
- enhanced conversion does not change the mental model;
- result clearly distinguishes reference rate from transaction rate;
- rate effective date/source are visible;
- same-currency/different-country use is meaningful;
- shared currencies do not force an incorrect country assumption;
- input errors preserve state;
- provider failures preserve only safe same-pair data;
- no enrichment failure breaks conversion;
- mobile layout works one-handed without horizontal scrolling;
- keyboard path is complete;
- screen-reader result announcement is concise;
- approximate local prices expose scope/date/source;
- basic use requires no account;
- no dark pattern competes with the conversion.

---

## 34. UX anti-patterns

Do not:

- call daily reference data “live”;
- ask for location permission on first load;
- force sign-up before conversion;
- auto-play cultural audio;
- make the user select a country when they only need a currency calculation;
- silently select a country for a shared currency and treat it as fact;
- use placeholder-only labels;
- put a full-screen spinner over an existing valid result;
- clear a valid result because cultural data failed;
- show stale data without a timestamp;
- reuse stale data for a different currency pair;
- use flags as currency identifiers;
- show exchange-rate precision that implies tradable accuracy;
- render a 200-item selector that is visually compact but unusable by keyboard;
- make hover the only way to discover source information;
- show fake-precise “what this buys” counts;
- move focus to the result after every debounced update;
- overload the first screen with charts, history, tips, culture and account features.

---

## 35. Open research questions

These should be answered through prototype/usability testing rather than assumption.

1. Is country-first or currency-first search faster for travellers?
2. Should the first source currency suggestion come from browser locale or remain empty?
3. Does keeping amount constant on Swap match user expectation better than swapping both amounts?
4. At what point should a country-context prompt appear for shared currencies?
5. Which three “what this buys” categories have the highest cross-country comprehension?
6. Is a contextual drawer or inline section better for cultural exploration on mobile?
7. How much provenance should be visible by default vs expanded?
8. Does auto-update after the first conversion feel faster or distracting on slow networks?
9. Do users understand “reference rate” without additional explanation?
10. Is local recent history valuable enough to justify persistence by default?

Until tested, these remain hypotheses rather than product facts.


---

## 36. Storytelling experience

Storytelling is optional progressive disclosure after the trusted financial result.

Experience order:

```text
conversion
→ trust metadata
→ local/historical meaning
→ story
```

The story entry point should feel like:

> **The story behind this rate**

not like a mandatory onboarding chapter.

A story is valuable when it helps the user understand:

- the currency era;
- a transition between currencies;
- the difference between selected historical and latest reference observations;
- a temporally relevant sourced context.

The story is not valuable when it merely adds generic country trivia.

## 37. Historical converter experience

Historical conversion is an extension of the main converter.

Default:

> Rate date — Latest available

Optional:

> Historical date — [date]

This preserves the existing mental model instead of creating a second converter.

The historical result must clearly show:

- requested date;
- actual observation/effective date;
- provider/source;
- whether a previous observation was substituted;
- whether the data is daily/monthly/other when granularity affects interpretation.

## 38. Historical temporal separation

In historical mode, hide current local-price/payment sections by default unless explicitly labelled as current context.

The user should never need to wonder:

> “Are these coffee prices from 1998 or from today?”

Temporal clarity is part of UX correctness.

## 39. Historical UX research questions

Test:

1. Is “Rate date” discoverable without cluttering the main converter?
2. Does “Latest available / Historical date” communicate the distinction better than “Today / Past”?
3. Do users understand requested date vs observation date on weekends?
4. Does a historical-currency suggestion feel helpful or corrective?
5. Is “The story behind this rate” compelling enough without becoming gimmicky?
6. Do people understand Then & now as an FX comparison rather than investment return?
7. Should historical story open inline, on a dedicated page, or in a mobile sheet?
