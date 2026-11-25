# Figure title, legend, and Results writing

For a complete, explicitly selected numeric CSV column, `scripts/check_caption_summary.py` compares row count and rounded arithmetic mean against supplied facts; missing or nonfinite values halt the check. This count is rows, not automatically independent n; transformations, exclusions, other statistics, and free text require separate review.

For a templated caption, `scripts/caption_facts.py` can render from explicitly supplied formatted facts and verify that the caption still matches them. It does not calculate statistics or validate untemplated text; retain scientific review and bind the fact source to the analysis output.

## Title

State the comparison or finding without exaggeration. Prefer a concrete noun phrase or restrained declarative sentence. Do not include an unsupported causal or mechanistic claim.

## Stand-alone legend

Write in panel order and include:

1. what each panel displays;
2. biological/material system and experimental condition;
3. axes, units, normalization and transformations not obvious from labels;
4. what points, lines, bands, boxes, bars and colors mean;
5. independent sample size and what `n` counts;
6. error/interval definition;
7. statistical test, sidedness, pairing, adjustment and exact meaning of symbols, if actually used;
8. abbreviations and any missing/interpolated/excluded values relevant to interpretation.

For spatial, forecast and decision figures, add the baseline period, geographic/data coverage, area weighting, time split, interval construction, cost assumptions or comparator as applicable. Distinguish an IQR across locations from uncertainty in an estimated mean; distinguish predictive quantiles from confidence intervals. Define stars, rings and outlines explicitly even when they are selection markers rather than significance symbols. State whether costs are money, measured quantities or illustrative loss units. A caption must preserve these distinctions when long on-canvas notes are moved out for journal layout.

Use `[待补充]` rather than guessing. If data are simulated, say so prominently and include the seed when useful.

For time-to-event plots, add endpoint, time origin/unit, group definition, censor-symbol meaning, interval method and risk-table counting convention; distinguish baseline n from changing support. For benchmark summaries, define metric direction, normalization, category weights, missing/failure handling, shown subset and score versus rank. Follow [survival](survival-figures.md) or [benchmark](benchmark-figures.md) rules for the analysis-specific details.

## Results draft

Lead with the observed contrast and give actual values or effect estimates with uncertainty where appropriate. Separate three layers:

- **Observation:** what the measurements show.
- **Interpretation:** the most direct scientific reading supported by the design.
- **Mechanism/speculation:** clearly qualified and only when external evidence or the experiment supports it.

Do not turn correlation into causation, statistical significance into practical importance, or non-significance into proof of no effect. Avoid “breakthrough,” “revolutionary,” “first,” “proved,” and similar terms unless independently substantiated. Match the reported precision to the measurement and analysis; do not create meaningless decimal places.

Default to concise professional Chinese. Provide an English version for English-language submission, preserving terms, numbers, panel references, units, tense, and uncertainty exactly.

## Caption consistency and destination-specific form

Keep the whole-figure title and the panel descriptions distinct. Follow the actual panel order, giving each panel its display meaning rather than repeating the Results argument. A journal's `Fig. N` punctuation or title styling is a destination choice, not a universal caption template.

For English captions, use present tense for what a reader sees and past tense for completed procedures when appropriate. In Chinese, preserve that distinction through clear wording rather than artificial tense markers. Keep scientific names and model identifiers exactly as defined; do not apply automatic title case to them.

Explain symbol and colour meanings needed for independent reading. Report only available n, intervals, tests and corrections using the existing checklist above; a polished caption must not conceal a missing definition.

Mention a Source Data file only if that file is actually supplied and linked to the figure. Adaptation and permission statements must describe real rights and provenance, not copied boilerplate. An optional interpretive sentence needs direct evidence and must be permitted by the destination; keep interpretation in Results when the journal requires a descriptive legend.

For a Nature or NMI submission, read [the stage-specific differences](nature-flagship-and-nmi-requirements.md) before applying a word limit. Count the complete caption including title and panel descriptions. Do not transfer a family journal's observed wording or historical limit to another journal.

For explicitly requested APA formatting, read [the APA profile](apa-figure-profile.md). When placing a completed figure in LaTeX, use [the inclusion guide](latex-inclusion.md) and the same canonical caption; do not rewrite a second caption in the manuscript.

Check compound caption claims separately against the analysis and record their limits in the existing manifest as described in [rendered QA](rendered-qa.md). Readable artwork cannot compensate for an unsupported interpretation.

Adapted from nature-figure (Apache-2.0)
Adapted from ARS-Codex 3.23.1 (CC BY-NC 4.0), Copyright (c) 2026 Cheng-I Wu
