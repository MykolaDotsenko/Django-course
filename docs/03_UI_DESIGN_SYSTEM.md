# UI Design System

This file is the executive design contract. Detailed implementation guidance lives in:

- [Visual foundations](03A_VISUAL_FOUNDATIONS.md)
- [Screen-by-screen blueprints](03B_SCREEN_BLUEPRINTS.md)
- [Component anatomy and dimensions](03C1_COMPONENT_ANATOMY_AND_DIMENSIONS.md)
- [Component states and microinteractions](03C_COMPONENT_STATES_AND_MICROINTERACTIONS.md)
- [Responsive, motion, accessibility and design QA](03D_RESPONSIVE_MOTION_ACCESSIBILITY.md)

The design language is named **Quiet Atlas**:

> **Nordic editorial utility — calm enough for money, warm enough for culture.**

The detailed documents are normative. If a visual implementation conflicts with them, the implementation must be changed or the design decision explicitly revised in documentation/ADR.


## 1. Design direction

The product should feel like a **calm premium travel utility**, not a banking dashboard and not a tourism collage.

Design keywords:

- clear;
- calm;
- trustworthy;
- warm;
- contextual;
- spacious;
- modern;
- culturally respectful.

The visual system must support the product hierarchy:

```text
conversion → trust → local meaning → payment context → culture
```

Decoration is never allowed to outrank the conversion result.

---

## 2. Stable shell, contextual atmosphere

Country selection may influence:

- subtle accent token;
- background artwork/pattern;
- editorial imagery;
- small cultural details.

It must not change:

- semantic hierarchy;
- control positions;
- focus order;
- validation language;
- fundamental component behaviour.

This prevents every country from becoming a custom mini-site and protects learnability when users switch destinations repeatedly.

---

## 3. Tailwind strategy

Tailwind CSS is a delivery mechanism, not the design architecture.

Define semantic tokens first:

```text
surface
surface-elevated
surface-muted
text
text-muted
border
border-strong
accent
accent-hover
accent-contrast
success
warning
danger
focus
stale
```

Avoid scattering country-specific raw colours through templates.

Country themes modify semantic tokens within safe contrast constraints.

---

## 4. Component inventory

P0 components:

- AppShell;
- SkipLink;
- Header;
- ConverterForm;
- CurrencyAmountField;
- CountryCurrencySelector;
- SwapButton;
- ConvertButton;
- ConversionResult;
- RateMeta;
- DataFreshnessBadge;
- ContextCard;
- TypicalPriceList;
- PaymentTips;
- Disclosure;
- InlineAlert;
- ErrorSummary;
- EmptyState;
- ScopedLoadingIndicator;
- SourceDetails;
- Footer/DataSources.

Prefer Django template partials and small HTMX targets.

A component must represent a stable user/interface concept, not merely a visual rectangle.

---

## 5. Primary layout

### Large screens

Use a balanced source/destination comparison when it improves scanning.

The result should visually bridge the two contexts rather than feel like a third competing column.

### Medium screens

Keep two columns only while controls remain comfortably readable and touch-friendly.

### Small screens

Stack in task order:

```text
Amount
From
Swap
To
Convert
Result
Trust metadata
Local value
Payment context
Culture
```

No horizontal dependency is required to understand the result.

Use container/layout primitives rather than device-name breakpoints where practical.

---

## 6. Visual hierarchy

Priority:

1. amount/result;
2. source and destination identity;
3. reference-rate trust metadata;
4. local purchasing meaning;
5. payment guidance;
6. cultural enrichment;
7. secondary save/share/history actions.

The converted amount should be prominent but must not resemble a speculative market ticker.

Do not display excessive decimal precision merely because the API returns it.

---

## 7. Form design

### Labels

All inputs have visible persistent labels.

Good:

> Amount

> From

> To

Do not rely on placeholder-only labels.

### Hints

Use short hint text only when most users need it.

Do not add explanatory paragraphs under every field.

### Errors

Place specific error text close to the affected field and connect it programmatically.

When several errors occur after a full submit, use an error summary if it improves recovery.

### Prefix/suffix

Currency codes/symbols may appear visually with amount fields, but the underlying label/value relationship remains clear.

---

## 8. Amount input

The amount control should be visually dominant enough to identify the primary task, without becoming oversized decoration.

Requirements:

- persistent Amount label;
- clear source currency code adjacent;
- mobile decimal keyboard hint where supported;
- no auto-formatting while the user is mid-edit if it moves the caret unexpectedly;
- error copy preserves the entered value;
- sufficient width for realistic travel/shopping amounts.

Do not show a default `0.00` in a way that looks like a completed conversion before the user acts.

---

## 9. Country/currency selector

The selector must communicate both concepts without conflating them.

Suggested row anatomy:

```text
🇯🇵  Japan
    Japanese yen · JPY
```

Currency-only option:

```text
€  Euro · EUR
   Used by multiple countries
```

### Search result emphasis

Primary:

- country name or currency name.

Secondary:

- currency code;
- currency name;
- usage context.

Flags are decorative/supportive, never sufficient identity.

### Selected value

Must remain understandable without flag imagery.

---

## 10. Swap control

Swap is a frequent action.

Requirements:

- comfortable touch target;
- visible label or accessible name;
- clear pressed/hover/focus states;
- visually located between From and To without becoming tiny;
- keyboard focus remains after activation.

On narrow mobile layouts, the icon may rotate/orient vertically while semantic meaning remains “Swap source and destination”.

---

## 11. Convert action

The first conversion has one obvious primary button:

> Convert

After a result exists, copy may become:

> Update

only if testing shows the state difference improves clarity.

A visible explicit action remains even when HTMX supports debounced enhancement.

Avoid simultaneous equally-prominent CTAs such as:

- Convert;
- Sign up;
- Track rate;
- Explore;
- Start trip.

---

## 12. Result component

Recommended anatomy:

```text
100 EUR ≈ 17,450 JPY

Reference rate
1 EUR = 174.50 JPY

Effective 18 Sep 2026
ECB via Frankfurter

Reference rate only — your payment provider may use a different rate or add fees.
```

### Status variants

- current reference;
- cached/stale;
- offline;
- same currency.

The variant must be understandable in text.

### Approximation symbol

Use `≈` or plain-language “approximately” where it reinforces that this is informational rather than a guaranteed executable quote.

---

## 13. Freshness/status design

Do not use green/red to imply “good/bad” rates.

Status is about data freshness, not financial desirability.

Possible badges:

- Reference rate
- Cached
- Offline
- Context unavailable

Badges supplement explicit dates.

“Last fetched” and “effective date” are different concepts and should not be visually merged.

---

## 14. Local-value cards

Cards should answer one question per item.

Example:

```text
☕ Coffee
roughly 26–34
Tokyo estimate
```

Keep provenance one interaction away, not hidden in an inaccessible tooltip.

Avoid a wall of 8–12 cards.

P0 target:

- 3 high-value categories when data quality permits.

---

## 15. Payment-guidance component

Prefer a compact ordered list over decorative cards for every fact.

Potential structure:

```text
Paying in Japan

Cards       Common in cities
Cash        Useful for smaller businesses
ATMs        Practical note…
Tipping     Usually not expected…
```

Use icons only as scan aids.

The wording carries meaning.

---

## 16. Cultural content presentation

Culture should feel editorial, not encyclopedic.

Use:

- short teaser;
- expandable section;
- dedicated Explore/country page later.

Avoid:

- giant hero imagery before result;
- auto-playing media;
- carousel-heavy content;
- unrelated trivia that pushes practical guidance down.

---

## 17. Typography

Typography roles:

### Display/result
Large but controlled numeric emphasis.

### Heading
Clear content hierarchy.

### Body
High legibility and moderate measure.

### Metadata
Smaller, but never so small/low-contrast that source/freshness becomes effectively hidden.

Trust metadata is secondary in visual weight, not optional in usability.

---

## 18. Spacing

Spacing should communicate relationships.

Tight group:

- amount + currency code;
- result + rate;
- status + effective date.

Larger separation:

- converter;
- local value;
- payment context;
- culture.

Do not rely on card borders to create all hierarchy.

Whitespace has higher ROI than unnecessary containers.

---

## 19. Touch targets

WCAG 2.2 AA defines a 24×24 CSS-pixel minimum target or sufficient spacing under its exceptions.

For this touch-heavy product, aim larger for primary controls.

Web/mobile frequent actions should be designed around comfortable finger use, not merely technical minimum compliance.

For iOS-native controls, platform guidance commonly targets at least 44×44 pt hit regions.

Priority large targets:

- Swap;
- Convert;
- country/currency picker trigger;
- saved pair;
- bottom navigation.

---

## 20. Focus styles

Use an unmistakable focus treatment.

The product should target a strong 2px-or-more equivalent outline with sufficient contrast rather than barely-visible browser-theme-dependent decoration.

Focus styling must survive:

- country themes;
- light/dark surfaces;
- error borders;
- stale/warning states.

Do not remove browser focus without a stronger replacement.

---

## 21. Motion

Allowed:

- small state transitions;
- swap affordance;
- drawer expansion;
- restrained result update;
- skeleton-to-content transition when actually useful.

Avoid:

- continuous decorative JS loops;
- motion tied to every keystroke;
- parallax in the primary workflow;
- count-up number animations that delay reading the real result.

Honor `prefers-reduced-motion`.

---

## 22. Theme requirements

Initial release:

- light theme as primary;
- dark theme only if it can reach equivalent contrast/quality without delaying core features.

Country theming is not a replacement for dark mode.

Cultural colour references must avoid stereotyping and should remain subtle.

---

## 23. Icons and flags

- use text currency codes alongside any symbol;
- use country names alongside flags;
- no emoji-only actionable control;
- avoid implying that one flag uniquely represents a currency;
- icons with directional meaning must be audited for RTL later.

---

## 24. Loading design

Use the smallest loading surface possible.

### First conversion

Scoped result loading state.

### Subsequent update

Retain previous result while the new one loads, but do not relabel it as belonging to the new inputs.

### Enrichment

Cultural/local-value loading does not block conversion.

Avoid full-page skeletons after the app shell already exists.

---

## 25. Error design

Error messages answer:

1. what happened;
2. whether previous data is still usable;
3. what the user can do next.

Good:

> The reference rate could not be refreshed. Showing the last successful EUR → JPY rate effective 18 Sep 2026. Retry.

Bad:

> Live rates unavailable.

Good:

> Enter an amount such as 1234.56 or 1234,56, without thousands separators.

Bad:

> Invalid value.

---

## 26. Empty-state design

An empty state should explain the next useful action.

Examples:

> Choose a destination to convert.

> Choose a destination country to see local prices and money customs.

> Local price context is not available for this destination yet.

Avoid illustrations that take more space than the guidance.

---

## 27. Source/provenance UI

Source information should be discoverable without needing hover.

Default result shows:

- rate effective date;
- concise source/provider.

Expanded detail may show:

- contributing provider;
- fetched timestamp;
- methodology note.

Typical-price context shows:

- place scope;
- observed date;
- source.

This is part of trust design, not legal fine print.

---

## 28. Content style

Prefer precise, restrained language.

Good:

> Cards are commonly accepted in urban areas.

Bad:

> Japan is basically cashless now!

Good:

> Typical coffee estimate · Tokyo · observed May 2026.

Bad:

> Coffee in Japan costs ¥500.

Good:

> Reference rate effective 18 Sep 2026.

Bad:

> Live rate.

Avoid hype, trading language and claims that imply guaranteed savings.

---

## 29. Responsive cultural imagery

If imagery is introduced:

- it loads after critical UI;
- it has intrinsic dimensions;
- it does not create CLS;
- meaningful imagery has appropriate text alternative;
- decorative imagery is ignored by assistive technology;
- cropped compositions remain culturally respectful on narrow screens.

The converter does not need imagery to function.

---

## 30. Data density

Desktop can expose more provenance/context without forcing extra navigation.

Mobile prioritizes:

1. result;
2. status;
3. local value;
4. payment guidance.

Secondary source detail may collapse into disclosure.

Do not simply shrink the desktop two-column experience.

---

## 31. Visual ROI rule

Every visual element must do at least one of:

- improve comprehension;
- improve navigation;
- communicate system state;
- establish useful hierarchy;
- strengthen cultural context without reducing clarity.

Otherwise remove it.

---

## 32. Design-system acceptance checklist

A component is ready only if:

- meaning survives without colour;
- keyboard focus is visible;
- target size/spacing is comfortable;
- error state is specific;
- loading state is scoped;
- reduced motion is respected;
- text can expand;
- no flag/icon is the only label;
- contrast survives country themes;
- source/freshness information remains legible;
- mobile stacking preserves logical reading order.


---

## 33. Historical converter UI additions

Historical mode adds only the controls required to change temporal context.

Recommended control:

```text
Rate date
[ Latest available ▾ ]
```

Historical selection reveals a date picker.

Do not permanently occupy primary-screen space with a large timeline or chart.

### Historical result badge

Use:

- Historical reference
- Previous available observation
- Monthly observation

Avoid:

- Old rate
- Live history
- Time-machine rate

## 34. Requested vs effective date presentation

When dates differ, use explicit stacked metadata:

```text
Requested
14 Jun 1998

Observation used
12 Jun 1998
```

Do not compress this into a tooltip.

The date discrepancy is central trust information.

## 35. Archived currency presentation

Archived currency rows should expose historical status.

Example:

```text
Finnish markka · FIM
Historical currency
Provider coverage 1972–2002
```

Current-mode selectors should not visually flood the list with retired currencies.

## 36. Story component

Product-facing label:

> The story behind this rate

Recommended structure:

- compact trigger/disclosure;
- semantic chapter headings;
- sourced chapter footer/detail;
- currency timeline only where useful;
- no auto-playing animation.

Story visual hierarchy remains lower than conversion and rate provenance.

## 37. Currency timeline

A timeline may visualize:

- introduction;
- selected date;
- transition;
- retirement/changeover;
- current currency.

Desktop may use horizontal presentation if labels remain readable.

Mobile should prefer a vertical timeline rather than forcing horizontal scroll.

Every milestone must remain understandable without visual position alone.

## 38. Then & now component

Use a neutral comparison layout:

```text
Then
15 Jun 2016
100 EUR ≈ X USD

Latest reference
18 Sep 2026
100 EUR ≈ Y USD
```

If a percentage difference is shown:

- state direction;
- avoid green/red “gain/loss” semantics;
- avoid investment framing.

## 39. Historical context card rule

Historical stories can use editorial cards, but each must answer a relevant temporal question.

Good:

> Finland was using FIM on this date.

Good:

> Euro cash replaced national notes/coins later in the transition.

Bad:

> Finland has thousands of lakes.

The last fact may be true but has low relevance to a money story.

## 40. Story motion

If timeline/story transitions use animation:

- motion never delays reading;
- selected date/result is available immediately;
- reduced-motion preference removes non-essential movement;
- no “counting through years” animation before showing result.

## 41. Historical colour semantics

Do not make historical mode sepia/brown merely to signal “old”.

That can make the product feel nostalgic rather than authoritative.

Use the same trust-oriented design system, with subtle temporal cues in typography/metadata rather than theme gimmicks.


---

## 42. Design implementation contract

All implementation work must preserve these system-level decisions:

1. **The product itself is the hero.** No marketing hero may push the converter below the initial viewport without a strong reason.
2. **Trust is visible.** Rate type, effective date and provenance cannot be reduced to visually inaccessible fine print.
3. **Semantic tokens before raw values.** Color, spacing, radius and motion use documented roles/scales.
4. **Country theme is atmosphere, not a new UI.** Layout and component behavior remain stable.
5. **Historical mode is archival, not nostalgic.** No sepia/typewriter visual cliché.
6. **Whitespace before extra containers.** Do not solve hierarchy by turning every section into a card.
7. **Motion is functional.** No count-up numbers, bounce, looping decoration or timeline theater.
8. **Touch targets exceed minimum where practical.** Frequent controls are designed for real travel conditions.
9. **Component state completeness matters.** Loading/error/stale/offline/focus/reduced-motion states are part of design, not later polish.
10. **Mobile is intentionally redesigned, not desktop compressed.**
11. **Accessibility is visible design quality.** Strong focus, readable metadata and resilient layout are considered premium design.
12. **Performance is a design constraint.** The visual language cannot require heavy web JavaScript or large above-fold media.

## 43. Design review requirement

Before a key screen is accepted, review it against the /100 scorecard in `03A_VISUAL_FOUNDATIONS.md`.

Target:

> **95+/100 with zero critical trust, accessibility or state-integrity issue.**

This target describes the implementation bar. It is not a claim about code that does not yet exist.
