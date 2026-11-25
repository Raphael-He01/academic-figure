summarise_trend <- function(trend, cfg) {
  trend$group <- factor(trend$group, levels = cfg$group_levels)
  keys <- interaction(trend$group, trend$day, drop = TRUE, lex.order = TRUE)
  pieces <- split(trend, keys)
  rows <- lapply(pieces, function(x) {
    n <- nrow(x)
    mean_value <- mean(x$response)
    se <- stats::sd(x$response) / sqrt(n)
    ci_half <- stats::qt(0.975, df = n - 1) * se
    data.frame(
      group = as.character(x$group[1]),
      day = x$day[1],
      n = n,
      mean = mean_value,
      sd = stats::sd(x$response),
      ci_low = mean_value - ci_half,
      ci_high = mean_value + ci_half,
      stringsAsFactors = FALSE
    )
  })
  out <- do.call(rbind, rows)
  rownames(out) <- NULL
  out$group <- factor(out$group, levels = cfg$group_levels)
  out <- out[order(out$group, out$day), ]
  rownames(out) <- NULL
  out
}

build_example_figure <- function(cfg, data_dir = "data", inputs = NULL) {
  if (is.null(inputs)) {
    read_input <- function(name) utils::read.csv(file.path(data_dir, name), check.names = FALSE)
    inputs <- list(trend = read_input("simulated_trend.csv"),
                   distribution = read_input("simulated_distribution.csv"),
                   heatmap = read_input("simulated_heatmap.csv"))
  }
  trend <- inputs$trend
  distribution <- inputs$distribution
  heatmap <- inputs$heatmap

  trend$group <- factor(trend$group, levels = cfg$group_levels)
  distribution$group <- factor(distribution$group, levels = cfg$group_levels)
  trend_summary <- summarise_trend(trend, cfg)

  p_trend <- ggplot2::ggplot(
    trend_summary,
    ggplot2::aes(
      x = day,
      y = mean,
      colour = group,
      shape = group,
      linetype = group,
      group = group
    )
  ) +
    ggplot2::geom_ribbon(
      ggplot2::aes(ymin = ci_low, ymax = ci_high, fill = group),
      alpha = 0.10,
      colour = NA,
      show.legend = FALSE
    ) +
    ggplot2::geom_errorbar(
      ggplot2::aes(ymin = ci_low, ymax = ci_high),
      linewidth = cfg$errorbar_line_mm,
      width = cfg$errorbar_width_days,
      show.legend = FALSE
    ) +
    ggplot2::geom_line(linewidth = cfg$data_line_mm) +
    ggplot2::geom_point(
      size = cfg$point_size_mm,
      stroke = 0.28,
      fill = "white"
    ) +
    ggplot2::scale_x_continuous(
      breaks = c(0, 7, 14, 21, 28),
      expand = ggplot2::expansion(mult = c(0.02, 0.04))
    ) +
    group_color_scale(cfg) +
    group_fill_scale(cfg) +
    group_shape_scale(cfg) +
    group_linetype_scale(cfg) +
    ggplot2::labs(
      title = "Time course",
      x = "Time after intervention (days)",
      y = "Response (a.u.)",
      colour = NULL,
      shape = NULL,
      linetype = NULL
    ) +
    academic_theme(cfg) +
    ggplot2::theme(
      legend.position = "top",
      legend.justification = "left",
      legend.box.margin = ggplot2::margin(0, 0, 2, 0)
    ) +
    ggplot2::guides(
      colour = ggplot2::guide_legend(
        nrow = 1,
        byrow = TRUE,
        override.aes = list(linewidth = 0.7, size = 2.2)
      )
    )

  p_distribution <- ggplot2::ggplot(
    distribution,
    ggplot2::aes(x = group, y = response, fill = group, colour = group)
  ) +
    ggdist::stat_halfeye(
      adjust = 0.75,
      width = 0.72,
      justification = -0.18,
      .width = 0,
      slab_alpha = 0.48,
      slab_colour = NA,
      point_colour = NA,
      show.legend = FALSE
    ) +
    ggplot2::geom_boxplot(
      width = 0.16,
      outlier.shape = NA,
      alpha = 0.82,
      colour = "#303030",
      linewidth = 0.36,
      position = ggplot2::position_nudge(x = -0.12),
      show.legend = FALSE
    ) +
    ggplot2::geom_point(
      position = ggplot2::position_jitter(width = 0.055, height = 0, seed = cfg$seed),
      size = 1.15,
      alpha = 0.72,
      stroke = 0,
      show.legend = FALSE
    ) +
    group_color_scale(cfg) +
    group_fill_scale(cfg) +
    ggplot2::scale_x_discrete(
      labels = c("Control" = "Control", "Treatment A" = "Treatment\nA", "Treatment B" = "Treatment\nB"),
      expand = ggplot2::expansion(add = c(0.38, 0.65))
    ) +
    ggplot2::labs(
      title = "Day 28 distribution",
      x = NULL,
      y = "Response (a.u.)"
    ) +
    academic_theme(cfg)

  condition_levels <- c(
    "Control_D7", "TreatmentA_D7", "TreatmentB_D7",
    "Control_D28", "TreatmentA_D28", "TreatmentB_D28"
  )
  condition_labels <- c(
    "Control\nD7", "Treatment A\nD7", "Treatment B\nD7",
    "Control\nD28", "Treatment A\nD28", "Treatment B\nD28"
  )
  heatmap$condition <- factor(heatmap$condition, levels = condition_levels)
  heatmap$feature <- factor(
    heatmap$feature,
    levels = rev(sprintf("Marker %02d", seq_len(10)))
  )

  p_heatmap <- ggplot2::ggplot(
    heatmap,
    ggplot2::aes(x = condition, y = feature, fill = z_score)
  ) +
    ggplot2::geom_tile(colour = "white", linewidth = 0.34) +
    ggplot2::scale_fill_gradient2(
      low = cfg$heatmap_low,
      mid = cfg$heatmap_mid,
      high = cfg$heatmap_high,
      midpoint = 0,
      limits = cfg$heatmap_limits,
      breaks = c(-2, -1, 0, 1, 2),
      na.value = cfg$missing_color,
      oob = scales::oob_keep,
      name = "Standardized\nresponse (z)"
    ) +
    ggplot2::scale_x_discrete(labels = condition_labels, drop = FALSE) +
    ggplot2::labs(
      title = "Standardized marker profile",
      x = NULL,
      y = NULL
    ) +
    academic_theme(cfg) +
    ggplot2::theme(
      panel.grid = ggplot2::element_blank(),
      axis.line = ggplot2::element_blank(),
      axis.ticks = ggplot2::element_blank(),
      axis.text.x = ggplot2::element_text(lineheight = 0.92),
      legend.position = "right"
    ) +
    ggplot2::guides(
      fill = ggplot2::guide_colourbar(
        title.position = "top",
        title.hjust = 0,
        display = "rectangles",
        barheight = grid::unit(34, "mm"),
        barwidth = grid::unit(2.8, "mm"),
        ticks.colour = "#333333",
        frame.colour = "#666666"
      )
    )

  if (isTRUE(cfg$heatmap_show_values)) {
    p_heatmap <- p_heatmap + ggplot2::geom_text(
      ggplot2::aes(label = sprintf("%.1f", round(z_score, 1) + 0)),
      colour = "#222222", size = cfg$axis_text_size_pt / 2.845,
      family = cfg$font_family
    )
  }
  top_row <- p_trend + p_distribution + patchwork::plot_layout(widths = c(1.18, 0.82))
  figure <- top_row / p_heatmap +
    patchwork::plot_layout(heights = c(1.02, 0.98)) +
    patchwork::plot_annotation(tag_levels = "A", caption = if (isTRUE(cfg$is_simulated)) "SIMULATED DATA | Workflow: Raphael He" else NULL) &
    ggplot2::theme(
      plot.tag = ggplot2::element_text(
        family = cfg$font_family,
        size = cfg$panel_tag_size_pt,
        face = "bold"
      )
    )

  list(
    figure = figure,
    trend = trend,
    distribution = distribution,
    heatmap = heatmap,
    trend_summary = trend_summary
  )
}

write_caption_and_results <- function(built, cfg, path = "docs/example_caption_and_results.md") {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  day28 <- built$distribution
  means <- stats::aggregate(response ~ group, day28, mean)
  sds <- stats::aggregate(response ~ group, day28, stats::sd)
  ns <- stats::aggregate(response ~ group, day28, length)
  summary28 <- Reduce(
    function(x, y) merge(x, y, by = "group"),
    list(
      setNames(means, c("group", "mean")),
      setNames(sds, c("group", "sd")),
      setNames(ns, c("group", "n"))
    )
  )
  summary28 <- summary28[match(c("Control", "Treatment A", "Treatment B"), summary28$group), ]

  difference_ci <- function(treatment) {
    x <- day28$response[day28$group == treatment]
    y <- day28$response[day28$group == "Control"]
    variance_x <- stats::var(x)
    variance_y <- stats::var(y)
    se_squared <- variance_x / length(x) + variance_y / length(y)
    degrees_of_freedom <- se_squared^2 / (
      (variance_x / length(x))^2 / (length(x) - 1) +
        (variance_y / length(y))^2 / (length(y) - 1)
    )
    margin <- stats::qt(0.975, df = degrees_of_freedom) * sqrt(se_squared)
    estimate <- mean(x) - mean(y)
    c(
      estimate = estimate,
      low = estimate - margin,
      high = estimate + margin
    )
  }
  diff_a <- difference_ci("Treatment A")
  diff_b <- difference_ci("Treatment B")

  fmt <- function(x) formatC(x, format = "f", digits = 1)
  md <- c(
    "# 示例图注与结果描述",
    "",
    "> 本页数值取自随附的模拟数据表，仅用于演示该图的分析与绘制。",
    "",
    "## 中文图题",
    "",
    "模拟干预组响应的时间趋势、终点分布与标志物谱。",
    "",
    "## 中文图注",
    "",
    paste0(
      "**图 1｜模拟干预组响应的多尺度展示。** ",
      "(A) 0-28 d 的模拟响应时间过程；符号表示各组均值，误差线和阴影表示 95% 置信区间，",
      "置信区间基于每个组别-时间单元的 t 分布均值区间；",
      "每个组别和时间点均包含 8 个相互独立的模拟观测。",
      "(B) 第 28 天的模拟分布；半眼图表示核密度，箱体表示四分位距，中线表示中位数，",
      "须线延伸至 1.5 倍四分位距范围内的最远值，点表示独立模拟观测。",
      "(C) 10 个模拟标志物在 6 个组别-时间组合中的标准化响应；色标以 0 为中心，",
      "显示范围为 -2.5 至 2.5，缺失值（本示例中无）预设为灰色。",
      "数据表登记的模拟种子为 ", cfg$seed, "；未执行假设检验，也未标注显著性。",
      "a.u.，任意单位。"
    ),
    "",
    "## 中文 Results 草稿",
    "",
    paste0(
      "在该模拟数据集中，第 28 天对照组、处理 A 组和处理 B 组的平均响应分别为 ",
      fmt(summary28$mean[1]), "、", fmt(summary28$mean[2]), " 和 ",
      fmt(summary28$mean[3]), " a.u.（每组 n = 8）。与对照组相比，处理 A 组的均值差为 ",
      fmt(diff_a["estimate"]), " a.u.（95% CI ", fmt(diff_a["low"]), " 至 ",
      fmt(diff_a["high"]), "），处理 B 组的均值差为 ", fmt(diff_b["estimate"]),
      " a.u.（95% CI ", fmt(diff_b["low"]), " 至 ", fmt(diff_b["high"]),
      "）。均值差区间采用 Welch-Satterthwaite 不等方差方法计算。",
      "这些描述仅概括模拟观测及其不确定性；未进行显著性检验，不能据此提出真实机制或因果结论。"
    ),
    "",
    "## English title",
    "",
    "Temporal response, endpoint distributions, and marker profiles in a simulated intervention dataset.",
    "",
    "## English legend",
    "",
    paste0(
      "**Figure 1 | Multiscale presentation of simulated intervention responses.** ",
      "(A) Simulated response trajectories from day 0 to day 28. Symbols show group means; ",
      "error bars and ribbons show t-based 95% confidence intervals for the mean. Each group-time cell contains ",
      "eight independent simulated observations. (B) Simulated day-28 distributions. ",
      "Half-eye slabs show kernel densities, boxes show interquartile ranges, center lines show medians, ",
      "whiskers extend to the most extreme value within 1.5 interquartile ranges, and points show ",
      "independent simulated observations. (C) Standardized responses for 10 simulated markers across ",
      "six group-time combinations. The color scale is centered at zero and spans -2.5 to 2.5; ",
      "missing values (none in this example) are mapped to gray. The input tables record simulation seed ",
      cfg$seed, ". No hypothesis tests or significance annotations were used. a.u., arbitrary units."
    ),
    "",
    "## English Results draft",
    "",
    paste0(
      "In this simulated dataset, the mean day-28 responses were ", fmt(summary28$mean[1]),
      ", ", fmt(summary28$mean[2]), ", and ", fmt(summary28$mean[3]),
      " a.u. for the control, treatment A, and treatment B groups, respectively (n = 8 per group). ",
      "Relative to control, the mean difference was ", fmt(diff_a["estimate"]),
      " a.u. for treatment A (95% CI ", fmt(diff_a["low"]), " to ", fmt(diff_a["high"]),
      ") and ", fmt(diff_b["estimate"]), " a.u. for treatment B (95% CI ",
      fmt(diff_b["low"]), " to ", fmt(diff_b["high"]),
      "). Mean-difference intervals used the Welch-Satterthwaite unequal-variance method. ",
      "These statements summarize only the simulated observations and their uncertainty. ",
      "No significance test was performed, and the data do not support a real mechanistic or causal claim."
    ),
    ""
  )
  writeLines(md, path, useBytes = TRUE)
  invisible(summary28)
}

export_example_figure <- function(built, cfg) {
  lapply(cfg$output_dirs, dir.create, recursive = TRUE, showWarnings = FALSE)

  width_in <- mm_to_in(cfg$width_mm)
  height_in <- mm_to_in(cfg$height_mm)
  pdf_path <- file.path(cfg$output_dirs$pdf, "academic_figure_example.pdf")
  svg_path <- file.path(cfg$output_dirs$svg, "academic_figure_example.svg")
  png_path <- file.path(cfg$output_dirs$png, "academic_figure_example.png")
  tiff_path <- file.path(cfg$output_dirs$tiff, "academic_figure_example.tiff")

  if (identical(Sys.info()[["sysname"]], "Darwin") && capabilities("aqua")) {
    pdf_device <- "quartz"
    grDevices::quartz(
      file = pdf_path,
      type = "pdf",
      width = width_in,
      height = height_in,
      family = cfg$font_family,
      bg = "white"
    )
  } else if (capabilities("cairo")) {
    # capabilities() alone can be TRUE even when Cairo shared libraries cannot load.
    probe_path <- tempfile(fileext = '.pdf')
    probe_device <- grDevices::dev.cur()
    probe_ok <- tryCatch(withCallingHandlers({
      grDevices::cairo_pdf(filename = probe_path, width = 1, height = 1)
      grDevices::dev.off()
      TRUE
    }, warning = function(w) stop(conditionMessage(w))), error = function(e) FALSE)
    if (grDevices::dev.cur() != probe_device) grDevices::dev.off()
    unlink(probe_path)
    if (!isTRUE(probe_ok)) stop('Cairo PDF device could not be initialized; choose and verify an available device before export.')
    pdf_device <- "cairo_pdf"
    grDevices::cairo_pdf(
      filename = pdf_path,
      width = width_in,
      height = height_in,
      family = cfg$font_family,
      onefile = TRUE,
      bg = "white"
    )
  } else {
    pdf_device <- "base_pdf_helvetica"
    warning("Cairo is unavailable; falling back to the base PDF device with Helvetica.")
    grDevices::pdf(
      file = pdf_path,
      width = width_in,
      height = height_in,
      family = "Helvetica",
      onefile = TRUE,
      bg = "white"
    )
  }
  print(built$figure)
  grDevices::dev.off()

  svglite::svglite(
    file = svg_path,
    width = width_in,
    height = height_in,
    bg = "white",
    system_fonts = list(sans = cfg$font_family)
  )
  print(built$figure)
  grDevices::dev.off()

  ragg::agg_png(
    filename = png_path,
    width = cfg$width_mm,
    height = cfg$height_mm,
    units = "mm",
    res = cfg$png_dpi,
    background = "white"
  )
  print(built$figure)
  grDevices::dev.off()

  ragg::agg_tiff(
    filename = tiff_path,
    width = cfg$width_mm,
    height = cfg$height_mm,
    units = "mm",
    res = cfg$tiff_dpi,
    compression = "lzw",
    background = "white"
  )
  print(built$figure)
  grDevices::dev.off()

  file.copy(
    png_path,
    file.path(cfg$output_dirs$previews, "academic_figure_example_preview.png"),
    overwrite = TRUE
  )
  utils::write.csv(
    built$trend_summary,
    file.path(cfg$output_dirs$qa, "trend_summary.csv"),
    row.names = FALSE
  )

  manifest <- data.frame(
    path = c(pdf_path, svg_path, png_path, tiff_path),
    format = c("PDF", "SVG", "PNG", "TIFF"),
    width_mm = cfg$width_mm,
    height_mm = cfg$height_mm,
    nominal_dpi = c(NA, NA, cfg$png_dpi, cfg$tiff_dpi),
    device = c(pdf_device, "svglite", "ragg_png", "ragg_tiff"),
    palette_id = cfg$palette$id,
    palette_version = cfg$palette$version,
    palette_mapping = as.character(jsonlite::toJSON(as.list(cfg$group_colors), auto_unbox = TRUE)),
    set_palette_mapping = as.character(jsonlite::toJSON(as.list(cfg$palette$mapping), auto_unbox = TRUE)),
    font_embedding = c(if (identical(pdf_device, "base_pdf_helvetica")) "not_embedded" else "pending", "not_applicable", "not_applicable", "not_applicable"),
    file_check = "pending",
    scientific_review = "pending",
    visual_review = "pending",
    acceptance = "pending",
    role = c(
      "vector draft; font and final acceptance pending",
      "editable vector interchange",
      "screen preview and review",
      "high-resolution raster fallback"
    ),
    stringsAsFactors = FALSE
  )
  utils::write.csv(
    manifest,
    file.path(cfg$output_dirs$qa, "export_manifest.csv"),
    row.names = FALSE,
    na = ""
  )

  write_caption_and_results(built, cfg)
  writeLines(
    capture.output(utils::sessionInfo()),
    file.path(cfg$output_dirs$qa, "session_info.txt"),
    useBytes = TRUE
  )

  invisible(manifest)
}
