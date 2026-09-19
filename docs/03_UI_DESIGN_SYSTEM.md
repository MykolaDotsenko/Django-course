# UI Design System

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

This prevents every country from becoming a custom mini-site.

## 3. Tailwind strategy

Tailwind CSS is a delivery mechanism, not the design architecture.

Define semantic tokens first:

```text
surface
surface-muted
text
text-muted
border
accent
accent-contrast
success
warning
danger
focus
```

Avoid scattering country-specific raw colours through templates.

## 4. Component inventory

P0 components:

- AppShell;
- Header;
- CurrencyAmountField;
- CountryCurrencySelector;
- SwapButton;
- ConversionResult;
- RateMeta;
- DataFreshnessBadge;
- ContextCard;
- TypicalPriceList;
- PaymentTips;
- Disclosure;
- InlineAlert;
- EmptyState;
- Skeleton/LoadingIndicator;
- Footer/DataSources.

Prefer Django template partials and small HTMX targets.

## 5. Responsive behaviour

### Large screens
Two-country comparison can use a balanced split.

### Medium
Keep two columns only while controls remain comfortably readable.

### Small
Stack source above destination. Result follows immediately after the destination selector.

Use container/layout primitives rather than device-name breakpoints where practical.

## 6. Typography

Prioritize:

1. numeric result;
2. amount/currency identity;
3. source freshness;
4. practical local context;
5. cultural enrichment.

The converted amount should be visually prominent but not resemble a speculative price ticker.

## 7. Motion

Allowed:

- small state transitions;
- swap affordance;
- drawer expansion;
- skeleton-to-content transition.

Avoid:

- continuous decorative JS loops;
- motion tied to every keystroke;
- parallax in the primary workflow.

Honor `prefers-reduced-motion`.

## 8. Theme requirements

Initial release:

- light theme as primary;
- dark theme only if it can reach equivalent contrast/quality without delaying core features.

Country theming is not a replacement for dark mode.

## 9. Icons and flags

- use text currency codes alongside any symbol;
- use country names alongside flags;
- no emoji-only actionable control;
- avoid implying that one flag uniquely represents a currency.

## 10. Content style

Prefer precise, restrained language.

Good:

> Cards are commonly accepted in urban areas.

Bad:

> Japan is basically cashless now!

Good:

> Typical coffee estimate, Tokyo, observed May 2026.

Bad:

> Coffee in Japan costs ¥500.

## 11. Loading design

Use the smallest loading surface possible.

- changing the amount should not blank the entire page;
- cultural enrichment should not block conversion;
- retain stable layout to reduce CLS;
- show “Updating…” only where state actually changes.

## 12. Error design

Error messages answer:

1. what happened;
2. whether previous data is still usable;
3. what the user can do next.

Example:

> Live rates could not be refreshed. Showing the last successful EUR → JPY rate from 09:00 UTC. Retry.

## 13. Visual ROI rule

Every visual element must do at least one of:

- improve comprehension;
- improve navigation;
- communicate system state;
- establish useful hierarchy;
- strengthen cultural context without reducing clarity.

Otherwise remove it.
