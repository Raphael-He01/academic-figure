# Plot supplied measurements only. Axis units and preprocessing must be stated by the caller.
plot_spectra <- function(data, x_label, y_label, colour = '#527F94') {
  if (!all(c('sample_id', 'wavelength', 'value') %in% names(data)) || !nrow(data)) stop('Missing spectral columns or rows')
  if (anyNA(data[c('sample_id', 'wavelength', 'value')]) || any(!nzchar(as.character(data$sample_id))) ||
      !is.numeric(data$wavelength) || !is.numeric(data$value) ||
      any(!is.finite(data$wavelength)) || any(!is.finite(data$value)) ||
      anyDuplicated(data[c('sample_id', 'wavelength')])) stop('Invalid spectral values or duplicate sample/wavelength keys')
  ggplot2::ggplot(data, ggplot2::aes(x = wavelength, y = value, group = sample_id)) +
    ggplot2::geom_line(colour = colour, alpha = .45, linewidth = .35) +
    ggplot2::labs(x = x_label, y = y_label) + ggplot2::theme_classic()
}

# Supply nodes in one coordinate system. Uniform segments show adjacency only.
plot_network <- function(nodes, edges, x_label, y_label, colour = '#527F94') {
  if (!all(c('id', 'x', 'y') %in% names(nodes)) || !all(c('from', 'to') %in% names(edges)) || !nrow(nodes)) stop('Missing node or edge columns')
  if (anyNA(nodes[c('id', 'x', 'y')]) || any(!nzchar(as.character(nodes$id))) || anyDuplicated(nodes$id) ||
      !is.numeric(nodes$x) || !is.numeric(nodes$y) || any(!is.finite(nodes$x)) || any(!is.finite(nodes$y))) stop('Invalid nodes')
  from <- match(edges$from, nodes$id); to <- match(edges$to, nodes$id)
  if (anyNA(from) || anyNA(to)) stop('Edges must reference supplied nodes')
  lines <- data.frame(x = nodes$x[from], y = nodes$y[from], xend = nodes$x[to], yend = nodes$y[to])
  ggplot2::ggplot() + ggplot2::geom_segment(data = lines, ggplot2::aes(x, y, xend = xend, yend = yend),
    colour = colour, alpha = .24, linewidth = .3) +
    ggplot2::geom_point(data = nodes, ggplot2::aes(x, y), colour = colour, size = 1.5) +
    ggplot2::coord_equal() + ggplot2::labs(x = x_label, y = y_label) + ggplot2::theme_classic()
}

# Zoom a rectangle in the original x/y variables, retaining the Cartesian coordinate
# settings (aspect ratio, flipped axes and clipping). Projected maps need a CRS-aware locator.
linked_zoom <- function(plot, xlim, ylim) {
  if (length(xlim) != 2 || length(ylim) != 2 || any(!is.finite(c(xlim, ylim))) ||
      xlim[1] >= xlim[2] || ylim[1] >= ylim[2]) stop('Invalid zoom bounds')
  coord <- plot$coordinates
  if (!inherits(coord, 'CoordCartesian') || inherits(coord, 'CoordSf') || !isTRUE(coord$is_linear())) {
    stop('linked_zoom requires linear Cartesian coordinates. Use a locator designed for this coordinate system.')
  }
  detail <- plot
  detail$coordinates <- ggplot2::ggproto(NULL, coord, limits = list(x = xlim, y = ylim), expand = FALSE)
  overview <- plot + ggplot2::annotate('rect', xmin = xlim[1], xmax = xlim[2],
    ymin = ylim[1], ymax = ylim[2], fill = NA, colour = '#8A5D51', linewidth = .45)
  list(overview = overview, detail = detail)
}
