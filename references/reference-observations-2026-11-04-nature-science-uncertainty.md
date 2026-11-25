# Journal learning: distributions, estimates and spatial uncertainty

Reviewed 2026-11-04. Scope: Nature Figures 3 and 6 and Science Figure 1 below. This batch reviews three figures, not all figures in either paper. Observations refer to inspected public PDF copies plus captions and relevant surrounding text. Design rationale is our inference about communication, not a claim about the authors' intentions. No study results were recalculated.

## Sources and access

- **N:** Maes et al., *Environmental drivers of increased ecosystem respiration in a warming tundra*, Nature 629, 105–113; published 2024-04-17, issue 2024-05-02; DOI [10.1038/s41586-024-07274-7](https://www.nature.com/articles/s41586-024-07274-7). [PMC full text and captions](https://pmc.ncbi.nlm.nih.gov/articles/PMC11062900/); [University of Lapland repository PDF](https://lacris.ulapland.fi/ws/portalfiles/portal/40481273/s41586-024-07274-7.pdf). Repository download contains 23 PDF pages including its cover; the inspected article pages use Nature layout. Figure 3: PDF page 6 / printed 108; Figure 6: PDF page 9 / printed 111. Publisher figure-page fetch failed; the institutional PDF is the visual evidence, not a claim of live publisher-image access. SHA-256: `08b968cb31333f45fdb3615fd968b3adfa004f9b0a08b41dcd4b0e2de8e0c677`.
- **S:** Poore and Nemecek, *Reducing food’s environmental impacts through producers and consumers*, Science 360, 987–992; online 2018-05-31, issue 2018-06-01; DOI [10.1126/science.aaq0216](https://doi.org/10.1126/science.aaq0216). [Author-hosted publisher-layout PDF](https://josephpoore.com/data/science-2018/Poore%20and%20Nemecek%20%282018%29%20Reducing%20foods%20environmental%20impacts%20through%20producers%20and%20consumers.pdf); [Oxford repository metadata](https://ora.ox.ac.uk/objects/uuid%3Ab0b53649-5e93-4415-bf07-6b0b1227172f). Figure 1: PDF page 2 / printed “2 of 6”; the download has seven pages. It displays an erratum notice dated 2019-02-22; correction scope and any later changes were not audited. SHA-256: `8070a0af10b568609d5e69aad76fddb222a9e4ee8a9fee87dbcc3cd8995d06fd`.
- These are Nature and Science main journals. Palette and arrangement choices below are author choices, not journal formatting standards. Original PDFs and reading images were temporary review material; only summaries and provenance enter the skill.

## N3 — Distribution and duration views

**Visible:** two horizontally aligned panels: a combines pale violet violins, grey variable-sized points and black point/interval summaries; b shows grouped duration regions, grey points and selected blue fit/band layers. A shared key sits above. Horizontal effect-size guides cross both panels, with a more prominent zero line.

**Caption/method statement:** response is Hedges' SMD; black intervals and fitted bands are 95% CIs. The point-size quantity is inverse square root of within-study variance, not sample count. Separate duration groups have separate reported sample sizes. Blue lines are significance-selected.

**Why this encoding helps — inference:**
- Panel a asks about group distribution and model estimates; a mean bar would hide heterogeneity. Panel b asks about change within duration ranges, which a grouped violin cannot show. Reusing the response scale lets a reader connect these distinct questions.
- Pale density fills provide a silhouette without taking contrast from the black summary. Grey observations preserve support for judging a fit; blue makes the model layer easy to find. This is a hierarchy of evidence roles, not a requirement to use violet and blue.
- Empty space above the marks holds the encoding key and annotations. A legend that explains mark roles is more useful here than a separate legend for every age class already labelled on the axis.

**Type, lines and labels:** the visible hierarchy is bold panel tags, regular axes and a compact shared key. Reference dashes, data outlines and interval caps have distinct roles. No font family, exact pt size, alpha or HEX is inferred. Numerical annotations are crowded at the top; after reduction, keep only those necessary to interpret the comparison and send remaining model details to the caption/table.

**Scientific and accessibility adjustments:** do not transplant generic SMD thresholds into another field without justification. A model weight needs its formula and an explicit area/size mapping; apparent diameter does not identify the mapping. Use colour plus line type/label when model identity matters. Do not silently omit fitted relationships because they fail a significance threshold; if selective display is intended, disclose the selection and keep the full model output accessible. Preserve numerical duration geometry when claiming rates or slope comparisons; categorical age labels alone cannot establish a common numerical x scale.

**Adopt / adapt / reject:** adopt separate but linked distribution and trend questions; adapt density transparency, line priority and annotation count to the data and final size; reject automatic significance-only curve filtering and automatic effect-threshold bands. Missing replicate/design information blocks inferential intervals, not the descriptive inspection of supported values.

**R application and acceptance:** use `geom_violin()` only with a defined density computation, `geom_point()` for validated observations, and separate supplied model-summary tables for intervals/lines/ribbons. Do not relabel raw means as metaregression estimates. Verify group IDs, weights, interval meaning, numeric time positions and layer coverage; visually inspect overlapping large points and shared guide lines. No new R figure was run in this review.

## N6 — Matched maps with different quantities

**Visible:** three equal-footprint maps with thin neutral outlines and separate horizontal colour bars: green-to-blue, pink-to-ochre/olive and green-to-purple. Short explanatory arrows accompany the third bar. Broad blank context keeps coloured regions dominant.

**Caption/method statement:** a shows predicted relative respiration change, b relative standard deviation, and c the standard deviation from input uncertainty alone divided by that from combined uncertainty. Monte Carlo propagation supplies the uncertainty estimates.

**Why this encoding helps — inference:**
- Position answers where; the aligned companion panels let the reader inspect whether a large estimate coincides with poor precision, then consider a source of uncertainty. Encoding all three quantities through hue, opacity and pattern on one map would raise decoding demands.
- Repeated geometry supplies the correspondence. Different colour families warn that columns contain different quantities, while local titles and scales provide the definitions. A shared colour bar would create false comparability.
- Boundary strokes are thin enough to preserve orientation without dominating the narrow mapped regions. Long bars beneath the maps give units and endpoint labels a stable reading position.

**Type, annotations and scientific limits:** panel tags and colourbar titles form the hierarchy; the third bar's arrows translate numeric direction into interpretation. Exact projection, original colours and stroke settings were not recovered from appearance. Blank space cannot automatically be read as measured zero. Saturated endpoints need an explicit clipping policy. CV is unstable when its mean denominator approaches zero; preserve a defined validity mask. A ratio of standard deviations is not an additive share of total variance, and a midpoint of 0.5 does not establish equal contributions. Do not turn the visual centre into an unsupported decision threshold.

**Adopt / adapt / reject:** adopt common geography with separate estimate/uncertainty views when both affect decisions; adapt palette lightness and legend wording after tests on actual marks; reject deriving uncertainty from the estimate alone or calling every uncertainty ratio a percentage contribution. If only an estimate grid exists, disclose that uncertainty data are missing.

**R application and acceptance:** build maps from keyed, compatible spatial layers and one stored extent/CRS. Use separate fill scales and retain the appropriate mask for each derived quantity. Add a third map only when its calculation is defined. Check cell correspondence, bounds, masking and units before layout QA; inspect boundaries and near-white colours under grayscale/CVD views on the actual export. These new project checks are guidance, not newly implemented spatial code.

## S1 — Aligned distributions across several indicators

**Visible:** food rows align across five indicator columns; lettered row groups A–I use whitespace and functional-unit labels. Grey interval glyphs, median/mean marks and adjacent numerical columns carry the first comparisons; muted ochre, turquoise and blue identify further indicator columns. Repeated axes, clipped-end arrows and a red comparator make scale interpretation consequential.

**Caption/text statement:** intervals represent producer variation (10th–90th percentiles), not CIs; n counts farm or regional inventories. Functional units differ among food groups. The paper describes production weighting.

**Why this encoding helps — inference:**
- Horizontal position preserves numerical comparison without compressing different indicators into a composite score. Row alignment lets the reader follow one item across outcomes; rows must not be independently sorted in each column.
- A percentile span plus distinct central statistics communicates skew and heterogeneity that a lone mean would conceal. A conventional box plot would substitute different quantiles; it is not an equivalent replacement unless relabelled.
- Whitespace carries semantic grouping, avoiding a heavy coloured background for every row. Muted indicator colours establish column identity; they do not mean “good”, “bad” or statistical certainty. Selective tabular values support exact lookup without labelling every mark.

**Type and layout adjustments:** column headings are stronger than row/tick labels; the dense matrix rewards consistent baselines. Such a tall display needs enough placed height. Split into readable metric blocks or a companion table before shrinking text. Keep unit headings next to every group and retain row keys across the split. Neutral outlines and reference strokes should remain subordinate to the data.

**Scientific and accessibility adjustments:** percentile spans may start away from zero because they encode ranges, not bars from a zero baseline. Different group functional units and reset axes forbid comparing lengths across all rows. A clipped endpoint requires an arrow plus accessible full value; prefer complete limits or a clearly labelled alternate view when feasible. Coloured columns still need titles and units in monochrome. Weighted distributions need the actual quantile algorithm/weights; do not substitute sample percentiles or count a regional inventory as one farm.

**Adopt / adapt / reject:** adopt row alignment, explicit group units and named distribution summaries; adapt the number of columns and numeric labels to the final width; reject treating these spans as inferential intervals, silently clipping tails, or using a shared colour ranking for incompatible metrics.

**R application and acceptance:** prepare one keyed row per item/metric with unit, quantiles, mean/median, weighting and n-definition; use horizontal segments and separate mean/median shapes. `geom_col()` is not the correct geometry for an interval starting above zero. Use aligned panels or facets with deliberate range policy. Verify joins, row order, unit groups, summary values, full endpoints and legend semantics. The existing template does not already implement this matrix.

## File evidence and boundaries

Complete figure pages and focused dense-region crops were inspected with PyMuPDF. Reading renders used 1.7× full pages and 3× crops (122.4 and 216 dpi); these are review settings, not source artwork DPI. Nature PDF page size was approximately 595.276 × 790.866 pt; Science approximately 593.972 × 756 pt. Page size is not individual figure size. The PDF copies allow more detail than a screenshot, but this batch did not audit embedded fonts, extract original object styles, measure placed figure typography, simulate CVD, or validate export compliance. A readable zoom is not a final-size acceptance result.

## Helper record and verification status

- Actual dsh version `0.2.1-rc.5`; one bounded public-only headless request using the existing credentials overlay. Exit 0, elapsed 178.2 seconds. No private data or local skill content was submitted; raw diagnostics were not retained.
- dsh reported two searches and six page attempts; it returned Nature Figure 6 from a search-result caption title, with no inspected image, and no verified Science candidate. Its `caption_only` label did not mean a full caption had been read. Primary review resolved the Nature lead using PMC and the repository PDF, added Figure 3 from the same paper, and independently located the Science source after the helper finished.
- Nature Figures 3/6 and Science Figure 1: **image + caption + relevant context inspected**, with the source-version limitations above. Other figures: not reviewed in this batch. Statistical replication, new-figure rendering and colour-vision testing: **not run**. No measured token/cost saving is claimed.

## Hypothetical transfer check

For project data containing product IDs, several impact measures, quantiles and heterogeneous functional units, choose aligned percentile displays within compatible unit groups; reject a single overall ranking or invented CI. For a spatial model with estimate and uncertainty rasters, choose matched maps after checking keys and the uncertainty definition; if the third layer is only a ratio of standard deviations, label it literally rather than a variance contribution. These are reasoning checks with hypothetical schemas, not generated datasets or completed graphics.

## Documentation acceptance

On 2026-11-04, quick_validate.py reported `Skill is valid!`; all 44 local Markdown links in the six touched references resolved. Backup comparison showed five modified references, this one new reference, and no deletions; SKILL.md, assets and scripts were byte-identical. The two added selection rows are reachable through the existing required data-selection step. No render or scientific-validity pass is implied.
