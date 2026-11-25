# Input: one row per supplied estimate, with explicit scale and interval meaning.
plot_forest <- function(data, null = 0, x_label = 'Effect estimate',
                        colour = '#527F94') {
  required <- c('label', 'estimate', 'lower', 'upper')
  if (!all(required %in% names(data)) || !nrow(data)) stop('Missing forest input columns or rows')
  if (anyNA(data[required]) || any(!is.finite(as.matrix(data[c('estimate', 'lower', 'upper')]))) ||
      any(data$lower > data$estimate | data$estimate > data$upper)) stop('Invalid interval values')
  data$label <- factor(data$label, levels = rev(unique(as.character(data$label))))
  if (anyDuplicated(as.character(data$label))) stop('Labels must uniquely identify rows')
  ggplot2::ggplot(data, ggplot2::aes(x = estimate, y = label)) +
    ggplot2::geom_vline(xintercept = null, colour = '#999999', linetype = 'dashed') +
    ggplot2::geom_errorbar(ggplot2::aes(xmin = lower, xmax = upper), orientation = 'y', width = .16, colour = colour) +
    ggplot2::geom_point(colour = colour, size = 2) +
    ggplot2::labs(x = x_label, y = NULL) + ggplot2::theme_classic()
}
