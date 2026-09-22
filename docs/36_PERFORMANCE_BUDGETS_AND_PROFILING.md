# Performance Budgets and Profiling Contract

Status: **performance execution contract**

Performance is a product constraint because the primary task is a fast conversion, not an animated content site.

Budgets are guardrails and must be measured against real pages before being tightened.

---

# 1. Performance hierarchy

Optimize in this order:

1. correctness;
2. primary conversion latency;
3. layout stability / interaction responsiveness;
4. network payload;
5. secondary media;
6. decorative effects.

Never trade financial correctness or provenance for a benchmark.

---

# 2. Request-path budget principles

The current conversion request path should have:

- one bounded FX provider dependency on cache miss;
- no cultural/archive search dependency;
- no runtime image generation;
- no AI call before explicit “Explain this” action;
- no unnecessary database writes;
- no network call inside intentional DB transaction.

Country/cultural context should come from local persisted/curated data where practical.

---

# 3. Web payload budget

Initial target before historical chart/media-heavy surfaces:

- no React web runtime;
- core custom web JavaScript target under approximately **100 KiB compressed** before lazy chart code;
- HTMX kept small/pinned;
- historical chart code lazy-loaded;
- route-only noncritical renderers should be dynamically imported when that removes code from the
  primary conversion path without creating state duplication;
- no external runtime fonts/scripts;
- SVG/static visuals optimized;
- below-fold media lazy-loaded.

These are design targets, not current measured claims.

If measurement shows a tighter realistic budget, update this document.

---

# 4. Critical rendering

Above the fold prioritize:

- H1/context;
- source/destination controls;
- amount;
- Convert;
- result/trust metadata.

Do not make first useful render wait for:

- culture story;
- archive media;
- chart library;
- AI explanation;
- below-fold country cards.

Hero media must not block the primary form/result.

---

# 5. Image performance

Rules:

- explicit width/height or aspect ratio;
- responsive source only where a genuinely different composition is needed;
- one eager/high-priority hero maximum;
- below-fold media lazy;
- no duplicate desktop/mobile bytes when `<picture>` can select one;
- prefer optimized release SVG/WebP for static art;
- object-storage/CDN only when content-media scale justifies it.

---

# 6. Database profiling

Profile before adding caches/denormalization.

For important views inspect:

- query count;
- duplicated queries;
- N+1;
- missing select_related/prefetch_related;
- index use for real filters;
- transaction duration.

Do not introduce generic query/repository abstractions to hide inefficient query shapes.

---

# 7. Cache policy

Cache protects latency/availability, not truth.

Measure:

- hit/miss ratio;
- provider latency;
- stale fallback frequency;
- key cardinality where relevant.

Do not add Redis because “production apps use Redis”.

Use the simplest cache backend that satisfies measured requirements.

---

# 8. Provider latency

Every external HTTP client needs:

- connect/read timeout;
- bounded retry;
- normalized error;
- observability.

Do not retry multiplication across several layers.

One layer owns retry policy.

---

# 9. Browser metrics

For production/preview profiling track representative:

- LCP;
- CLS;
- INP;
- transferred bytes;
- JS/CSS size;
- image bytes;
- request count.

Use real throttled browser runs before making optimization claims.

Do not claim “fast” from local desktop rendering alone.

---

# 10. Server metrics

Measure representative:

- request duration p50/p95;
- provider call duration/error rate;
- DB query count/time;
- cache behaviour;
- template/render time where useful.

Exact SLOs should be set only after a deployed baseline exists.

---

# 11. Performance regression rule

A PR that materially increases:

- critical JS/CSS;
- above-fold image bytes;
- primary query count;
- provider calls;
- conversion request latency

must explain why the cost is justified.

For intentional increases, record before/after measurement.

---

# 12. Profiling workflow

Use:

```text
observe
→ reproduce
→ measure baseline
→ identify dominant cost
→ smallest fix
→ measure again
→ keep only material improvement
```

Do not optimize by intuition alone.

---

# 13. Historical/chart surfaces

Historical charts are secondary.

Rules:

- lazy-load chart library;
- server/text/table fallback remains useful;
- do not fetch long time series before user enters historical/chart context;
- cache stable historical series aggressively according to semantic policy.

---

# 14. Mobile

Mobile performance budgets prioritize:

- fast launch to usable converter;
- bounded API payload;
- durable offline cache only for explicit product data;
- no image-heavy startup;
- no unnecessary global state/store;
- list virtualization only where list size proves need.

Re-check with real Expo/React Native profiling when mobile implementation begins.

---

# 15. Performance Definition of Done

For a performance-sensitive PR:

- baseline captured;
- bottleneck identified;
- change measured;
- no semantic regression;
- no accessibility regression;
- complexity increase justified;
- result documented in PR.

A micro-optimization without measurable product value should not merge.
