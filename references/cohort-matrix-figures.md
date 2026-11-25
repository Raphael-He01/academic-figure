# Aligned cohort and event matrices

Use for patient/sample-aligned multi-track matrices, genomic event displays and related conditional composition summaries. Source: N3 in [Nature/Science learning](nature-science-learning-2026-10-17.md). This is design guidance, not a new executable heatmap implementation.

## Alignment and encoding

- Declare whether a column is a person, specimen, visit or paired trajectory. Keep a stable unique key through joins; never align tracks by current row position.
- Compute one declared ordering and reuse it in every linked track. If a cohort is reordered independently, label that distinction; aligned positions across independent cohorts do not imply matched patients.
- Separate continuous burden/intensity scales from discrete event categories. Event type, timing, coverage and clinical annotation need independent keys where their meanings differ.
- Distinguish no event, unknown status, not assayed and missing coverage. A blank cell must have one stated meaning; it cannot silently represent all four.
- Add only tracks needed for the question, group related tracks with restrained separators, and move long definitions to the caption. Dense legends are a reason to simplify or split a figure, not shrink everything.

## Denominators and comparisons

- Record total cohort size, assay-eligible size, event-positive size and the analysis subset per panel. Explain changes in inclusion; do not invent reasons for an unexplained difference.
- Distinguish an event rate among all eligible cases from composition among event-positive cases. Name the denominator beside each summary and clarify multiple events per case or overlapping categories.
- Shared row labels/order can aid paired summaries, but axes and directions must remain readable, especially with mirrored bars. Reference thresholds require units, provenance and a stated interpretation.
- For longitudinal samples, keep patient identity and timepoint/paired status recoverable. A representative cell is not an independent replicate merely because it occupies another column.

## Final-size checks

Inspect thin cells, shape-over-fill encodings, row labels, missing-state keys and alignment after export. Add redundant labels/patterns or fewer tracks when colour-only event categories fail grayscale or colour-vision review. Retain the keyed matrix and ordering configuration with the editable output; verify from data, not from the displayed mosaic.
