# Official References

These are preferred primary references for implementation and UX decisions. Version-match documentation before each implementation PR.

## Django

- Django 5.2 documentation  
  https://docs.djangoproject.com/en/5.2/
- Django 5.2 release notes / LTS status  
  https://docs.djangoproject.com/en/dev/releases/5.2/
- Security  
  https://docs.djangoproject.com/en/5.2/topics/security/
- Deployment checklist  
  https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
- Caching  
  https://docs.djangoproject.com/en/5.2/topics/cache/
- Performance  
  https://docs.djangoproject.com/en/5.2/topics/performance/

## HTMX

- Documentation  
  https://htmx.org/docs/
- Security guidance  
  https://htmx.org/docs/#security
- Reference  
  https://htmx.org/reference/

Important implementation note: full-page and HTMX-fragment representations sharing a URL require correct cache variation semantics, commonly `Vary: HX-Request`.

## Tailwind CSS

- Documentation  
  https://tailwindcss.com/docs/
- Installation  
  https://tailwindcss.com/docs/installation
- Browser compatibility  
  https://tailwindcss.com/docs/compatibility
- Upgrade guide  
  https://tailwindcss.com/docs/upgrade-guide

Tailwind 4 targets modern browsers; verify target-browser requirements before implementation.

## FX data — Frankfurter

- API documentation  
  https://frankfurter.dev/
- Python examples  
  https://frankfurter.dev/python/

Relevant API characteristics:

- daily exchange rates from central banks and official sources;
- latest reference rates;
- individual pair rates;
- historical dates;
- time series;
- provider filtering;
- provider attribution;
- current and legacy currency metadata.

### UX implication

Frankfurter explicitly describes its data as mostly daily and states it is not intended for live trading.

Therefore product copy must not describe P0 exchange data as “live” or “real-time”.

Use:

- reference rate;
- effective date;
- provider/source attribution.

## Accessibility — W3C

- WCAG 2.2 Recommendation  
  https://www.w3.org/TR/WCAG22/
- WCAG overview  
  https://www.w3.org/WAI/standards-guidelines/wcag/
- What's new in WCAG 2.2  
  https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- Understanding Target Size (Minimum) — SC 2.5.8  
  https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum
- Understanding Focus Appearance  
  https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance

Relevant UX constraints include:

- WCAG 2.2 AA target-size/spacing requirements;
- visible and unobscured keyboard focus;
- non-colour-only state communication;
- predictable form/error behaviour.

## Form UX reference — GOV.UK Design System

The project does not copy GOV.UK visual styling. These references are used for mature form-interaction guidance.

- Text input  
  https://design-system.service.gov.uk/components/text-input/
- Select  
  https://design-system.service.gov.uk/components/select/
- Error message  
  https://design-system.service.gov.uk/components/error-message/
- Error summary  
  https://design-system.service.gov.uk/components/error-summary/

Relevant guidance:

- visible labels rather than placeholder-only fields;
- concise hint text;
- field-specific errors;
- programmatic description/error association;
- predictable native controls where appropriate.

## Native mobile UX — Apple Human Interface Guidelines

- Buttons  
  https://developer.apple.com/design/human-interface-guidelines/buttons
- Accessibility  
  https://developer.apple.com/design/human-interface-guidelines/accessibility
- UI design tips  
  https://developer.apple.com/design/tips/

Relevant mobile considerations:

- primary touch controls should have comfortable hit regions;
- iOS guidance commonly uses at least 44×44 pt for standard button hit regions;
- custom buttons need clear pressed states;
- spacing is important for users with limited touch precision.

Android/Material platform-specific guidance should be added and version-checked when React Native UI implementation begins.

## React Native

- React Native documentation  
  https://reactnative.dev/docs/getting-started
- React Native 0.87 release notes  
  https://reactnative.dev/blog/2026/08/11/react-native-0.87

Do not assume the newest RN line is automatically the Expo production choice.

## Expo

- Latest Expo SDK reference / compatibility table  
  https://docs.expo.dev/versions/latest/
- Expo documentation  
  https://docs.expo.dev/

Select Expo + React Native + React as a supported compatibility matrix.

## Django REST Framework

- Documentation  
  https://www.django-rest-framework.org/

Use only for the explicit mobile API boundary, not as an unnecessary intermediary for the Django web UI.

## Country and currency standards

Prefer ISO-style stable identifiers in the domain.

Where external country metadata is used, import/normalize only fields the product actually owns and displays.

Any third-party country-data provider must be replaceable through import/normalization boundaries and must not become an implicit domain schema.

## Competitive UX benchmarks

These are **benchmarks, not authorities**.

They help identify established user expectations for the primary conversion task.

### Wise Currency Converter

https://wise.com/us/currency-converter/

Current observed hierarchy:

- amount;
- source currency;
- destination currency;
- converted result;
- mid-market/reference-rate explanation;
- tracking/history as secondary actions.

### Xe Currency Converter

https://www.xe.com/currencyconverter/

Current observed hierarchy:

- amount;
- From;
- To;
- result;
- rate timestamp/context;
- tracking/historical tools.

### Product conclusion

Mainstream converters validate a very low-friction conversion hierarchy.

Cultural Currency Converter should not compete with that workflow.

Its differentiation begins **after the trusted result**:

```text
conversion
→ trust/freshness
→ local purchasing context
→ payment guidance
→ culture
```

Commercial CTAs such as money transfer, account upsell or rate tracking are not copied merely because competitors use them.


## Historical FX and archived currencies

### Frankfurter currency catalog

https://frankfurter.dev/currencies/

Current documented capability:

- active and archived currencies;
- historical coverage per currency;
- provider counts;
- archived examples including FIM, DEM, ATS, ESP and others.

### Frankfurter historical/time-series API

https://frankfurter.dev/

Relevant endpoints/capabilities:

- specific historical date;
- date ranges;
- time series;
- `scope=all` for legacy currencies;
- provider-specific queries;
- provider attribution.

Historical UX must communicate per-pair/per-provider coverage rather than claiming every pair exists back to 1948.

### ECB euro reference rates

https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html

Important trust guidance:

- ECB reference rates are normally updated on working days;
- they are published for information purposes;
- ECB explicitly discourages using them for transaction purposes.

This reinforces product copy such as “reference rate” rather than guaranteed transaction/live rate.

## Future historical purchasing-power research

These are candidate primary sources for a separate later methodology. They are **not** interchangeable with FX-rate data.

### World Bank Indicators API

https://datahelpdesk.worldbank.org/knowledgebase/topics/125589-developer-information

Useful for official indicator-series access and provenance.

Before implementation, identify the exact CPI/inflation indicator and verify country/time coverage and methodology.

### OECD price level indices / PPP

https://www.oecd.org/en/data/indicators/price-level-indices.html

OECD price-level indices compare relative country price levels using purchasing power parities and market exchange rates.

This may support later cross-country price-level interpretation, but does not by itself answer all historical consumer purchasing-power questions.

### Methodology rule

Do not combine:

```text
historical FX
+
current price cards
```

and label the result historical purchasing power.

Any future “what could this buy then?” feature requires an explicit, documented price/inflation methodology.


# External API and Data-Source References

The detailed evaluation and selected roles live in:

- [API research and data-source strategy](11_API_RESEARCH_AND_DATA_SOURCES.md)
- [External API integration contracts](12_EXTERNAL_API_CONTRACTS.md)

The links below are primary/current documentation sources to re-check before implementation.

## Frankfurter

- Main API / v2 documentation  
  https://frankfurter.dev/
- Currency catalog and historical coverage  
  https://frankfurter.dev/currencies/
- Provider catalog  
  https://frankfurter.dev/providers/
- Open-source repository / self-hosting  
  https://github.com/lineofflight/frankfurter

Implementation policy:

- general FX source = Frankfurter v2;
- use source/provider attribution;
- keep current vs historical semantics explicit;
- no silent switching to another provider methodology.

## ECB Data Portal / SDMX

- Web service / SDMX API guidance  
  https://data.ecb.europa.eu/help/getting-data-web-services-sdmx-0
- Euro foreign-exchange reference rates  
  https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html

Use as an authoritative ECB reference/verification source and possible explicit provider adapter, not as an invisible fallback for blended Frankfurter data.

## REST Countries

- Documentation  
  https://restcountries.com/docs
- Country API documentation  
  https://restcountries.com/docs/countries
- Terms of Service  
  https://restcountries.com/legal/terms-of-service

Re-check authentication, quota, pricing and redistribution terms before production import automation.

Use as import/enrichment, not request-path infrastructure.

## Wikidata

- Data access  
  https://www.wikidata.org/wiki/Wikidata:Data_access
- Stable interface policy  
  https://www.wikidata.org/wiki/Wikidata:Stable_Interface_Policy
- Licensing  
  https://www.wikidata.org/wiki/Wikidata:Licensing

Use stable targeted entity APIs for ingestion.

SPARQL/query-service tooling is valuable for research but not required for user-facing runtime rendering.

## Wikimedia APIs / Commons

- Wikimedia API rate limits  
  https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits
- API etiquette  
  https://www.mediawiki.org/wiki/API:Etiquette
- Commons reuse/licensing guidance  
  https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/licenses/en

Persist per-file creator/licence/source metadata for any external media that is displayed.

## Europeana

- APIs overview  
  https://www.europeana.eu/en/apis
- API documentation / access guidance  
  https://pro.europeana.eu/page/apis

Use only as optional cultural-heritage enrichment with server-side credentials and record-level rights checks.

## Eurostat

- Web services  
  https://ec.europa.eu/eurostat/data/web-services
- Data Browser API access  
  https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/

Candidate dataset families include:

- HICP monthly indices such as `prc_hicp_midx`;
- purchasing-power / price-level datasets such as `prc_ppp_ind` and related tables.

Do not use PPP/price-level indices as a substitute for domestic CPI/HICP time-series inflation.

## OECD

- OECD API / SDMX guidance  
  https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html
- OECD Data Explorer  
  https://data-explorer.oecd.org/

Candidate PPP/price-level dataflow:

```text
DSD_PPP@DF_PPP_CPL
```

Dataset identifiers/versions must be re-checked at implementation time.

## World Bank Indicators API

- API documentation  
  https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
- CPI index indicator  
  https://data.worldbank.org/indicator/FP.CPI.TOTL
- Consumer inflation indicator  
  https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG
- PPP conversion factor  
  https://data.worldbank.org/indicator/PA.NUS.PPP
- Price-level ratio  
  https://data.worldbank.org/indicator/PA.NUS.PPPC.RF

Preserve indicator/dataset attribution and verify indicator-specific reuse terms.

## Numbeo

- API documentation and pricing  
  https://www.numbeo.com/common/api.jsp
- Terms of Use  
  https://www.numbeo.com/common/terms_of_use.jsp

Evaluated as a potentially strong item-price provider but deliberately not selected as a required P0/P1 dependency.

Current cost/licensing and crowdsourced provenance must be re-evaluated if the product later funds this integration.

## Source-review requirement

Before implementing any external API:

1. confirm the current version;
2. confirm authentication;
3. confirm rate/quota limits;
4. confirm pricing;
5. confirm licence/redistribution rules;
6. capture representative fixtures;
7. confirm source update frequency;
8. document outage/fallback behaviour;
9. record the review date in the implementation PR.


# Product Design References

The detailed design specifications are informed by current official/platform guidance and are adapted to this product rather than copied visually.

## Apple Human Interface Guidelines

- Human Interface Guidelines  
  https://developer.apple.com/design/human-interface-guidelines/
- Design principles  
  https://developer.apple.com/design/human-interface-guidelines/design-principles
- Layout  
  https://developer.apple.com/design/human-interface-guidelines/layout
- Typography  
  https://developer.apple.com/design/human-interface-guidelines/typography
- Color  
  https://developer.apple.com/design/human-interface-guidelines/color
- Materials  
  https://developer.apple.com/design/human-interface-guidelines/materials
- Motion  
  https://developer.apple.com/design/human-interface-guidelines/motion

Relevant principles used here:

- purpose and clarity before decoration;
- consistent relationships between controls/content;
- essential information receives sufficient space;
- limited typeface count and readable weights;
- semantic color rather than arbitrary color reuse;
- materials/translucency represent hierarchy, not generic decoration;
- motion communicates status/feedback and respects accessibility settings.

Apple's current material guidance is not used as a reason to copy Liquid Glass into web content cards.

## W3C / WCAG 2.2

- WCAG 2.2  
  https://www.w3.org/TR/WCAG22/
- What's new in WCAG 2.2  
  https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- Understanding Target Size (Minimum)  
  https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum
- Understanding Focus Appearance  
  https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance

Design implications include:

- AA target-size/spacing requirements;
- focus must remain visible/not obscured;
- focus indication needs strong visible area/contrast;
- color cannot be the sole state channel;
- high zoom/reflow is part of layout quality.

The project intentionally targets larger frequent-action hit areas than the 24×24 CSS-pixel AA minimum where practical.

## Tailwind CSS 4

- Theme variables  
  https://tailwindcss.com/docs/theme
- Responsive design and container queries  
  https://tailwindcss.com/docs/responsive-design
- Tailwind CSS v4 overview  
  https://tailwindcss.com/blog/tailwindcss-v4

Design-system implications:

- semantic tokens map naturally to `@theme` variables;
- CSS custom properties remain available at runtime;
- container queries are first-class;
- modern logical properties and CSS capabilities improve localization/RTL readiness.

## Progressive disclosure

- Nielsen Norman Group — Progressive Disclosure  
  https://www.nngroup.com/articles/progressive-disclosure/

The product applies progressive disclosure to:

- source methodology;
- historical charts;
- storytelling;
- advanced context;
- account/saved features.

Frequently needed conversion/trust information remains visible up front.

## Reference interpretation rule

External design systems/guidelines are **principle references**, not a visual template.

Cultural Currency Converter does not attempt to look exactly like:

- Apple;
- Material;
- Wise;
- Xe;
- GOV.UK.

The design must remain recognizably its own product while preserving familiar interaction behavior.


# Design System Research References

Research reviewed: **2026-09-19**.

These references support the Quiet Atlas visual-system decisions. They are principles and platform guidance, not visual templates to copy.

## Apple Human Interface Guidelines

### Branding

https://developer.apple.com/design/human-interface-guidelines/branding

Relevant current guidance:

- brand identity should defer to useful content;
- accent colour is stronger when used judiciously rather than across every control;
- familiar components/patterns preserve learnability;
- custom typography must remain legible and accessibility-compatible.

Quiet Atlas implication:

- fjord teal is scarce and meaningful;
- country atmosphere lives mostly in content/editorial layers;
- the converter remains familiar and immediately usable.

### Text fields

https://developer.apple.com/design/human-interface-guidelines/text-fields

Relevant guidance:

- visible context/label remains useful after placeholder disappears;
- size fields for expected input;
- preserve logical tab order;
- use input/keyboard types appropriate to the data.

Quiet Atlas implication:

- Amount has a persistent label;
- mobile uses decimal-appropriate input;
- From/To/search controls retain explicit labels.

### Entering data

https://developer.apple.com/design/human-interface-guidelines/entering-data

Relevant guidance:

- minimize unnecessary data entry;
- use information already available where appropriate;
- make requested data clear.

Quiet Atlas implication:

- country/currency suggestions reduce work but never silently overwrite explicit intent;
- no onboarding form before conversion.

### Gestures

https://developer.apple.com/design/human-interface-guidelines/gestures

Relevant guidance:

- familiar gestures behave familiarly;
- custom gestures are supplementary;
- important actions need non-gesture alternatives.

Quiet Atlas implication:

- no gesture-only Swap;
- sheets may swipe-dismiss but retain Close/Back;
- mobile interaction never depends on hidden gestures.

### Toolbars

https://developer.apple.com/design/human-interface-guidelines/toolbars

Relevant guidance:

- choose toolbar actions deliberately;
- avoid overcrowding;
- titles/actions should orient and support current content.

Quiet Atlas implication:

- global header stays compact;
- secondary actions do not compete with Convert.

### Apple design resources / current platform system

https://developer.apple.com/design/

Apple's current design system includes Liquid Glass and platform-native material/control guidance.

Quiet Atlas implication:

- native mobile may use current platform materials in navigation/control layers;
- web content surfaces do **not** imitate Liquid Glass simply because it is fashionable.

## W3C WCAG 2.2

### Target Size (Minimum) — 2.5.8

https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum

WCAG AA minimum:

- 24×24 CSS px, subject to documented spacing/exceptions.

Quiet Atlas intentionally targets larger frequent controls:

- roughly 44px+ web touch controls;
- 48–56px primary mobile controls.

### Focus Visible — 2.4.7

https://www.w3.org/WAI/WCAG22/Understanding/focus-visible

Keyboard focus must be visibly identifiable.

### Focus Appearance — 2.4.13

https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance

Although Level AAA, its 2-CSS-pixel-perimeter style guidance is used as a strong product target because the converter is form-heavy.

### Non-text Contrast — 1.4.11

https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast

Used when reviewing:

- control boundaries;
- focus indicators;
- chart markers;
- interactive states.

### Reflow — 1.4.10

https://www.w3.org/WAI/WCAG22/Understanding/reflow

Supports the design requirement that core conversion works under narrow/high-zoom layouts without two-dimensional scrolling.

## GOV.UK Design System

The visual style is not copied. The mature form/error interaction patterns remain useful references.

- Text input  
  https://design-system.service.gov.uk/components/text-input/
- Select  
  https://design-system.service.gov.uk/components/select/
- Error message  
  https://design-system.service.gov.uk/components/error-message/
- Error summary  
  https://design-system.service.gov.uk/components/error-summary/

Quiet Atlas uses the same broad principles:

- visible labels;
- clear field-level errors;
- predictable controls;
- error summaries only when they improve recovery.

## Material Design 3

Primary reference:

https://m3.material.io/

Relevant categories to re-check during React Native implementation:

- accessible design;
- typography;
- colour;
- motion;
- navigation;
- text fields;
- buttons;
- sheets.

Material is used as cross-platform interaction research, not as a requirement to make the product visually resemble a Material app.

## Current converter benchmarks

### Wise Currency Converter

https://wise.com/us/currency-converter/

Observed current hierarchy:

- amount;
- source/destination;
- rate/result;
- chart/history;
- secondary rate-tracking actions.

### Xe Currency Converter

https://www.xe.com/currencyconverter/

Observed current hierarchy:

- amount;
- From/To;
- converted result;
- rate metadata;
- history/chart and transfer-related secondary actions.

### Xe Currency Charts

https://www.xe.com/currencycharts/

Observed pattern:

- pair selection;
- period selection;
- simple historical line visualization;
- informational-rate disclaimer/context.

Quiet Atlas conclusion:

- match the low-friction conversion mental model users already know;
- differentiate **after** the trusted result with local meaning, payment context, historical storytelling and provenance;
- do not copy competitors' transfer/upsell hierarchy because our product goal is different.

## Design-source precedence

When guidance conflicts:

1. task correctness and user trust;
2. WCAG/accessibility requirements;
3. platform-native expectations for mobile;
4. product UX contract;
5. Quiet Atlas visual language;
6. trends/aesthetic inspiration.

A design trend never overrides clarity, provenance or accessibility.


# Frontend Technology References

Research reviewed: **2026-09-19**.

The selected frontend stack and rationale live in:

- [Frontend technology strategy](13_FRONTEND_TECHNOLOGY_STRATEGY.md)
- [Web frontend architecture](14_WEB_FRONTEND_ARCHITECTURE.md)
- [Mobile frontend architecture](15_MOBILE_FRONTEND_ARCHITECTURE.md)

Versions must be re-checked immediately before implementation.

## Node.js

- Release status / LTS lines  
  https://nodejs.org/en/about/previous-releases
- Node 24 archive  
  https://nodejs.org/en/download/archive/v24

Current decision:

- Node 24 LTS for both web build tooling and mobile tooling;
- do not default to Node 26 Current merely because it is newer.

## Vite

- Vite 8 announcement  
  https://vite.dev/blog/announcing-vite8
- Vite 8.1 announcement  
  https://vite.dev/blog/announcing-vite8-1
- Backend integration / manifest  
  https://vite.dev/guide/backend-integration
- Build manifest option  
  https://vite.dev/config/build-options.html#build-manifest

Key architecture reference:

Vite explicitly documents traditional-backend integration through `build.manifest` and a backend-rendered asset mapping.

The project uses this contract directly rather than requiring a Django-specific bridge library.

## TypeScript

- TypeScript 5.9 release notes  
  https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html
- TSConfig reference  
  https://www.typescriptlang.org/tsconfig/

Use strict type checking.

Vite transpilation does not replace `tsc --noEmit`.

## HTMX

- Documentation  
  https://htmx.org/docs/
- Reference  
  https://htmx.org/reference/
- Changelog  
  https://htmx.org/changelog/
- `hx-sync`  
  https://htmx.org/attributes/hx-sync/
- `hx-push-url`  
  https://htmx.org/attributes/hx-push-url/

Current policy:

- production uses stable HTMX 2.x;
- HTMX 4 beta is not selected until stable and migration value is reviewed;
- use synchronization/cancellation rules for trust-critical conversion updates.

## django-htmx

- Documentation  
  https://django-htmx.readthedocs.io/
- Installation / supported Django versions  
  https://django-htmx.readthedocs.io/en/stable/installation.html
- Middleware / `request.htmx` / Vary guidance  
  https://django-htmx.readthedocs.io/en/latest/middleware.html
- Changelog  
  https://django-htmx.readthedocs.io/en/latest/changelog.html

Current documentation confirms Django 5.2 support and keeps htmx 2 as the default while htmx 4 remains beta.

## django-template-partials

- PyPI / project documentation  
  https://pypi.org/project/django-template-partials/

The package supports Django 5.2 and is used only as a compatibility bridge.

Django 6.0 added built-in template partials; migrate when the backend version is deliberately upgraded.

## Tailwind CSS

- Vite installation  
  https://tailwindcss.com/docs/installation/using-vite
- Compatibility / browser baseline  
  https://tailwindcss.com/docs/compatibility
- Theme variables  
  https://tailwindcss.com/docs/theme
- Responsive/container queries  
  https://tailwindcss.com/docs/responsive-design
- Tailwind v4 architecture  
  https://tailwindcss.com/blog/tailwindcss-v4

Current v4 baseline:

- Chrome 111+
- Safari 16.4+
- Firefox 128+

Tailwind recommends its dedicated Vite plugin for Vite-based projects.

## Native web platform references

### Dialog

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/dialog

### Details / Summary

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/details

### Date input

https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/input/date

### Intl

https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl

### Web Share

https://developer.mozilla.org/en-US/docs/Web/API/Web_Share_API

### View Transitions

https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API

Native features are preferred when they already meet the interaction need.

Newer APIs such as View Transitions remain progressive enhancements, never correctness dependencies.

## GitHub combobox navigation

- Repository/package  
  https://github.com/github/combobox-nav

Use only as a focused ARIA keyboard-navigation primitive for the enhanced country/currency picker.

The project retains ownership of markup, server search, visual styling, selection and accessibility tests.

## Chart.js

- Documentation  
  https://www.chartjs.org/docs/latest/
- Accessibility  
  https://www.chartjs.org/docs/latest/general/accessibility.html

Use only on historical web chart surfaces and lazy-load it.

Canvas visualization always has text/table alternatives.

## Inter / Fontsource

- Fontsource Variable fonts  
  https://fontsource.org/docs/getting-started/variable
- Inter package  
  https://fontsource.org/fonts/inter

Fonts are bundled/self-hosted through Vite.

No runtime Google Fonts/CDN request.

## Heroicons

- Heroicons  
  https://heroicons.com/
- Repository  
  https://github.com/tailwindlabs/heroicons

Use a small local subset as static SVG template partials.

Do not ship an icon runtime merely for a handful of glyphs.

## Biome

- Biome v2  
  https://biomejs.dev/blog/biome-v2/
- Language support  
  https://biomejs.dev/internals/language-support/

Biome v2 supports TypeScript 5.9.

Use it for JS/TS/JSON linting/formatting, with `tsc` retained for authoritative TypeScript type checking.

## djLint

- Documentation  
  https://djlint.com/
- Repository  
  https://github.com/djlint/djLint

Use for Django template formatting/linting.

## Playwright

- Documentation  
  https://playwright.dev/docs/intro
- Accessibility testing  
  https://playwright.dev/docs/accessibility-testing

Playwright's official accessibility guide uses `@axe-core/playwright` and explicitly notes that automated scans do not replace manual accessibility review.

## React Native

- Documentation  
  https://reactnative.dev/docs/getting-started
- React Native 0.87 release  
  https://reactnative.dev/blog/2026/08/11/react-native-0.87

RN 0.87 being standalone-stable does not imply that an Expo app should mix it into an older Expo SDK.

Use the Expo compatibility matrix.

## Expo SDK

- SDK 57  
  https://expo.dev/sdk/57
- SDK 57 release notes  
  https://expo.dev/changelog/sdk-57
- Version matrix  
  https://docs.expo.dev/versions/latest/

At the research date:

```text
Expo SDK 57
React Native 0.86
React 19.2.3
Minimum Node 22.13.x
```

The project uses Node 24 LTS.

## Expo Router

- Router API  
  https://docs.expo.dev/versions/latest/sdk/router/
- Testing  
  https://docs.expo.dev/router/reference/testing/

Use stable Stack/Tabs/navigation APIs.

ExperimentalStack is not a production dependency.

## Expo UI

- Expo UI overview  
  https://docs.expo.dev/versions/latest/sdk/ui/
- Cross-platform DateTimePicker replacement  
  https://docs.expo.dev/versions/latest/sdk/ui/drop-in-replacements/datetimepicker/

Expo UI's date picker maps to modern native SwiftUI and Material 3/Jetpack Compose controls.

## Expo SQLite

- Documentation  
  https://docs.expo.dev/versions/latest/sdk/sqlite/
- Storage guidance  
  https://docs.expo.dev/develop/user-interface/store-data/

SQLite data persists across app restarts and is selected for explicit durable offline product data.

## Expo Localization

- API  
  https://docs.expo.dev/versions/latest/sdk/localization/
- Localization guide  
  https://docs.expo.dev/guides/localization/

Use with standard `Intl` for locale-aware presentation.

Do not equate device locale with the user's explicit home currency preference.

## Expo SecureStore

- Documentation  
  https://docs.expo.dev/versions/latest/sdk/securestore/

Introduce only when authentication/token storage exists.

Do not use SecureStore as a general application database.

## react-native-svg

- Expo documentation  
  https://docs.expo.dev/versions/latest/sdk/svg/

Selected for the small project-owned mobile historical line chart.

No full native chart framework is required by the current design.

## openapi-typescript / openapi-fetch

- openapi-typescript documentation  
  https://openapi-ts.dev/
- openapi-fetch  
  https://openapi-ts.dev/openapi-fetch/

Use generated backend schema types plus the small Fetch-based typed client.

Do not hand-maintain duplicate mobile endpoint DTOs.

## TanStack Query

- React Native guide  
  https://tanstack.com/query/latest/docs/framework/react/react-native
- Network modes  
  https://tanstack.com/query/latest/docs/framework/react/guides/network-mode

Use for active remote state, network lifecycle, cancellation and in-memory caching.

Durable offline product state remains explicit in Expo SQLite.

## Expo/Jest/React Native Testing Library

- Expo unit testing  
  https://docs.expo.dev/develop/unit-testing/
- Expo Router testing utilities  
  https://docs.expo.dev/router/reference/testing/

Use:

- Jest;
- jest-expo;
- @testing-library/react-native.

Do not overuse snapshots as the primary UI correctness signal.

## Maestro

- Expo E2E with Maestro  
  https://docs.expo.dev/tutorial/cicd/e2e-tests/
- EAS workflow example  
  https://docs.expo.dev/eas/workflows/examples/e2e-tests/

Use for selected high-value native end-to-end flows.

Cloud EAS workflow cadence can be adjusted for cost/maturity; local Maestro remains useful.


# Backend Architecture References

Research reviewed: **2026-09-19**.

The detailed backend contracts live in:

- [Backend system design](16_BACKEND_SYSTEM_DESIGN.md)
- [Information flow and request lifecycles](17_INFORMATION_FLOW_AND_REQUEST_LIFECYCLES.md)
- [Application services and domain orchestration](18_APPLICATION_SERVICES_AND_DOMAIN_ORCHESTRATION.md)
- [Data consistency, caching and concurrency](19_DATA_CONSISTENCY_CACHING_AND_CONCURRENCY.md)
- [API, security, observability and operations](20_API_SECURITY_OBSERVABILITY_AND_OPERATIONS.md)
- [Backend scenario catalog](21_BACKEND_SCENARIO_CATALOG.md)
- [Data import, scheduled jobs and maintenance](22_DATA_IMPORT_JOBS_AND_MAINTENANCE.md)

## Django transactions

https://docs.djangoproject.com/en/5.2/topics/db/transactions/

Key implementation guidance:

- Django uses autocommit by default;
- transaction.atomic() defines explicit atomic sections;
- long-running transactions have a cost;
- transaction.on_commit() is designed for work such as cache invalidation/background actions after successful commit;
- catching DB exceptions around an atomic boundary is safer than hiding them inside a broken transaction.

Project conclusion:

- no global ATOMIC_REQUESTS;
- short explicit write transactions;
- no external HTTP while a transaction is open;
- after-commit cache invalidation.

## Django asynchronous support

https://docs.djangoproject.com/en/5.2/topics/async/

Django 5.2 supports asynchronous queries and views in many areas, but its documentation explicitly states that transactions do not yet work in async mode and recommends wrapping transactional work in a synchronous function when needed.

Project conclusion:

- synchronous backend request model initially;
- do not add async views for novelty;
- revisit only for measured async workloads.

## Django QuerySet locking

https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update

Important behavior:

- select_for_update locks selected rows until transaction end on supported DBs;
- evaluating it outside a transaction on PostgreSQL raises TransactionManagementError;
- TestCase transaction wrapping can hide incorrect usage, so lock behavior needs TransactionTestCase/real transaction testing.

Project conclusion:

- pessimistic locking is exceptional;
- concurrency tests use PostgreSQL semantics.

## Django constraints

https://docs.djangoproject.com/en/5.2/ref/models/constraints/

Use:

- CheckConstraint;
- UniqueConstraint;
- conditional/functional constraints where a durable invariant justifies them.

Project conclusion:

- database constraints protect race-sensitive durable invariants;
- application validation improves user feedback but does not replace DB guarantees.

## Django cache framework

https://docs.djangoproject.com/en/5.2/topics/cache/

Relevant guidance:

- cache APIs include add/get_or_set/get_many/set_many/delete/touch;
- LocMemCache is process-local and is not a strong production shared-cache choice;
- cache backends are accessed through Django's abstraction.

Project conclusion:

- cache is optimization/fallback, not domain authority;
- no correctness depends on LocMemCache cross-worker behavior;
- production backend remains configurable.

## Django cache/Vary utilities

https://docs.djangoproject.com/en/5.2/ref/utils/#module-django.utils.cache

Relevant for full-document vs HTMX fragment responses.

The Vary header defines request headers that affect a cached representation.

Project conclusion:

- dual full/fragment views vary on HX-Request when cacheable.

## Django management commands

https://docs.djangoproject.com/en/5.2/howto/custom-management-commands/

Django explicitly supports custom management commands and notes they are useful for standalone/periodic scheduled work.

Project conclusion:

- scheduled imports begin as management commands + platform scheduler;
- command handle() remains a thin transport over reusable import services.

## Django database optimization

https://docs.djangoproject.com/en/5.2/topics/db/optimization/

Use query profiling and appropriate select_related/prefetch_related instead of guessing.

Project conclusion:

- query shape drives indexes/prefetch;
- focused query-count regression tests only where N+1 risk is real.

## Django PostgreSQL database notes

https://docs.djangoproject.com/en/5.2/ref/databases/

Review current PostgreSQL/psycopg requirements and connection behavior when implementation/deployment begins.

Django has supported psycopg-based connection pooling in recent 5.x releases, but pooling remains a deployment decision based on worker/connection constraints.

Do not add pooling blindly.

## Django logging

https://docs.djangoproject.com/en/5.2/howto/logging/

Use namespaced Python/Django loggers and production structured logging configuration.

Project conclusion:

- request/provider/cache/import events use consistent structured fields;
- secrets/private payloads are not logged.

## Django system checks

https://docs.djangoproject.com/en/5.2/topics/checks/

Django's extensible system-check framework can detect project configuration issues and is run by management commands; deployment should invoke checks explicitly.

Project conclusion:

- use manage.py check --deploy;
- add custom checks only for meaningful project-specific configuration invariants.

## Django deployment checklist

https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

Re-run immediately before deployment.

Production hardening follows Django's deployment checklist rather than a custom security folklore list.

## Django REST Framework schemas

https://www.django-rest-framework.org/api-guide/schemas/

DRF's built-in OpenAPI generation is deprecated.

DRF recommends third-party schema packages.

## DRF API documentation recommendations

https://www.django-rest-framework.org/topics/documenting-your-api/

DRF currently identifies drf-spectacular as the recommended OpenAPI 3 replacement.

## drf-spectacular

https://drf-spectacular.readthedocs.io/en/latest/

Use for:

- OpenAPI 3 generation;
- explicit schema annotations where introspection is insufficient;
- deterministic client-generation contract.

At the research date, current documentation supports Django 5.2 and contemporary DRF releases.

## DRF versioning

https://www.django-rest-framework.org/api-guide/versioning/

Project uses a URL namespace/version boundary under /api/v1/.

Do not scatter version-condition business logic throughout application services.

## DRF throttling

https://www.django-rest-framework.org/api-guide/throttling/

Important documented limitations:

- DRF throttling is intended for policy/basic over-use protection;
- it is not a security/DDoS control;
- built-in cache-based throttles can be fuzzy under concurrency.

Project conclusion:

- use DRF throttling as fair-use protection;
- use platform/edge controls if hostile abuse becomes a real concern.

## DRF pagination

https://www.django-rest-framework.org/api-guide/pagination/

Paginate only collections that can actually grow.

Bounded country/currency metadata can remain complete if payload size supports offline picker value.

## PostgreSQL transaction isolation

https://www.postgresql.org/docs/current/transaction-iso.html

Review transaction isolation and retry behavior before introducing stronger-than-default isolation.

Project conclusion:

- default isolation + constraints/explicit conflicts is sufficient initially;
- do not globally enable SERIALIZABLE.

## PostgreSQL explicit locking

https://www.postgresql.org/docs/current/explicit-locking.html

Use row locks only for demonstrated contention/invariants and keep locked transactions short.

## OpenTelemetry Python

https://opentelemetry.io/docs/languages/python/

Optional future production observability.

Initial backend does not depend on OpenTelemetry; structured logs/request IDs/provider/cache signals are sufficient for the first deployment.

## Backend source precedence

When backend guidance conflicts:

1. correctness and source/provenance integrity;
2. Django/PostgreSQL documented semantics;
3. security/privacy;
4. explicit product/domain contracts;
5. operational simplicity;
6. performance measurements;
7. architectural fashion.

A more sophisticated pattern is not better if it introduces a second source of truth or hides control flow.


# Media and Generative Image References

Research reviewed: **2026-09-19**.

## Django staticfiles

https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/

Use for files that belong to the code/release:

- CSS;
- JavaScript;
- logo;
- icons;
- versioned UI art.

Do not use staticfiles as the growing editorial/historical media library.

## Django file storage

https://docs.djangoproject.com/en/5.2/ref/files/storage/

Django's Storage API is the abstraction boundary for media files.

Project conclusion:

- FileSystemStorage for local development;
- object storage through a compatible backend in production;
- MediaAsset stores metadata/storage key rather than binary image data in PostgreSQL.

## django-storages S3 backend

https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html

## django-storages S3-compatible providers

https://django-storages.readthedocs.io/en/latest/backends/s3_compatible/

Useful if deployment chooses Amazon S3, Cloudflare R2, Backblaze B2 or another S3-compatible service.

The media domain stays vendor-neutral.

## Wikimedia Commons ImageInfo API

https://www.mediawiki.org/wiki/API:Imageinfo/en

Can retrieve file information/upload history and is a useful ingestion metadata source.

## Wikimedia Commons reuse guidance

https://commons.wikimedia.org/wiki/Commons:Contact_us/Reuse

https://commons.wikimedia.org/wiki/Commons:First_steps/Reuse

https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia/licenses/en

Important:

- individual files have their own licence requirements;
- attribution/licence terms must be followed;
- Commons itself does not guarantee every description/licensing statement is error-free;
- approved media should retain canonical source/creator/licence metadata.

Wikimedia's reuse guidance notes that downloading a file for reuse is a normal supported approach; this aligns with the project's managed-copy strategy after rights review.

## Europeana APIs

https://www.europeana.eu/en/apis

Europeana exposes Search, Record and IIIF APIs for cultural-heritage discovery/metadata.

Use in ingestion/editorial workflows, not the user request path.

## Europeana metadata and rights

https://www.europeana.eu/eu/rights/europeana-data-sources

Europeana descriptive metadata is broadly reusable under CC0 terms, but this does **not** mean every underlying digital object/image has unrestricted reuse.

The media pipeline must inspect the object's own rights statement.

## OpenAI image generation

https://openai.com/index/image-generation-api/

OpenAI documents server-side image generation with moderation controls and usage-based pricing.

Project conclusion:

- suitable benchmark candidate;
- variable generation cost reinforces pre-generation/caching rather than generation on every selector change;
- provider is not selected permanently until implementation-time comparison.

## Stability AI Platform

https://platform.stability.ai/docs/api-reference

https://platform.stability.ai/pricing

Stability exposes multiple image-generation quality/speed tiers and credit-based pricing.

At the research date, 1 Platform API credit is documented as USD 0.01, with generation services priced by model/tier.

Project conclusion:

- suitable benchmark candidate for controlled editorial generation;
- never called directly from browser/mobile.

## Google Vertex AI image model lifecycle

https://docs.cloud.google.com/vertex-ai/generative-ai/docs/release-notes

Google's 2026 release notes show active image-model endpoint deprecations/migrations across Imagen/Gemini generations.

Project conclusion:

- image-provider identity/model names must remain isolated behind an adapter;
- published assets are not regenerated simply because provider model lifecycle changes.

## Media source precedence

When choosing an image:

1. factual relevance and authenticity;
2. rights/licence clarity;
3. temporal/geographic accuracy;
4. accessibility/attribution;
5. visual quality;
6. performance;
7. novelty.

AI visual novelty never outranks historical truth.


# AI Architecture References

Research reviewed: **2026-09-19**.

## OpenAI current model catalog

https://developers.openai.com/api/docs/models

Current guidance identifies:

- GPT-5.6 Sol as flagship professional model;
- GPT-5.6 Terra as balanced intelligence/cost tier;
- GPT-5.6 Luna as cost-sensitive/high-volume tier;
- GPT-Image-2.5 Sunburst as the most capable image-generation/editing model;
- GPT-Image-2.5 Flare as the fast high-quality image model.

Project conclusion:

- use capability-tier routing rather than one expensive model everywhere.

## GPT-5.6 Terra

https://developers.openai.com/api/docs/models/gpt-5.6-terra

Current documented pricing at research date:

- input: USD 2 / 1M tokens;
- cached input: USD 0.20 / 1M;
- output: USD 12 / 1M.

Supports:

- Responses;
- function calling;
- Structured Outputs;
- image input;
- reasoning levels.

Project use:

- primary editorial structured generation.

## GPT-5.6 Luna

https://developers.openai.com/api/docs/models/gpt-5.6-luna

Current documented pricing at research date:

- input: USD 0.20 / 1M tokens;
- cached input: USD 0.02 / 1M;
- output: USD 1.20 / 1M.

Project use:

- narrow low-risk/high-volume structured tasks only.

## GPT-5.6 Sol

https://developers.openai.com/api/docs/models

Current documented pricing at research date:

- input: USD 4 / 1M tokens;
- cached input: USD 0.40 / 1M;
- output: USD 20 / 1M.

Project use:

- rare audit/eval escalation rather than default generation.

## OpenAI Structured Outputs

https://developers.openai.com/api/docs/guides/structured-outputs

OpenAI recommends Structured Outputs over legacy JSON mode when supported.

Structured Outputs constrain model responses to a supplied JSON Schema.

Project conclusion:

- use strict structured output for application-integrated text generation;
- still run semantic/factual validators after schema parsing.

## OpenAI Responses API

https://developers.openai.com/api/reference

The Responses API supports text/image inputs, structured text output and tools.

Project conclusion:

- use Responses for bounded structured text capabilities;
- do not enable web/file/tool orchestration in P1 editorial workflows.

## OpenAI prompt caching

https://developers.openai.com/api/docs/guides/prompt-caching

GPT-5.6 supports current prompt-cache controls.

Project conclusion:

- stable prompt prefixes can benefit from caching later;
- cache is an optimization, not correctness dependency.

## GPT-Image-2.5 Sunburst

https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst

OpenAI currently describes Sunburst as its most capable image-generation/editing model.

Project use:

- high-value final/featured image generation or precise edit.

## OpenAI image generation API

https://developers.openai.com/api/reference

The current Image API supports GPT-Image-2.5 Sunburst/Flare, multiple quality settings, common output formats and flexible supported dimensions.

Project conclusion:

- Image API is the simplest path for one-shot editorial generation;
- Responses image tooling is reserved for a genuinely multi-step multimodal workflow.

## OpenAI moderation

https://developers.openai.com/api/reference

https://developers.openai.com/api/docs/models/omni-moderation-latest

`omni-moderation-latest` accepts text and image inputs and is the current capable multimodal moderation model.

Project conclusion:

- moderation is an additional safety layer;
- it is not historical truth or licensing validation.

## OpenAI API data/privacy

https://openai.com/business-data/

https://platform.openai.com/docs/models/default-usage-policies-by-endpoint

Current OpenAI business/API policy states API inputs/outputs are not used to train or improve models by default unless the customer explicitly opts in.

Provider retention/abuse-monitoring behavior can still apply depending on endpoint/account controls.

Project conclusion:

- minimize AI payloads;
- P0/P1 editorial AI uses public/curated product content only;
- do not promise zero retention unless deployment configuration actually provides it.

## Gemini Interactions API

https://ai.google.dev/gemini-api/docs/interactions-overview

Google currently recommends the Interactions API for new Gemini applications and supports structured outputs and multimodal workflows.

## Gemini structured output

https://ai.google.dev/gemini-api/docs/structured-output

Gemini supports schema-constrained JSON, while documentation still recommends application-level value validation.

Project conclusion:

- viable benchmark/fallback provider for structured generation;
- not a parallel production dependency initially.

## Gemini image generation

https://ai.google.dev/gemini-api/docs/image-generation

Current Gemini image models support text-to-image and image editing with configurable formats/sizes.

Project conclusion:

- viable image-provider benchmark;
- provider lifecycle remains isolated behind the project's ImageGenerator capability.

## Anthropic tool/JSON-schema patterns

https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview

Claude supports tool inputs described with JSON Schema and strong structured tool workflows.

Project conclusion:

- strong text benchmark candidate;
- not selected as the initial unified provider because this project also needs a first-party image generation stack.

## Anthropic model lifecycle

https://docs.anthropic.com/en/docs/about-claude/model-deprecations

The current deprecation history demonstrates why provider model IDs must remain configuration and why model upgrades need eval gates.

## AI source precedence

When an AI design choice conflicts:

1. product/domain truth and provenance;
2. deterministic validation/security/privacy;
3. graceful AI-free fallback;
4. eval-measured quality;
5. operational cost/latency;
6. provider convenience;
7. novelty.

AI capability breadth never outranks trust.


# Zero-Cost Portfolio AI References

Research reviewed: **2026-09-19**.

## Gemini Developer API pricing

https://ai.google.dev/gemini-api/docs/pricing

Current pricing page lists Free Tier input/output as free of charge for multiple text models including Gemini 3.1 Flash-Lite.

Project decision:

- use Gemini 3.1 Flash-Lite for the one live recruiter-visible text feature;
- do not attach paid fallback to the public demo.

The same pricing page lists Gemini 3.1 Flash Image and Flash Lite Image with **Free Tier: Not available**.

Project decision:

- zero runtime image-generation calls;
- images are sourced/pre-generated/stored.

## Gemini 3.1 Flash-Lite

https://ai.google.dev/gemini-api/docs/models/gemini-3.1-flash-lite

Google describes it as a low-latency, cost-effective model for lightweight/high-volume tasks and documents Structured Outputs support.

Project use:

- bounded “Explain this” structured explanation over already verified facts.

## Gemini rate limits

https://ai.google.dev/gemini-api/docs/rate-limits

Google documents RPM/TPM/RPD rate limiting, but actual limits vary by model/project/account and are visible in AI Studio.

Project conclusion:

- do not hard-code a provider daily quota as a business invariant;
- handle 429 with cache/deterministic fallback;
- add an application-level live-call ceiling.

## Gemini API keys

https://ai.google.dev/gemini-api/docs/api-key

Current Gemini API documentation requires current restricted/auth-key handling and rejects unrestricted standard keys during the 2026 migration.

Project conclusion:

- server-only key;
- never browser/mobile/public environment.

## Free-tier data handling

The Gemini pricing page marks Free Tier content as used to improve Google products.

Project conclusion:

- send public/non-sensitive data only;
- no user profile/private trip/personal location data to free-tier AI.

## OpenRouter free plan

https://openrouter.ai/pricing

https://openrouter.ai/openrouter/free/

OpenRouter currently offers free models and a free plan with a documented request limit.

Project conclusion:

- useful for local experiments only;
- not automatic production fallback because free model availability/routing can change.

## Hugging Face Inference Providers pricing

https://huggingface.co/docs/inference-providers/en/pricing

Hugging Face currently provides only a very small monthly free credit for free accounts.

Project conclusion:

- not competitive as the primary zero-cost runtime path for this demo.
