# Supplied reference: global points and linked spatial panels

Reviewed 2026-10-27. Source: one user-supplied composite JPEG, 1179 × 1552 px; its embedded article screenshot, teaching diagrams and captions are different components. This is a visual reference, not a verified copy of the source papers or an official journal standard. Only design notes are retained; original image and data are not included.

## Upper-left global point map and distribution

- **Visible:** a world-shaped map is the main spatial panel, with pale neutral ocean, softly coloured land groupings, light coastline outlines and an approximately horizontal dashed reference. Numerous point symbols vary in colour and apparent size; a multi-step legend presents a named cooling measure in °C. A companion panel shows groupwise dots, boxes and half-violin distributions with brackets, p-values and n labels. The visible figure caption names 468 urban areas, but the JPEG and truncated caption do not verify data, methods or inference.
- **Hierarchy/layout:** the large map answers where the sites are; the grouped distribution answers how displayed values vary across selected groupings. Colours on the land, colours on the point values and the category colours in the distribution have distinct meanings; keep those encodings separately explained. Crowded location clusters obscure some marks and the point key has many bins; a future figure should check density and legend readability at its final size.
- **Typography/marks:** panel letters, heading and map precede smaller latitude/longitude labels and explanatory key. The distribution uses small scattered observations over a box and a one-sided density; brackets add comparison annotations. Exact fonts, point sizes, colour values, line widths, image projection and sample independence cannot be established from the screenshot.
- **Scientific contract:** apparent colour-bin endpoints, p-values and n are source-image claims only. Latitude/longitude conventions, point-size meaning, data exclusions, distribution bandwidth, grouping definition and test methodology are not fully visible. They must be recovered from actual data/methods for a new research figure, not guessed or transferred.

## Upper-right network and urban grid panels

- **Visible:** a dense network of translucent blue/green edges on a pale geographic background includes a local inset; four compact raster-like urban panels use cool peripheral cells and warm central cells. The source, exact mapping, direction, scale, geographic support and treatment of overlapping lines cannot be established from the crop.
- **Transfer condition:** show spatial connections only when actual origin/destination and direction are available, define edge weight and transparency, and use an inset, filtering rule or aggregation to control dense crossings. Urban grids need a shared legend and declared value range, cell size and missing-data colour; matching visual colours alone does not establish comparability.

## Lower teaching diagrams

- **Visible:** one schematic arranges a global point map above a latitude trend and group comparison. A separate schematic places a network beside an enlarged region, then small multiple urban grids; annotations explain foreground/background hierarchy. These are instructional recreations, not copies or validated data from the original articles.
- **Transfer:** align each companion panel to a separate question; use neutral context and restrained foreground emphasis; explain what the inset covers. For repeated locations or heatmaps retain comparable scale, window, geographic units and classification only when the supplied data justify them. Avoid carrying their region categories, colours or asterisk annotations into an unrelated dataset.

## Adopt, adapt, reject

- Adopt: an unobtrusive geographic base and legible marks; a clearly labelled value key; optional companion panels with distinct evidence roles; small-multiple consistency when comparisons justify it.
- Adapt: projection, thresholds, point size, category palette, map extent and panel layout to the real question, coordinate quality, journal dimensions and available data. Reference JPEG dimensions are screen pixels, not known source export resolution or print dimensions.
- Reject: copying the original dots, values, significance, distinctive composition or labelling; claiming exact original HEX/fonts/projection from the screenshot; assuming every visible site is independent or that a latitude curve establishes causality.

Implementation and checks: [spatial figures](spatial-figures.md) and [rendered QA](rendered-qa.md). An actual RStudio demonstration must be separately labelled if its coordinates or values are simulated; reference review alone does not validate a new figure.
