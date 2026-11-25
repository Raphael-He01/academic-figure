# Schematic visual grammar

Read while laying out an editable diagram with the [editable schematic workflow](vector-schematic-workflow.md). These defaults are adjustable design choices, not a journal's universal requirements.

## Typography and boxes

- Use a coherent family and a small hierarchy for group headings, entity labels and secondary descriptions. Follow the selected journal profile rather than assigning all schematics one point-size range.
- Preserve manuscript spelling, symbols and capitalization. Avoid automatic title-casing of model or gene identifiers.
- Size containers from measured text plus padding. Prefer short labels and purposeful line breaks; move explanatory prose to the caption.
- Align repeated labels consistently. Check apparent centring and multiline baselines after export rather than relying only on coordinates.
- Keep lettering editable where possible and verify glyph availability. Neutral dark lettering is the default; meaningful coloured labels need adequate contrast.

## Colour and evidence

- Reuse the [palette system](palette-system.md). Category, magnitude and evidence status are different variables and need distinct mappings.
- A quiet background and limited emphasis help identify the main path, but there is no universal rule requiring a particular hue or exactly one highlighted component.
- Distinguish established, proposed and unavailable relationships with words plus line/shape cues. A vivid colour must not make a hypothetical relationship appear established.
- Avoid decorative shading, perspective and effects that imply an unsupported quantity or hierarchy. Any purposeful gradient must encode a defined variable.

## Connections

- Define what direction and arrowheads mean. Bidirectional transfer, inhibition and undirected association require different, explained marks.
- Give each dash pattern one stable semantic role within the diagram. When feedback and uncertainty coexist, encode them separately.
- Attach links to intentional points on the correct entity. Keep links away from labels, container titles and unrelated outlines.
- Distinguish a crossing from a true branch or junction. Add an explicit junction mark where needed, and check whether a gap is misread as a broken connection.
- Prefer simple routes with adequate clearance. Rearrange boxes before adding unnecessary bends; a fixed maximum bend count must not override a correct topology.
- A link to a whole container must actually refer to that group, not to an unlabeled internal member.

## Repeated structures and hierarchy

Align entities with the same role and keep repeated spacing and internal order consistent. Use whitespace to separate levels without obscuring relationships. Add container nesting only when it represents real structure.

Represent repeated identical units compactly only if their count and shared behavior are known. Do not turn an unmeasured population into a misleading multiplicity mark.

Use a local legend when symbols are otherwise ambiguous, regardless of how many colours exist. Step numbers are useful only when the flow and caption refer to the same ordered process.

## Final semantic walk

Trace each path from start to destination, including return flows and conditional branches. Compare the actual topology to the brief. Inspect label/edge separation, arrowhead scale, image/text contrast and grayscale meaning at publication size. Use [rendered QA](rendered-qa.md) for the mechanical and visual checks; a clean diagram cannot validate the proposed mechanism.

Adapted from nature-figure (Apache-2.0)

## Linked conceptual scales

When evidence supports tissue-to-organelle-to-molecular context, link a selected region to its detailed view using a visually distinct connector labelled as scale/context, separate from material-transfer or causal arrows. Keep entity and compartment IDs consistent, define the roles of arrow colour, head and line style, and trace each edge, return route and compartment boundary against the cited brief. Where an inset connector and a scientific feedback path both use dashes, change their mark or label to prevent confusion. Reserve neutral negative space around small labels and inspect paths at final size; conceptual geometry is not to scale and arrow width is not flux unless explicitly defined. Store geometry and entity relations separately in project-specific editable R/Origin work; this is not an implemented template. See [reference evidence](reference-observations-2026-11-10-spectral-multiscale.md).
