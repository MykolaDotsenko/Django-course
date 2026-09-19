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
