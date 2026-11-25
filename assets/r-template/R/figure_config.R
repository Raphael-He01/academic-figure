# Registry values are pinned inside each scaffolded project.
resolve_colour_card <- function(id, groups, registry_path = "data/palettes/catalog.json") {
  if (!requireNamespace("jsonlite", quietly = TRUE)) stop("Missing R package: jsonlite")
  if (anyDuplicated(groups) || anyNA(groups) || any(!nzchar(groups))) stop("Groups must be unique, nonempty names")
  registry <- jsonlite::fromJSON(registry_path, simplifyVector = FALSE)
  hits <- Filter(function(x) identical(x$id, id) || identical(x$name, id) || id %in% unlist(x$aliases), registry$palettes)
  if (length(hits) != 1L) stop("Unknown or ambiguous colour card: ", id)
  card <- hits[[1]]
  colours <- unlist(card$main, use.names = FALSE)
  if (!identical(card$kind, "categorical") || length(groups) > length(colours)) {
    stop("Card does not support these categories; use facets or an explicitly reviewed extension")
  }
  list(id = card$id, version = card$version, name = card$name,
       status = card$status, mapping = stats::setNames(colours[seq_along(groups)], groups),
       support = unlist(card$support, use.names = FALSE), background = card$background, text = card$text)
}

figure_config <- function(palette_id = "rose_mist", groups = c("Control", "Treatment A", "Treatment B"),
                          registry_path = "data/palettes/catalog.json", set_groups = groups) {
  set_names <- as.character(set_groups)
  displayed <- as.character(groups)
  if (!length(set_names) || length(set_names) > 3L) stop("Example scaffold supports one to three groups per set")
  card <- resolve_colour_card(palette_id, set_names, registry_path)
  if (!length(displayed) || anyDuplicated(displayed) || !all(displayed %in% set_names)) {
    stop("Display groups must be distinct members of the figure set")
  }
  colours <- card$mapping[displayed]
  shapes <- stats::setNames(c(16, 17, 15)[seq_along(set_names)], set_names)
  lines <- stats::setNames(c("solid", "longdash", "dotted")[seq_along(set_names)], set_names)
  cfg <- list(
    seed = 20261009L,
    is_simulated = TRUE,

    # Final-size canvas. The example is designed as a generic double-column figure.
    width_mm = 183,
    height_mm = 148,
    png_dpi = 300,
    tiff_dpi = 600,

    font_family = "Arial",
    base_size_pt = 7.5,
    axis_title_size_pt = 8.0,
    axis_text_size_pt = 7.0,
    legend_text_size_pt = 7.0,
    legend_title_size_pt = 7.2,
    panel_title_size_pt = 8.2,
    panel_tag_size_pt = 10.0,

    axis_line_mm = 0.38,
    grid_line_mm = 0.22,
    data_line_mm = 0.62,
    point_size_mm = 1.75,
    errorbar_line_mm = 0.42,
    errorbar_width_days = 0.75,

    plot_margin_pt = c(4, 5, 4, 5),
    panel_spacing_pt = 7,

    group_levels = groups,
    palette = card,
    group_colors = colours,
    group_shapes = shapes[displayed],
    group_linetypes = lines[displayed],

    heatmap_show_values = TRUE,
    heatmap_low = "#3B6FB6",
    heatmap_mid = "#F7F7F7",
    heatmap_high = "#C44E52",
    heatmap_limits = c(-2.5, 2.5),
    missing_color = "#D9D9D9",

    output_dirs = list(
      pdf = "output/pdf",
      svg = "output/svg",
      png = "output/png",
      tiff = "output/tiff",
      qa = "output/qa",
      previews = "output/previews"
    )
  )
  cfg$colour_roles <- list(group_fill = colours, group_line = colours,
                           interval_fill = stats::setNames(grDevices::adjustcolor(colours, alpha.f = .2), displayed),
                           emphasis = unname(card$mapping[1]),
                           background = card$background, text = card$text,
                           missing = cfg$missing_color, support = card$support)
  cfg
}

mm_to_in <- function(x) x / 25.4
