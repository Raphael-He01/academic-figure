# Spatial maps and linked summaries

Use for geographic fields, regional detail, locator maps, area distributions and latitude profiles. Derived from visual review of user references 1–2 on 2026-10-17; the displayed data/source claims were not verified. No spatial runtime or package installation is implied.

## Select and arrange

- Use the main map for location and spatial heterogeneity; add a locator only when geographic context is needed. Add a distribution for how much area occupies each value range, or a latitude profile for a zonal question. These panels answer different questions and need not receive equal widths.
- A regional main map may use a narrow column containing locator, key summary and distribution. A global map may share latitude orientation with an adjacent profile. Align latitude landmarks only if the projection-to-profile geometry supports it; otherwise mark the profile as an independent summary.
- Global and regional views of the same variable should share units, baseline period, colour centre, breaks and limits. If a regional rescaling is necessary, identify it explicitly. Use one readable colourbar per shared mapping.

## Data and geometry contract

- Require coordinates, CRS/projection, grid geometry, resolution, time aggregation, reference period and missing mask. Record smoothing/regridding/interpolation and its source; visible coarse cells must not be presented as local-resolution measurements.
- Select a projection for the geographic question; do not identify an exact projection from a screenshot. Compute statistics using geodesic cell areas or other justified physical weights, not the area of projected screen pixels. A cosine-latitude approximation needs a compatible regular grid and a documented justification.
- Declare the geographic mask, land/ocean inclusion, valid-data denominator and coverage. Area-fraction histogram bars must use area weights; distinguish fraction per bin from a probability density and define bin widths.
- For zonal means and spatial IQR, define latitude bins, valid cells and whether quantiles are weighted. A spatial spread band is not an inferential confidence interval.
- Transform locator boxes/polygons through the chosen projection. Boundaries, graticules, scale bars and north direction must be projection-aware; omit unnecessary north arrows or scale bars rather than placing uncalibrated decorations.

## Mark and annotation grammar

- Draw field colours below thin muted coastline/boundary strokes. Graticules are tertiary. Keep missing colour distinct from a true zero or neutral centre and explain both.
- Use diverging colours only for a meaningful signed baseline; include the centre tick and state clipping. Symmetric limits support comparing positive/negative deviations when scientifically appropriate, not as a blanket rule.
- Reference cities/sites can use small hollow points with restrained label halos. Identify whether they are reference locations, sample sites or measurement stations; never imply fine-scale data from coarse-grid values.
- Place a regional aggregate near its locator only if the geographic bounds, units and averaging method are unambiguous. The same mean may be marked in a distribution with a separately explained dashed line.

## Global point-location maps

- Use a world point map to show geographic coverage or a site-level variable; require an identifier, longitude, latitude, coordinate reference system, variable, unit and source per point. Validate finite coordinates, valid ranges, duplicates and missing values. Check longitude conventions and antimeridian handling; never fabricate site locations or observations.
- Choose a projection appropriate to the question; Mollweide can show global distribution with an equal-area projection but distorts shapes, distances and point overlap. Record the projection, central meridian and area of use. Keep coastlines subordinate to data and document the base map and its license; do not imply national borders or territory status from a land-only layer.
- Use a perceptually ordered sequential colour scale for nonnegative magnitude, a diverging scale only for a meaningful signed centre, and named categorical colours for unordered groups. Declare limits, units, missing values and out-of-range treatment. Avoid implying that a sequential metric is categorical merely because a reference image used bins.
- If both size and colour encode data, name each variable separately; point area, not radius, should encode an amount. Draw a legend with representative values. Avoid suggesting more precise locations than the coordinate data support; determine an explicit policy for duplicates and dense regions instead of silently removing or displacing points.
- Use smaller markers, partial transparency, aggregation with a clearly stated denominator, or geographic insets to manage overlap. State the method; opacity blending can alter apparent colours. A map shows coverage and spatial pattern, not statistical association, a causal mechanism or a spatially representative sample by itself.
- Pair a map with a latitude profile or group distribution only when those data and comparisons answer a distinct question. Define the binning, weighting, independent unit, sample counts and interval meaning, and document multiple comparisons when applicable. Do not copy the reference's comparison groups or significance labels.
- In RStudio, a lightweight installed route uses `ggplot2`, `maps` and `mapproj` for Mollweide projection, with `jsonlite` for a GeoJSON basemap where needed; `ragg`/`svglite` supply export devices. The installed versions and licensing are recorded in [sources](sources.md). Prefer `sf` and a suitable CRS-aware workflow for geodesic measurement, complex geometry or larger spatial analyses; it is not installed by this route. Execute saved R code, preserve source data and projection parameters, and check exported geometry and legibility.
- Copy the RStudio point-map template into a project with `data/sites.csv` (id, longitude, latitude, value) and a Natural Earth GeoJSON land file at `data/ne_110m_land.geojson`. Set the title, unit, value limits, data source, observation period and basemap credit before delivery. Unfilled label fields produce a warning and a visible DRAFT title. The template uses macOS Quartz for PDF. Adapt and verify the PDF device on other systems. Use supplied points and label simulated inputs explicitly. [RStudio point-map template](../assets/global-points-template.R)
- At final size inspect coastline integrity, dateline seams, pole edges, fixed point sizes, overlaps, transparent blending, colourbar, missingness, grey-scale and common colour-vision views. A single map is not applicable to multi-panel alignment; do not report an alignment pass. [Reference observations](reference-observations-2026-10-27-global-points.md) separate this screenshot's visible choices from reusable rules.

## Export and review

Preserve vector labels/boundaries where possible; raster fields may remain raster within a vector container. Check effective raster resolution at final size, coastline thickness, label halos, locator legibility, colourbar endpoint ticks and the source/coverage note. Do not promise editable underlying data merely from a PDF/SVG export.

For multi-city raster small multiples, preserve each source grid, CRS, native resolution, valid mask and any documented resampling. Distinguish a common absolute scale from anomalies relative to each city's own baseline; shared anomaly colours do not imply shared absolute values. Keep one declared colour range and zero across comparable panels, distinguish missing cells from zero, and disclose clipping or saturation beyond endpoints. Local scale bars must be calculated in appropriate projected/geodesic units for each extent; keep crop boxes, insets and bar labels clear of data. See [the urban raster observations](reference-observations-2026-10-27-network-thermal-matrix.md).

For discretely classified rasters, store numeric breaks and an explicit lower/upper endpoint inclusion rule once, including out-of-range and missing-value policies; apply that same function and named colour mapping to all panels that claim common thresholds. Equal-width legend swatches identify categories and do not imply equal numeric intervals. Give missing land, water/background and a valid neutral class distinguishable meanings. If baselines are independently computed per city, disclose the population/mask and period used for each baseline; identical categories then compare relative deviations, not absolute temperatures.

For a native-cell inset, derive the crop geometry and main-map selection box from the same stored extent and CRS. When preservation of source cells is claimed, check the overlapping source cell IDs/coordinates, values, class assignments and masks between views, and record any actual reprojection or resampling; nearest-neighbour display may preserve class labels but does not independently prove source-grid preservation. Compute each local scale bar using suitable projected or geodesic units. Inspect the box, connector, scale bar and labels at final size so they do not obscure evidence. See [the three 2026-10-28 observations](reference-observations-2026-10-28-raster-inset-commuting.md).

For geographic networks, node/edge encodings, coordinate-linked insets and graph provenance, read [network and model-association rules](network-and-model-association-figures.md).

## Prediction and uncertainty as separate map questions

When uncertainty affects interpretation and compatible layers are supplied, use matched estimate and uncertainty maps with one stored geography but metric-specific scales; add uncertainty-source diagnostics only when calculated and defined. Validate masks independently for quantities such as CV, whose denominator may approach zero. A standard-deviation ratio is not an additive variance contribution: label the actual formula, and do not infer equal source contributions from a diverging palette midpoint. These checks precede palette selection. See [Nature Figure 6, inspected with its caption](reference-observations-2026-11-04-nature-science-uncertainty.md).
