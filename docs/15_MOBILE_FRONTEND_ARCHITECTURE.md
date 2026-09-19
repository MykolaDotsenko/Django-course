# Mobile Frontend Architecture

Research date: **2026-09-19**.

This document is the implementation contract for the React Native mobile client.

The mobile app is not a web wrapper and not a second source of business truth.

It is a native travel-oriented presentation of the same Django domain.

---

# 1. Stable runtime decision

Current selected compatibility matrix:

```text
Expo SDK 57
React Native 0.86.x
React 19.2.3
Node 24 LTS
TypeScript strict
```

Why:

- Expo 57 is stable;
- Expo 57 officially targets RN 0.86;
- the Expo 58 line is pre-release/beta at this research point;
- no product feature requires a beta/canary runtime;
- stable integrated ecosystem beats chasing standalone RN version 0.87.

Before implementation begins, re-check the latest stable Expo matrix.

If Expo 58 or newer is stable then, upgrade only after dependency compatibility review.

---

# 2. Mobile architecture goal

Keep state ownership explicit:

```text
React component state
        ↓
screen-local UI only

TanStack Query
        ↓
online server state lifecycle

Expo SQLite
        ↓
durable offline product data

Django API
        ↓
business/domain source of truth
```

No general global state library is required.

---

# 3. Proposed mobile repository layout

Candidate:

```text
mobile/
├── app/
│   ├── _layout.tsx
│   ├── index.tsx
│   ├── convert/
│   ├── explore/
│   ├── saved/
│   └── trips/
│
├── src/
│   ├── api/
│   │   ├── client.ts
│   │   ├── schema.d.ts
│   │   ├── queries.ts
│   │   └── errors.ts
│   │
│   ├── components/
│   │   ├── AmountField.tsx
│   │   ├── CurrencyPicker.tsx
│   │   ├── ConversionResult.tsx
│   │   ├── DataFreshness.tsx
│   │   └── ...
│   │
│   ├── features/
│   │   ├── conversion/
│   │   ├── historical/
│   │   ├── culture/
│   │   ├── saved/
│   │   └── trips/
│   │
│   ├── storage/
│   │   ├── database.ts
│   │   ├── migrations.ts
│   │   ├── rates.ts
│   │   ├── destinations.ts
│   │   └── favourites.ts
│   │
│   ├── theme/
│   │   ├── tokens.ts
│   │   ├── typography.ts
│   │   └── useTheme.ts
│   │
│   ├── hooks/
│   ├── formatting/
│   └── testing/
│
├── __tests__/
├── .maestro/
├── app.json
├── eas.json
├── package.json
└── tsconfig.json
```

Feature folders should not become mini-frameworks.

---

# 4. Navigation — Expo Router

Use Expo Router.

Reasons:

- first-party Expo integration;
- file-based routes;
- native navigation primitives;
- predictable deep links;
- testing utilities;
- good fit for future shareable conversion/history links.

Use stable `Stack`/`Tabs` primitives.

Do **not** use ExperimentalStack/alpha navigation APIs in production.

---

# 5. Initial navigation shape

P0/P1:

```text
Convert
Explore
Saved
```

Trips appears when the trip feature ships.

Do not render an empty Trips tab just to match the long-term information architecture.

---

# 6. Mobile web is not a goal

The Django web application already exists.

The Expo app targets:

- iOS;
- Android.

Expo web compatibility may remain technically possible, but we do not duplicate our production web frontend through React Native Web.

One strong web frontend is enough.

---

# 7. TypeScript policy

Use strict TypeScript.

Adopt React Native's strict public TypeScript API through the supported Expo/RN matrix.

Enable:

- `strict`;
- `noUncheckedIndexedAccess`;
- `exactOptionalPropertyTypes`.

Avoid:

- `any`;
- deep React Native imports;
- untyped API JSON.

---

# 8. Styling decision

Use:

- React Native `StyleSheet`;
- typed Quiet Atlas design tokens;
- platform-aware components.

Do not use NativeWind initially.

Why:

- web and native layout semantics differ;
- Quiet Atlas design system is small and intentional;
- StyleSheet has no runtime dependency;
- platform variants remain explicit;
- avoids pretending CSS and native style capabilities are identical.

---

# 9. Shared design tokens

Share semantic values, not necessarily source files.

Conceptual token contract:

```ts
export const colors = {
  canvas: "#F6F7F3",
  surface: "#FFFFFF",
  textPrimary: "#14211D",
  textSecondary: "#596660",
  brand: "#0B6B61",
  history: "#345E7D",
  warning: "#9A5A13",
  danger: "#A93632",
  success: "#2D6A4F",
} as const;
```

Spacing/radius/typography also mirror Quiet Atlas semantics.

The mobile app may adjust physical sizing for native ergonomics.

---

# 10. Platform-native controls

Use `@expo/ui` selectively when it provides high-value native controls.

Examples:

- DateTimePicker;
- Picker where appropriate;
- platform-native buttons/controls only where design fit is good.

Do not rebuild native platform primitives simply to make them visually identical across iOS and Android.

Quiet Atlas defines hierarchy and tokens; platform conventions define some interaction details.

---

# 11. Historical date picker

Use:

```text
@expo/ui/community/datetime-picker
```

It provides modern:

- SwiftUI date picker on iOS;
- Material 3 / Jetpack Compose date picker on Android.

Reasons:

- native accessibility;
- locale;
- input behavior;
- less custom code;
- modern platform visual language.

The selected date still receives server validation.

---

# 12. Currency/country picker on mobile

Do not force a small native dropdown for hundreds of searchable options.

Use a dedicated search route/sheet:

```text
CurrencyPickerScreen
├── search field
├── recent choices
├── current currencies
├── historical currencies when mode requires
└── result rows
```

Server/domain supplies normalized dataset through Django API.

Filtering can happen locally after metadata download if the dataset is complete and small enough.

Historical/date-dependent validity remains server authoritative.

---

# 13. Local search strategy

Country/currency metadata is small and changes slowly.

Mobile can cache it locally.

Search can be local for:

- name;
- currency code;
- currency name.

Server still validates final combination/date.

Benefits:

- instant search;
- offline picker;
- no request per keystroke.

---

# 14. API contract generation

Backend publishes OpenAPI.

Use:

```text
openapi-typescript
```

to generate TypeScript types.

Generated file:

```text
src/api/schema.d.ts
```

Do not hand-copy serializer interfaces.

CI should fail when generated contract is out of date.

---

# 15. API client

Use:

```text
openapi-fetch
```

Reasons:

- generated OpenAPI typing;
- small runtime;
- native Fetch API;
- no Axios-specific abstraction;
- path/method/type safety.

Concept:

```ts
import createClient from "openapi-fetch";
import type { paths } from "./schema";

export const api = createClient<paths>({
  baseUrl: config.apiBaseUrl,
});
```

---

# 16. HTTP ownership

A small API wrapper owns:

- base URL;
- auth header later;
- request correlation header if needed;
- response error normalization;
- timeout/AbortController strategy.

It does not own business fallback rules.

---

# 17. TanStack Query

Use TanStack Query for **remote server state lifecycle**.

Good uses:

- country/currency metadata;
- current conversion request;
- destination context;
- story content;
- historical time series;
- authenticated saved/trip queries later.

It owns:

- request lifecycle;
- in-memory caching;
- refetch;
- cancellation;
- deduplication;
- stale timing.

It does not become the durable product database.

---

# 18. Query key design

Query keys must reflect semantics.

Examples:

```ts
["currencies", "current"]
["currencies", "all"]
["quote", base, quote, requestedDate]
["destination-context", countryCode]
["history", base, quote, from, to, group]
["story", base, quote, requestedDate, countryCode]
```

Do not key quote merely by:

```text
["quote"]
```

because stale data could cross pairs.

---

# 19. Query retry policy

Do not accept TanStack defaults blindly for financial-looking data.

Candidate:

- no retry for validation/unsupported/out-of-coverage;
- at most one bounded retry for transient request/network failure;
- server already has provider/cache fallback logic;
- avoid client retry storms.

Django is the provider-resilience boundary.

---

# 20. Query online/focus integration

React Native does not have browser `window online/focus` semantics.

Connect TanStack Query to:

- Expo Network / native connectivity;
- React Native AppState.

On reconnect/foreground:

- refresh stale data where appropriate;
- preserve cached result until replacement succeeds.

No blank-screen refetch.

---

# 21. Expo SQLite

Use Expo SQLite as durable local persistence.

Why:

- persisted across app restarts;
- structured queries;
- migrations;
- ideal for offline rates/context/saved data;
- already provides optional key-value storage;
- avoids adding AsyncStorage for data we can store in one persistence layer.

---

# 22. What SQLite stores

Candidate tables:

```text
schema_migrations
cached_quotes
country_metadata
currency_metadata
destination_context
typical_prices
favourites
recent_conversions
cached_story_chapters
trip_drafts
```

Not everything must ship P0.

---

# 23. Cached quote schema

Concept:

```text
cached_quotes
- cache_key
- base
- quote
- requested_date nullable
- effective_date
- amount/rate/result strings
- provider
- fetched_at
- stored_at
- stale_after
- payload_version
```

Use Decimal strings.

Never store JS float as canonical rate.

---

# 24. Offline quote semantics

When offline:

1. form/request defines exact pair/date;
2. local database lookup uses exact semantic key;
3. matching cached quote may render;
4. UI marks Offline/Cached;
5. effective and last-sync dates remain visible.

No matching cache:

> This pair/date is not available offline yet.

Never select “closest” pair silently.

---

# 25. SQLite and TanStack Query relationship

Do not blindly persist the entire QueryClient as opaque state in P0.

Instead:

```text
TanStack Query
= active network/server lifecycle

SQLite repositories
= intentionally durable domain snapshots
```

Query functions may:

1. read appropriate local snapshot;
2. attempt network refresh when allowed;
3. persist validated network result;
4. return authoritative latest/cached state with freshness metadata.

This makes offline trust semantics inspectable and testable.

---

# 26. Why not generic query-cache persistence

Persisting every query can:

- store accidental/unneeded data;
- obscure freshness semantics;
- make migrations harder;
- make stale policy dependent on query internals.

Our financial/context product needs explicit durability rules.

Use SQLite models/repositories for persisted user-value data.

---

# 27. Small preferences

For small key-value preferences:

- expo-sqlite `kv-store` is acceptable;
- no need to add AsyncStorage solely for theme/last-tab preference.

Examples:

- preferred UI theme later;
- last selected pair;
- onboarding flag if onboarding ever exists.

---

# 28. SecureStore

Use `expo-secure-store` when authentication ships.

Store only appropriate secrets/tokens.

Do not store:

- large API response cache;
- country metadata;
- ordinary preferences.

SecureStore is not the application database.

---

# 29. Authentication state later

Possible ownership:

```text
SecureStore
→ refresh/session secret

React memory
→ current auth state

TanStack Query
→ current profile/server ownership data
```

Logout clears:

- tokens;
- authenticated Query cache;
- protected local records according to policy.

Anonymous public rate cache may remain if privacy policy allows.

---

# 30. No Redux

No Redux in P0/P1.

We do not have complex cross-domain client state that warrants:

- reducers;
- action architecture;
- extra devtools conventions.

Use:

- component state;
- Context only for narrow app-level concerns;
- TanStack Query;
- SQLite repository.

---

# 31. No Zustand initially

Zustand is smaller than Redux but still solves a problem we do not currently have.

Do not introduce a global bag of UI state.

If later a clearly cross-screen local state appears, evaluate then.

---

# 32. State ownership matrix

| State | Owner |
|---|---|
| amount field while typing | component state |
| picker search text | screen/component |
| selected pair before submit | conversion feature state |
| server quote | TanStack Query / server response |
| durable cached quote | SQLite |
| country metadata | Query + SQLite |
| favourites anonymous | SQLite |
| auth token later | SecureStore |
| profile | TanStack Query |
| navigation | Expo Router |
| theme preference | SQLite kv-store |
| business rate logic | Django |

---

# 33. React component design

Prefer components that receive explicit props.

Good:

```tsx
<ConversionResult
  amount={quote.amount}
  result={quote.result}
  effectiveDate={quote.effectiveDate}
  status={quote.status}
/>
```

Avoid components that fetch hidden data simply because they can.

Screen/features coordinate queries.

Pure presentation components remain easy to test.

---

# 34. Feature hooks

Use hooks only when they encapsulate real behavior.

Examples:

- `useConversionQuote`;
- `useOnlineStatus`;
- `useCachedQuote`.

Avoid a hook for every one-line `useState`.

---

# 35. Error model

API exposes machine code + detail.

Mobile maps stable codes to state.

Examples:

```text
validation_error
rate_unavailable
out_of_coverage
unsupported_currency
historical_observation_missing
authentication_required
```

Never parse English error messages to determine behavior.

---

# 36. Offline status

Use explicit native connectivity state.

But:

> device says online

does not guarantee API is reachable.

Final state combines:

- connectivity;
- request outcome;
- local cache availability.

UI says what it knows, not what it assumes.

---

# 37. Background/resume

On app foreground:

- restore existing visible state immediately;
- refresh stale queries opportunistically;
- do not blank result;
- update only after new result succeeds.

This supports travel interruption/resume.

---

# 38. Formatting

Use JavaScript `Intl` for:

- number display;
- date display;
- currency labels where appropriate.

Use `expo-localization` for:

- device locale;
- region;
- decimal/grouping context;
- text direction.

Locale may suggest defaults, never infer user intent as fact.

---

# 39. Internationalization

P0 UI can be English-only if product scope requires, but code must be translation-ready.

Avoid concatenated grammar like:

```ts
"Rate " + date + " ago"
```

Use message units.

When actual localization is introduced, evaluate a translation library then.

Do not add i18n framework before translations exist solely for architecture theatre.

---

# 40. RTL

Use RN logical/layout direction behavior.

Test:

- picker;
- amount code;
- Swap icon;
- timeline;
- chart labels.

Source/destination semantics are not left/right semantics.

---

# 41. Accessibility

Native components must define:

- `accessibilityRole`;
- `accessibilityLabel` where visible label insufficient;
- state;
- hints only when useful.

Do not over-label visible text and create repetitive VoiceOver/TalkBack output.

---

# 42. Dynamic result announcements

Use platform accessibility announcements sparingly.

After completed conversion:

> 100 euros is approximately 17,450 Japanese yen. Reference rate effective 18 September 2026.

Do not announce full local context automatically.

---

# 43. Dynamic Type / font scaling

Do not lock text scaling off.

Quiet Atlas native components must survive:

- large accessibility font settings;
- multiline buttons/labels;
- stacked layouts.

Critical numeric results can have bounded scaling strategy only if necessary to avoid unusable overflow, but equivalent information must remain readable.

---

# 44. Touch targets

Primary controls:

- roughly 48–56dp/pt equivalent hit area;
- adequate spacing.

Use `hitSlop` only to increase, not hide poor visual affordance.

---

# 45. Safe areas

Use Expo/React Native safe-area primitives.

Header, sheets and bottom navigation respect:

- status/notch area;
- home indicator;
- landscape edges.

No content should rely on hard-coded iPhone dimensions.

---

# 46. Keyboard

Amount:

- decimal keyboard.

Search:

- search/text keyboard.

Forms remain usable when keyboard is open.

Avoid permanent bottom action that gets trapped behind or overlaps keyboard.

---

# 47. Motion

Use native platform transitions and small RN animations.

Do not install Reanimated solely for decorative converter motion.

If Expo Router/@expo UI dependency already brings animation infrastructure internally, application code still stays restrained.

No number count-up.

---

# 48. Haptics

Optional `expo-haptics`.

Use only for deliberate tactile moments:

- Save favourite;
- explicit Swap;
- successful meaningful confirmation.

Never for every tap.

Respect platform/user expectations.

---

# 49. Mobile chart technology

Use:

```text
react-native-svg
+ small project-owned typed LineChart
```

Do not install a full chart framework initially.

Why this works:

Our required chart is intentionally simple:

- one rate line;
- selected historical point;
- latest point;
- high/low;
- simple axes/grid;
- optional tap point.

`react-native-svg` gives native SVG primitives on iOS/Android and is supported in Expo.

---

# 50. Mobile chart math

Project-owned chart utilities calculate:

- padded plot bounds;
- x date/epoch → pixel;
- y rate → pixel;
- path points;
- selected marker.

Use plain numeric display geometry only.

This is not financial domain arithmetic.

Rates arrive as decimal strings and are parsed for visualization only after trusted textual values already exist.

The accessible text remains the canonical representation.

---

# 51. Why not Victory/large chart library

Current chart scope does not need:

- multiple chart families;
- animation engine;
- gestures;
- complex legends;
- theming framework.

A large dependency would solve more than required.

If chart requirements later expand substantially, reassess.

---

# 52. Chart accessibility on mobile

The SVG is supplemental.

Screen includes:

- selected result;
- latest value;
- period;
- high/low;
- text summary.

Accessibility element can describe the chart broadly.

Do not expose hundreds of points as individual accessibility nodes.

---

# 53. API time-series size

Server controls downsampling/grouping.

Mobile should not download 20,000 daily points just to render a 390px chart.

Query period can request appropriate grouping.

UI must disclose granularity if it changes interpretation.

---

# 54. Deep links

Expo Router can map incoming deep links to:

- current conversion;
- historical conversion;
- country Explore;
- story.

Deep link input is still validated by API/domain.

Never render an unvalidated archived-currency assumption from URL alone.

---

# 55. Share

Use React Native/Expo platform Share API.

Share canonical web URL when possible.

Benefits:

- recipient does not need app;
- one public truth URL;
- app may deep-link itself when installed.

No third-party social SDK.

---

# 56. Images

Use Expo-native image solution available in selected SDK where it improves caching/performance.

Image data comes with source/licence metadata.

Do not place network images behind conversion controls.

Cultural/story imagery is lower priority than task content.

---

# 57. Icons

Use a coherent Expo-compatible local icon source.

Avoid shipping several icon sets.

The exact native icon implementation can follow Expo platform conventions:

- SF Symbols where appropriate on iOS;
- equivalent vector icon on Android;
- or one cross-platform set for consistency.

Accessible name belongs to the control, not the glyph.

Do not over-invest before implementation.

---

# 58. Network timeouts

`fetch` wrapper uses AbortController.

Client timeout should not exceed backend/provider request design excessively.

Django remains responsible for upstream Frankfurter timeout.

Mobile timeout covers the API request itself.

---

# 59. Request cancellation

Changing pair/date rapidly should cancel/ignore obsolete conversion request.

TanStack Query/query keys help isolate results.

UI also checks semantic key before promoting a result.

Same invariant as web:

> result and visible pair/date always belong together.

---

# 60. Optimistic updates

Safe uses:

- favourite locally;
- simple local preference.

Do not optimistically invent:

- rate;
- conversion result;
- historical observation;
- source metadata.

Trust-sensitive data waits for authoritative server/cache result.

---

# 61. Favourites

Anonymous favourite can persist locally immediately.

When accounts ship:

- server sync becomes authoritative for cross-device state;
- merge policy is explicit.

Do not block Save on network if anonymous local Save is supported.

---

# 62. Recent history

SQLite stores bounded list.

Store only useful fields.

Candidate:

- amount;
- pair;
- country context;
- requested/effective date;
- timestamp.

User can clear.

No analytics backend required for private recent list.

---

# 63. Database migrations

SQLite schema is versioned.

Use explicit migrations.

Never assume app update can destroy/recreate user database.

Migration tests cover upgrade from previous schema where persistent user data exists.

---

# 64. Database query safety

Use bound parameters/prepared APIs.

Never interpolate user strings into SQL.

This applies even to local-only DB.

---

# 65. API schema CI

Backend generates OpenAPI artifact.

Mobile command:

```text
npm run api:generate
```

CI verifies clean git diff after generation.

If backend contract changes, mobile types must update intentionally.

---

# 66. OpenAPI type boundary

Generated types stay generated.

Do not edit generated `schema.d.ts`.

Create small domain/view-model mapping functions where UI semantics differ.

This keeps generator updates painless.

---

# 67. App configuration

Environment:

- API base URL;
- app environment;
- optional observability DSN later.

Public app config must not contain private backend/provider secrets.

Third-party FX/API keys never ship to client.

---

# 68. EAS

Use Expo Application Services only where it provides concrete value:

- builds;
- simulator/emulator test artifacts;
- releases;
- optional update pipeline.

Avoid coupling core development to paid cloud behavior.

Local development remains possible.

---

# 69. OTA update policy

EAS Update can later deliver compatible JS/asset changes.

But:

- native dependency changes require new binary;
- API compatibility must remain;
- financial/trust fixes need disciplined release notes/testing.

Do not use OTA to bypass quality gates.

---

# 70. Testing stack

## Unit/component

Use:

- Jest;
- `jest-expo`;
- `@testing-library/react-native`.

Expo Router integration tests can use:

- `expo-router/testing-library`.

## E2E

Use Maestro for high-value black-box smoke flows.

Why:

- Expo has first-party documentation/workflow integration;
- cross-platform user-level syntax;
- good fit for critical navigation/conversion flows.

EAS Maestro job is currently not required on every commit if cost/alpha workflow status is excessive.

Run locally or on selected PR/nightly/release gates.

---

# 71. What to unit test

Worth testing:

- formatting;
- SQLite migrations/repositories;
- stale/offline state mapping;
- API error normalization;
- query key construction;
- conversion result presentation variants;
- historical requested/effective distinction.

Avoid:

- snapshot testing every visual component.

Expo itself recommends E2E over overreliance on UI snapshots.

---

# 72. Mobile E2E flows

Initial Maestro:

1. launch;
2. current conversion;
3. swap;
4. historical conversion;
5. inspect requested/effective date;
6. save favourite;
7. relaunch and verify persistence;
8. offline cached conversion;
9. offline uncached state.

Add navigation/story flows when shipped.

---

# 73. Accessibility testing

Automated RN accessibility tooling is less complete than web axe.

Required:

- component semantic assertions where practical;
- iOS VoiceOver manual review;
- Android TalkBack manual review;
- large font testing;
- reduced motion;
- contrast/design token review;
- physical device touch review.

Do not claim WCAG/platform accessibility based only on Jest.

---

# 74. Offline test matrix

Test:

- app starts online;
- app starts offline with cache;
- app starts offline with no cache;
- goes offline mid-request;
- returns online;
- cached rate expired;
- cached context present but rate absent;
- schema migration with cache;
- pair changes offline.

---

# 75. Performance

Main screens should not mount huge context trees.

Strategies:

- route-level screen separation;
- lazy secondary content where sensible;
- FlatList for long picker/search results;
- memoization only after profiling;
- SQLite indexed lookup for cache keys;
- small image assets.

Do not cargo-cult `memo` everywhere.

---

# 76. Picker performance

Country/currency list is small enough for simple local filtering, but use FlatList if rows are numerous.

Stable keys:

- country/currency semantic ID.

Avoid rendering all cultural media or extra metadata inside result rows.

---

# 77. Bundle dependency budget

Every native dependency increases upgrade surface.

Core intentional dependencies include:

```text
expo
expo-router
@expo/ui
expo-sqlite
expo-localization
expo-secure-store [later]
expo-haptics [optional]
react-native-svg
@tanstack/react-query
openapi-fetch
```

Plus testing/tooling.

Do not add multiple libraries for the same concern.

---

# 78. Reanimated policy

Do not explicitly add Reanimated just for Quiet Atlas microinteractions unless selected Expo/router/native components require it or a later interaction cannot be implemented cleanly otherwise.

Our product does not need gesture-heavy animation.

---

# 79. Gesture Handler policy

Same principle.

If navigation/library ecosystem already requires it, use the supported version.

Do not build custom gesture-first converter interaction.

---

# 80. Native module upgrade policy

Always use:

```text
npx expo install <package>
```

for Expo-supported native packages so compatible versions are selected.

Do not manually install arbitrary latest native module versions that conflict with SDK matrix.

---

# 81. Stable over latest

Examples of rejected choices:

- RN 0.87 standalone while Expo stable is 0.86;
- Expo 58 beta;
- experimental Expo Router stack;
- beta native UI APIs for core conversion.

Portfolio quality is demonstrated by compatibility judgment, not version-number chasing.

---

# 82. Mobile CI gates

Before merge:

```text
TypeScript
lint/format
Jest/component tests
API generated types current
Expo doctor/check as appropriate
build config validation
```

Selected PR/release:

```text
Android/iOS build
Maestro smoke
```

---

# 83. Error boundary

Use a top-level React error boundary for unexpected rendering errors.

Provide:

- calm fallback;
- retry/restart path;
- no raw stack trace.

Expected API/domain errors do not go through fatal ErrorBoundary.

---

# 84. Logging

Client logs can include:

- normalized error code;
- request correlation ID;
- screen;
- offline status.

Do not log:

- auth token;
- raw private trip notes;
- external provider secrets;
- excessive user financial amounts unless analytics/privacy policy explicitly permits it.

---

# 85. Analytics

No analytics SDK is required for P0.

When product analytics becomes useful, choose privacy-conscious event model.

Do not install Firebase/Segment/etc. just for portfolio appearance.

---

# 86. Crash reporting

Can be added after deployment.

Do not make an external observability SDK part of initial frontend foundation unless actual production monitoring needs it.

---

# 87. Native privacy

Local histories/favourites remain local until user explicitly has sync/account behavior.

App privacy disclosure must match actual storage/analytics behavior.

No hidden cross-device upload.

---

# 88. Web/mobile consistency

Same phrase semantics:

- Reference rate;
- Historical reference;
- Effective date;
- Cached;
- Offline.

Do not let native UI invent different trust terminology.

Copy contract can be documented centrally.

---

# 89. Platform-specific design

Allowed differences:

- picker presentation;
- sheets;
- navigation;
- date controls;
- haptics;
- platform typography metrics.

Not allowed differences:

- rate semantics;
- freshness meaning;
- historical date meaning;
- error truth;
- provenance.

---

# 90. Mobile implementation acceptance

The foundation is accepted when:

- Expo stable compatibility matrix is locked;
- Expo Router navigation works;
- Quiet Atlas typed tokens exist;
- current conversion screen uses native ergonomic layout;
- OpenAPI-generated client compiles;
- TanStack Query cancellation/stale behavior is tested;
- SQLite migrations/cache repository work;
- app relaunch restores last useful cached state;
- offline state cannot show wrong pair;
- native date picker supports historical flow;
- React Native SVG line chart renders without a heavyweight chart framework;
- Jest/RNTL are green;
- one Maestro smoke flow runs locally or CI;
- VoiceOver/TalkBack manual checklist exists.
