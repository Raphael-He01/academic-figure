minimum_pairwise_delta_e <- function(colors) {
  if (length(colors) < 2L) return(NA_real_)
  rgb <- farver::decode_colour(colors, to = "rgb")
  distances <- farver::compare_colour(
    rgb,
    rgb,
    from_space = "rgb",
    to_space = "rgb",
    method = "cie2000"
  )
  min(distances[upper.tri(distances)])
}

run_palette_qa <- function(cfg, qa_dir = cfg$output_dirs$qa) {
  dir.create(qa_dir, recursive = TRUE, showWarnings = FALSE)

  simulations <- list(
    Original = identity,
    Deuteranopia = colorspace::deutan,
    Protanopia = colorspace::protan,
    Tritanopia = colorspace::tritan,
    Grayscale = colorspace::desaturate
  )
  variants <- lapply(simulations, function(simulate) simulate(unname(cfg$group_colors)))
  names_by_group <- names(cfg$group_colors)

  palette_table <- do.call(
    rbind,
    lapply(names(variants), function(variant) {
      data.frame(
        simulation = variant,
        group = names_by_group,
        color = variants[[variant]],
        stringsAsFactors = FALSE
      )
    })
  )
  palette_table$simulation <- factor(
    palette_table$simulation,
    levels = names(variants)
  )
  palette_table$group <- factor(palette_table$group, levels = cfg$group_levels)
  black_contrast <- as.numeric(colorspace::contrast_ratio(palette_table$color, "#000000"))
  white_contrast <- as.numeric(colorspace::contrast_ratio(palette_table$color, "#FFFFFF"))
  palette_table$label_color <- ifelse(black_contrast >= white_contrast, "#000000", "#FFFFFF")
  palette_table$label_contrast_ratio <- pmax(black_contrast, white_contrast)

  distances <- data.frame(
    simulation = names(variants),
    minimum_pairwise_delta_e_2000 = vapply(
      variants,
      minimum_pairwise_delta_e,
      numeric(1)
    ),
    stringsAsFactors = FALSE
  )
  distances$passes_illustrative_delta_e_10 <-
    distances$minimum_pairwise_delta_e_2000 >= 10
  distances$screen <- ifelse(
    is.na(distances$minimum_pairwise_delta_e_2000), "NOT APPLICABLE",
    ifelse(distances$passes_illustrative_delta_e_10, "PASS", "REVIEW")
  )
  distances$redundant_encoding <-
    "Group is also encoded by shape and line type in the trend panel."

  heatmap_anchors <- c(
    Negative = cfg$heatmap_low,
    Midpoint = cfg$heatmap_mid,
    Positive = cfg$heatmap_high
  )
  heatmap_variants <- lapply(simulations, function(simulate) simulate(heatmap_anchors))
  heatmap_distances <- data.frame(
    simulation = names(heatmap_variants),
    minimum_anchor_delta_e_2000 = vapply(
      heatmap_variants,
      minimum_pairwise_delta_e,
      numeric(1)
    ),
    negative_positive_delta_e_2000 = vapply(
      heatmap_variants,
      function(colors) {
        decoded <- farver::decode_colour(colors[c("Negative", "Positive")], to = "rgb")
        farver::compare_colour(
          decoded[1, , drop = FALSE],
          decoded[2, , drop = FALSE],
          from_space = "rgb",
          to_space = "rgb",
          method = "cie2000"
        )[1]
      },
      numeric(1)
    ),
    stringsAsFactors = FALSE
  )
  heatmap_distances$passes_illustrative_delta_e_10 <-
    heatmap_distances$minimum_anchor_delta_e_2000 >= 10

  utils::write.csv(
    palette_table,
    file.path(qa_dir, "palette_accessibility.csv"),
    row.names = FALSE
  )
  utils::write.csv(
    heatmap_distances,
    file.path(qa_dir, "heatmap_palette_accessibility.csv"),
    row.names = FALSE
  )
  report <- c(
    "Palette accessibility check",
    sprintf("Run date: %s", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
    "",
    sprintf(
      "%-16s minimum pairwise CIEDE2000 = %.1f (%s illustrative 10-unit screen)",
      distances$simulation,
      distances$minimum_pairwise_delta_e_2000,
      distances$screen
    ),
    "",
    "Heatmap diverging anchors:",
    sprintf(
      "%-16s minimum anchor CIEDE2000 = %.1f; negative-positive = %.1f (%s illustrative 10-unit screen)",
      heatmap_distances$simulation,
      heatmap_distances$minimum_anchor_delta_e_2000,
      heatmap_distances$negative_positive_delta_e_2000,
      ifelse(heatmap_distances$passes_illustrative_delta_e_10, "PASS", "REVIEW")
    ),
    "",
    "Use these numerical screens alongside final-size visual review.",
    "A single group has no pairwise colour-distance measurement.",
    "The trend panel does not rely on color alone; group is repeated with shape and line type.",
    "Check signed heatmap values or other redundant cues when grayscale weakens the distinction between endpoints."
  )
  writeLines(report, file.path(qa_dir, "palette_accessibility.txt"), useBytes = TRUE)

  swatch <- ggplot2::ggplot(
    palette_table,
    ggplot2::aes(x = group, y = simulation, fill = color)
  ) +
    ggplot2::geom_tile(colour = "white", linewidth = 0.8) +
    ggplot2::geom_text(
      ggplot2::aes(label = color, colour = label_color),
      family = cfg$font_family,
      size = 3,
      fontface = "bold"
    ) +
    ggplot2::scale_fill_identity() +
    ggplot2::scale_colour_identity() +
    ggplot2::scale_y_discrete(limits = rev(names(variants))) +
    ggplot2::labs(x = NULL, y = NULL, title = "Group palette under common viewing simulations") +
    ggplot2::theme_minimal(base_family = cfg$font_family, base_size = 9) +
    ggplot2::theme(
      panel.grid = ggplot2::element_blank(),
      plot.title = ggplot2::element_text(face = "bold", size = 10),
      axis.text = ggplot2::element_text(colour = "#222222")
    )

  swatch_path <- file.path(qa_dir, "palette_accessibility.png")
  ragg::agg_png(
    swatch_path,
    width = 165,
    height = 84,
    units = "mm",
    res = 180,
    background = "white"
  )
  swatch_device <- grDevices::dev.cur()
  on.exit(grDevices::dev.off(swatch_device), add = TRUE)
  print(swatch)

  if (any(distances$screen == "REVIEW")) {
    warning("At least one palette simulation fell below the illustrative Delta E screen.")
  }
  if (!all(heatmap_distances$passes_illustrative_delta_e_10)) {
    message("Heatmap palette has low separation in at least one simulation. Review the signed cues in the figure.")
  }

  invisible(distances)
}
