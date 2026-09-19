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
