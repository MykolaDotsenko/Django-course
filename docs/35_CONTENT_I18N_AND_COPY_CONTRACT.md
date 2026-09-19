# Content, Internationalization and Copy Contract

Status: **content-quality contract**

Cultural Currency Converter combines financial data with cultural context.

Copy therefore has to be precise enough for money and respectful enough for culture.

---

# 1. Language principle

User-facing copy should be:

- concise;
- factual;
- calm;
- non-promotional;
- explicit about uncertainty;
- easy to translate.

Avoid fintech hype, tourism clichés and artificial “AI voice”.

---

# 2. Product terminology

Use consistently:

- **source** / **from**;
- **destination** / **to**;
- **currency** for money unit;
- **country** for cultural/geographic context;
- **reference rate** when provider data is a reference observation;
- **requested date** vs **effective date** for historical data;
- **stale** only when defined by cache/freshness policy;
- **illustrative visual** for generated/non-archival historical-looking art.

Do not call reference data “live” unless the selected provider contract actually guarantees that semantic.

---

# 3. Country and currency are different concepts

Copy must not imply:

> one country = one currency

or:

> one currency = one country.

Examples:

- EUR may map to many country contexts;
- a historical country may have multiple currency eras;
- same-currency/different-country exploration is valid.

Controls and explanatory text must preserve this distinction.

---

# 4. Money formatting

Formatting belongs to presentation rules, not string concatenation.

Requirements:

- currency code/symbol semantics are explicit;
- Decimal value is preserved until formatting boundary;
- locale-aware grouping/decimal separators when locale support ships;
- no scientific notation for user-facing money;
- excessive precision is not displayed;
- converted amount and rate precision are not assumed identical.

Do not parse formatted display strings back into financial domain values.

---

# 5. Date/time formatting

Historical UI must visibly distinguish:

- requested date;
- effective observation date.

Use unambiguous localized dates.

Avoid ambiguous all-numeric formats when locale context is unclear.

Timestamps such as provider fetch time may be lower hierarchy than the effective financial date.

---

# 6. Uncertainty language

Preferred:

- “Typical price range”
- “Roughly equivalent to”
- “Reference rate”
- “Last available observation”
- “Current payment guidance”
- “Data unavailable for this period”

Avoid:

- “You will pay exactly”
- “Guaranteed rate”
- “This always costs”
- “People in this country always…”
- unsupported causal cultural claims.

---

# 7. Cultural claims

Cultural copy should describe documented practices without essentializing people.

Prefer:

> “Card payments are widely accepted in the sources reviewed.”

Avoid:

> “Japanese people prefer X.”

Where practice varies by region, merchant type, generation or context, say so if relevant.

Current cultural/payment guidance must not be silently backdated into historical mode.

---

# 8. Translation readiness

Initial implementation may ship with one UI locale.

Even then:

- user-facing strings should be extracted/localizable;
- no English sentence fragments assembled in templates;
- no text baked into generated/static imagery;
- pluralization must use localization mechanisms;
- date/number formatting must not assume English punctuation;
- layout must tolerate longer translated strings.

Do not claim support for a locale until the product has been reviewed in that locale.

---

# 9. Translation keys

Keys should describe semantic intent, not exact English text.

Good:

```text
conversion.result.effective_date
history.no_observation
payment.cash_guidance.heading
explore.everyday_value
```

Avoid:

```text
label_1
blue_card_text
click_here
```

---

# 10. Error messages

Errors should answer:

1. what happened;
2. whether the user can act;
3. what to do next.

Good:

> “We could not refresh this rate. Showing the last cached observation from 18 Sep 2026.”

Avoid:

> “API error 500.”

Provider internals do not belong in normal user-facing messages.

---

# 11. Accessibility copy

Labels must make sense without visual position.

Avoid:

- “left currency”;
- “green button”;
- “click icon”.

Prefer:

- “Source country”
- “Destination currency”
- “Swap source and destination”
- “Show rate source”

Live-region announcements should be concise and avoid re-reading large cultural sections after every HTMX update.

---

# 12. Media captions

For sourced factual media include, where applicable:

- title/description;
- creator/source;
- date or date precision;
- licence/rights;
- context.

For AI/generated historical-looking media:

> “Illustrative visual — not an archival photograph.”

Do not imply exact year/place when the media metadata only supports an era/region.

---

# 13. AI-generated copy

AI text is not automatically publishable truth.

AI may receive a trusted fact/source packet and produce a candidate.

Published copy must obey:

- allowed fact IDs/source references;
- schema validation;
- semantic validation;
- no unsupported precision;
- no invented causal claims;
- deterministic fallback available.

---

# 14. Audio copy

If optional pronunciation/audio ships:

- provide visible text label;
- explicit play/pause control;
- no autoplay;
- transcript/meaning where relevant;
- source/licence where required.

Audio is enrichment, never required to complete conversion.

---

# 15. Editorial checklist

Before publishing cultural/historical copy:

- Is the claim sourced?
- Is the date precision honest?
- Is current vs historical context clear?
- Is the statement overly universal?
- Is terminology consistent with product docs?
- Can it be translated cleanly?
- Does the media/caption imply more certainty than the source supports?
