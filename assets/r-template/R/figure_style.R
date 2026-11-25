academic_theme <- function(cfg) {
  ggplot2::theme_classic(
    base_family = cfg$font_family,
    base_size = cfg$base_size_pt
  ) +
    ggplot2::theme(
      text = ggplot2::element_text(
        family = cfg$font_family,
        colour = "#222222"
      ),
      axis.title = ggplot2::element_text(
        size = cfg$axis_title_size_pt,
        colour = "#222222"
      ),
      axis.text = ggplot2::element_text(
        size = cfg$axis_text_size_pt,
        colour = "#333333"
      ),
      axis.line = ggplot2::element_line(
        linewidth = cfg$axis_line_mm,
        colour = "#333333"
      ),
      axis.ticks = ggplot2::element_line(
        linewidth = cfg$axis_line_mm,
        colour = "#333333"
      ),
      axis.ticks.length = grid::unit(2.2, "pt"),
      panel.grid.major.y = ggplot2::element_line(
        linewidth = cfg$grid_line_mm,
        colour = "#E2E5E9"
      ),
      panel.grid.major.x = ggplot2::element_blank(),
      panel.grid.minor = ggplot2::element_blank(),
      plot.title = ggplot2::element_text(
        size = cfg$panel_title_size_pt,
        face = "bold",
        margin = ggplot2::margin(b = 3)
      ),
      plot.tag = ggplot2::element_text(
        size = cfg$panel_tag_size_pt,
        face = "bold",
        hjust = 0
      ),
      plot.tag.position = c(0, 1),
      legend.title = ggplot2::element_text(
        size = cfg$legend_title_size_pt,
        face = "plain"
      ),
      legend.text = ggplot2::element_text(
        size = cfg$legend_text_size_pt
      ),
      legend.key.height = grid::unit(10, "pt"),
      legend.key.width = grid::unit(18, "pt"),
      legend.spacing.x = grid::unit(4, "pt"),
      panel.spacing = grid::unit(cfg$panel_spacing_pt, "pt"),
      plot.margin = ggplot2::margin(
        cfg$plot_margin_pt[1],
        cfg$plot_margin_pt[2],
        cfg$plot_margin_pt[3],
        cfg$plot_margin_pt[4]
      )
    )
}

group_color_scale <- function(cfg) {
  ggplot2::scale_colour_manual(
    values = cfg$group_colors,
    breaks = cfg$group_levels,
    drop = FALSE
  )
}

group_fill_scale <- function(cfg) {
  ggplot2::scale_fill_manual(
    values = cfg$group_colors,
    breaks = cfg$group_levels,
    drop = FALSE
  )
}

group_shape_scale <- function(cfg) {
  ggplot2::scale_shape_manual(
    values = cfg$group_shapes,
    breaks = cfg$group_levels,
    drop = FALSE
  )
}

group_linetype_scale <- function(cfg) {
  ggplot2::scale_linetype_manual(
    values = cfg$group_linetypes,
    breaks = cfg$group_levels,
    drop = FALSE
  )
}
