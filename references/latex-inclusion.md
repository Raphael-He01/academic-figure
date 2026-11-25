# Place completed figures in LaTeX

Read when PDF/SVG artwork and its caption already exist and the task is manuscript insertion. This workflow does not regenerate plots, change their scientific content or introduce Python drawing.

## Keep one caption and one artifact identity

Use the delivered figure stem and canonical caption. If the manuscript needs TeX, transcribe/escape that same caption once into a reusable TeX fragment and compare its text, numbers, symbols and panel references with the delivered version. Do not author a second interpretive caption during insertion.

Place a stable `label` after the caption so cross-references inherit the correct counter. Confirm that each substantive manuscript use agrees with the existing manifest's supported claims and limitations.

## Choose the placement

| Situation | Insertion choice | Check |
|---|---|---|
| Completed single-column composite | `figure` with `graphicx` | Target column width and aspect ratio |
| Completed double-column composite | Template-supported `figure*` | Class-specific float placement |
| Separate finished panel files | `subcaption` only if the class permits | Existing panel letters, ordering and no duplicated numbering |
| Wide completed figure | Template-supported landscape page, commonly `pdflscape` | Orientation, usable page width and readable caption |

Prefer inserting an already assembled composite as one object. Do not split it simply to imitate an upstream multi-panel example.

The following is an insertion pattern, not a plotting template. The referenced artwork and caption fragment must already be part of the delivery; substitute their real shared stem without inventing content.

```latex
% Preamble: \usepackage{graphicx}
\begin{figure}[tbp]
  \centering
  \includegraphics[width=\linewidth,keepaspectratio]{figures/fig02_topic_v01.pdf}
  \caption{\input{captions/fig02_topic_v01.tex}}
  \label{fig:topic}
\end{figure}
```

Use a bare `includegraphics` or an explicit verified physical width when natural-size placement is required. The example's `linewidth` placement is appropriate only after comparing it with the delivered width. Do not specify inconsistent width and height that distort geometry.

Standard PDF-oriented LaTeX workflows accept PDF artwork directly. SVG insertion depends on the compiler/toolchain; do not silently enable shell escape, install a converter or substitute a raster. If no verified PDF is available, report the supported route and the remaining conversion requirement. Any new scientific export follows the current authorized RStudio/Origin production route, with saved editable source and export checks.

## Verify the placed result

- Check the log for missing files, unresolved references and overflow; compilation success alone does not verify layout.
- Compare placed width with export width. A placement scale multiplies effective font sizes and line weights; inspect the actual manuscript page.
- Preserve the figure's crop and aspect ratio. Check legends, colourbars, small symbols and panel letters after reduction.
- Confirm caption text and panel references match the canonical caption, with no duplicated subfigure labels.
- Keep APA formatting choices in [the opt-in APA profile](apa-figure-profile.md); do not set them implicitly in general insertion code.
- Record whether compilation and page inspection actually occurred. When the manuscript/toolchain is unavailable, deliver insertion instructions with that validation pending.

Use [rendered QA](rendered-qa.md) for any affected final-size checks. LaTeX inclusion is a new placement of an existing deliverable, not evidence that a new plot was produced.

Adapted from ARS-Codex 3.23.1 (CC BY-NC 4.0), Copyright (c) 2026 Cheng-I Wu
