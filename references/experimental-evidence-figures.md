# Experimental, structural and schematic evidence

Use when a figure combines a workflow, physical/biological structure, representative images and quantitative validation. Source observations are in [Nature/Science learning](nature-science-learning-2026-10-17.md); these are selected lessons, not a universal journal layout.

## Build an evidence sequence

Let the schematic explain the design or hypothesis, representative images show what was observed, and a quantitative panel test the stated comparison. Include only panels needed for that argument. An attractive model or representative image does not replace measurements and independent sample counts.

- Distinguish data-flow arrows, experimental operations and causal/mechanistic claims. Label feedback and iterative paths; do not use an unlabeled arrow to imply causality from a computational pipeline.
- Use aligned bands or compartments for conceptual layers and a small set of consistent shapes. Define any matrix inset as an example, schematic or real measurement; a stylized texture is not a numerical heatmap.
- Reuse method identity across validation panels. If benchmark sets or scales differ, make that difference visible and keep comparison claims within their common evaluation basis.
- For long method labels, prefer horizontal point/interval plots. Bars that encode magnitude should start at zero; a localized scale is better represented by explicitly scaled points and intervals. Find the actual interval definition before plotting it.

## Structure and image comparisons

- Distinguish experimental reference, predicted model, fitted result and illustrative hypothesis. A muted reference and a coloured overlay can work, but the legend must say which is which.
- Record alignment/superposition method, view orientation, scale and the region included in a quantitative comparison. Use comparable views or explain differences; independent camera fitting can disguise geometric differences.
- Link close-ups to an overview with unambiguous locator boxes and panel references. Preserve entity colours across views; distinguish an entity key from a key for model/configuration outlines. Do not use unlabeled changes of orientation to imply structural agreement.
- Do not conflate sequence position, chain/domain identity, confidence, predicted error and observed residual. Give each mapping a local label/key with units where relevant. A sequence-position rainbow convention is not evidence that rainbow is appropriate for general scalar magnitude.
- If low-confidence regions, residues, observations or background are omitted, define the rule and provide access to the unfiltered record. Display filtering must not silently change the statistical denominator or make a model look more accurate.
- For microscopy, define representative-image selection, scale bars, channels, acquisition/display adjustments and replicate unit. Apply comparable display ranges for image comparisons; a montage does not establish a sampling distribution.

## Link to functional measurements

Bind sample size, replicate unit, interval definition and tests to the specific quantitative panels they describe; a structural panel does not inherit the biological replicate count of a response curve. Define significance symbols and comparison families rather than guessing conventional star thresholds. For dose-response plots, identify normalization and fitted versus observed values. A zero-dose control cannot occupy an ordinary logarithmic coordinate: use a clearly labeled separate control slot/panel or a justified, named transformation, never an unexplained pseudo-position.

## Event-aligned temporal matrices and trial summaries

Read this section when many objects or trials share a meaningful time reference; visual rationale and contrasts are in [the Nature/Science temporal review](reference-observations-2026-11-04-temporal-ordering.md). These rules also apply to repeated sensor, behavioural or assay measurements when the same input conditions hold.

- Require object, trial and independent-subject/session identifiers where applicable, timestamps, event times, measurement units and sampling/bin definitions. State what a heatmap row represents. Align to the declared event by keys; mark gaps and unequal observation windows, and do not time-warp them into equal lengths without a documented transformation.
- Distinguish an event raster (individual timestamps) from binned counts/rates or continuous-response heatmaps. Do not infer event times from binned means. A rate needs a known exposure/bin duration; irregular bins need faithful numeric geometry or an explicitly transformed axis. Save smoothing, aggregation and normalization separately from styling.
- Decide whether the comparison requires identity-preserving rows or only compares distributions. For the former, compute one ordering from a declared reference and reuse its ID vector across conditions. Independently sorted actual/null views may be appropriate for distributional questions, but must be labelled unpaired in row order. Never silently claim corresponding cells are matched.
- Name the sorting statistic, reference data and tie handling. Peak sorting can produce a diagonal by construction; it is a display choice, not proof of a reproducible temporal sequence. Such a claim needs an appropriate independent-trial/held-out or justified null analysis; do not invent either from the image. Keep sorting/selection fitted within the relevant training split when used in validation.
- Declare normalization scope (row, panel or global), baseline/denominator and handling of zero or near-zero denominators. Row-normalized patterns cannot establish between-row absolute amplitude. Pair with raw-unit summaries when magnitude is part of the question; choose a sequential palette for non-negative magnitude or a diverging scale for a defined signed deviation. Provide a numeric key, units and missing-data colour.
- Separate single-trial examples, trial averages, cell summaries and independent-subject summaries. A pooled average can hide timing variability; add the trial view only when it answers that question. Preserve selection rules and give proportion numerators/denominators, especially with few trials. Do not manufacture intervals or treat cells/time bins as independent subjects.
- In R, prepare one keyed long table and a separate ordering/summary table; use appropriate tile/rectangle or event-segment layers and aligned summaries with shared time limits. Keep event windows, bin widths, ordering, limits and scales in project configuration. These are project extensions, not analysis functions already supplied by the scaffold.
- At final size, inspect thin rows, time-zero markers, group separators, raw/fitted overlays and local keys; omit internal cell grids when they obscure patterns. For very dense matrices, documented rasterization can coexist with vector labels. Verify cell/row mappings and colour/grayscale visibility, not merely whether the resulting image looks smooth.

## Deliver and verify

Keep diagrams and labels editable. Molecular renderings and microscopy may be raster within a vector composite; retain scene settings or original calibrated images and record effective resolution at publication size. An SVG container alone does not make embedded pixels editable or recover 3D geometry. Do not install structural-rendering software for a reference-only learning task.

At final size, inspect arrows, tiny residue/site labels, overlapping outlines, crop boundaries, colour-legend semantics and correspondence between representative images and summary data. Confirm that every uncertainty marker is defined and that selected examples do not imply a stronger result than the quantitative evidence supports.
