# Engineering model narratives and comparisons

Use for solar/building/thermal models and similar engineering studies that link geometry, a physical abstraction, competing designs and scenario response. Evidence: private-source example (excluded from this release). These are design rules, not a tested building simulator or validation of that paper's results. Keep figure creation/execution in RStudio.

## Let each figure answer a different question

An optional sequence is geometry/context → model assumptions/topology → candidate trade-offs → selected designs → response/robustness. Choose only the stages needed by the claim. A rendered building explains a proposal, a circuit explains an abstraction, and a simulated response explains model behaviour; none alone proves physical performance. Name simulation, measurement, prediction and concept explicitly.

For a workflow overview, use short aligned stage labels, input/output names and a small number of clear arrows. Thumbnail charts can identify a stage but cannot serve as the only readable quantitative result. Do not fill every box with miniature equations, screenshots or ornamental scenes. Detailed plots belong at a readable size elsewhere.

## Geometric and network diagrams

- Use 3D when spatial orientation, occlusion or ray geometry is the question. Fix camera, aspect, coordinate convention, scale and reference time across comparisons. Give sun/path or boundary-condition labels and distinguish schematic coordinates from calibrated physical dimensions. A geometry illustration is not a measured time series.
- For dimensions/angles, use dimension lines and angle arcs attached to their actual reference objects. Retain symbols consistent with equations. Do not label a length bracket as an angle or imply ray propagation physics only through an attractive arrow.
- Define nodes, connections, reference/ground, sources, storage and resistance meanings in a network. Explain the electrical–thermal analogy rather than assuming electrical symbols are literal building components. Mark junctions versus crossings, and preserve component IDs across the network and equations.
- Compare alternative topologies with stable node placement. Highlight only changed components and explain additions/removals; do not infer that a highlighted omission is physically valid without its model assumption. Check captions against the final left/right or top/bottom arrangement.
- Simplify drawings for final size instead of shrinking CAD screenshots. R `grid` or ggplot2 geometry can provide an editable schematic; a photorealistic external rendering is not required. If a new task genuinely requires a different editor, follow the skill's explicit-exception boundary.

## Strategy and performance comparisons

- Do not combine kWh, hours and a dimensionless index into one magnitude axis. Prefer aligned panels with original units. A normalized profile is acceptable only with a documented formula, fixed comparison bounds, reference and improvement direction; preserve raw values alongside it.
- Distinguish power (kW), energy (kWh), irradiance and integrated radiation. Relabel a variable only when the analysis establishes that conversion or relationship. Relative reduction needs an explicit baseline, evaluation period and aggregation; a June plot cannot silently stand in for an annual result.
- For before/after trajectories, use matched times and consistent condition identity. A fill between curves means a difference only when defined; a fill under one curve is an area treatment, not an uncertainty band. A numerical integrated saving must include the sampling interval and compatible units.
- For temperature and power, prefer vertically aligned panels with a shared time axis rather than unrelated dual axes. Retain relevant temperature variation and separately show a scientifically defined comfort/threshold band. Do not extend an axis solely to make the response appear stable; do not infer a coupling from arbitrary curve crossings.
- Coordinate plot, table, caption and prose from the same keyed result object. Check orientation IDs, metric names, units, period and numbers before describing agreement. A small point or bar is not necessarily a small scientific effect if mixed-unit scales suppressed it.

## Trade-offs, surfaces and representative designs

See [multi-objective rules](spatial-model-decision-figures.md) for objective directions, dominance, normalization and sampled-set limits. Keep response surfaces over decision variables separate from a nondominated set in objective space; one does not establish the other.

A 3D scatter can supplement a genuinely three-objective question. Provide readable two-dimensional projections or a quantitative profile when occlusion makes the comparison hard. If a third objective is colour-coded, give its unit and scale; selected-design symbols use a separate key. Keep selected IDs consistent across plots and tables. Explain selection of a knee, balanced plan or extreme using a stated rule, not a decorative star. Surface interpolation needs a method and sampled-domain statement; do not join unrelated feasible points as if a continuous physical surface were known.

Audit each visual layer separately: coordinate variables, surface colour, point colour, selected-point symbols and colourbars. If a surface and overlaid points use different palettes, identify the quantity and range for each; a single nearby colourbar must not ambiguously claim both. With orientation facets, prefer the same camera and encoding for comparable quantities. When ranges differ for a scientific reason, label this explicitly rather than matching hues while hiding different scales.

## Heat, sensitivity and perturbation diagnostics

- For component-by-time heatmaps, define row variables, clock/time zone, spacing and representative-day selection or aggregation. Retain absolute units for between-component comparison. A row-standardized companion answers a different question and must be labelled. Use an appropriate sequential or scientifically centred diverging palette, with explicit missing/out-of-range rules.
- Label sensitivity indices precisely: first-order, total-effect or another estimator, not generic “importance”. Total-effect indices are not parts of a whole; do not force them to sum to one or draw them as a composition. State parameter ranges/distributions and dependence assumptions, evaluation design and available uncertainty. Any “high sensitivity” threshold needs a declared source or project-specific convention.
- When one metric is evaluated under unrelated perturbation scenarios, use a horizontal dot/difference plot with a baseline reference. Do not infer robustness from radar polygon area, spoke adjacency or a visually compact shape. If radar is genuinely useful for a small multi-metric profile, document axis bounds/order, normalization and direction, and retain quantitative values.
- Distinguish one-at-a-time and joint perturbations, fixed and reoptimized designs, tested ranges and the acceptance criterion. Robustness within tested scenarios is not a general guarantee. Add uncertainty only when actually calculated; deterministic scenarios and sampling uncertainty are different.

## Implementation and delivery gate

Keep geometry/configuration, model outputs and styling separate. In RStudio, supplied response tables can use `geom_line`, defined `geom_ribbon`, `geom_tile`, zero-based `geom_col`, or point/segment comparisons with `patchwork` assembly; statistical or physical results must exist before plotting them. No new package is required merely to learn these designs.

At final size, verify variable/metric identity across every panel and table; caption orientation; temporal units; topology crossings; readable text; separate keys for changed components, categories and magnitudes; and whether all shading has a defined meaning. Inspect embedded image dimensions at their actual placed size where relevant. High PPI cannot fix tiny physical text; a PDF containing a raster chart does not restore editable axes. Deliver genuine vector text/lines where available and retain calibrated raster content only where appropriate.

## Map learned rules to the actual R scaffold

The following are adaptation routes, not a newly implemented engineering model. Existing keys live in [figure_config.R](../assets/r-template/R/figure_config.R), consumed by [figure_style.R](../assets/r-template/R/figure_style.R) and [render_example_figure.R](../assets/r-template/R/render_example_figure.R). Use the copied project's files; do not edit the installed template just to produce one paper.

| Learned decision | Existing configuration / required project change | Check |
|---|---|---|
| Allocate readable panel space, not tiny four-across 3D views | `width_mm`, `height_mm`, `plot_margin_pt`, `panel_spacing_pt`; choose and bind project-specific patchwork widths/heights | Inspect every label at final physical size; no guessed source pt values |
| Distinguish title, axes, key and annotation | `font_family`, `base_size_pt`, `axis_title_size_pt`, `axis_text_size_pt`, `legend_text_size_pt`, `legend_title_size_pt`, `panel_title_size_pt`, `panel_tag_size_pt`; add annotation size only if used | Font availability, exported symbols, embedding/substitution and readable smallest text |
| Preserve condition/solution identity, including grayscale | Named `group_levels`, `group_colors`, `group_shapes`, `group_linetypes`; adapt actual level names and consume them through manual scales | Reordering rows does not change identity; colour and shape keys match |
| Keep marks above grids and distinguish references | `data_line_mm`, `axis_line_mm`, `grid_line_mm`, `point_size_mm`, `errorbar_line_mm`; bind any additional reference-line or alpha parameters in project code | Read small marks and translucent overlaps, not only colour swatches |
| Retain real thermal units and meaningful colour centre | `heatmap_low`, `heatmap_mid`, `heatmap_high`, `heatmap_limits`, `missing_color`; select sequential vs diverging scale from the quantity | The example's standardized limits and hardcoded zero midpoint are not absolute-temperature defaults; change both the configuration and scale implementation |
| Separate temperature and power; keep time aligned | Add project time range, temperature/power ranges, facet/patchwork layout and threshold definitions; bind to scales and layers | Units remain separate; clocks/samples match; threshold and range have a scientific basis |
| Export by destination rather than screenshot appearance | `width_mm`, `height_mm`, `png_dpi`, `tiff_dpi`; current submission requirements control final settings | Decode PDF/SVG/required bitmaps, verify placed size, fonts and raster dimensions |

The bundled renderer still contains example-specific layout ratios, legend positions, some alpha settings and axis choices. Move these into the new project's config when adapting them; merely documenting a new key does not make the code use it. Current numeric defaults are generic starting points, not measurements of the ICM figures, fixed journal standards or proof of accessibility. The template's trend/distribution/heatmap example does not implement RC networks, Sobol estimation or engineering optimization.

## Caption and Results application example — not a generated figure

Suppose a user supplies matched time, indoor/outdoor temperature and heating-power columns. Select aligned temperature and power panels, not the source's unrelated dual axes; show a comfort band only if a justified threshold is supplied. Derive summary quantities from the same checked data, not from reference-image labels.

**图题模板：**指定条件下的温度与供暖功率响应。**图注模板：**“a，室内与室外温度；b，同期供暖功率。数据为[实测/模拟，待确认]，时间范围、采样间隔、方案和独立重复为[待补充]。阴影表示[已定义含义；无阴影则删除]。参考线依据[待补充]。缺失值处理及统计方法为[待补充/确认不适用]。”

**Results 规则：**数据检查后才填写事件前后差值、效应量和实际已算的不确定性；没有检验就不写“显著”。只有功率时，未完成时间积分不能报告能耗/节能率；模拟内温变化小不能独自证明真实建筑舒适性。完整写作规则见 [caption-and-results.md](caption-and-results.md)。

## Robust feasibility and uncertainty sets

When the question concerns a bounded adversarial decision and a two-variable geometric slice is interpretable, pair feasible-region boundaries and selected solutions with the actual uncertainty-set geometry and objective-versus-budget curve. Require the objective, constraints, bounds, admissible set, solution and solver status; label projections/slices of higher-dimensional models. A budget is not a failure probability, and protection applies only to the declared set. Check all plotted points against constraints and objective; record solver tolerances, non-uniqueness and tie-breaking. Explain nested shading and use an aligned table or separate panels when overlapping regions hide boundaries. Stack decision components only if commensurate and additive. Settings and drawing layers belong in project-specific R/Origin files; no bundled implementation is implied. See [reference review](reference-observations-2026-11-09-network-robust-mixture.md).

### Solved protection paths and out-of-design stress

Use this extension when results contain protection-level IDs, solver status, objective values, additive decisions, design-scenario losses and a separate stress-draw table. Give each view a different role: cost versus design-set loss, component substitution, broader stress risk, and a complete scenario audit. These require more than a single optimum or a scalar robustness score. See [the four-reference review](reference-observations-2026-11-12-robustness-sensitivity-ranking.md).

- Plot discrete solved levels as points and columns or justified steps; connecting them is a reading aid, not evidence that intermediate solutions were solved. Keep substitutions and jumps visible. Preserve configured resource levels, including zero-use resources, and distinguish a verified zero from a missing result. Numeric level spacing must remain honest.
- Define the cost-premium denominator and zero-baseline handling. Name the scenario set and loss aggregation on the trade-off axis. Do not silently identify the protection parameter, cost premium, failure probability and resource total: these are different quantities. A decreasing design loss does not prove a general Pareto frontier or out-of-set reliability.
- Freeze each selected design while evaluating the same keyed stress draws, with their generating distribution, dependence, weights and count recorded. Reoptimization is a separate experiment. Use [the exceedance rules](forecast-decision-figures.md) for empirical steps, inequality convention, log zeros and tail support; a probability guide is a decision threshold only if supplied and justified.
- Retain every required design scenario in an aligned point/segment comparison, even when all methods coincide at zero. Redundant shapes or small declared categorical offsets can expose overlapping marks without altering numerical values. A line between design outcomes is not a confidence interval; label it as a comparison and keep the scenario membership separate from broader stress draws.
- In project code, wire proposed fields `protection_levels`, `solver_status`, `design_scenario_ids`, `stress_draw_id`, `stress_weights` and `cost_baseline` to validated result tables before using `geom_point`, `geom_col`, `geom_segment` and `geom_step`. Reconcile stack totals, zero-use categories, all scenario rows and common draw IDs. These fields and optimization routines are not implemented by the bundled scaffold.

### Boundary maps, sensitivity indices and scenario envelopes

For a model with a defined equilibrium or failure boundary, combine a two-input field with a labelled threshold and a companion sensitivity or response view only when those outputs exist. State each panel's estimand: normalized state, yield and variance share need not have the same parameter dependence. Hold other inputs fixed or describe their integration; do not infer a boundary from a colour transition alone.

- Visually separate an exact model boundary, an analyst-selected operating threshold and a reference point using labels and line/shape redundancy. An extinction or zero-output regime is a valid state, not missing data. Save equations or computed boundary tables, units and grid resolution; numeric approximations need their own tolerance record.
- Show supplied first-order and total-order sensitivity estimates side by side with named uncertainty, rather than stacked as percentages. Check the estimator's input-dependence assumptions. The total-minus-first difference is not an isolated pairwise interaction estimate, and Monte Carlo precision intervals are not biological or observational confidence intervals. Retain failed estimates and investigate out-of-range sampling estimates instead of clipping them to look valid.
- For a response sweep, reuse matched nuisance-parameter draws across the control axis when comparing changes. Document the central statistic and probability levels of scenario envelopes; they are not automatically confidence or prediction intervals. Preserve genuine zero-output mass and changes of regime; do not smooth them away or assume a central line is the mean from appearance.
- Put boundary definitions, draw IDs/distributions, `response_summary`, `interval_kind` and `interval_levels` in the copied project's analysis/configuration, and bind them to tiles/contours, points/intervals and ribbons. Check boundary points against the model, interval ordering and common draws; inspect threshold contrast on the actual field. This is a proposed project extension, not a supplied Sobol estimator or simulator.
