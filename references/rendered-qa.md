# Unified rendered-figure QA

Read for figure production, revision and final delivery. This is the single detailed QA workflow; the existing export verifier remains part of it. Reference-only skill learning does not require generating a figure.

## Execution order: four layers

1. **Evidence and saved source.** Validate the data contract, units, denominators, exclusions, pairing, transformations and named intervals. For R, parse saved code; for Origin, inspect native data bindings, saved analysis/settings and any automation used. In both routes inspect data-to-mark mappings, scale guards, interpolation ordering, random seeds where relevant and export settings. Reconcile plotted data as described below. Missing statistics remain missing. No absent upstream source validator is implied to be running.
2. **Measured layout.** For R patchworks, execute saved code in RStudio and measure actual plot-area rectangles through `panel_alignment.R`, then audit their JSON. For Origin use independently verified native page/layer measurements or a measured manifest in the same schema; the R adapter cannot measure an Origin project. Keep unavailable mechanical alignment NOT AUDITABLE, perform a scoped visual/manual check, and do not substitute one for the other.
3. **Files and geometry.** Run the existing `scripts/verify_exports.py`, then the applicable font, text-size, collision and SVG checks below on the same exported revision. Preserve their reports under the project's existing `output/qa/`.
4. **Visual and scientific review.** Inspect each panel, the assembled figure, dense details and its actual manuscript placement. Compare to the supplied data and caption; review all machine warnings. Repair the authoritative R source or Origin project, rerun/export in the selected application and regenerate affected checks.

Allow at most two repair cycles in one QA pass. Remaining failures require a specific unresolved-issue report and author review; reaching the cycle limit never turns a failure into a pass. Without visual capability, mark visual review pending for a human rather than inferring it from file tests.

## Reuse evidence only within its revision scope

Compare inputs, saved code/configuration, dependency/font/device information, export size and output revision before reusing a prior result. Keep the decision in the existing QA notes/manifest; do not create a parallel audit system. A selective rerun saves unchanged analysis work, not the final-file checks required for newly exported files.

| Change | What becomes stale |
|---|---|
| Data, joins, filters, statistics, transformations or model parameters | Data-to-mark reconciliation and affected claims/intervals, plus affected rendered/layout/file/visual evidence |
| Scale, palette, mark/label mapping, font, geometry or physical placement | Relevant semantic checks, alignment where applicable, colour/readability and affected mechanical/file checks; refresh the actual visual review |
| External caption/Results only, with identical figure bytes | Claim/statistic/unit/caption consistency; figure-file evidence may be retained with its exact input revision. Text embedded in artwork requires rerendering and affected QA |
| Format, device or export settings only | All applicable checks for the new files and cross-format appearance; a prior device's geometry/font result does not transfer automatically |

After any figure rerender, verify each new file's integrity and applicable text/font/collision evidence and inspect the final assembly at its intended size. Preserve prior data checks only when their inputs/methods are unchanged and explicitly identified. A pending or failed gate stays pending/failed until its evidence changes; restarting the pass count does not resolve it.

## Alignment gate

The R measurement helper requires `patchwork`, `grid` and `jsonlite`; the JSON auditor uses Python's standard library. Source the installed `scripts/qa/panel_alignment.R` from the saved project entrypoint, then call `require_patchwork_panel_alignment()` with the final export dimensions, manifest/report paths, comparable groups and any narrow exemptions.

Patchwork 1.3 can store panel tracks as `null` units. Converting those tracks outside their laid-out viewport can return zero. The adapted helper measures drawn viewports instead and expresses geometry in PDF points (72 per inch), not R typographic points. Measurements must use the same dimensions and compatible font/device metrics as the final export.

Layout JSON uses `schema_version: 1`, positive `figure.width_pt/height_pt`, unique panel IDs and `bbox_pt: [left,bottom,right,top]`. Optional grid start/stop indices support group inference; explicit row/column groups refine known comparisons. Measured label anchors are separate evidence, not inferred from a panel rectangle.

The current R adapter supports flat ggplot patchworks, including spanning cells and a single panel, on a temporary base-PDF measurement device. It rejects nested, faceted, fixed-aspect composite, inset and custom wrapped layouts as NOT AUDITABLE. Explicit groups alone cannot make an unsupported layout measurable. A different production device/font metric requires a separately verified measurement adapter; a base-PDF layout result does not automatically certify SVG geometry.

- Default edge, dimension and repeated-gap tolerance: **1.5 PDF pt**. Keep it fixed when granting a local exception.
- A row compares top/bottom and height; a column compares left/right and width. Rows of three or more equal-span panels also compare widths. Spanning panels compare shared boundaries, not inappropriate equal heights.
- Exemptions name the affected panel IDs, checks and reason. Insets, colourbars or intentional unequal widths must not silently disappear from the audit scope.
- One panel is **NOT APPLICABLE**, not an alignment PASS. Multiple panels without usable comparison groups are **NOT AUDITABLE**.
- Missing requested label-anchor evidence is not a geometric failure and cannot be described as a completed label-alignment check.

Patchwork reserves space for axis lettering between adjacent plot regions, so different y variables and label widths can produce unequal horizontal gaps; this is real layout geometry, not measurement noise.
Inspect the individually reported gap measurements first: a discrepancy concentrated beside narrower axis labels indicates a lettering-width contribution.
Normalize the space occupied by neighbouring axis text, sharing axes only when units and scales permit or removing inner y-axis text only when interpretation remains clear, then measure again.
For a deliberately unequal gap, declare an `exemptions` entry with `horizontal-gutter`, the affected panel IDs and a reason, and disclose that exception in the audit report without relaxing the global 1.5 pt tolerance.
The gate correctly flags this geometry; its frequency does not justify widening the tolerance or silently skipping the check.

Run commands from the installed skill directory; set `PROJECT` to the authorized project directory in the calling environment. Paths below refer to already produced files, not supplied example data.

```bash
python3 scripts/qa/audit_panel_alignment.py "$PROJECT/output/qa/figure.alignment-layout.json" --json-out "$PROJECT/output/qa/figure.alignment.json" --strict
python3 scripts/qa/audit_pdf_fonts.py "$PROJECT/output/pdf/figure.pdf" --json-out "$PROJECT/output/qa/figure.fonts.json"
python3 scripts/qa/audit_pdf_text.py "$PROJECT/output/pdf/figure.pdf" --min-pt 5 --json
python3 scripts/qa/audit_figure_collisions.py "$PROJECT/output/pdf/figure.pdf" --json-out "$PROJECT/output/qa/figure.collisions.json" --overlay-pdf "$PROJECT/output/qa/figure.collisions.pdf"
python3 scripts/qa/audit_svg_schematic.py "$PROJECT/output/svg/figure.svg" --json
```

Use the SVG schematic checker only for applicable schematics and set its width/type thresholds to the active profile; its defaults are not universal journal rules. The PDF 5 pt floor is a screening floor for the relevant dense-journal profile, not a recommended ordinary label size. Assess scripts and small symbols after placement scaling as well.

## Verdicts and missing dependencies

| Result | Required handling |
|---|---|
| PASS / exit 0 | Record exactly which checks ran; review any reported warnings |
| FAIL / exit 1 | Correct the saved R source and rerun the affected checks before delivery |
| NOT AUDITABLE / exit 2 | Record missing dependency, unsupported content or invalid geometry; no pass claim |
| WARN / REVIEW REQUIRED | Inspect each finding and fix or document its intentional meaning; strict mode makes warnings blocking where supported |
| NOT APPLICABLE | Record the reason and scope; do not count it as evidence of a passed test |

R's blocking wrapper stops on nonzero auditor results; inspect the saved report to distinguish a failed layout from unavailable evidence. A shell's R error status is not itself the auditor's semantic verdict.

The PDF helpers load PyMuPDF on demand. `verify_exports.py` reads page geometry with PyMuPDF or Poppler. It reports `NOT AUDITABLE` with exit 2 when neither reader is present, and exit 1 for a failed requested dimension or an unexpected page count. Use the font helper for embedded-font evidence.

Base-14 Helvetica supplied by a PDF viewer is **not embedded**. A PDF from `pdf()` therefore needs inspection, not an automatic pass. If Cairo is unavailable, retain the editable `svglite` SVG master and report PDF delivery as pending unless another approved R/Origin export route produces a verified embedded-font PDF. SVG alone does not prove that a journal accepts it or that its fonts are embedded.

## Collision and text limitations

The collision detector flags material text/text overlap, strokes crossing text and page-edge clipping. Partial fill/image overlap is ambiguous and requires visual review. Fully contained labels can be intentional. Do not erase data with opaque masks to silence a detector.

Optional alignment SVGs and marked collision PDFs are diagnostic products only. They must never replace scientific exports or enter the submission bundle as final artwork. Keep input and report paths distinct. Refresh checks after changes to data, labels, fonts, intervals, geometry or placement size.

Font embedding, text-size extraction and selectable text are different properties. Unsupported PDF text, missing glyphs, rasterized labels, outlined letters and extraction differences limit what a text audit can establish. The SVG checker does not prove arrow correctness, non-overlapping text boxes or complete editability.

## Reconcile the data with the displayed marks

For each actual figure, record the source table/file and key, panel population, filter/exclusion rules and counts before and after each relevant step, including missing/nonfinite rows. Compare these with the plotted layer inputs and rendered result, rather than treating a valid export as proof of data fidelity. Apply the following checks where relevant; record **not applicable** or **not run** with a reason instead of inventing a pass.

- Verify row/observation IDs and group counts against the layer's input; separately identify intentional aggregation, summaries, density estimation, binning, sampling, rasterization and overplotting. One mark need not represent one row. For summaries or histograms, reconcile group denominators, bin edges/counts and any excluded or censored observations to the data contract; report missing groups or empty bins explicitly where relevant.
- Recompute selected displayed raw values and summaries from the validated input by key, using declared units, precision, conversions and transformations; verify category ordering and named colours/shapes/linetypes against the configuration across panels. Use an independent calculation or cross-check of source values where practical, not only the same plotting expression twice.
- Check both the **mapping** and **visible extent**: transformations and log-domain invalid values, axes, null/reference lines, coordinate zoom, clipping, out-of-range handling and heatmap centre/limits/NA colour. In ggplot2, scale limits can remove data before a statistic is computed, whereas coordinate limits can zoom without altering the statistical input; check the actual layer/statistic and account for both filtered and visually hidden data. Do not silently drop points, interval ends or heatmap cells.
- For intervals, tests or annotations, match values and meaning to the analysis output, including observational/experimental unit, independence or pairing, method, interval level and multiplicity if applicable. Absence of this evidence is `missing`, not permission to generate inferential results from visual appearance or sample counts alone.
- Keep a concise reconciliation outcome with relevant counts, calculations, discrepancies and repair status in the existing project `output/qa/` or notes; tie claim/provenance information to the existing export manifest. These checks show whether the figure reflects its inputs, not whether the inputs or scientific model are correct.

After data reconciliation, inspect the exported whole, each panel and dense or low-contrast details at intended print/placement size. Assess actual marks, labels and legends in the colour-vision and grayscale views described in [the palette system](palette-system.md), including alpha overlaps and tiny points/lines. If a problem is found, revise the authoritative R source or Origin project, rerender and repeat affected data and visual checks; record anything not inspectable as pending. No simulation constitutes universal accessibility certification.

## Visual checklist

- Check all requested groups/observations against source records; use numeric reconciliation for values. A visual estimate is not a statistical recomputation.
- Review axes, null lines, transforms, clipping, units, missingness and colourbar limits/centre.
- Name each interval and replicate unit; check comparable panels and annotation clearance above interval ends.
- Inspect plot-region alignment separately from outside labels, legends and panel-title baselines.
- Check small symbols, mathematics, subscripts, line wrapping, font substitution and label clipping at the final placed size.
- Verify legend keys, direct labels, consistent identities and uncertainty semantics; do not require redundant legends when direct labels suffice.
- Inspect actual marks under colour-vision simulations and grayscale; colour metrics alone cannot determine emphasis or accessibility.
- For images, record raw/processed linkage, crop, contrast/gamma, pseudocolour, calibration, stitching and reuse. Preserve evidence-relevant background.
- For schematics, check each entity, connection, direction and uncertainty marking against its evidence source.
- Keep review data local; this workflow does not authorize uploading figures or underlying datasets to another service.

## Extend the existing export manifest

Use the existing `output/qa/export_manifest.csv` and shared figure stem/path; do not introduce another trace file. In future project R export code, add at most these five fields, serializing structured values within CSV cells where needed:

| Field | Required meaning |
|---|---|
| `source_data` | Actual input identifiers, project-relative files and relevant checksums |
| `transformation` | Saved R script and hash, or a precise manual operation with a document locator |
| `caption_claim` | The claim made by the caption, decomposed when it contains independent assertions |
| `supported_manuscript_claims` | Claim text and optional locator; verify both listed citations and substantive uses elsewhere |
| `limitations` | Known qualifications and where they are disclosed; an empty list means review needed, not no limitations |

Retain existing size, format, resolution and version information. This is a workflow extension: the installed example template is unchanged and does not automatically populate these fields. Never invent caveats, claim IDs or unavailable analysis to complete a row.

## What the checks cannot establish

File validity and geometric agreement do not validate a model, causal interpretation, mechanism, sample independence, completeness of the literature or acceptance by an editor. Record evidence-level outcomes separately from machine and visual outcomes. A good-looking rendering with an unsupported caption still fails scientific review.

Adapted from nature-figure (Apache-2.0)
Adapted from ARS-Codex 3.23.1 (CC BY-NC 4.0), Copyright (c) 2026 Cheng-I Wu
