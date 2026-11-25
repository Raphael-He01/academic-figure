# Embedding and single-cell atlas figures

Use for UMAP/t-SNE views and composites linking sample provenance, cell identities, expression, composition and experimental validation. Design evidence and limits are in [the 2026-10-25 journal record](journal-learning-2026-10-25.md). These rules do not implement an embedding algorithm or certify a biological annotation.

When embeddings accompany a ranked metric matrix, also use [benchmark rules](benchmark-figures.md) and the [completed Fig. 2 review](journal-learning-2026-10-25-survival-benchmark.md). Preserve method/configuration IDs, score/rank semantics and metric coverage; diagnostic geometry alone is not a quantitative ranking.

## Establish comparable views

- Keep a keyed coordinate table (`cell_id`, embedding coordinates, method/configuration ID) separate from metadata. Recolour the same coordinates for another attribute; do not recompute the layout for each colour mapping. Check uniqueness and join completeness before plotting.
- A method-by-feature matrix is useful only for a defined comparison. Hold sample subset, preprocessing and feature order constant where the scientific question requires it; disclose any differences. Different methods' axes are not directly comparable numerical coordinates.
- Record preprocessing, initialization, seed, key hyperparameters and software version when available. Document stability checks before claiming robust layout or a method advantage. A published comparison is not a timeless ranking; check linked corrections/discussions when interpreting such claims.
- Label the embedding method even when axis ticks carry no physical meaning. Keep aspect ratio consistent within a reused embedding. Do not infer biological distance, abundance, discrete populations or causal relationships just from island area, separation or arrangement.

## Separate colour meanings

- Bind category colours to named levels. Cell type, tissue, batch and donor are different variables: each needs its own labelled key. The same coordinates do not imply the same palette across unrelated variables.
- For continuous expression, state measurement/normalization/transform, numeric limits, missing value treatment and clipping. Non-negative magnitude normally calls for a sequential palette; use a diverging palette only when a scientific centre exists. A paper's blue–white–red scheme does not make middle expression equal to zero.
- Compare the same marker across methods with the same mapping where justified. Different markers may need independent ranges, but disclose this and avoid implying absolute cross-marker comparability.
- Inspect small/rare groups, overlap, label collisions and colour discrimination at final size. If using sampling, rasterization, transparency or reordered points, record the procedure and retained count. Check the actual marks under grayscale/colour-vision simulations before claiming accessibility; a legend swatch or many points alone does not establish failure or success.

## Connect provenance and evidence without conflating them

- Select panels by question: sampling/workflow, cohort overview, embedding, quantitative composition, marker summary and independent assay have different roles. A wide atlas composite is one option, not a five-panel template.
- Report independent donor/biological replicate counts separately from the number of cells, nuclei, images or technical measurements. A donor icon is not a count of contributed cells. Preserve sample/assay IDs so the analysis can support donor-level inference where appropriate.
- State the analysis population for every summary: nuclei-only, cells-only, enriched subset or combined. Do not assume the composition panel has the embedding's denominator. Percentages need a clear denominator and missing/unassigned categories; avoid interpreting aggregate captured-cell fractions as unbiased tissue abundance.
- Shared identity colours may connect embedding clusters to a composition plot; keep assay channels separate from cell-identity colours. Representative microscopy needs marker/channel names, calibrated scale bars, selection criteria and reproducibility details; link to methods when those details are elsewhere.
- A missing error bar or replicate number in one panel does not prove the paper lacked replication. Check the caption's methods pointer before evaluating reproducibility. Conversely, a representative image alone does not establish effect size or population uncertainty.

## RStudio implementation and QA

Use the established RStudio workflow and existing packages; no new single-cell package is required merely to plot supplied coordinates. Join metadata by ID, create a named encoding configuration, build the needed ggplot2 panels and assemble with the existing layout tools. Keep calculated proportions/marker summaries in a separate analysis table. Export editable vector labels/lines; dense point layers may be rasterized only with a recorded reason and adequate effective resolution.

Before delivery: compare ID sets and denominators; confirm no silent dropped joins; check shared coordinates, scales and category order; inspect dense regions and rare groups; verify legends, units/transform, donor and cell counts, accessibility and final-size export. Do not claim that a visually pleasing embedding validates the model or the underlying biology.

For broader genome/protein composites that connect prompt/generation embeddings, cluster summaries, association plots, sequence-domain maps, structure comparisons and functional assays, read the [2026-11-02 user-reference review](reference-observations-2026-11-02-genome-protein-composites.md). Transfer only the evidence sequence and scale/legend rules relevant to the current question; do not copy the reference's full panel inventory or infer the biological validity of its displayed results.
