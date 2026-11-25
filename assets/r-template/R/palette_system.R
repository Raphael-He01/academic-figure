academic_palettes <- function(n_continuous = 9L, n_cyclic = 12L) {
  stopifnot(n_continuous >= 3L, n_cyclic >= 4L)
  list(
    af_qualitative_light = c(
      blue = "#0072B2", orange = "#E69F00", green = "#009E73",
      purple = "#CC79A7", sky = "#56B4E9", vermillion = "#D55E00"
    ),
    af_emphasis_light = c(
      context_light = "#C7CBD1", context_mid = "#858B94",
      context_dark = "#4B515A", focus_blue = "#0072B2",
      focus_vermillion = "#D55E00"
    ),
    af_sequential_cividis = viridisLite::viridis(n_continuous, option = "E"),
    af_diverging_bwr = grDevices::colorRampPalette(
      c("#3B6FB6", "#A9C4DF", "#F7F7F7", "#E7B1A8", "#B64A3A"),
      space = "Lab"
    )(n_continuous),
    # Generate one extra colour and drop the repeated endpoint. The first and
    # last displayed phases remain neighbours without becoming duplicates.
    af_cyclic_phase = colorspace::rainbow_hcl(
      n_cyclic + 1L, c = 55, l = 62, start = 15, end = 375
    )[seq_len(n_cyclic)]
  )
}

palette_registry <- function() {
  data.frame(
    name = c("af_qualitative_light", "af_emphasis_light", "af_sequential_cividis", "af_diverging_bwr", "af_cyclic_phase"),
    class = c("qualitative", "emphasis", "sequential", "diverging", "cyclic"),
    recommended_n = c("3-6", "1 focus + up to 3 context", "continuous", "continuous around declared centre", "continuous phase/angle"),
    background = c("light", "light", "light or dark after review", "light", "light"),
    limitation = c(
      "Use shape/line type when categories are dense or grayscale output matters.",
      "Do not use both focus colours unless two focal meanings are explicit.",
      "Do not use for unordered categories.",
      "Not sufficient for grayscale-only interpretation; declare centre and limits.",
      "Only for periodic variables; inspect wrap seam."
    ),
    stringsAsFactors = FALSE
  )
}

minimum_palette_delta_e <- function(x) {
  rgb <- farver::decode_colour(x, to = "rgb")
  d <- farver::compare_colour(rgb, rgb, from_space = "rgb", to_space = "rgb", method = "cie2000")
  min(d[upper.tri(d)])
}

audit_palette_system <- function(output_dir = "output/qa", font_family = "Arial") {
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  palettes <- academic_palettes()
  variants <- list(original = identity, deutan = colorspace::deutan,
    protan = colorspace::protan, tritan = colorspace::tritan,
    grayscale = colorspace::desaturate)
  rows <- do.call(rbind, lapply(names(palettes), function(pn)
    do.call(rbind, lapply(names(variants), function(vn) {
      cols <- variants[[vn]](unname(palettes[[pn]]))
      lab <- farver::decode_colour(cols, to = "lab")
      data.frame(palette = pn, simulation = vn, index = seq_along(cols),
        color = cols, lightness_L = lab[, "l"],
        contrast_white = as.numeric(colorspace::contrast_ratio(cols, "white")),
        stringsAsFactors = FALSE)
    }))))
  metrics <- do.call(rbind, lapply(split(rows,
    list(rows$palette, rows$simulation), drop = TRUE), function(z)
      data.frame(palette = z$palette[1], simulation = z$simulation[1],
        minimum_pairwise_delta_e_2000 = minimum_palette_delta_e(z$color),
        minimum_contrast_on_white = min(z$contrast_white),
        lightness_span = diff(range(z$lightness_L)), stringsAsFactors = FALSE)))
  utils::write.csv(palette_registry(), file.path(output_dir, "palette_registry.csv"), row.names = FALSE)
  utils::write.csv(rows, file.path(output_dir, "palette_system_colors.csv"), row.names = FALSE)
  utils::write.csv(metrics, file.path(output_dir, "palette_system_metrics.csv"), row.names = FALSE)

  discrete <- subset(rows, palette %in% c("af_qualitative_light", "af_emphasis_light"))
  marks <- ggplot2::ggplot(discrete,
    ggplot2::aes(index, lightness_L, colour = color, group = simulation)) +
    ggplot2::geom_line(linewidth = 0.45, colour = "#A7ABB2") +
    ggplot2::geom_point(size = 2.6) +
    ggplot2::geom_point(ggplot2::aes(x = index + 0.12), size = 5.2, alpha = 0.35) +
    ggplot2::scale_colour_identity() +
    ggplot2::facet_grid(simulation ~ palette, scales = "free_x") +
    ggplot2::labs(x = "Palette index (bind real colours by level name)",
      y = "CIELAB lightness", title = "Small marks, thin lines and alpha overlap") +
    ggplot2::theme_minimal(base_family = font_family, base_size = 8) +
    ggplot2::theme(panel.grid.minor = ggplot2::element_blank(),
      strip.text = ggplot2::element_text(size = 7))
  continuous <- subset(rows, palette %in% c("af_sequential_cividis",
    "af_diverging_bwr", "af_cyclic_phase"))
  strips <- ggplot2::ggplot(continuous, ggplot2::aes(index, simulation, fill = color)) +
    ggplot2::geom_tile() + ggplot2::scale_fill_identity() +
    ggplot2::facet_wrap(~palette, ncol = 1, scales = "free_x") +
    ggplot2::labs(x = "Mapped value / phase", y = NULL,
      title = "Continuous mapping under viewing simulations") +
    ggplot2::theme_minimal(base_family = font_family, base_size = 8) +
    ggplot2::theme(panel.grid = ggplot2::element_blank(),
      strip.text = ggplot2::element_text(size = 7))
  combined <- marks / strips + patchwork::plot_layout(heights = c(1.35, 1))
  ragg::agg_png(file.path(output_dir, "palette_system_qa.png"),
    width = 183, height = 210, units = "mm", res = 220, background = "white")
  print(combined)
  grDevices::dev.off()
  seq_original <- subset(rows,
    palette == "af_sequential_cividis" & simulation == "original")
  monotonic <- all(diff(seq_original$lightness_L) >= -0.5) ||
    all(diff(seq_original$lightness_L) <= 0.5)
  writeLines(c("Academic palette system QA",
    sprintf("Run date: %s", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
    sprintf("Cividis lightness path broadly monotonic: %s", monotonic),
    "CVD: deutan/protan/tritan; grayscale: chroma removal.",
    "Reviewed: small points, thin lines, alpha overlap, continuous strips.",
    "Numerical screens support review; they do not prove universal accessibility.",
    "Diverging heatmaps need values/contours or a monochrome alternative in grayscale."),
    file.path(output_dir, "palette_system_qa.txt"))
  package_versions <- vapply(
    c("R", "ggplot2", "patchwork", "colorspace", "viridisLite", "farver", "ragg"),
    function(pkg) if (pkg == "R") as.character(getRversion()) else
      as.character(utils::packageVersion(pkg)), character(1)
  )
  writeLines(
    sprintf("%s: %s", names(package_versions), package_versions),
    file.path(output_dir, "palette_package_versions.txt")
  )
  invisible(list(colors = rows, metrics = metrics,
    sequential_monotonic = monotonic))
}
