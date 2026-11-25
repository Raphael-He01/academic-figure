# Adapted from nature-figure (Apache-2.0). QA-only helper; it never renders a figure.
# Modified: measure drawn viewport and tag coordinates in PDF points; reject unsupported layouts, preserve audit error codes, and guard output paths.
# Modified from the upstream tool.
#
# The first line describes production scope: this helper never produces a
# scientific delivery figure. Measurement DOES draw the supplied plot on a
# temporary base-R PDF QA device, which is always removed. It exports only JSON
# geometry and optional diagnostic reports/overlays. Run figure production in
# RStudio; terminal Rscript is suitable for isolated helper regression tests.
# Dependencies: patchwork, grid (included with R), jsonlite; python3 for the gate.
# The temporary device uses base PDF font metrics. Match the final export size
# and font/device metrics; a different production device needs its own QA.
#
# Supported: flat patchwork ggplot panels, including spanning cells and a single
# panel. Composite/faceted, nested, inset, and unknown panel layouts are rejected
# as NOT AUDITABLE, rather than partially measured. Simple scalar ggplot tags
# are measured at their actual text anchors; unsupported or absent tags remain
# explicitly unmeasured. This does not test glyph outlines or text collisions.

.academic_alignment_source <- local({
  files <- lapply(sys.frames(), function(frame) frame$ofile)
  files <- Filter(function(path) is.character(path) && length(path) == 1L && nzchar(path), files)
  if (length(files)) normalizePath(tail(files, 1L)[[1L]], mustWork = FALSE) else NULL
})

.academic_alignment_error <- function(message, exit_code = 2L) {
  stop(structure(
    list(message = message, call = NULL, exit_code = as.integer(exit_code)),
    class = c("panel_alignment_error", "error", "condition")
  ))
}

.academic_alignment_auditor <- function() {
  if (is.null(.academic_alignment_source)) {
    .academic_alignment_error("Cannot locate this sourced helper; supply audit_script explicitly")
  }
  file.path(dirname(.academic_alignment_source), "audit_panel_alignment.py")
}

.academic_alignment_path <- function(path) {
  if (!is.character(path) || length(path) != 1L || is.na(path) || !nzchar(path)) {
    .academic_alignment_error("Each QA path must be one non-empty filename")
  }
  path <- path.expand(path)
  if (!grepl("^/|^[A-Za-z]:[/\\\\]", path)) path <- file.path(getwd(), path)
  normalizePath(path, mustWork = FALSE)
}

.academic_alignment_paths <- function(outputs, protected = character()) {
  normalized <- vapply(outputs, .academic_alignment_path, character(1))
  protected <- vapply(protected, .academic_alignment_path, character(1))
  if (anyDuplicated(normalized) || any(normalized %in% protected)) {
    .academic_alignment_error("QA output paths must be distinct and must not overwrite input scripts")
  }
  invisible(normalized)
}

.academic_alignment_groups <- function(groups) {
  if (is.null(groups)) return(NULL)
  if (!is.list(groups)) .academic_alignment_error("Alignment groups must be a list")
  lapply(groups, function(group) {
    if (is.list(group) && !is.null(group$panels)) {
      group$panels <- I(as.character(unlist(group$panels, use.names = FALSE)))
      group
    } else {
      I(as.character(unlist(group, use.names = FALSE)))
    }
  })
}

.academic_alignment_panel_rows <- function(grob) {
  names <- grob$layout$name
  recognized <- grepl("^panel(?:-[0-9]+)?$", names, perl = TRUE)
  unsupported <- grepl("^panel", names) & !recognized & names != "panel-area"
  # Insets and wrapped external grobs cannot silently disappear from this gate.
  unsupported <- unsupported | grepl("^inset|^(full|plot|patchwork-table)(-|$)", names)
  if (any(unsupported) || !any(recognized)) {
    detail <- if (any(unsupported)) paste(names[unsupported], collapse = ", ") else "no recognized plot panels"
    .academic_alignment_error(paste("NOT AUDITABLE: unsupported patchwork layout:", detail))
  }
  rows <- grob$layout[recognized, , drop = FALSE]
  rows[order(rows$t, rows$l), , drop = FALSE]
}

.academic_alignment_viewport <- function(row, viewports) {
  name <- paste0(row$name, ".", row$t, "-", row$r, "-", row$b, "-", row$l)
  indices <- which(viewports$name == name & viewports$type == "vpListing")
  if (length(indices) != 1L) {
    .academic_alignment_error(paste("NOT AUDITABLE: missing or ambiguous final viewport", name))
  }
  parent <- viewports$vpPath[indices]
  path <- paste(parent, name, sep = "::")
  pieces <- strsplit(path, "::", fixed = TRUE)[[1L]]
  pieces <- pieces[pieces != "ROOT"]
  grid::upViewport(0)
  grid::downViewport(do.call(grid::vpPath, as.list(pieces)), strict = TRUE)
  path
}

.academic_alignment_bbox <- function(row, viewports) {
  path <- .academic_alignment_viewport(row, viewports)
  # null units are resolved by the drawn gtable layout, not by root conversion.
  # deviceLoc(valueOnly=TRUE) returns device coordinates in INCHES. PDF points
  # are inches * 72; R's "pt" is 1/72.27 inch and must not be mixed into this JSON.
  lower <- grid::deviceLoc(grid::unit(0, "npc"), grid::unit(0, "npc"), valueOnly = TRUE)
  upper <- grid::deviceLoc(grid::unit(1, "npc"), grid::unit(1, "npc"), valueOnly = TRUE)
  bbox <- unname(c(lower$x, lower$y, upper$x, upper$y) * 72)
  if (length(bbox) != 4L || any(!is.finite(bbox)) || bbox[3] <= bbox[1] || bbox[4] <= bbox[2]) {
    .academic_alignment_error(paste("NOT AUDITABLE: non-positive final panel viewport", path))
  }
  list(bbox = bbox, viewport = path)
}

.academic_alignment_tag <- function(panel_row, grob, viewports) {
  suffix <- sub("^panel", "", panel_row$name)
  index <- which(grob$layout$name == paste0("tag", suffix))
  if (length(index) != 1L) return(list(status = "not-audited", reason = "No unique tag grob"))
  tag <- grob$grobs[[index]]
  # Restrict to the empirically verified ggplot titleGrob -> one text child path.
  # Custom gTrees, rich text, and child viewports require a separate adapter.
  if (!inherits(tag, "titleGrob") || !is.null(tag$vp) || length(tag$children) != 1L) {
    return(list(status = "not-audited", reason = "Unsupported tag grob structure"))
  }
  label <- tag$children[[1L]]
  if (!inherits(label, "text") || !is.null(label$vp) || length(label$x) != 1L ||
      length(label$y) != 1L || length(label$label) != 1L ||
      !is.character(label$label) || is.na(label$label) || !nzchar(trimws(label$label))) {
    return(list(status = "not-audited", reason = "Tag is not a scalar text anchor"))
  }
  tryCatch({
    path <- .academic_alignment_viewport(grob$layout[index, , drop = FALSE], viewports)
    grid::pushViewport(grid::viewport(gp = if (is.null(tag$gp)) grid::gpar() else tag$gp))
    grid::pushViewport(grid::viewport(gp = if (is.null(label$gp)) grid::gpar() else label$gp))
    location <- grid::deviceLoc(label$x, label$y, valueOnly = TRUE)
    grid::popViewport(2)
    anchor <- unname(c(location$x, location$y) * 72)
    if (length(anchor) != 2L || any(!is.finite(anchor))) stop("non-finite anchor")
    list(status = "measured", label = label$label, anchor = anchor, viewport = path)
  }, error = function(error) {
    grid::upViewport(0)
    list(status = "not-audited", reason = paste("Tag viewport measurement failed:", conditionMessage(error)))
  })
}

write_patchwork_panel_layout <- function(
  plot, manifest_path, width_in, height_in, panel_ids = NULL,
  row_groups = NULL, column_groups = NULL, exemptions = list()
) {
  for (package in c("patchwork", "grid", "jsonlite")) {
    if (!requireNamespace(package, quietly = TRUE)) {
      .academic_alignment_error(sprintf(
        "Package '%s' is required; this QA helper requires patchwork, grid and jsonlite (no automatic installation)", package
      ))
    }
  }
  valid_size <- function(value) is.numeric(value) && length(value) == 1L && is.finite(value) && value > 0
  if (!valid_size(width_in) || !valid_size(height_in)) {
    .academic_alignment_error("width_in and height_in must be positive finite numbers")
  }
  .academic_alignment_paths(c(manifest_path), .academic_alignment_source)
  parent <- dirname(manifest_path)
  if (!dir.exists(parent) && !dir.create(parent, recursive = TRUE, showWarnings = FALSE)) {
    .academic_alignment_error(paste("Cannot create QA output directory:", parent))
  }
  probe_path <- tempfile(pattern = ".panel-probe-", tmpdir = parent, fileext = ".pdf")
  temporary_path <- tempfile(pattern = ".panel-layout-", tmpdir = parent, fileext = ".json")
  probe_device <- NULL
  on.exit({
    if (!is.null(probe_device) && probe_device %in% grDevices::dev.list()) grDevices::dev.off(probe_device)
    unlink(c(probe_path, temporary_path))
  }, add = TRUE)
  # Open BEFORE constructing the grob: font-metric queries can otherwise open
  # an implicit Rplots.pdf device in the working directory.
  grDevices::pdf(probe_path, width = width_in, height = height_in, useDingbats = FALSE)
  probe_device <- grDevices::dev.cur()
  grob <- tryCatch(patchwork::patchworkGrob(
    if (inherits(plot, "patchwork")) plot else patchwork::wrap_plots(plot)
  ), error = function(error) {
    .academic_alignment_error(paste("NOT AUDITABLE: cannot construct patchwork layout:", conditionMessage(error)))
  })
  # Only wrap a single ggplot; wrapping an existing patchwork introduces nesting.
  panel_rows <- .academic_alignment_panel_rows(grob)
  if (is.null(panel_ids)) {
    panel_ids <- vapply(seq_len(nrow(panel_rows)), function(index) {
      if (index <= length(letters)) letters[index] else paste0("panel-", index)
    }, character(1))
  }
  panel_ids <- as.character(panel_ids)
  if (length(panel_ids) != nrow(panel_rows) || anyNA(panel_ids) || anyDuplicated(panel_ids) || any(!nzchar(trimws(panel_ids)))) {
    .academic_alignment_error("panel_ids must be unique, non-empty, and match the measured patchwork panels")
  }
  grid::grid.newpage()
  grid::grid.draw(grob)
  grid::grid.force()
  viewports <- grid::grid.ls(viewports = TRUE, grobs = FALSE, print = FALSE)
  labels <- vector("list", nrow(panel_rows))
  panels <- lapply(seq_len(nrow(panel_rows)), function(index) {
    row <- panel_rows[index, , drop = FALSE]
    measured <- .academic_alignment_bbox(row, viewports)
    tag <- .academic_alignment_tag(row, grob, viewports)
    labels[[index]] <<- tag$status
    panel <- list(
      id = panel_ids[index], bbox_pt = measured$bbox, grid_id = "patchwork-grid-1",
      row_start = as.integer(row$t - 1L), row_stop = as.integer(row$b),
      col_start = as.integer(row$l - 1L), col_stop = as.integer(row$r),
      measurement_viewport = measured$viewport,
      panel_label_measurement = tag[c("status", "reason", "viewport")]
    )
    panel$panel_label_measurement <- Filter(Negate(is.null), panel$panel_label_measurement)
    if (identical(tag$status, "measured")) {
      panel$panel_label <- tag$label
      panel$panel_label_anchor_pt <- tag$anchor
    }
    panel
  })
  grDevices::dev.off(probe_device)
  probe_device <- NULL
  missing_labels <- panel_ids[unlist(labels) != "measured"]
  if (length(missing_labels)) message("Panel labels NOT AUDITED for: ", paste(missing_labels, collapse = ", "))
  manifest <- list(
    schema_version = 1L, backend = "r-patchwork",
    figure = list(width_pt = width_in * 72, height_pt = height_in * 72),
    panels = panels, exemptions = exemptions,
    measurement = list(
      method = "final drawn viewport deviceLoc(npc) in inches times 72",
      device = "base-R pdf temporary QA device", units = "PDF points (72 per inch)",
      panel_labels = if (length(missing_labels)) "not-fully-audited" else "all-anchors-measured",
      unmeasured_panel_labels = I(missing_labels)
    )
  )
  normalized_rows <- .academic_alignment_groups(row_groups)
  normalized_columns <- .academic_alignment_groups(column_groups)
  if (!is.null(normalized_rows)) manifest$row_groups <- normalized_rows
  if (!is.null(normalized_columns)) manifest$column_groups <- normalized_columns
  jsonlite::write_json(manifest, temporary_path, auto_unbox = TRUE, pretty = TRUE, digits = NA)
  if (!file.rename(temporary_path, manifest_path)) {
    .academic_alignment_error("Could not activate the patchwork alignment manifest atomically")
  }
  invisible(manifest)
}

require_patchwork_panel_alignment <- function(
  plot, manifest_path, report_path, width_in, height_in, panel_ids = NULL,
  row_groups = NULL, column_groups = NULL, exemptions = list(),
  audit_script = .academic_alignment_auditor(), python = Sys.which("python3"),
  overlay_svg = NULL, tolerance_pt = 1.5, gutter_tolerance_pt = 1.5,
  strict = TRUE, require_panel_labels = FALSE
) {
  if (!is.character(python) || length(python) != 1L || is.na(python) || !nzchar(python)) {
    .academic_alignment_error("python3 is required for the panel-alignment JSON audit; supply python explicitly if needed")
  }
  if (!file.exists(audit_script)) .academic_alignment_error(paste("Panel-alignment audit script not found:", audit_script))
  .academic_alignment_paths(c(manifest_path, report_path, overlay_svg), c(audit_script, .academic_alignment_source))
  valid_tolerance <- function(value) is.numeric(value) && length(value) == 1L && is.finite(value) && value >= 0
  if (!valid_tolerance(tolerance_pt) || !valid_tolerance(gutter_tolerance_pt)) {
    .academic_alignment_error("Alignment and gutter tolerances must be finite non-negative numbers")
  }
  write_patchwork_panel_layout(
    plot, manifest_path, width_in, height_in, panel_ids,
    row_groups, column_groups, exemptions
  )
  args <- c(
    shQuote(audit_script), shQuote(manifest_path), "--json-out", shQuote(report_path),
    "--tolerance-pt", format(tolerance_pt, scientific = FALSE),
    "--gutter-tolerance-pt", format(gutter_tolerance_pt, scientific = FALSE)
  )
  if (!is.null(overlay_svg)) args <- c(args, "--overlay-svg", shQuote(overlay_svg))
  if (isTRUE(strict)) args <- c(args, "--strict")
  if (isTRUE(require_panel_labels)) args <- c(args, "--require-panel-labels")
  output <- suppressWarnings(system2(python, args = args, stdout = TRUE, stderr = TRUE))
  status <- attr(output, "status")
  if (is.null(status)) status <- 0L
  if (length(output)) message(paste(output, collapse = "\n"))
  if (status != 0L) {
    # Preserve the Python exit code in a typed R error. An unhandled R error
    # itself exits Rscript with 1; a CLI caller may catch e$exit_code and quit().
    .academic_alignment_error(sprintf(
      "Panel alignment gate failed with exit code %d; inspect %s", status, report_path
    ), exit_code = status)
  }
  invisible(jsonlite::read_json(report_path, simplifyVector = TRUE))
}
