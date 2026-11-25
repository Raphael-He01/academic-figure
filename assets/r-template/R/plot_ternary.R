# Input: observed fractions on the same basis; no interpolation or fitted surface.
plot_ternary_points <- function(data, tolerance = 1e-6, colour = '#C289A0') {
  # Closure is measured on the fraction scale. A tolerance of one admits an empty mixture.
  if (!is.numeric(tolerance) || length(tolerance) != 1L || !is.finite(tolerance) ||
      tolerance < 0 || tolerance >= 1) stop('tolerance must be a finite scalar in [0, 1)')
  if (!all(c('a', 'b', 'c') %in% names(data)) || !nrow(data)) stop('Missing composition columns or rows')
  x <- as.matrix(data[c('a', 'b', 'c')])
  if (!is.numeric(x) || any(!is.finite(x)) || any(x < 0) || any(abs(rowSums(x) - 1) > tolerance))
    stop('Fractions must be finite, nonnegative and sum to one')
  points <- data.frame(x = data$b + data$c / 2, y = data$c * sqrt(3) / 2)
  boundary <- data.frame(x = c(0, 1, .5, 0), y = c(0, 0, sqrt(3)/2, 0))
  ggplot2::ggplot() + ggplot2::geom_path(data = boundary, ggplot2::aes(x, y), colour = '#555555') +
    ggplot2::geom_point(data = points, ggplot2::aes(x, y), colour = colour, size = 2) +
    ggplot2::annotate('text', x = c(0, 1, .5), y = c(-.04, -.04, sqrt(3)/2 + .04), label = c('A', 'B', 'C')) +
    ggplot2::coord_equal(clip = 'off') + ggplot2::theme_void() +
    ggplot2::theme(plot.background = ggplot2::element_rect(fill = 'white', colour = NA),
                   plot.margin = ggplot2::margin(15, 20, 15, 20))
}
