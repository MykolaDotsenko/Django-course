# Design System

## Design direction

The current visual language is **Quiet Atlas**: calm, editorial and travel-oriented, with restrained use of colour and imagery.

The design should support trust and legibility before decoration.

## Stable visual ideas

Prefer:

- a quiet neutral canvas;
- clear surface hierarchy;
- strong readable typography;
- one obvious primary action;
- country atmosphere used as context, not as a control-state mechanism;
- deliberate whitespace;
- media that explains or sets atmosphere rather than filling space.

Avoid:

- trading-dashboard aesthetics;
- excessive gradients/glass effects;
- dense decorative iconography;
- country stereotypes;
- layouts whose meaning depends on colour;
- novelty interactions that make conversion slower.

## Country atmosphere

Source and destination can have independent atmosphere through subtle accents, surfaces, illustration or contextual media.

The converter’s mechanics, validation and trust semantics should remain consistent across countries.

The existing `data-country-theme` mechanism is one implementation, not a requirement to preserve forever.

## Components

The current UI is composed from reusable Django templates/partials plus CSS and small TypeScript enhancements.

Important component families include:

- amount/input fields;
- country/currency picker;
- swap action;
- conversion result/provenance;
- historical controls/chart;
- contextual cards;
- media/image frame;
- saved/recent state;
- account surfaces.

Prefer reusing or simplifying existing patterns before adding another component abstraction.

## Information hierarchy

For conversion surfaces, visual emphasis generally follows:

1. task/amount/result;
2. selected source and destination;
3. trust/provenance/date;
4. practical interpretation;
5. exploration/save utilities;
6. decorative media.

This hierarchy can be adapted when a screen has a different primary task.

## Media

Use imagery when it adds local atmosphere, historical evidence or explanation.

Quiet Atlas release-owned SVGs are valid deterministic fallbacks. Managed sourced media can replace them where it improves authenticity.

Do not use a misleading historical photo merely because an image slot exists.

## Motion

Motion should clarify state change, not decorate routine interaction.

Respect reduced-motion preferences and avoid animations that delay access to information.

## Responsive design

Prefer flexible layout rules over fixed breakpoint-specific replicas.

Components should survive:

- narrow screens;
- large text;
- 200% text zoom/reflow;
- long country/currency names;
- browser font differences.

Exact pixel values belong in CSS/tests when needed, not in this document.

## Accessibility visual baseline

Maintain:

- readable contrast;
- visible keyboard focus;
- non-colour state cues;
- sufficient interactive target area;
- text that can wrap without hiding functionality;
- layouts that do not require horizontal scrolling for core tasks at narrow reflow widths.

## Evolving the design system

The design system is a shared language, not a frozen visual specification.

If a new pattern improves comprehension, accessibility, consistency or product value, it can replace the existing pattern. Update this document when the new pattern becomes a project-level convention.
