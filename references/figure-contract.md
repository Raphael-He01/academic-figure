# Figure planning contract

Read before planning a new figure or changing what an existing figure argues. This expands the claim section in SKILL.md; it does not establish another intake or plotting backend.

## Five decisions, one record

1. **Question and supported claim.** Name the comparison and response. Write a conclusion only when the supplied analysis supports it. For an exploratory request, record the question and mark the conclusion `missing`; a plausible story is not a result.
2. **Evidence roles.** Give each intended panel a question, comparison and contribution to the whole figure. Identify which observations, controls and limitations must remain visible.
3. **Composition.** Choose a quantitative grid, explanation-led composite, representative-image-plus-measurement layout, or mixed-modality arrangement. These describe spatial organization, not proof strength.
4. **Data and inference boundary.** Identify observational units, dependencies, source records, transformations, uncertainty definitions and unresolved risks. Separate measured, simulated and hypothesized relationships.
5. **Destination and export agreement.** Record journal/article type/stage, physical size, required editable/raster formats, caption carrier, and applicable QA. Missing submission details remain provisional.

Keep these five decisions together in the project's existing notes. Recover facts from provided files before asking; request only information needed to resolve a consequential ambiguity. Independent data checking can continue while an interpretive decision is missing.

## Integrity before arrangement

- Retain the original inputs. For any exclusion, record counts before and after, the selection expression and its scientific reason. Never silently choose convenient columns or remove awkward observations to fit a layout.
- Use density, binning, or rasterized marks through the R workflow when point count demands it; state the aggregation or sampling rule. A faster renderer does not justify undisclosed data loss.
- Identify paired units before summarizing. If the question concerns change within a unit, inspect that change rather than inferring it from marginal overlap.
- A missing interval, denominator, unit or test is a missing input, not permission to manufacture one. Use the existing caption rules for unresolved information.
- Distinguish illustration from measurement: a schematic arrow cannot establish a causal link, and a representative image does not quantify a population.

## Choose a composition without forcing a template

| Arrangement | Useful when | Guardrail |
|---|---|---|
| Quantitative grid | Several comparisons need direct scale matching | Retain comparable axes and sufficient room for each estimate |
| Explanation-led composite | Readers need the system or procedure before interpreting measurements | Keep the explanation only as large as comprehension requires |
| Image with measurement | A visible phenomenon needs quantified support | Preserve calibration, selection criteria and raw-image traceability |
| Mixed modalities | Different evidence types answer one question | Allocate space by readability and inference, not by equal cell counts |

For multi-panel reasoning, read [evidence architecture](multipanel-evidence-architecture.md). Do not map one input table to one output figure automatically. Several tables may support one question; one table may serve distinct questions.

## Resolve readiness

- Proceed with production only when required data mappings and evidence meanings are available; a preliminary layout can retain explicit missing decisions.
- Prefer fewer panels when removing one loses no necessary inference. Do not demote a negative result that changes the conclusion.
- Use the selected approved RStudio/Origin route and retain its editable source and execution evidence. This contract does not authorize an unrelated renderer, external generation service or new dependency installation.
- Before delivery, reconcile the contract with the actual outputs and the [rendered QA record](rendered-qa.md). A contract documents intent; it is not validation evidence.

## Reviewer-risk prompts

Before writing plotting code, ask these four questions; an unanswered question identifies a weakness in the proposed figure.

- Does the displayed evidence support the conclusion? → Correlation or a single observed result is being used to argue causation or universal applicability.
- Does the control address the relevant alternative explanation? → The comparator misses the alternative a reviewer would raise, or the comparison criteria differ.
- Is uncertainty visible and defined? → Intervals, sample counts or their definitions are absent, or visual choices conceal the distribution.
- Are both sides compared on the same basis? → Units, denominators, populations or samples, time windows, or preprocessing differ on one side.

If any answer fails, revise the design or obtain the needed data before styling; record unavailable information as `missing` rather than inventing it.

Adapted from nature-figure (Apache-2.0)
