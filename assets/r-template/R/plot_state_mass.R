# One row per state sample at a numeric time. Weights are relative within time.
state_mass_table <- function(data, times, breaks, threshold = 0) {
  fields <- c("time", "state", "weight")
  if (!is.data.frame(data) || !all(fields %in% names(data)) || anyDuplicated(names(data)))
    stop("Supply a table with unambiguous time, state and weight columns")
  if (!all(vapply(data[fields], is.numeric, logical(1))) ||
      any(!is.finite(as.matrix(data[fields]))) || any(data$weight < 0))
    stop("Time, state and weight must be finite numeric values with nonnegative weights")
  if (!is.numeric(times) || !length(times) || any(!is.finite(times)) || anyDuplicated(times))
    stop("Supply the distinct finite numeric times of the intended schedule")
  if (!is.numeric(breaks) || length(breaks) < 2L || any(!is.finite(breaks)) ||
      is.unsorted(breaks, strictly = TRUE))
    stop("Bin edges must be finite and strictly increasing")
  if (!is.numeric(threshold) || length(threshold) != 1L || !is.finite(threshold))
    stop("The branch threshold must be one finite number")
  if ("particle" %in% names(data) &&
      (anyNA(data$particle) || any(!nzchar(trimws(as.character(data$particle)))) ||
       anyDuplicated(data[c("time", "particle")])))
    stop("Each supplied particle ID must be present and unique within its time")

  times <- sort(times)
  index <- match(data$time, times)
  if (anyNA(index)) stop("The schedule omits time values present in the input")
  groups <- split(seq_len(nrow(data)), factor(index, levels = seq_along(times)))
  n_bins <- length(breaks) - 1L
  mass <- matrix(NA_real_, nrow = n_bins, ncol = length(times))
  summary <- data.frame(time = times, n = unname(lengths(groups)), above = NA_real_,
                        below_range = NA_real_, above_range = NA_real_, ess = NA_real_)
  for (j in which(summary$n > 0L)) {
    rows <- groups[[j]]
    state <- data$state[rows]
    w <- data$weight[rows]
    peak <- max(w)
    if (peak == 0) stop("All weights are zero at time ", times[j])
    # Scaling before summing keeps finite, very large raw weights usable.
    w <- w / peak
    total <- sum(w)
    bin <- findInterval(state, breaks, rightmost.closed = TRUE)
    mass[, j] <- 0
    inside <- bin >= 1L & bin <= n_bins
    if (any(inside)) {
      sums <- tapply(w[inside], bin[inside], sum)
      mass[as.integer(names(sums)), j] <- sums / total
    }
    summary$above[j] <- sum(w[state > threshold]) / total
    summary$below_range[j] <- sum(w[bin == 0L]) / total
    summary$above_range[j] <- sum(w[bin > n_bins]) / total
    summary$ess[j] <- total^2 / sum(w^2)
  }
  cells <- data.frame(time = rep(times, each = n_bins),
                      lower = rep(head(breaks, -1), length(times)),
                      upper = rep(tail(breaks, -1), length(times)), mass = as.vector(mass))
  list(cells = cells, summary = summary, threshold = threshold)
}

plot_state_mass <- function(result, high = "#527F94", low = "#FBF8F5", mass_max = 1) {
  cells <- result$cells
  schedule <- result$summary$time
  # Rounding in large within-bin sums can exceed the mathematical limit by a few ulps.
  if (!is.numeric(mass_max) || length(mass_max) != 1L || !is.finite(mass_max) ||
      mass_max <= 0 || mass_max > 1 ||
      any(cells$mass > mass_max * (1 + 8 * .Machine$double.eps), na.rm = TRUE))
    stop("mass_max must cover the observed bin masses and be in (0, 1]")
  cells$display_mass <- pmin(cells$mass, mass_max)
  width <- if (length(schedule) > 1L) min(diff(schedule)) else 1
  cells$left <- cells$time - width / 2
  cells$right <- cells$time + width / 2
  p <- ggplot2::ggplot(cells) +
    ggplot2::geom_rect(ggplot2::aes(xmin = left, xmax = right, ymin = lower, ymax = upper,
                                    fill = display_mass)) +
    ggplot2::scale_fill_gradient(low = low, high = high, limits = c(0, mass_max),
                                 na.value = "#D3CFCA", name = "Bin probability") +
    ggplot2::labs(x = "Time", y = "State") + ggplot2::theme_classic()
  missing <- result$summary[result$summary$n == 0L, , drop = FALSE]
  if (nrow(missing)) {
    missing$mid <- mean(range(c(cells$lower, cells$upper)))
    p <- p + ggplot2::geom_point(data = missing, ggplot2::aes(time, mid),
                                 shape = 4, colour = "#343334") +
      ggplot2::labs(caption = "Crossed grey column = no state samples at this time.")
  }
  p
}
