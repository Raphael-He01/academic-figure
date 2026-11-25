# State trajectories, missing observations and uncertainty

Use for Kalman-style/state-space trajectory and diagnostic figures. Visual rationale: K1 in [the two-image record](reference-observations-2026-10-25-gam-kalman.md). This is a plotting/interpretation contract, not an implemented filter. Use saved R code in RStudio for figure creation; do not infer a model implementation from its illustration.

## Establish the state and time contract

- Require timestamp, coordinate frame/units, state estimate, uncertainty representation, observation timestamps/mask and reference provenance. Keep observation noise, latent-state uncertainty and estimation error distinct. Align by timestamps/IDs, not presumed equal row positions.
- State whether outputs are prior predictions, filtered estimates conditional on data available so far, or smoothed estimates using future data. An offline smoother is not evidence of real-time filtering performance. Record which covariance belongs to which stage and model assumptions.
- Describe missingness and gap boundaries, timing convention and any unequal sampling intervals. Show prediction propagation across gaps when supplied by the model, but do not insert/interpolate points and label them as actual observations. Plot actual uncertainty propagation/updates, not an artistically imposed widening wedge or contraction.

## Trajectory and state regions

- For coordinates in the same physical unit, preserve metric geometry with an equal-unit aspect ratio. If axes represent different units or a non-Cartesian coordinate frame, use a justified transformation and document it rather than imposing equal aspect blindly.
- Distinguish estimate, known reference and noisy observations with line/mark type as well as colour. Give time direction or selected timestamps where path ordering is otherwise ambiguous. Explain whether highlighted points mark a gap, an update or trajectory endpoints.
- Use the appropriate position covariance/submatrix and stated distribution/coverage construction for joint regions; retain covariance orientation/correlation rather than drawing independent axis intervals as an ellipse. Validate finite, symmetric and positive-semidefinite covariance; report degeneracy or invalid estimates rather than silently repairing them for appearance.
- Distinguish a joint spatial region from marginal coordinate intervals and from a simultaneous-in-time region. A common confidence/probability percentage does not make their constructions interchangeable. Show selected times under a stated rule that does not hide large-error/high-uncertainty periods; avoid an unreadable stack of ellipses.

## Error and uncertainty over time

- With a known state reference, define subtraction direction and plot coordinate errors against a visible zero baseline. Without truth, use appropriately named innovations/residuals or other diagnostics with their own reference and covariance; they are not ground-truth state errors.
- A band drawn around zero from state-uncertainty standard deviations is a model-based reference envelope for the error magnitude, not an error bar centred on each realised error. Name the multiplier/level, marginal dimension and assumptions; do not claim calibrated or whole-trajectory coverage from an attractive plot or one simulation run.
- Reuse exact time limits, units, gap boundaries and observation/update alignment across coordinate diagnostic panels. Keep gap shading semantically separate from uncertainty fill; distinguish no observation from missing/failed state estimates. Comparable y scales are preferred when comparing error magnitudes, otherwise flag the differences.
- For Gaussian-style marginal bands, check that the supplied uncertainty matches the displayed estimator and reference. Innovation diagnostics require observation/prediction uncertainty, not a reused posterior-state band. Missing covariance or a method definition is a request for information, not permission to invent a band.

## Verification and delivery

Before rendering, check timestamp joins, state/covariance dimensions, gap masks and reference availability. Afterwards inspect aspect ratio, time labels, small observation points, uncertainty/gap overlap, clipped regions and legend meanings at final size. Keep uncertainty calculation provenance and selected-ellipse times with the saved R code. Clearly label simulations, and explain deviations rather than hiding them through smoothing, filtering or selective snapshot choice.
