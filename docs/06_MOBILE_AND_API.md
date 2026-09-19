# Mobile and API

## 1. Mobile strategy

The mobile app is a **separate React Native client**, not a wrapped web view.

Selected delivery stack at the 2026-09-19 research point:

- Expo SDK 57 stable;
- React Native 0.86.x through the Expo compatibility matrix;
- React 19.2.3;
- TypeScript strict;
- Expo Router;
- @expo/ui selectively for native controls;
- openapi-typescript + openapi-fetch;
- TanStack Query for remote server state;
- Expo SQLite for durable offline product data;
- React Native StyleSheet + typed Quiet Atlas tokens;
- react-native-svg for the intentionally small historical line chart;
- the Django backend as the source of truth.

The standalone React Native 0.87 release is newer than Expo 57's supported RN line, but the product deliberately prefers the current stable Expo compatibility matrix over mixing framework versions.

Re-check the stable Expo matrix immediately before mobile implementation. Do not select a beta SDK merely for a higher version number.

Detailed implementation rules live in `15_MOBILE_FRONTEND_ARCHITECTURE.md`.

## 2. Mobile product goal

The mobile client optimizes the same domain for travel conditions:

- fast one-hand conversion;
- saved pairs;
- cached destination context;
- explicit offline/stale behaviour;
- later trip budget access.

The mobile UI does not need to mirror the desktop split-screen layout.

## 3. Suggested mobile navigation

```text
Convert
Explore
Trips
Saved
```

P0 mobile can ship only Convert + Saved if that keeps the first release focused.

## 4. API boundary

Use Django REST Framework for the mobile API.

The web UI does **not** consume this JSON API. Web requests remain Django templates + HTMX.

This prevents the common anti-pattern:

```text
Django -> JSON -> JavaScript -> HTML
```

when Django can return the HTML directly.

## 5. Versioning

All mobile endpoints live under:

```text
/api/v1/
```

Breaking contract changes require a new API version or an explicit backward-compatibility strategy.

## 6. Core P0 endpoints

### GET /api/v1/countries/
Returns only fields required by the mobile client.

### GET /api/v1/currencies/
Returns supported current currencies.

### POST /api/v1/conversions/quote/

Request:

```json
{
  "amount": "100.00",
  "base": "EUR",
  "quote": "JPY",
  "source_country": "FI",
  "destination_country": "JP"
}
```

Response:

```json
{
  "amount": "100.00",
  "base": "EUR",
  "quote": "JPY",
  "rate": "174.500000",
  "result": "17450",
  "effective_at": "2026-09-18",
  "provider": "frankfurter",
  "stale": false
}
```

Numbers representing money/rates are serialized as decimal strings.

### GET /api/v1/destinations/JP/context/
Returns payment context and available typical-price items.

## 7. Authentication

Basic conversion does not require authentication.

When accounts are added:

- use an explicit mobile authentication design;
- do not reuse browser session assumptions accidentally;
- store tokens/secrets using platform-appropriate secure storage;
- keep refresh/revocation semantics documented.

Authentication implementation is deliberately deferred until saved cross-device state requires it.

## 8. Offline semantics

Mobile may cache:

- last successful rates;
- supported country/currency metadata;
- destination payment context;
- published typical-price context;
- saved pairs;
- trip budgets.

Offline display rules:

1. show last update timestamp;
2. label the rate as cached/offline;
3. never imply that stale data is live;
4. allow manual retry;
5. prevent data from one pair appearing as another pair's result.

## 9. API errors

Use stable machine-readable error codes plus human-readable detail.

Example:

```json
{
  "code": "rate_unavailable",
  "detail": "The EUR/JPY reference rate is temporarily unavailable.",
  "retryable": true,
  "fields": {},
  "request_id": "01..."
}
```

Do not make the mobile client parse English text to decide behaviour.

## 10. API schema

Use **drf-spectacular** for deterministic OpenAPI 3 schema generation.

Django REST Framework's built-in OpenAPI schema generation is deprecated, so the mobile contract must not depend on it.

The schema is a CI contract:

```text
Django/DRF serializers + views
        ↓
drf-spectacular OpenAPI
        ↓
schema validation
        ↓
openapi-typescript
        ↓
mobile generated types
```

Generated clients/types must not obscure basic HTTP behavior or application error semantics.

## 11. Mobile testing

Minimum:

- unit tests for local formatting/cache logic;
- component tests for critical states;
- API contract tests against fixtures;
- one E2E smoke path on supported platforms when CI cost is reasonable.

## 12. Shared business rules

Do not duplicate:

- conversion arithmetic;
- rate freshness semantics;
- provider normalization;
- country/currency validity;
- price-context trust rules.

Those belong to Django/domain code.

The client owns:

- presentation;
- navigation;
- optimistic local interaction where safe;
- local cache lifecycle;
- device capability integration.


## 13. Historical conversion on mobile

The mobile client supports the same historical semantics as web.

The conversion request may include:

```json
{
  "amount": "100.00",
  "base": "FIM",
  "quote": "USD",
  "date": "1998-06-15",
  "source_country": "FI"
}
```

The response distinguishes:

- requested date;
- effective observation date;
- observation granularity;
- historical/current mode;
- previous-observation fallback;
- provider/source attribution.

The client must not reconstruct these semantics independently.

## 14. Historical mobile UX

Entry point:

```text
Rate date
Latest available >
```

Historical selection:

```text
Latest available
Historical date
[date picker]
```

Result:

```text
100 FIM ≈ X USD

Historical reference
Observation 15 Jun 1998
[See the story]
```

When requested/effective dates differ, both are visible.

## 15. Archived currencies on mobile

Archived currencies are discoverable only in historical mode or explicit historical search.

The API provides metadata required to:

- label archived currencies;
- expose supported/provider date coverage;
- avoid cluttering normal current conversion.

Country/date historical-currency suggestions come from server-normalized domain data.

## 16. Story contract

Storytelling may be delivered as structured chapters rather than one opaque prose blob.

Concept:

```json
{
  "chapters": [
    {
      "kind": "currency_era",
      "title": "Finland used the markka",
      "body": "...",
      "sources": ["..."]
    }
  ]
}
```

Benefits:

- native presentation flexibility;
- accessibility;
- localization;
- source display;
- deterministic fallback.

Do not force the mobile client to parse Markdown/HTML story blobs.

## 17. Offline historical data

A previously fetched historical quote is particularly cache-friendly.

Offline display still exposes:

- requested date;
- effective date;
- source;
- cached/offline status.

An uncached historical pair/date returns an explicit offline-unavailable state.

## 18. Mobile temporal integrity

The mobile app must not:

- treat requested date as effective date;
- show a current quote for an archived currency;
- attach current local prices to a historical story without current-context labeling;
- infer investment return from Then & now;
- generate story facts locally without server-provided sourced context.


## 19. Mobile state architecture

State ownership is deliberately split.

### React local state

Owns transient interface state:

- input drafts;
- picker search;
- sheet/dialog state;
- local presentation toggles.

### TanStack Query

Owns active remote server state:

- conversion quote;
- destination context;
- historical series;
- story;
- server-backed saved state later.

### Expo SQLite

Owns durable offline product data:

- exact-key cached quotes;
- country/currency metadata;
- destination context snapshots;
- favourites;
- recent conversions;
- trip drafts later.

Do not use Redux/Zustand merely as an additional middle layer.

## 20. OpenAPI-generated client

The backend OpenAPI schema is the mobile type source.

Use:

- `openapi-typescript` to generate endpoint types;
- `openapi-fetch` to make typed requests.

Generated schema files are never edited manually.

CI should detect schema/type drift.

## 21. Stable Expo rule

As of this documentation update:

```text
Expo 57 stable
→ React Native 0.86
→ React 19.2.3
```

Expo's next SDK line is not selected until stable.

React Native standalone releases do not override the Expo compatibility matrix.

## 22. Native control policy

Prefer current platform-native controls where they reduce custom behavior.

Historical date selection uses the Expo UI DateTimePicker, backed by:

- SwiftUI on iOS;
- Material 3 / Jetpack Compose on Android.

Large searchable currency/country selection remains a dedicated product search screen rather than a small native picker.

## 23. Mobile chart policy

Historical chart:

```text
react-native-svg
+ project-owned LineChart
```

No full chart framework initially.

The chart remains supplemental to text summaries and accessible values.

## 24. Mobile testing stack

Use:

- Jest + jest-expo;
- @testing-library/react-native;
- Expo Router testing utilities where navigation integration matters;
- Maestro for high-value black-box E2E smoke flows.

Maestro cloud execution may be limited to selected PR/release workflows depending on cost and current EAS workflow maturity.


## 25. API application-service ownership

DRF is a transport layer.

A mobile request follows:

```text
serializer
→ typed command/query
→ same application use case used by web
→ domain/application result
→ response serializer
```

DRF serializers/views do not own:

- FX arithmetic;
- provider fallback;
- historical observation policy;
- source/provenance rules;
- trip transaction semantics.

This prevents web/mobile behavior drift.

## 26. API error contract

All expected mobile API failures use stable machine-readable codes.

Canonical envelope:

```json
{
  "code": "historical_out_of_coverage",
  "detail": "Historical data for this pair starts on 1972-01-03.",
  "retryable": false,
  "fields": {},
  "request_id": "01..."
}
```

The client may render `detail`, but behavior is driven by `code` and structured fields.

Unknown exceptions map to a generic server error and are correlated by `request_id`.

## 27. API versioning ownership

All mobile contracts live under:

```text
/api/v1/
```

Breaking transport changes require compatibility work or a new version.

Business/application services are not duplicated per version unless their semantics genuinely differ.

## 28. API throttling boundary

DRF throttling may provide anonymous/user fair-use limits.

It is not treated as exact security or DDoS protection.

If hostile public abuse becomes meaningful, enforce stronger limits at the platform/edge while keeping domain correctness independent from throttle counters.

## 29. Mobile ownership/concurrency rule

When authenticated resources ship:

- every object query is ownership-scoped server-side;
- IDs are not authorization;
- duplicate favourite writes are protected by database uniqueness;
- future multi-device Trip editing may use optimistic version conflicts;
- the mobile client handles `409 conflict` explicitly instead of silently overwriting newer server state.
