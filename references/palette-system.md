# Reusable scientific palette system

Use this reference when colour encodes data, links meanings across panels, or needs review. This is a generic high-level-journal workflow until a field and target journal are supplied; recheck the target journal's official artwork rules at submission.

For a set of related R figures, store the chosen card ID and the full ordered group names in the project configuration. Pass both to each figure, for example `figure_config(palette_id = set_card, groups = displayed_groups, set_groups = all_groups)`. A panel showing just the second group keeps its original colour, point shape and line style. The scaffold saves both the displayed and set-wide colour mappings in its export manifest.

## Decide from semantics

- **Qualitative:** unordered groups. Bind colours by stable names, never by current sort order. Prefer a small set; use the selected card’s category limit (three main colours in the initial cards). Above that, add facets, direct labels, shape, line type or a documented tested extension.
- **Sequential:** ordered or continuous magnitude. Require a broadly monotonic lightness path. Use `viridisLite::viridis(..., option = "E")` (cividis) or a reviewed HCL sequential scale.
- **Diverging:** signed deviation around a scientifically meaningful centre. Declare centre, limits, clipping, and missing colour. Do not use it merely because the data have a wide range.
- **Cyclic:** angle, phase, orientation, or time-of-cycle only. Check the wrap seam and do not substitute a cyclic palette for ordered magnitude.
- **Emphasis:** one focal condition against neutral context. Limit strong accents and repeat meaning with shape/line type when small marks or grayscale matter.

The bundled `R/palette_system.R` defines `academic_palettes()` and `audit_palette_system()`. Copy the palette values into the project configuration; do not call a generator independently in different panels because level order may change.

When learning from published figures, distinguish palettes by their role rather than copying a paper-wide set of hues. A map selection, a group identity, and an ordered property can legitimately use different mappings in the same figure if each has a clear key. Shared category rows do not require unrelated continuous variables to share one colourbar. See the inspected [Nature/Science examples](nature-science-learning-2026-10-17.md); their palettes are author choices, not journal standards. Exact colour values should come from a reviewed project configuration, not guessed from compressed previews.

## Default soft-warm profile (2026-11-04)

Use for new figures unless the user or the data's established semantics require another mapping. [The supplied palette review](reference-observations-2026-11-04-soft-palettes.md) records all 11 sheets, ten unique palettes, printed HEX/computed RGB, chart-level observations and limits.

- Prefer a white/near-white ground, warm apricot/cream or dusty rose fills, and limited jade, grey-blue or lavender counterpoints. Start with 2–4 distinct groups; same-hue pale tints are supporting layers, not extra independent categories.
- Keep text and essential axes neutral and dark. Use pale colour primarily for areas and uncertainty bands; separate fill and stroke roles when thin curves/small points would disappear. Darker anchors are compatible with a light overall design.
- Select colours by named group once and reuse across panels; match fills to darker outlines, with shape/line type or direct labels for redundancy. Alpha overlap must be inspected on the actual background; it is not a substitute for a deliberate lighter fill.
- Warm style does not override magnitude, sign, missingness or established group semantics. Never interpolate an entire categorical swatch list into a heatmap. Review sequential lightness or the two arms around a defined diverging centre separately. Do not use a light midpoint to imply a nonexistent threshold.
- Apply selected values to the copied project's `cfg$group_colors` alongside `cfg$group_shapes` and `cfg$group_linetypes`; configure `heatmap_low/mid/high` only for the already defined signed scale. If fill/stroke need separate mappings, add and wire project-level mappings explicitly; the scaffold does not supply an automatic pastel transformation.
- The bundled palettes below remain alternatives. New scaffolds now resolve `rose_mist` from a project-pinned JSON registry through `figure_config()`; pass a confirmed card ID to choose another card. Existing project mappings remain unchanged. Actual-mark CVD, grayscale and final-size checks below remain required before accepting a figure.
- When panels or figures compare the same metric, reuse a single scale definition with the same unit, reference, transform, limits and ticks. For a signed value, reuse the centre as well. Use a shared bar where the layout makes the connection clear.

## Selection and application: one maintained workflow

1. **Browse or resolve.** For “show/select/save a palette”, read [the colour-card usage guide](palette-library.md) and open its visual library. Resolve the current card by name/ID from the registry, not an old observation table. Honour a specified card when its semantics fit; otherwise start with `rose_mist` (雾海玫瑰; user default updated 2026-11-05), then `apricot_jade` or `lavender_apricot` as useful alternatives. At step 6, present 2–3 suitable cards and wait for one choice for the entire figure set, unless its choice already exists, is explicitly specified, or selection is delegated. Save that decision and do not ask again for each figure or on resumption. While waiting, continue only work independent of the palette. This is a design-preference checkpoint, not software permission.
2. **Check eligibility.** Establish categorical, ordered, signed or cyclic meaning, group count, background, mark size and existing project mappings. The default cards have three main category colours; for more groups use facets/labels or an explicitly documented extension. Supporting fills are not additional categories. Keep existing semantic mappings unless a deliberate migration is requested and recorded.
3. **Bind and apply.** Assign exact colours to verified group names, never current row order. Read main/support roles from the card; keep them across related panels. Copy actual values into `cfg$group_colors` with shape/line-type redundancy. Separate fill/stroke mappings require explicit wiring in project code. Continuous scales follow their own centre/limits/missingness contract and must not concatenate a categorical card.
4. **Render and verify.** Save ID, version, exact mapping, role adaptations and selection reason in the existing configuration/manifest; execute saved R in RStudio or apply the matching native Origin settings and inspect its export. Inspect the actual marks under the validation protocol below. Adjust strokes/fills, reduce categories or select an alternative when needed, and recheck changed exports. A browser card or metadata ID is not a rendered scientific figure.
5. **Deliver and learn.** Report the chosen name and any departures, plus QA scope. Only a user-requested change reopens the set-level palette choice; apply and record that change consistently within its requested scope, without recolouring unrelated old projects. For useful new references, add a named candidate via the library's intake procedure; preserve provenance and distinguish project-context validation from universal approval.

A single-group series uses one main colour with neutral context. A missing centre, unit, group definition or interval remains missing; choosing a colour does not supply the analysis. The JSON registry is authoritative for selectable combinations; historical HEX records and legacy R presets serve different roles.

## Validation protocol

1. Render representative points, thin lines, error bars/bands, labels, and heatmap cells at final physical size—not only swatches.
2. Simulate deutan, protan, and tritan viewing with `colorspace`; create a grayscale rendering.
3. Inspect adjacent colours, foreground/background and label contrast, alpha compositing, and the lightness path of continuous scales.
4. Numerical screens such as CIEDE2000 and WCAG contrast support review but are not universal pass/fail laws for scientific marks. Record thresholds as project-specific screening values.
5. If colour distinctions weaken, repair with fewer colours, altered lightness/chroma, direct labels, shape, line type, facets, or a separate monochrome design. Do not claim that a CVD simulation proves universal accessibility.

## Bundled palettes

- `af_qualitative_light`: restrained blue/orange/green/purple/sky/vermillion on white; recommended 3–6. Yellow is excluded as a primary small-mark colour on white.
- `af_emphasis_light`: one blue or vermillion focus plus neutral greys; recommended one focal series and up to three context series.
- `af_sequential_cividis`: continuous low-to-high; generated by `viridisLite`, broadly monotonic in lightness.
- `af_diverging_bwr`: blue–near-white–vermillion for deviations around an explicit centre; not a grayscale-only solution.
- `af_cyclic_phase`: constant-lightness HCL circle for phase/angle only; use redundant direction/labels where exact reading matters.

## Sources and status

Checked 2026-10-10:

- Nature Research figure guide, official requirements: https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/ — accessible palette, minimum text, labelled units, standard fonts; avoid decorative complexity and coloured legend text.
- Nature formatting guide, official requirements: https://www.nature.com/nature/for-authors/formatting-guide — figures should be simple enough for clarity; statistics/error bars belong in the legend.
- `colorspace` reference, implementation method: https://colorspace.r-forge.r-project.org/reference/index.html — HCL palettes, CVD simulation, desaturation, and contrast tools.
- `viridisLite` CRAN record, implementation method: https://CRAN.R-project.org/package=viridisLite — perceptually uniform, colour-vision-friendly continuous maps; package version must be recorded by the project.
- Scientific Colour Maps, design reference rather than journal policy: https://www.fabiocrameri.ch/colourmaps/ — perceptual uniformity/order, CVD and black-and-white diagnostics, versioned/citable maps.

These sources establish principles and tools. The bundled HEX choices are workflow defaults, not an official Nature palette and not copied from a paper.

## Colour roles within evidence layers

For observations plus densities and fitted estimates, assign visual priority deliberately: quiet distribution fill, identifiable raw marks, a clear estimate and a lighter correctly named interval. Keep model/group identity distinct from significance; do not hide unsupported or non-significant comparisons through colour selection. For adjacent maps of different quantities, choose separate scales with explicit titles even when geometry is shared. A contrasting or pale midpoint does not establish a scientific threshold. The [2026-11-04 Nature/Science review](reference-observations-2026-11-04-nature-science-uncertainty.md) explains these choices and alternatives. Map them into the project's style configuration; screenshot colours are not new palette constants, and the bundled template has not been changed.
