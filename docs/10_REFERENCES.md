# Official References

These are preferred primary references for implementation decisions. Version-match documentation before each implementation PR.

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
- Security guidance is included in the official docs  
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

Relevant API capabilities:

- latest rates;
- single pair rates;
- historical dates;
- time series;
- provider filtering;
- provider attribution;
- currencies including legacy scope.

## Accessibility

- WCAG 2.2 Recommendation  
  https://www.w3.org/TR/WCAG22/
- WCAG overview  
  https://www.w3.org/WAI/standards-guidelines/wcag/
- What's new in 2.2  
  https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/

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

Prefer ISO-style stable identifiers in the domain. Where external country metadata is used, import/normalize only fields the product actually owns and display.

Any third-party country-data provider must be replaceable through import/normalization boundaries and must not become an implicit domain schema.
