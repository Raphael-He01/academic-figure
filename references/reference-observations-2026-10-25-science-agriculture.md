# Science agriculture Figure 4: visual observation and transfer

查阅日期：2026-10-25。Rasmussen et al., “Joint environmental and social benefits from diversified agriculture,” *Science* 384(6691), 87–93 (2024), DOI [10.1126/science.adj1914](https://doi.org/10.1126/science.adj1914)。[Science article page](https://www.science.org/doi/10.1126/science.adj1914)；[public publisher-layout PDF copy hosted by Washington State University](https://s3.wp.wsu.edu/uploads/sites/2701/2024/04/science.adj1914.pdf), which identifies the download as from science.org and is marked “Corrected 17 April 2024.” The reviewed page is PDF page 5 of 7 and printed page 5. This is a copy of the publisher-layout article PDF hosted by an institution, not a direct fetch from the publisher endpoint. The article page also records a later author-list correction; the figure artwork itself was not re-compared against a later file.

本文记录设计选择和可见信息，不复制原图，不验证研究数据、模型或统计结论，也不把该设计称为 Science 官方模板。

## Evidence card

### Question and chart type

- **可见/文述：** Figure 4 uses six forest-plot panels to compare estimates across five agricultural-diversification strategies plus two aggregate rows (number of strategies; number of practices), conditional on landscape category. The outcomes are biodiversity, ecosystem services, reduced externalities, human well-being, food security, and yield.
- **迁移条件：** Appropriate when direction and magnitude of an estimate relative to zero are central and uncertainty is available. It does not by itself show the raw distribution, study-level heterogeneity, or the sample support behind each estimate.

### Layout, hierarchy, and reading path

- **可见：** Six panels form a 3-column × 2-row grid, read A–C then D–F. Panel letters and bold outcome labels sit above each plot. The seven rows keep the same order in all panels. Row names appear only at the left of panels A and D, allowing the other aligned panels to omit repeated text. A clear vertical gap separates the five strategy rows from the two total-count rows. A shared three-category legend is centered beneath the grid; the explanatory caption follows immediately below.
- **可见：** Plot frames, ticks, zero references, and data are contained within each panel; no background grid dominates the colored intervals. The page continues into three-column article text after the figure caption (corrected on 2026-10-25 from the inspected page layout).
- **Transfer:** Reuse aligned plot regions and shared row labels where order is genuinely identical. Preserve a visible distinction between different row families. Repeat labels if panel spacing, cropping, or independent reuse would make the shared labels ambiguous.

### Marks, colour, text, and annotation

- **可见：** Each estimate is a small filled circle with a same-colour horizontal interval. The three landscape categories use black, orange, and light blue. A thin, light-gray dashed vertical line marks zero. A bottom legend labels each colour in text. Exact colours, font family, point size, stroke width, and transparency are **not measured** from the rendered view and must not be copied as HEX or journal specifications.
- **可见：** Figure headings, row labels, tick labels, and axis labels use a compact sans-serif-looking hierarchy, while surrounding article text is serif. Do not infer the exact font from appearance. The row labels and panel titles are heavier than the ticks; the plot uses a white background and thin rectangular borders.
- **Transfer:** Stable category colour and a separate legend make repeated group identities easy to follow. For a new figure, use restrained category hues and test added shape or line-type redundancy if grayscale/colour-vision discrimination matters. Such accessibility validation was **not run** on this published figure.

### Axes and scientific semantics

- **文述：** The caption describes standardized effect-size means and 95% confidence intervals. Landscape composition is defined by seminatural habitat within a 3000 m radius: cleared <5%, simple 5–20%, complex >20%. The article points to Table S10 for sample sizes. The main text says farmer adoption was observational rather than experimentally assigned.
- **可见：** Each x-axis is labeled “Estimate,” and each panel has a zero line. The ranges differ: panels A, C, D, and F visibly span about −0.6 to 0.6; B and E span about −1.0 to 1.0. Tick labels make the difference inspectable, but visually comparing distance across outcomes without reading each axis can mislead. The y-rows are the same across panels, while estimates and intervals vary by outcome and landscape category.
- **文述/待核验：** The caption says a confidence interval not overlapping zero indicates a significant effect. This wording alone does not establish the interval construction, exact model contrast, sidedness, or any familywise/multiplicity adjustment for all displayed comparisons. The displayed figure does not show stratum-specific n; a table pointer is supplied. Do not infer equal or independent sample sizes from the overall farm count.
- **Transfer:** Use a common scale when cross-panel effect magnitudes are the target. If panels need different scales to reveal structure, label them clearly and state the comparison boundary. Preserve uncertainty and denominators. Verify multiple-testing and model semantics before translating CI–zero overlap into a significance claim. Because the underlying adoption is observational, figure language should remain associational unless a causal design justifies more.

### Export and scale evidence

- **可见/文件检查：** The public PDF is 7 pages; page 5 has a physical media box of 593.972 × 756 pt (approximately 209.5 × 266.7 mm). The page was rendered for inspection at 240 dpi (1980 × 2520 px); those pixels describe the inspection render, not the original figure export resolution. The figure and labels are readable in that rendering.
- **待核验：** Figure-only placed dimensions, native artwork format, font embedding/substitution, grayscale reproduction, and legibility at a smaller journal column width were not measured or tested. Do not treat the PDF page size as the figure's placed size.

## Transfer decision

- **Adopt:** aligned small multiples, stable row order, concise repeated-label suppression, a gap between individual and aggregate rows, category-consistent point/interval colours, and a zero reference in every panel.
- **Adapt:** expose interval meaning and standardized units in the axis/caption; include stratum n or a clear pointer; choose shared versus independent scales according to the comparison claim; add non-colour identity cues where required; audit multiplicity and observational wording.
- **Do not copy:** the specific black/orange/light-blue values, exact six-panel order, typography, or the article's CI-based significance sentence as a universal journal or statistical rule.

Implementation is linked in [forest-plot rules](forest-plot-figures.md). It is an RStudio plotting recipe, not a tested re-creation of this article's models or numbers. No new figure was produced in this reference-only review.
