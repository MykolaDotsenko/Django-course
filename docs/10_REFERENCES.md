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
