# Forecast, decision and robustness figures

Read only for these chart families. Derived from user references 3–5 reviewed on 2026-10-17; methods described on the images are reference claims, not independently validated analysis. Preserve the separation between predictive quality, decision utility and robustness.

## Forecast diagnostics

- **Time series with nested bands:** plot observations, a named centre estimate and ordered predictive quantiles on a common time axis. Draw the wider, lighter band first, narrower band second, then lines; label probability levels and time split. Check quantile crossing. Do not smooth observations away or call a predictive band a confidence interval.
- **Calibration:** put nominal quantile on x and empirical fraction below the predicted quantile on y, both in [0,1]; use a subdued identity line. Define comparison convention at ties, sample/time unit and evaluation set. A curve near identity is a diagnostic, not proof of future coverage.
- **Paired point metrics:** two endpoints joined for different metrics are not an uncertainty interval. Explain filled/open markers, units and which metric is smaller/better; compare methods on the same cases. Use grouping or direct labels when connecting endpoints could be mistaken for confidence limits.
- **Training diagnostics:** put model complexity/iterations on x and the named objective on y. Separate training and held-out/calibration curves by line type as well as colour. Disclose which model/quantile and split are shown; do not choose a model on the final test set.

## Decision comparisons

- Specify action, capacity constraint, loss components, cost ratio, comparator and matched evaluation cases before plotting. Distinguish observed outcomes, model-based counterfactuals and hypothetical scenarios. Better forecast error alone does not establish better decisions.
- **Cumulative regret:** declare the benchmark and formula, time aggregation, sign and unit; state when the comparator uses unavailable hindsight. Do not imply a deployable oracle or extrapolate cumulative growth beyond the evaluation period.
- **Stacked loss bars:** start at zero and verify components sum to total. If hue encodes method and shade encodes component, provide both keys and reinforce component identity with labels, consistent stack order, or hatching for grayscale. End labels show totals only when clearly identified.
- **Paired effects:** define subtraction direction and null value. Display the estimate and named interval with a visible zero line; state what lower/higher favours. Preserve pairing and temporal dependence in uncertainty calculations; for a supplied block bootstrap, record block construction, block length, replicate count and confidence method. Do not choose these settings from image appearance.
- **Average versus tail risk:** label both axes and the tail-risk definition (including tail level, empirical convention and units). Use direct method labels with collision control. Similar means need not imply similar tail behaviour; avoid ranking solely by colour or proximity without the stated criterion.

## Robustness and sensitivity

- **Trade-off curves:** plot both objectives and declare improvement direction. Connect only ordered policies for which connection is meaningful. Distinguish selected policies and sampled nondominated points with explained markers; sampled nondominance does not establish a global Pareto frontier. Stars are selection markers only when defined that way.
- **Sensitivity heatmaps:** define both scenario axes, baseline and the percent-change denominator; handle a zero/near-zero denominator explicitly. For signed gains/losses, show a zero-centred diverging scale and interpret positive/negative direction. Irregular scenario values need numeric cell boundaries or an explicitly discrete grid; show the selected scenario using an outline plus a legend definition. Do not infer significance from that outline or its star.
- **Stress curves:** identify what changes and what remains fixed (e.g. observations rescaled while forecasts/actions remain fixed). Put a reference at the unchanged scenario. State whether retraining/reoptimization occurs; label the exercise hypothetical and do not treat sensitivity as a causal effect.
- **Exceedance curves:** define the empirical probability and `>` versus `>=` convention, use steps rather than arbitrary smoothing, report sample count and any unequal weights. For a log probability axis label percentages/log scale, omit zero probabilities transparently, and keep steps/last positive levels consistent with the denominator. Sparse tails need explicit limits; do not draw smooth precision beyond the observations.

## Implementation and final review

Existing ggplot2 layers can express these designs (`geom_ribbon`, `geom_line`, `geom_segment`, `geom_errorbar` with orientation, `geom_col`, `geom_tile`/`geom_rect`, and `geom_step`); layer availability does not validate the statistics. Build validated summaries first. Use named method mappings across the figure series; uncertainty/component encodings require their own grammar. At final size check crowded tails, long method labels, endpoint symbols, baseline lines, log ticks and heatmap legends. Journal profiles may need extra figures rather than shrinking a dense report page.
