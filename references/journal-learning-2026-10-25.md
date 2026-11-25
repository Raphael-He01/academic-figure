# Journal learning and helper audit — 2026-10-25

Scope: public figure-design learning, not source-data analysis, model training, reproduction of findings or a fresh journal-submission standards audit. Summaries only; no original figure, caption, data or screenshot was copied into the skill. Two figures were visually reviewed with captions in this initial batch; P1 was resolved in the separately recorded follow-up below. Exact font, point size, HEX, physical print dimensions, original vector structure, colour-vision accessibility and source-data validity were not tested.

## J1 — Sample provenance, embedding and composition

**Source:** Litviňuková et al., *Cells of the adult human heart*, **Nature** 588, 466–472 (2020), DOI `10.1038/s41586-020-2797-4`. [Article](https://www.nature.com/articles/s41586-020-2797-4) · [Fig. 1](https://www.nature.com/articles/s41586-020-2797-4/figures/1). Official metadata distinguishes published 2020-09-24, version of record 2020-11-23 and issue date 2020-12-17.

**Evidence:** dsh suggested the paper after reading its caption. The primary agent then viewed the whole figure in the browser, read the complete figure caption and checked article metadata plus the relevant main-text population description. Public official article/figure pages were accessible. Source data and supplementary tables were not analysed.

**Observed design:** a wide asymmetric composite gives the large labelled embedding the right side. The left/centre hold a sampling/processing diagram, compact donor overview, two aligned percentage bars and a microscopy strip. Thus the reading structure is not a simple row of five equal panels. Cell identity colours connect the embedding and composition key; channel labels beneath the micrographs use their own meanings. Sparse quantitative grids, panel letters, direct cluster labels and nearby marker names reduce repeated legend lookup. Black microscopy fields remain distinct from the white analytical background; scale bars are visible and defined in the caption.

**Interpretation boundary:** the donor diagram shows age, sex and contribution to cell/nucleus datasets, not a quantitative cell-count plot. The embedding combines cells and nuclei, whereas the regional composition panel is nuclei-based. Its percentage axis has a clear denominator concept but no donor-level distribution in that panel. This does not show that donor variation or microscopy replication was absent from the study: the caption explicitly points to methods for reproducibility details.

**Transfer:** connect sampling provenance to the plotted population; carry identity colours only between semantically matching panels; declare assay subsets and independent sample units; complement an embedding with quantitative evidence when the claim needs it. Do not reproduce the anatomical illustration, marker list or particular composite arrangement. Do not infer abundance from cluster footprint or treat an aggregate proportion as donor-level inference.

## J2 — Fixed embeddings, different attributes

**Source:** Becht et al., *Dimensionality reduction for visualizing single-cell data using UMAP*, **Nature Biotechnology** 37, 38–44 (2019), DOI `10.1038/nbt.4314`; online/version of record 2018-12-03. [Article](https://www.nature.com/articles/nbt.4314) · [Fig. 1](https://www.nature.com/articles/nbt.4314/figures/1). This is not Nature main journal.

**Evidence:** an internal reviewer visually inspected the full figure in two browser regions, read the caption and checked metadata on 2026-10-25. The official figure page was public; the article body was a subscription preview. No access restriction was bypassed, data downloaded or algorithm rerun.

**Observed design:** paired UMAP/t-SNE views separately show cell identity and tissue; marker-expression panels form a method-by-feature matrix with consistent feature order. White backgrounds, small points, panel letters and row/column labels carry the hierarchy, without dense numeric coordinate grids. Category keys are separate from expression encoding; a blue–pale–red expression scheme denotes low, intermediate and high expression in the caption, not a signed biological zero.

**Transfer:** retain the same ID-keyed coordinates while changing metadata; separate categorical and quantitative palettes; make repeated comparisons easy through consistent feature order and mapping. For new data, provide actual expression limits/transforms rather than merely qualitative low/high labels. Treat small points, many category colours and dense labels as QA targets, not an accessibility verdict from the screenshot. Numeric range, per-panel n and original print properties cannot be reconstructed from this figure page alone.

**Method qualification:** the article links Kobak & Linderman, *Initialization is critical for preserving global data structure in both t-SNE and UMAP*, Nature Biotechnology 39, 156–157 (2021), DOI [10.1038/s41587-020-00809-z](https://www.nature.com/articles/s41587-020-00809-z). The reviewer read its public discussion of initialization effects. It supports recording initialization/seed and limiting comparative claims; it was not counted as a visually reviewed figure. Do not save “UMAP always preserves global structure better” as a design rule.

## P1 — Initially pending; resolved in the later follow-up

dsh also returned Luecken et al., *Benchmarking atlas-level data integration in single-cell genomics*, Nature Methods 19, 41–50 (2022; online 2021-12-23), DOI `10.1038/s41592-021-01336-8`, [Fig. 2](https://www.nature.com/articles/s41592-021-01336-8/figures/2). In this initial batch the helper reported reading the caption and checking metadata, but independent image inspection was incomplete; its layout, weighting and ranking claims were not adopted. A planned reviewer reached its usage limit. It was not counted among the two verified examples above.

**Later review on 2026-10-25:** the primary agent inspected the publisher image, caption and relevant aggregation/visualization methods. The resolved evidence, retained unknowns and accepted rules are recorded as B1 in [the survival/benchmark follow-up](journal-learning-2026-10-25-survival-benchmark.md). This does not retroactively change the initial helper-only evidence status.

## What was corrected before adoption

- Reading image dimensions or an HTTP success response is not seeing the image. Browser inspection can verify a public image without saving it into the skill; downloading is not the only route.
- The helper's claim of displayed donor cell counts was corrected against J1. Shared colours do not imply the same assay denominator across all panels.
- “Many cells must mean severe overplotting” and “many colours must be colour-blind unfriendly” were not retained as findings. Actual rendering and accessibility checks are required. Neither doubling information density nor token savings was measured.
- In P1, the helper described separate identity/batch encodings but also claimed the same cell-type colours across those views. This internal inconsistency is a reason for verification, not a rule to preserve.
- A missing detail in a caption is not evidence that the whole study omitted it. Keep “not checked” distinct from “not reported anywhere”.

## Reuse

Operational rules: [embedding/atlas figures](embedding-atlas-figures.md). Delegation protocol: [assisted journal learning](assisted-journal-learning.md). Existing [Nature/Science cases](nature-science-learning-2026-10-17.md) remain available; no new Science figure was visually reviewed here.

**Hypothetical application, not an executed plot:** for a supplied single-cell coordinate CSV and donor metadata, the skill would first verify unique cell IDs and donor/assay counts, reuse one coordinate table for cell-type and batch views, and add donor-level composition or a marker summary only if needed for the question. It would choose appropriate separate palettes, execute the saved R code in RStudio, inspect exports at final size and write a caption from real computed values. No data or result is invented in this example.
