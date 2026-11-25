# Temporal matrices: alignment, ordering and response magnitude

Reviewed 2026-11-04 for a gap in dense temporal-response displays. Read when selecting event-aligned heatmaps, trial views or linked response summaries. Editorial notes: Raphael He; AI-assisted source review and rule drafting. Research and artwork remain attributed to the paper authors. This record does not reproduce their analyses or create new scientific figures.

## Source inventory and actual access

| ID | Source | Version and visual scope |
|---|---|---|
| T1 | Pastalkova et al., *Internally Generated Cell Assembly Sequences in the Rat Hippocampus*, **Science** 321(5894), 1322–1327 (2008), DOI [10.1126/science.1159775](https://doi.org/10.1126/science.1159775); [public PMC manuscript, Figure 5](https://pmc.ncbi.nlm.nih.gov/articles/PMC2570043/) | Final publication dated 2008-09-05; the inspected version is the author manuscript available in PMC from 2008-10-20. Complete figure, caption and adjacent behavioural-comparison text inspected; focused reading of B/C and the counts in D. |
| T2 | Tsao et al., *Integrating time from experience in the lateral entorhinal cortex*, **Nature** 561, 57–62 (2018), DOI [10.1038/s41586-018-0459-6](https://www.nature.com/articles/s41586-018-0459-6); [Extended Data Figure 3](https://www.nature.com/articles/s41586-018-0459-6/figures/8) | Online 2018-08-29. Complete publisher extended-data image and caption inspected, with focused reading of a/b heatmaps and l's response/waveform views. This is an extended-data figure from Nature main, not main Figure 8. |

- dsh was used through its desktop interface for **discovery only**. It returned the T2 article as an unviewed lead, without a confirmed figure number. Its reported total was two queries and three failed page-read attempts; its UI showed completion in 1 min 52 s, six steps and 103K tokens. These counters do not prove savings against a different task. It did not supply inspected images or a verified Science figure.
- Primary verification identified T2's actual figure via the publisher's link, and independently located T1's public author manuscript. Both ordinary HTTPS pages and their linked image assets were retrieved successfully; no access challenge was solved or bypassed. The helper's mention of a different Nature-family article was not adopted. No second screenshot task was needed because readable source assets were available.
- T1 image: 600 × 772 px; SHA-256 `ae6052829a04b28cec8b961df27293c9640f71599ebfae886a25de561102349f`. T2 image: 1953 × 1612 px; SHA-256 `d57c171bea0b33faec60c605f10cce1fbf3c70d0975dd7e851fb057567f161d9`.
- Labels: **Visible** = inspected pixels; **Caption/context** = what the paper states, not recomputation; **Proposal** = our transferable design reasoning; **Unknown** = evidence not established. Only summaries and links enter the skill. No source image, data or full caption is bundled.

## T1 — preserve identity across conditions and single-trial evidence

### Panel roles and chart-choice rationale

| Panels | Visible structure | Possible communication reason, inferred |
|---|---|---|
| A | Two example-cell heatmaps, with trial classes separated by thin white rules | Shows whether one example changes across trial classes while retaining within-class variation; a single average trace would suppress that variation. |
| B | Two equally sized population heatmaps on a shared time range | Permits corresponding rows to be compared across conditions; alignment only works when the same cells really occupy those rows. |
| C | One event-locked trial displayed below the population view | Tests whether a selected trial resembles the reference pattern; a single example cannot establish population reliability. |
| D | Three zero-based percentage bars, each annotated with a success/total count | Keeps small denominators visible beside apparent high percentages; it is a summary across subjects, not another heatmap. |

### Eight-dimension evidence card

1. **Purpose/data:** the figure links examples, a population reference, one trial and a numerical summary. **Caption/context:** B uses 43 simultaneously recorded cells ordered using correct-left peak timing; that order is retained for the other condition and C. This ordering provenance is central to interpretation.
2. **Layout:** A and B use paired columns; C reuses the left column footprint and D occupies the right. Large regular plot areas make rows and time positions easier to follow. **Proposal:** keep the reference/comparison matrices geometrically matched and use a subordinate summary only when it answers a separate question; do not force this exact four-part composition.
3. **Typography/marks:** bold letters and short panel headings outrank compact axes. Heatmap cells have no internal grid, avoiding a competing lattice; white horizontal rules separate trial groups in A. **Unknown:** original typeface, pt sizes, line widths, smoothing kernel and sampling/binning resolution.
4. **Colour:** low values appear dark blue, with cyan/green/yellow/red highlights. **Adopt:** background-to-signal contrast exposes localized activity. **Reject as a default:** a multihue ramp for an ordered non-negative rate can create artificial visual boundaries and weak grayscale ordering. Prefer a tested sequential palette, or a diverging scale only for a defined signed baseline.
5. **Legends/annotations:** conditions and time units are local; a reported correlation appears in C; D includes visible small denominators. **Unknown:** the full numerical colour scale and normalization formula are not established by this image/caption. Do not infer a colour-to-rate conversion or attach significance to the displayed correlation. A new figure needs an explicit colourbar and preprocessing definition.
6. **Scientific axes:** time is relative to wheel running, while rows change meaning between trials in A and cells in B/C. **Caption/context:** C is a single error trial; D summarizes prediction outcomes. **Proposal:** name the row unit in each panel, keep subject/cell/trial counts separate and avoid interpreting a sample-sorted diagonal alone as independent evidence of a sequence.
7. **Scale/export:** the available raster is only 600 × 772 px. Text and broad patterns are readable, but exact cell boundaries, small labels and original resolution cannot be certified at print size. No vector master, embedded-font audit or colour-vision/grayscale test was available. Magnification cannot recover lost detail.
8. **Transfer:** adopt fixed keyed ordering across paired conditions and explicit denominators. Adapt the palette and legend, add raw-unit summaries when amplitude comparisons matter, and retain the example-selection rule. Reject independently re-sorting every comparison to obtain a stronger diagonal or making all small-denominator percentages appear equally certain.

## T2 — show a sorted pattern alongside a stated null comparison

### Panel roles and chart-choice rationale

| Panels | Visible structure | Possible communication reason, inferred |
|---|---|---|
| a–b | Three-row stacks of actual/shuffled heatmap pairs, split into trial and intertrial blocks | Makes differences in temporal organization inspectable while keeping each period's time scale explicit; a clean diagonal is not the only information shown. |
| c/f | Two sets of compact group point-and-summary panels | Exposes individual subject values instead of showing only a pooled cell percentage. |
| d–e/g–h | Aligned small histograms for timing and information metrics | Shows where a summary comes from and whether a distribution is concentrated or broad; each metric retains its own axis. |
| i | Two rows of compact predictor sketches with a highlighted component | Makes model-input assumptions visible before interpreting fit output. These are explanatory constructions, not measured responses. |
| j–k | Fit-quality histogram and grouped selectivity points | Provides quantitative context beyond attractive example fits. |
| l | Four observed/fitted response rows with adjacent waveform comparisons | Keeps raw response, model prediction and recording-stability context distinct; a waveform inset does not independently validate the model. |

### Eight-dimension evidence card

1. **Purpose/data:** a/b address temporal pattern; c–h quantify selected properties; i–l expose model construction and fit. **Caption/context:** heatmap rows are peak-time ordered; actual and shuffled panels do not preserve cell identity. Circles in summary panels denote animals and summary intervals are SEM. Thus a row-to-row paired comparison across the two heatmaps would be invalid here.
2. **Layout:** large heatmap blocks lead at left; model explanation and example fits occupy the right; compact summaries sit underneath the relevant comparisons. Trial and intertrial blocks have different time ranges. **Proposal:** make row-preserving comparisons and distribution-level null comparisons visibly distinguishable; a publication's many small panels should not become the default for a simpler question.
3. **Typography/lines:** clear bold letters and local headings distinguish blocks; outlines surround heatmaps but internal cell grids are omitted. Sparse ticks reduce clutter. In l, grey measured traces remain visible around a blue fitted line. Small waveform scale bars have their own units. **Unknown:** exact fonts, line widths and original label sizes.
4. **Colour:** a/b use a white-to-blue intensity scale; purple, light blue and gold identify brain areas in summaries. i uses a single coloured predictor against grey alternatives; l uses separate colours for prediction and waveform comparisons. **Mechanism:** a continuous scale and local categorical keys allocate colour to different tasks. **Proposal:** preserve those semantic separations, not the exact hues; light categories and thin lines require final-size contrast checks.
5. **Legends/annotations:** heatmap bars run from zero to a labelled maximum; row and time titles are present, while area identity for the stacked heatmaps depends on caption context. **Proposal:** put short area labels beside each block and explicitly identify independent sorting. A maximum label alone does not tell a new reader whether scaling was per cell, per panel or global; the exact scope remains unverified in this review.
6. **Scientific axes:** histogram metrics include time and information units; rate traces and waveform units are distinct. **Proposal:** use relative event time consistently without silently stretching unequal intervals, document sorting/normalization and keep independent subjects visible. A shuffled panel has inferential value only when the null construction is justified; it is not a generic aesthetic control to invent.
7. **Scale/export:** the 1953 × 1612 web raster supports reading the full layout and key details. It does not establish physical dimensions, original vector content, print DPI or embedded fonts. Some rows and faint marks are dense; no final-placement or colour-vision acceptance was performed.
8. **Transfer:** adopt sequential magnitude colour, paired comparison blocks with explicit identity semantics, visible subject-level summaries and restrained model-versus-data overlays. Adapt density and panel count to the new figure. Reject treating every sorted blue diagonal as evidence, inferring amplitude from an undefined maximum scale, or mistaking the schematic predictor sketches for data.

## Synthesis: decisions to carry into a new project

| Observation → transferable mechanism | Eligibility and R implementation | Future acceptance evidence |
|---|---|---|
| Same rows in paired comparisons enable meaningful visual tracking | Verified object IDs and one ordering table reused by ggplot factor levels; experimental rules specify when separate sorting is permissible | Check ordered ID vectors, matrix dimensions and unmatched IDs before plotting |
| Ordering makes timing readable but can manufacture apparent regularity | Store the sorting statistic, source condition and tie rule in processing; a claim about reproducible order needs appropriate independent data/null analysis | Separate the display operation from evidence for temporal structure; do not infer a validation result from the heatmap |
| Relative activity and absolute amplitude answer different questions | Store normalization scope, denominator/baseline and zero handling; keep raw units for an amplitude panel when supported | Same colour does not imply same absolute rate after row normalization; check values and displayed scale |
| Intensity, category and fitted-versus-measured status need distinct keys | Existing `cfg$group_colors`, line types, point sizes and panel spacing can supply style; new project parameters define time bins, event window and sorting | Inspect actual heatmap marks, keys and linked summaries at final size, with grayscale/colour-vision views |
| Small proportions need visible denominators | Derive numerator/denominator from the correct subject/trial grouping; only show intervals supported by an appropriate analysis | Reconcile counts and distinguish subject replication from repeated trials/cells |

The substantive delta belongs in [experimental evidence rules](experimental-evidence-figures.md), reached through [data-to-chart selection](data-and-chart-selection.md). Binning, normalization, sorting and intervals remain project-specific analysis; the bundled template has not gained an automatic neural-data analysis pipeline.

## Application checks and status

- **Eligible hypothetical task:** timestamped sensor responses with object/trial IDs, known event times, units and two conditions. Validate joins and sampling; align to the declared event; choose a keyed temporal heatmap plus a supported summary if it adds evidence. Fix a declared ordering for matched conditions and label any normalized scale. Run saved R in RStudio and inspect actual exports when production is requested.
- **Missing-input counterexample:** only a screenshot or a table of per-group means is supplied. Do not reconstruct events, trial IDs, a sequence order, a heatmap distribution or inferential bands. Use supported mean/estimate displays with explicit missing information, or request the input that changes the intended comparison.
- **Completed:** full-image and caption/context inspection, focused reading, source metadata/checksum capture, useful-delta comparison, rule integration and these two decision walkthroughs. Original scientific results, normalization details not stated in the inspected material, new R execution and original export quality remain unverified.
- **Batch boundary:** these two figures complete the selected scope. No pending image retrieval remains; source-method unknowns above are not hidden. A later continuation should choose a different communication gap or explicitly resolve one of those unknowns rather than rediscover the same articles.
