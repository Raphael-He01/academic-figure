# Forest plots and multi-outcome effect panels

Use for point estimates with named intervals across predictors, outcomes, strata, or studies. Source-specific observations are recorded in [the Science agriculture Figure 4 review](reference-observations-2026-10-25-science-agriculture.md). These are design rules, not proof that a particular model, interval, or causal interpretation is valid.

## Choose and structure the display

- Use a forest plot when the main question concerns direction, magnitude, and uncertainty of estimates relative to a meaningful reference value. Preserve raw observations or a separate distribution view when those are needed to assess heterogeneity or sample support.
- Store one row per estimate with explicit outcome, predictor, group/stratum, estimate, lower and upper interval bounds, interval type/level, sample denominator, unit/standardization, and model/provenance identifiers. Keep transformation and inference outside the plotting function.
- Use small multiples for many outcomes or contexts only when readers need side-by-side comparison. Keep row identities and order stable across panels. Show shared row labels once per aligned panel block when the remaining panels unambiguously retain that order; otherwise repeat concise labels.
- Separate substantively different row families (for example, individual strategies versus aggregate counts) with whitespace or a subtle divider and retain their explicit labels. Whitespace may encode grouping, not missing rows.

## Encode estimates and scales honestly

- Draw the point estimate and a horizontal interval whose exact meaning is stated (for example, 95% confidence interval, credible interval, or prediction interval). Use a visible vertical reference at the null or decision threshold. The line is a reference, not a significance symbol.
- Use a common quantitative axis when readers are expected to compare magnitudes across panels. If each outcome gets its own range to reveal within-panel structure, keep ticks and units visible, mark ranges plainly, and say that apparent distances across panels are not directly comparable. A shared zero line alone does not make different ranges comparable.
- For standardized effects, name the standardization and reference population/scale in the axis or caption; avoid a generic “Estimate” when space permits. Use consistent units and transformations across panels only when the underlying quantities support that comparison.
- Do not equate an interval crossing zero with a complete inferential result. Verify the model contrast, interval construction, assumptions, sidedness, multiplicity handling and any preregistered threshold. Report whether inference is nominal or adjusted. If unavailable, describe estimates and intervals without asserting significance.
- Give stratum-specific sample sizes or a clear table pointer; do not reuse the pooled study total as the denominator for every point. State whether strata are independent, overlapping, paired, clustered, or observational as applicable.

## Use colour and layout to reduce decoding

- Bind a stable colour to each named comparison group and reuse it across all panels. Prefer restrained hues and neutral axes/text. If colour alone carries identity, add shape or line-type redundancy when groups must remain identifiable in grayscale or for common colour-vision differences.
- Keep confidence intervals visually lighter/thinner than their point estimates but dark enough to survive final-size reduction. Check overlapping intervals; use slight vertical dodging only if it does not imply a different row or sample.
- A shared legend is efficient when the encoding and categories are identical throughout. Put it outside the data region and define every category in words; avoid relying only on coloured direct labels.
- Align plot regions and panel titles. Keep axes and typography large enough at final physical size; suppress duplicated labels only when alignment preserves interpretation. Use panel tags consistently and reserve a clear, stable gap for distinct row families.

## RStudio implementation and checks

- In RStudio, build the panel data in long form and keep estimates, intervals, labels and style in separate inputs. Map `estimate` to x, the named row factor to y, and the interval endpoints to the horizontal interval layer; add the reference with `geom_vline()` and assemble aligned panels with patchwork or a suitable facet layout.
- Define row order, group colours/shapes, panel-specific or shared limits, reference value, dimensions, fonts and exports in the project's central style/configuration file. Do not set scale limits that silently drop estimates or interval ends.
- Before export, check all interval endpoints against panel ranges, row alignment and order, zero/reference placement, within-panel overlap, labels and units. At final size, inspect whether point and interval marks survive grayscale and colour-vision simulation. Check PDF/SVG text and font handling when the actual export file is available.
- The caption should identify the response/outcome, estimate unit/standardization, interval level and construction, groups/threshold definitions, denominator or sample-size pointer, model/test and multiplicity treatment, and observational/experimental design. Results prose should describe estimates and uncertainty first, then separate explanation or causal interpretation.

## Funnel plots: a separate, conditional diagnostic

Use only when the question concerns study-size-related patterns in a defensible evidence synthesis. The following are this workflow's conservative criteria; the imported ARS templates do not supply publication-bias decision rules.

- Require independent study-level effects on a comparable scale and their valid standard errors, with study IDs, selection rules and effect/SE derivation available. Do not count dependent contrasts as independent studies.
- Treat about 10 eligible studies as a minimum screening threshold for considering this diagnostic, not a guarantee of power or validity. With 12 studies, first inspect heterogeneity, study comparability, effect-size properties and the planned method; do not generate a funnel automatically.
- With 5 studies and substantial heterogeneity, decline a publication-bias funnel assessment in this workflow. Prefer the study-level forest display and a documented assessment of heterogeneity and missing-evidence risks; a sparse visual pattern is not a reliable bias diagnosis.
- Place effect on the horizontal scale and a clearly identified precision measure on the vertical scale. If using SE, show the more precise studies at the top and explain any transformation.
- Derive any centre and contour from the stated synthesis model. A template's arithmetic mean is not automatically the appropriate pooled estimate; pseudo-confidence contours are not an interval for the pooled effect.
- Asymmetry can reflect heterogeneity, study quality, chance, effect-size/SE relationships or selective reporting. It does not uniquely identify publication bias; apparent symmetry does not exclude it.
- Do not add an asymmetry test, trim-and-fill correction or significance claim merely because a funnel is drawn. Each requires its own justified analysis and assumptions.
- Label the display as an exploratory diagnostic. State the study count, effect scale, precision measure, model/contour construction, major comparability limits and what cannot be inferred.

Implement only from verified analysis outputs using the selected RStudio/Origin route and preserve the analysis-to-mark mapping. Retain the original study data and report decisions not to draw the diagnostic when prerequisites fail. These criteria were written for this skill, rather than attributed to the upstream plotting examples.
