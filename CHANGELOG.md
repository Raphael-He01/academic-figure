# Changes

## 0.1.6-beta · 2026-11-26

- Check the selected rendering environment on first use, assist with missing software and project dependencies, and resume the original figure request after verification.
- Open a scaffold directly in RStudio. Build the full offline trial, palette download and Pages site from a fresh checkout.
- Verify required distribution notices, stabilize release archive metadata and exercise the complete plotting path in CI.

## 0.1.5-beta · 2026-11-23

- Route new figures, sets, revisions, audits and reference learning from the existing project state. The ten production steps specify when to resume, which checks to rerun and where to keep the existing set-level decision.
- Connect the figure index to the evidence checker for five directly matched primary views. Optional `--facts` shows missing evidence during lookup.
- Bind colours, shapes and line types to named groups across reordered panels and subsets. Record both displayed and full-set palette mappings in new export manifests.
- Reuse existing simulated inputs on reruns and surface incomplete inputs before rendering. Verify the endpoint subset against its source records.

## 0.1.4-beta · 2026-11-23

- Add a searchable [V01–V32 guide](references/figure-family-index.md) distilled from scholarly-visualization-lab. Each entry names the research question, a candidate view and the evidence needed to use it. The [lookup script](scripts/figure_routes.py) searches by ID or terms.
- Add reusable R components for [weighted state fields](references/weighted-state-fields.md) and [keyed sample atlases](references/sample-atlas.md), with simulated SVG/PNG examples, comparison tables and a shared [rendering script](examples/model-output/render.R). Extend the explicit chart-evidence check from seven to nine families.
- Preserve Cartesian orientation, transformations and aspect in linked zooms. Reject unsupported coordinate systems and invalid ternary closure tolerances.

## 0.1.3-beta · 2026-11-22

- Distil model-output selection into a short Chinese guide. It covers joint posterior draws, linked stage counts and reconciled contributions, with alternatives when only summaries are available.
- Extend the existing chart evidence check to these three families. Use `--list` for its vocabulary and `--suggest` to retrieve eligible candidates across all seven supported families.

## 0.1.2-beta · 2026-11-18

- Add a Chromium draft PDF route for self-contained svglite figures with optional exact label checks and local font subsetting.
- Harden the experimental PyMuPDF SVG converter against lost style defaults, clipping, dashes, opacity, masks and filters.
- Check PDF geometry with PyMuPDF or Poppler and report missing geometry evidence explicitly.
- Improve swatch label contrast, add tritanopia simulation, and report single-group colour distance as inapplicable. Flag unfinished metadata in the global point map template.
- Add CSV preflight, conditional chart checks, template caption facts, a limited CSV summary check, figure evidence hashes and scaffold plotting components.
- Verify archive contents and byte hashes before delivery. Exclude R session outputs and dependency caches, and keep archive paths portable.

## 0.1.1-beta · 2026-11-16

- Bound export review status to file SHA-256; fixed cross-directory paths, dimension checks, stale font evidence and atomic manifest updates.
- Added full-raster deutan/protan/tritan/grayscale review through existing R colorspace, with explicit dependencies and hashed diagnostic copies.
- Preserved upstream ARS NOTICE and pinned copyright-bearing licence; checked historical nature-figure 2.8.0 public tree for notices.
- Expanded local regression from 10 to 14 tests, including dimension failures, review invalidation, malformed manifests and raster review.
- Kept GUI, cross-platform and final-print acceptance separate from local mechanical checks.

## 0.1.0-beta

Initial local review candidate: connected named colour cards to R, added pending export metadata, public documentation/licence mapping, simulated demos and offline regression/CI configuration.
