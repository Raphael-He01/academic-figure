# User-supplied reference review: genome and protein evidence composites

Review date: 2026-11-02  
Input: three compressed screenshots supplied by the user. No article title, caption, methods, source data, vector original, or intended journal was provided. The visible figure labels are used only to distinguish panels. This review records visible design choices, not the validity of the underlying study.

## Image 1 — embedding, association, domain and structure sequence

### Purpose and panel sequence

- **A–B, two embedding views:** the same broad point-cloud silhouette appears twice. A layers dark generation points over pale prompt regions and encodes a continuous sequence-identity-to-training scale; B colours point groups by category. These appear intended to compare provenance/identity and group structure. Method, coordinate identity, and legend completeness are not verifiable from the screenshot.
- **C, cluster composition:** a scatter of cluster size against percentage of generations, with prompt-enriched and generation-enriched regions named in the background. This locates clusters by two interpretable summaries, though the origin of each point and count denominator are not explained in the crop.
- **D, cross-genome association:** a dense scatter with dashed fitted trend and both Pearson and Spearman coefficients. This makes linear and rank association visible alongside a numeric summary. Sample definition, transformations beyond z-scores, and uncertainty for the trend are not visible.
- **E, network summary:** five large circles display node count, edge count, average path length, density and median degree. The circles act as metric containers, but no area/colour scale is shown; they should be treated as labelled badges, not quantitative bubble marks.
- **F, four feature-level association panels:** separate scatterplots compare co-occurrence frequency with relative enrichment; point colour maps a combined score. Labels identify selected features. The visible score bars have different maxima across facets, so cross-facet colour intensity cannot be compared unless the values are recalibrated to one common scale.
- **G–H, candidate follow-up:** sequence/domain architecture tracks and predicted/compared protein structures connect candidate examples to domain annotations and model-match scores. Structure imagery supports a follow-up hypothesis; it does not alone establish function. Some small titles and structural details are too compressed to read reliably.

### Layout, marks and visual treatment

The top two embeddings dominate the first row; smaller statistical panels form a middle bridge; sequence and structure examples occupy the lower row. The reading order therefore moves from global organization to quantitative association and then selected molecular examples. Neutral white space separates the rows, while consistent panel letters support cross-reference. Point-cloud panels use small, translucent marks to reveal dense and sparse regions. Teal/green tones unify several quantitative views, while panel B uses multiple hues to distinguish groups. Exact colour values, font family, point size and output resolution cannot be inferred from the screenshot.

## Image 2 — generation workflow and dataset-level summaries

### Purpose and panel sequence

- **A, three-step workflow:** compact numbered boxes, sequence/protein glyphs and arrows summarize prompt construction, generation and ORF characterization. It functions as a method map before the data panels. The icons are schematic; their precise biological meaning requires the article caption/methods.
- **B, scale summary:** bars compare prompt and generated sequence/protein counts, while adjacent circles hold prompt-feature counts. The direct labels communicate scale, but circle size appears decorative unless a documented area mapping is supplied.
- **C, radial distribution:** radial bars compare generated ORFs with prompt ORFs across sequence categories. The circular layout is visually distinctive; category labels are dense and must remain readable at final placement size. Radial length should be interpreted only through the shown scale and baseline.
- **D, sorted stacked bars:** leading Leiden clusters show generation and prompt sequence counts, with a percentage annotation for generation composition. Sorting supports rapid rank comparison; the denominator behind each percentage should be stated in a caption.
- **E, length distributions:** overlaid filled distributions compare ORF length across OpenGenome and SynGenome. The shared baseline makes overall shift and spread visible; sample weighting and smoothing are not recoverable from the screenshot.
- **F, paired frequency histograms:** separate panels show occurrence counts for two protein collections. Their shared axes and repeated styling invite comparison; verify common binning and whether both panels use the same transform/range.
- **G, log-log comparison:** a point cloud compares frequencies in two sources, with a diagonal equality line, fold-change colour scale and Pearson coefficient. The log axes are visibly marked; point density and overplotting require close-up inspection.
- **H, chord diagram:** a circular network connects named domains/families. This is suitable only when the relationship structure is central and the link set can be read; the screenshot alone does not show the edge-weight or filtering rule.
- **I–J, selected family and domain detail:** small association plots and sequence/domain/structure examples narrow from population-level patterns to candidates. Direct labels focus attention, but selection criteria and score semantics are not available here.

### Design observations

The sequence starts with process and scale, then moves through composition, distributions, cross-source association and selected examples. Teal is reused for generated/selected content while gray or pale fills provide comparison context; label and group meanings still need explicit legends. The chord and radial panels are the most label-dense; neither should be copied as a default decorative element. The screenshot is enough to inspect overall arrangement, not enough to assess exact labels, line weights, font embedding or final-size legibility.

## Image 3 — functional assays, sequence comparisons and structural models

### Purpose and panel sequence

- **A, grouped frequency bars:** toxin, antitoxin and combined categories are compared across prompts; small overlaid points appear to expose individual values. The legend defines conditions, but the number and independence of replicates and the meaning of error bars need source verification.
- **B, ranked category frequencies:** two compact bar charts show prompt-type and Pfam-domain frequency. Descending order helps ranking; rotated labels trade footprint for legibility and may become hard to read when reduced.
- **C, six-step pipeline:** numbered stages map sequence generation, ORF filtering, protein-length criteria, low-complexity removal, structure comparison and BLAST filtering. It is an evidence-processing flow, not a quantitative panel; thresholds and software versions belong in the caption or methods.
- **D–F, growth curves:** D and E compare selected toxin/antitoxin conditions over time; F expands the comparison into many small panels. Repeated axes and shared visual roles aid comparison, but overlapping trajectories and direct labels create crowding. The screenshot does not establish whether pale traces are replicates, fitted curves or other conditions.
- **G–H, identity/conservation matrices:** two heatmaps encode pairwise identity and residue conservation. Their colour bars indicate different quantities and ranges; retain separate titles, units/definitions, missing-data treatment and fixed limits where panels are compared.
- **I–L, structure and alignment summaries:** repeated protein-model comparisons pair molecular renderings with pairwise error matrices. The matrices carry numerical comparison, while structure views provide spatial context. The displayed “AF3 expected position error” is a metric label, not independent experimental validation. Exact models, alignment procedure and units should be confirmed from methods.

### Layout and visual hierarchy

Panel C spans the upper-right method area; panels D–F occupy a broad center band; sequence/structure comparisons fill the bottom. The many lettered panels offer an evidence chain but impose a high reading burden. Repeated curve panels, matrix conventions and structure pairs create visual consistency; direct labels around curves are dense and require final-size QA. Green/teal is the dominant family for sequence or assay results, with gray/black for secondary conditions and structure contrasts. Do not infer a single shared meaning for green across all panels without checking the legends.

## Transferable rules

1. Build a multi-panel figure as a question-led evidence sequence: workflow/context → global distribution → quantitative comparison → selected mechanism/candidate follow-up. Include a stage only when it supports the claim; several screenshots' worth of panel types is not a target.
2. Keep the same embedding coordinates fixed when recolouring by another metadata variable. Give continuous identity scores and categorical groups distinct encodings and complete legends; preserve point order/sampling and disclose it when density changes.
3. Treat each scale independently by default. If facet colour bars, heatmaps, axes, bins, normalization or denominators differ, label the difference next to the panel; use a shared mapping only when units and interpretation genuinely match.
4. A bubble can encode magnitude only with a defined area-to-value map, units, baseline and readable scale. Otherwise use a labelled metric card or direct number. Avoid using circles merely to decorate counts.
5. For association panels, report the paired analysis population, transform, sample count and correlation definition; pair a trend with uncertainty when supported. Pearson/Spearman summaries are descriptive association, not causal evidence.
6. Use direct labels sparingly on crowded curves/scatters. Prefer a ranked subset or small multiples, and preserve the full comparison in a separate panel/table when selection would hide evidence. Recheck label collision and font size after final reduction.
7. Align repeated time-course or distribution panels to common time/bins/units where comparison is intended. Distinguish raw replicates, summaries and uncertainty bands in a visible key; never infer their roles from opacity alone.
8. In protein/domain composites, link sequence position, domain annotation, structural alignment and score through matching IDs and explicit scales. State when structure/AI predictions are computational support rather than functional or experimental validation.

## Unknowns and non-adoption

The screenshots do not provide source article metadata, complete captions, raw values, methods, sample sizes, tests, uncertainties, software versions, exact palette values, physical figure dimensions or original export files. Those details remain unknown. The chord diagram, circular radial chart, oversized bubble badges and dense direct-label placement are image-specific choices, not default recommendations; adopt them only when their relationship structure or space constraint is essential and the final-size view remains legible.
