# One column per observed sample. Values are supplied on a common analysis scale.
plot_sample_atlas <- function(samples, annotation, features, group_colours, value_label,
                              id = "sample_id", group = "group", sample_order = NULL,
                              medoid_ids = character(), midpoint = NULL,
                              low = if (is.null(midpoint)) "#E9F0F1" else "#527F94",
                              high = if (is.null(midpoint)) "#527F94" else "#C289A0",
                              neutral = "#FAF7F5", na_colour = "#B9B9B9", base_size = 9,
                              group_label = group, limits = NULL) {
  if (!is.data.frame(samples) || !is.data.frame(annotation) || !nrow(samples) ||
      anyDuplicated(names(samples)) || anyDuplicated(names(annotation)) ||
      !all(c(id, features) %in% names(samples)) || !all(c(id, group) %in% names(annotation))) {
    stop("Supply a nonempty sample table and a keyed annotation table with the declared columns")
  }
  if (!is.character(features) || !length(features) || anyNA(features) ||
      anyDuplicated(features) || id %in% features || identical(id, group) ||
      !all(vapply(samples[features], is.numeric, logical(1)))) {
    stop("Choose distinct numeric feature columns and separate ID and group fields")
  }
  check_ids <- function(x, label) {
    x <- as.character(x)
    if (anyNA(x) || any(!nzchar(trimws(x))) || anyDuplicated(x)) {
      stop(label, " must contain unique, nonmissing sample IDs")
    }
    x
  }
  ids <- check_ids(samples[[id]], "Sample table")
  annotation_ids <- check_ids(annotation[[id]], "Annotation table")
  if (!setequal(ids, annotation_ids)) stop("Annotation and sample tables must contain the same IDs")
  ordered <- if (is.null(sample_order)) ids else check_ids(sample_order, "Display order")
  if (!setequal(ordered, ids)) stop("Display order must include every sample exactly once")
  medoids <- check_ids(medoid_ids, "Medoid list")
  if (!all(medoids %in% ids)) stop("Each medoid must identify an actual sample")

  labels <- as.character(annotation[[group]][match(ordered, annotation_ids)])
  if (anyNA(labels) || any(!nzchar(trimws(labels))) || anyDuplicated(names(group_colours)) ||
      !all(labels %in% names(group_colours)) || anyNA(group_colours[labels])) {
    stop("Supply an explicit annotation group and a named group colour for every sample")
  }
  medoid_groups <- names(medoid_ids)
  if (!is.null(medoid_groups) && !identical(unname(medoid_groups), unname(labels[match(medoids, ordered)]))) {
    stop("Named medoids must belong to the declared annotation groups")
  }
  row_info <- data.frame(sample_id = ordered, position = seq_along(ordered),
                         group = labels, is_medoid = ordered %in% medoids)
  values <- as.matrix(samples[match(ordered, ids), features, drop = FALSE])
  finite <- values[is.finite(values)]
  if (any(is.infinite(values)) || any(is.nan(values)) || !length(finite)) {
    stop("Check undefined numeric results or use a coverage-only map")
  }
  if (!is.null(midpoint) && (!is.numeric(midpoint) || length(midpoint) != 1L || !is.finite(midpoint))) {
    stop("The diverging scale requires a finite midpoint")
  }
  if (!is.null(limits) && (!is.numeric(limits) || length(limits) != 2L ||
      any(!is.finite(limits)) || limits[1] >= limits[2] ||
      min(c(finite, midpoint)) < limits[1] || max(c(finite, midpoint)) > limits[2])) {
    stop("Shared limits must contain the finite values and any declared midpoint")
  }

  n_features <- length(features)
  cells <- row_info[rep(seq_len(nrow(row_info)), times = n_features), , drop = FALSE]
  cells$feature <- rep(features, each = length(ids))
  cells$row_index <- rep(rev(seq_along(features)), each = length(ids))
  cells$value <- as.vector(values)
  if (is.null(midpoint)) {
    scale <- ggplot2::scale_fill_gradient(low = low, high = high, limits = limits, na.value = na_colour)
  } else {
    scale <- ggplot2::scale_fill_gradient2(low = low, mid = neutral, high = high, midpoint = midpoint,
                                           limits = limits, na.value = na_colour)
  }

  plot <- ggplot2::ggplot(cells) +
    ggplot2::geom_tile(ggplot2::aes(x = position, y = row_index, fill = value), width = 1, height = 1) +
    ggplot2::geom_segment(data = row_info, ggplot2::aes(x = position - 0.5, xend = position + 0.5,
                          colour = group), y = n_features + 1, yend = n_features + 1, linewidth = 1.6) +
    scale + ggplot2::scale_colour_manual(values = group_colours)
  if (anyNA(cells$value)) {
    plot <- plot + ggplot2::geom_point(data = cells[is.na(cells$value), , drop = FALSE],
                  ggplot2::aes(x = position, y = row_index, shape = "Missing measurement"),
                  size = 1.2, colour = "#34383D")
  }
  if (length(medoids)) {
    plot <- plot + ggplot2::geom_point(data = row_info[row_info$is_medoid, , drop = FALSE],
                  ggplot2::aes(x = position, shape = "Observed medoid"), y = n_features + 1.55,
                  size = 2, colour = "#34383D", fill = "#34383D")
  }
  ticks <- seq_along(ordered)
  if (length(ticks) > 16L) {
    ticks <- if (length(medoids)) which(row_info$is_medoid) else unique(round(seq(1, length(ids), length.out = 7)))
  }
  plot + ggplot2::scale_shape_manual(values = c("Observed medoid" = 25, "Missing measurement" = 4)) +
    ggplot2::scale_x_continuous(breaks = ticks, labels = ordered[ticks], expand = c(0.01, 0),
                                guide = ggplot2::guide_axis(check.overlap = TRUE)) +
    ggplot2::scale_y_continuous(breaks = seq_len(n_features + 1L),
                                labels = c(rev(features), group_label),
                                limits = c(0.5, n_features + if (length(medoids)) 1.8 else 1.25),
                                expand = ggplot2::expansion(add = 0.12)) +
    ggplot2::labs(x = "Sample ID (display order)", y = NULL, fill = value_label,
                  colour = group_label, shape = NULL) +
    ggplot2::theme_minimal(base_size = base_size) +
    ggplot2::theme(panel.grid = ggplot2::element_blank())
}
