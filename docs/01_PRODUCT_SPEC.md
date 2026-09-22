# Product

## Product statement

Cultural Currency Converter helps a traveller answer three connected questions:

1. **How much is my money worth there?**
2. **What does that amount roughly mean locally?**
3. **What should I know about money and payment culture in that destination?**

The conversion is the primary task. Context and culture should make the conversion more useful, not turn the product into an encyclopedia.

## Core experience

The intended loop is:

```text
Convert → Understand → Explore → Save → Return
```

The signature interaction keeps source and destination identities visible together. Country context can change atmosphere and enrichment while the financial calculation remains stable and independently trustworthy.

## Primary users

The product is mainly for:

- travellers converting money before or during a trip;
- expats and international students building local intuition;
- cross-border shoppers comparing rough value;
- curious users exploring currencies and money culture.

## Current product capabilities

The web product currently supports:

- current FX conversion;
- historical FX conversion;
- explicit requested/effective observation dates;
- bilateral country/currency selection;
- historical trend views and Then & Now;
- sourced current destination context;
- everyday-value examples;
- cash/card/ATM/tipping guidance;
- deterministic money/culture storytelling;
- optional AI explanation;
- anonymous local favourites/recent conversions;
- account-owned favourites;
- separately opt-in account recent history.

Current code and tests are the authoritative detail for these capabilities.

## Product principles

### Utility first

A user should be able to convert money quickly without consuming enrichment.

### Context is progressive

Useful destination context should be close to the conversion result. Deeper history/culture can be opened when desired.

### Trust is visible

Rates, historical observations, typical prices and factual cultural claims should carry enough provenance and timing context to avoid false precision.

### Current and historical meaning are separate

Historical FX does not automatically make today’s prices or payment customs historical. Current context should be clearly labelled when shown next to a historical conversion.

### Optional systems are optional

Media, external enrichment and AI should degrade gracefully. Core conversion should not depend on them.

### Country and currency are distinct

A currency can belong to multiple countries and country/currency relationships change over time. Product language and data modelling should preserve that distinction.

## Non-goals

The product is not intended to be:

- a trading terminal;
- a remittance execution service;
- a bank/accounting ledger;
- regulated financial advice;
- a guarantee of merchant/card/ATM fees;
- a universal cost-of-living database;
- a source of unsourced historical or cultural claims.

## Future direction

Likely future areas include:

- a versioned mobile API;
- a native mobile client;
- trip/budget workflows;
- richer sourced destination data;
- research into historical purchasing power.

These are directions, not fixed implementation commitments. Technology choices should be re-evaluated when each area becomes active.
