# Origin handoff

Origin is optional and must be selected by the current user. Verify version, license and runtime access; no personal standing authorization is inherited. Account actions, purchases and installations require their own authorization.

## Supported boundary

Previously recorded environment guidance (recheck installed version and compatibility at execution): Origin/OriginPro 2026b SR2 is a Windows x64 application. OriginLab's official Mac guidance routes Apple Silicon users through Windows 11 ARM in Parallels or VMware Fusion; it does not provide a native full editor and does not recommend Wine/CrossOver. A VM, Windows license and Origin license are external requirements. Do not create, purchase, activate or log into them without user authorization.

Origin's free trial requires an OriginLab account/email and exported graphs carry a watermark. Trial exports are unsuitable as final submission masters.

## Stable handoff package

For an R-to-Origin handoff, export from R (for direct Origin production, build equivalent metadata from the supplied data):

- an XLSX workbook with `Metadata`, `Levels`, data sheets and `Dictionary`;
- equivalent CSV files for transparent diffing and automation;
- an explicit ordered-level table containing labels, order, colors, shapes and line types;
- units, full-precision numeric values, display precision and provenance;
- an existing R-rendered reference/preview if available; do not require a redundant R figure for direct Origin production.

Excel formulas are imported as their current values. Factor levels do not travel automatically through CSV/XLSX, so apply the supplied order explicitly. Origin numeric display precision is not storage precision; do not round source values merely to control labels.

## Windows/Origin steps

1. Reuse the available licensed Origin and inspect version/access. Install/activate only if necessary and separately authorized; do not reinstall a working environment.
2. Open the XLSX with Excel Connector or import CSV through a Data Connector. Map long name, units and comments where available.
3. Apply category order from `Levels`; confirm labels, units, numeric formats and missing values.
4. Rebuild native Origin plots from the imported data. Inserting the R PDF/SVG is a visual reference only and does not restore native data bindings.
5. Apply the already confirmed figure-set palette (ask only once at the set level if still undecided). Set page size, fonts, line widths, group colors/symbols, axes, legends and layer spacing. Save reusable graph templates as `.otpu` and graph themes as `.oth`.
6. Use native Batch Plotting only for structurally equivalent sheets/workbooks. Merge/arrange layers, then inspect every panel.
7. Use Graph Publisher and Theme Preview only after checking version compatibility; use Color Editor only when needed. Prefer built-in batch plotting over the older Batch Plotting App.
8. Export through `expGraph` to the journal's required PDF/SVG/PNG/TIFF settings. Check font handling, dimensions, color and watermark absence.
9. Save the validated project as `.opju` and record every manual adjustment.

Any supplied `originpro` or LabTalk script must be labeled “syntax-checked only” until executed in a compatible licensed Origin environment.

## Official links

- System requirements: https://www.originlab.com/index.aspx?go=Products&pid=54
- Mac guidance: https://www.originlab.com/index.aspx?go=Support&pid=1059
- Trial/licensing: https://docs.originlab.com/license/eval-lic/
- Excel import: https://docs.originlab.com/origin-help/import-excel/
- File connectors: https://docs.originlab.com/origin-help/connect-to-file/
- Graph templates: https://docs.originlab.com/origin-help/graph-template-elements/
- Themes: https://docs.originlab.com/origin-help/customizeorigin-theme/
- Batch plotting: https://docs.originlab.com/origin-help/graphing-batch-plotting/
- Export: https://docs.originlab.com/origin-help/expgraph-to-image/

## Verification status

Experimental workflow guidance. End-to-end native data entry, graph creation, project save and export have not been certified for this release. An installed or launched application is insufficient evidence.
