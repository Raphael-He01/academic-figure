# RStudio implementation with reproducible R code

### Mixed-script export check

Check Greek letters and super/subscripts in both the rendered PDF and extracted text. A local Quartz test with PingFang SC produced missing-glyph boxes despite embedded font programs. Cairo failed to initialize on that macOS setup because its X11 libraries were unavailable. The matching ragg PNG rendered the test string visibly.

For a self-contained svglite SVG, try the optional draft exporter below with an installed Chromium browser and PyMuPDF. On macOS use the executable inside the application bundle. To supply glyphs for specific labels, also install fontTools and add `--label "中文 α β μ x² H₂O" --font /path/to/embeddable.ttf`. Repeat `--label` for each exact SVG text element you need to verify. Choose a font licensed for embedding. The command uses a temporary font subset for those labels and checks their exact PDF text. The exported draft retains a pending status.

```sh
python3 scripts/print_svg_pdf.py figure.svg draft.pdf --browser /path/to/chromium
```

One macOS Chrome run preserved the map clipping, dashed guides, transparent bands and colour bars in four example figures. A mixed-script title in the full statistical figure had matching glyphs and extractable text with the selected font. Verify exact labels, actual size, linework, fills, image resources and any collision flags on every export. Chromium can round page dimensions. Use a device that meets the target tolerance.

Use `scripts/experimental_svglite_pdf.py` for diagnosis of the separate PyMuPDF conversion path. It inlines selected svglite style defaults and blocks clipping, dashes, opacity, masking, filters and inherited glyph paint by default. `--allow-unsupported` generates diagnostic drafts with the detected features listed in the output record.

### Optional scaffold components

For supported inputs, project files `R/plot_forest.R`, `R/plot_ternary.R`, and `R/plot_spectra_network.R` offer basic plotting components, including coordinate-linked overview/detail views. Supply and verify units, interval semantics, coordinate system and documented edges; these components do not fit models, infer roads, or replace final-size review. Configure group colour roles via the pinned card, but verify each actual mark; the example heatmap has a separate meaningful diverging scale. To bind a single data file, figure and caption by file identity, use `scripts/figure_evidence.py` from the skill; changed files invalidate the record, but unchanged hashes do not verify numeric consistency or scientific interpretation.

## Execute in RStudio

For the R production route, execute saved R code in RStudio. Choose the production application under the active skill’s [使用范围](../SKILL.md#使用范围). For an Origin figure, record the native project and checks under the [Origin workflow](origin-handoff.md).

1. Reuse the intended RStudio project and its R environment. Open its existing `.Rproj`, or establish a project for a new folder without overwriting user files or global preferences. Confirm project root, selected R, dependency paths and required fonts before rendering; do not reuse an unrelated RStudio session unnoticed.
2. Save transformations, style, plotting and export code in project files, then execute the entrypoint through RStudio's Source/Console in that project. For the bundled example, use `source("R/run_example.R")` from the project root after the required dependencies are available. Keep necessary commands in the saved code, not only transient console history.
3. Show the relevant plot object in Plots, or an appropriate Viewer preview, and inspect the actual exported files at final size. A plot-pane thumbnail is not final-size export verification. Use an external file viewer when needed for export QA; it does not replace RStudio creation.
4. Record the project/entrypoint, R and RStudio versions when available, session/dependency information, observed execution outcome and preview/export checks. Claim RStudio execution only after observing the actual session run; the app being open, a file timestamp or a terminal log alone is insufficient.
5. Shell/Python utilities may scaffold, preprocess or inspect files, and independent command-line tests may supplement QA. For the explicit test profile, saved R may run through Rscript for automated regression; record that limited scope. Such a run does not establish GUI execution or final figure acceptance. They must not become the sole interactive figure-production run. If RStudio access is blocked, prepare the source files and identify the missing capability; use the authorized Origin route if suitable, or report the actual blocker; never claim an unobserved RStudio run.

These execution steps do not apply to reference-only learning or documentation updates. Do not launch RStudio or rerender existing figures just to save a preference.

## Project structure

Keep a stable separation:

```text
data/                 immutable or generated inputs plus dictionary
R/                    validation, processing, plotting, export
output/pdf/           vector master
output/svg/           editable interchange
output/png/           screen/review copy
output/tiff/          raster fallback when required
output/qa/            validation, manifest, session and palette checks
docs/                 legend, Results draft, methods/provenance
renv.lock             resolved package versions
```

Use relative paths inside a project. Do not set a global working directory in reusable scripts.

For an Excel handoff, the [workbook builder](../assets/r-template/scripts/build_example_workbook.mjs) uses the bundled `@oai/artifact-tool` when available. Use the [R read-back check](../assets/r-template/R/validate_excel_handoff.R) to compare the workbook with its source CSVs. Keep the CSV and saved R transformations as the numeric source.

## Central configuration

Put these in one list or structured object:

- final width and height in mm;
- raster DPI per intended output;
- font family and role-specific point sizes;
- axis, grid, data, error-bar and reference-line widths;
- point size, alpha, jitter seed, error-bar cap width;
- panel margins, spacing and layout ratios;
- ordered group levels, colors, shapes and line types;
- continuous/diverging palette, center, limits, clipping and missing color;
- output directories and file stem.

For reference-derived designs, also configure `profile` (journal/report), title visibility, panel design/relative sizes, grid direction, shared-legend position, interval definitions and any axis transforms. Use `patchwork` design areas/relative widths for unequal panel roles and collect legends only when mappings agree. These are extension points, not fields already implemented in every bundled template.

Apply one semantic variable mapping consistently across every panel. Combine color with shape or line type when group recognition matters.

## Dependency policy

Restore an existing `renv.lock` before installing. Prefer CRAN/Bioconductor binaries compatible with the installed R. The default minimal set is:

- `ggplot2`: graphics grammar;
- `patchwork`: multi-panel composition;
- `ggdist`: distributions and uncertainty;
- `ggrepel`: collision-resistant direct labels;
- `colorspace`: palette design/simulation;
- `ragg`: high-quality PNG/TIFF;
- `svglite`: editable SVG;
- `readxl`: Excel input.

`viridisLite` commonly arrives through `scales` and ggplot2 already exposes viridis scales. `cowplot` overlaps patchwork. Add `ComplexHeatmap` only for sophisticated annotations, splits, clustering, or multiple linked heatmaps.

## Rendering

For a new project, use the existing scaffold; for a revision, reuse its saved entrypoint and configuration rather than regenerating the project. Confirm runtime/font availability in the intended RStudio session, but do not reinstall unchanged working dependencies or repeat broad environment inventories. Retain exact input, processing/parameter and environment versions when reusing analysis results; changed provenance or failed checks invalidate that reuse.

Inspect a representative high-density or difficult panel at its planned physical size before assembling expensive outputs. This is an early diagnostic, not whole-figure acceptance: every panel, the final assembly and requested format still need inspection. During refinement, render only the relevant draft/master formats; after layout and mappings settle, generate the requested delivery set. Any subsequent change must regenerate affected exports and checks under [rendered QA](rendered-qa.md). Never downsample, drop tails or substitute simulated data just to speed up a draft without a declared, appropriate analysis purpose.

Design at final physical size. Prefer Quartz PDF on macOS when it yields the configured installed font; otherwise use Cairo PDF when available. Use `svglite` for SVG and `ragg` for PNG/TIFF. After export:

1. verify page/pixel dimensions and format signatures;
2. inspect font names and embedding/substitution in PDF;
3. render the PDF to an image and inspect at 100% and final-size equivalent;
4. inspect SVG text/paths and raster transparency/background;
5. compare panel labels, legend keys, line weights and colorbar direction across formats.

Do not claim that a file is editable merely because it is vector: outlined text is not editable text, and inserted raster content remains raster.

## Statistical communication

Label intervals by name. Distinguish SD, SE, confidence intervals, credible intervals, predictive quantiles, spatial IQR and ranges. When observations are dependent, report what `n` counts and the dependence structure; do not label repeated days, fields or technical measurements as independent replicates. Plot derived summaries only after preserving the underlying observations and analysis logic.

## Release verification additions (2026-11-16)

New scaffolds pin the current colour registry and resolve a named card through `figure_config(palette_id = "rose_mist")`; this applies categorical colours only. Install `jsonlite` with the project dependencies. Export manifests now record device, card version/mapping and pending acceptance. From the project root, run `python3 <installed-skill>/scripts/reconcile_export_status.py output/qa/export_manifest.csv` to reconcile file/font evidence. Mechanical success leaves scientific/visual acceptance pending; base-PDF Helvetica is never presumed embedded. For the host check and a repair in the actual project library, use [first-run setup](first-run.md). No production run is implied by a dependency check.

Export-status reconciliation now binds to `file_sha256`; unbound or changed-file human reviews revert to pending. Paths are inferred relative to the manifest's project root (or `--project-root`), and declared dimensions are audited. A companion `render_colour_review.py` can generate full-raster CVD/gray diagnostic copies through installed R colorspace, with source/output hashes; these copies never auto-approve accessibility.
