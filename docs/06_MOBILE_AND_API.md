# Mobile and API

## 1. Mobile strategy

The mobile app is a **separate React Native client**, not a wrapped web view.

Recommended delivery stack:

- React Native;
- TypeScript;
- Expo stable SDK compatible with the chosen React Native line;
- native navigation appropriate to Expo/RN;
- the Django backend as the source of truth.

Avoid pinning the mobile project to a raw React Native version before the Expo compatibility matrix is selected during implementation.

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
  "detail": "A live EUR/JPY rate is temporarily unavailable.",
  "retryable": true
}
```

Do not make the mobile client parse English text to decide behaviour.

## 10. API schema

Generate and validate an OpenAPI schema.

The mobile client can later derive types or fixtures from the schema, but generated clients should not obscure basic HTTP behaviour.

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
