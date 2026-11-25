# Editable schematic workflow

Read for architecture, mechanism, pipeline or process diagrams. Quantitative panels still use the data workflow. For AI-assisted planning, also read [the policy and provenance boundary](ai-graphical-abstract-workflow.md).

## Evidence brief

Before drawing, identify the system boundary, intended audience, central message and publication role. List each entity with its manuscript label, function, container and evidence source. List each connection with endpoints, direction, what is transferred, activation conditions and whether it is observed or hypothetical.

Check relationships against available methods, implementation or analysis, not merely an attractive verbal summary. Record unresolved assumptions; ask only when the answer changes scientific meaning or structure. Existing clear authorization does not require another routine design approval.

Distinguish the contribution from established context without assuming that every diagram has exactly one new component. A mechanism draft cannot gain unsupported steps merely to form a complete-looking chain.

## Size and arrangement

Use [journal requirements](journal-requirements.md), and the [Nature/NMI differences](nature-flagship-and-nmi-requirements.md) only for those destinations. Set physical dimensions before arranging entities. Reduce detail or split the scope when labels no longer fit; do not shrink important text indefinitely.

| Structure in the evidence | Candidate arrangement |
|---|---|
| Ordered procedure | A consistent horizontal or vertical progression |
| Functional tiers | Aligned containers with stated relationships |
| Central interaction | A hub with labelled incoming/outgoing links |
| Feedback | An explicit return route distinct from forward transfer |
| Matched alternatives | Repeated structure with changes identified |

An agent/tool diagram follows the implemented call and return structure. Do not impose a loop on a one-pass system or a linear pipeline on an iterative system.

## Construct the master

For the R route, create saved grid/ggplot2 code and execute it in RStudio. When Origin is selected under the current skill’s [使用范围](../SKILL.md#使用范围) and its native objects can express the schematic, preserve the object relationships and settings in an editable project and inspect its exports. The following R implementation details apply only to the R route. Keep entity/edge definitions separate from layout coordinates and style. Use stable identifiers in the R objects and a mapping back to the brief; preserve SVG element IDs when the chosen export route supports them, but do not claim automatic semantic IDs from every R device.

Measure label extents with the selected font/device, then set box size and padding. Use the [schematic style rules](vector-schematic-style-rules.md) to keep arrows, containers, labels and evidence states consistent. Export through the saved R workflow to an editable SVG and any required, verified PDF/raster formats.

Live text and vector shapes are preferred. Declare any raster portion or outlined symbol; do not silently convert labels into paths. Avoid scripts, external resource references, filters or effects that impair reliable editing and publication handling.

## Check and revise

Follow [rendered QA](rendered-qa.md), including the applicable SVG audit. Inspect the complete export and the changed region after revisions. The XML audit cannot verify semantic relationships or detect every crossing and collision.

Walk the brief against the final output: all required entities and edges exist, optional/hypothetical links are distinguishable, arrows reach the intended entity, repeated labels agree, and numbered steps match the caption. A design with unavailable scientific evidence remains a draft even if its files pass.

Deliver saved R source, centralized style/layout settings, SVG, required verified exports, caption and unresolved assumptions. State how entities map to source definitions and which text remains editable. Do not introduce an external editor or image-generation route without a task-specific user exception.

Adapted from nature-figure (Apache-2.0)
