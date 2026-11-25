validate_example_data <- function(cfg, data_dir = "data", qa_dir = cfg$output_dirs$qa) {
  dir.create(qa_dir, recursive = TRUE, showWarnings = FALSE)

  trend <- utils::read.csv(file.path(data_dir, "simulated_trend.csv"), check.names = FALSE)
  distribution <- utils::read.csv(
    file.path(data_dir, "simulated_distribution.csv"),
    check.names = FALSE
  )
  heatmap <- utils::read.csv(file.path(data_dir, "simulated_heatmap.csv"), check.names = FALSE)

  required_trend <- c(
    "day", "group", "replicate", "response", "response_unit",
    "is_simulated", "simulation_seed"
  )
  required_heatmap <- c(
    "feature", "condition", "z_score", "unit", "is_simulated",
    "simulation_seed"
  )

  checks <- list(
    trend_columns = identical(names(trend), required_trend),
    distribution_columns = identical(names(distribution), required_trend),
    heatmap_columns = identical(names(heatmap), required_heatmap),
    trend_no_missing = !anyNA(trend),
    distribution_no_missing = !anyNA(distribution),
    heatmap_no_missing = !anyNA(heatmap),
    trend_finite = all(is.finite(trend$response)),
    heatmap_finite = all(is.finite(heatmap$z_score)),
    response_units = all(trend$response_unit == "a.u.") && all(distribution$response_unit == "a.u."),
    heatmap_units = all(heatmap$unit == "z-score"),
    group_set = setequal(trend$group, cfg$group_levels),
    trend_unique_keys = !anyDuplicated(trend[c("day", "group", "replicate")]),
    distribution_unique_keys = !anyDuplicated(distribution[c("group", "replicate")]),
    heatmap_unique_keys = !anyDuplicated(heatmap[c("feature", "condition")]),
    distribution_day_28 = all(distribution$day == 28),
    simulation_flag = all(trend$is_simulated) &&
      all(distribution$is_simulated) && all(heatmap$is_simulated),
    seed_matches = all(trend$simulation_seed == cfg$seed) &&
      all(distribution$simulation_seed == cfg$seed) &&
      all(heatmap$simulation_seed == cfg$seed),
    heatmap_within_declared_scale = all(
      heatmap$z_score >= cfg$heatmap_limits[1] &
        heatmap$z_score <= cfg$heatmap_limits[2]
    )
  )

  # Both panels describe the same day-28 records. Join by the sample keys,
  # retaining the values, units, simulation flag and seed in the comparison.
  endpoint_rows <- function(data) {
    result <- data[order(data$group, data$replicate), required_trend, drop = FALSE]
    rownames(result) <- NULL
    result
  }
  checks$endpoint_matches_trend <- isTRUE(all.equal(
    endpoint_rows(trend[trend$day == 28, , drop = FALSE]),
    endpoint_rows(distribution), tolerance = 0
  ))
  cell_counts <- stats::aggregate(
    replicate ~ group + day,
    trend,
    length
  )
  demo_days <- c(0, 7, 14, 21, 28)
  checks$balanced_trend_cells <- setequal(trend$day, demo_days) &&
    nrow(cell_counts) == length(demo_days) * length(cfg$group_levels) && all(cell_counts$replicate == 8L)
  conditions <- c("Control_D7", "TreatmentA_D7", "TreatmentB_D7",
                  "Control_D28", "TreatmentA_D28", "TreatmentB_D28")
  checks$complete_heatmap_grid <- nrow(heatmap) == 60L &&
    setequal(heatmap$feature, sprintf("Marker %02d", 1:10)) && setequal(heatmap$condition, conditions)

  failed <- names(checks)[!unlist(checks)]
  report_lines <- c(
    "Academic figure example data validation",
    sprintf("Run date: %s", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
    sprintf("Simulation seed: %d", cfg$seed),
    "",
    sprintf("%-40s %s", names(checks), ifelse(unlist(checks), "PASS", "FAIL")),
    "",
    sprintf("Trend rows: %d", nrow(trend)),
    sprintf("Distribution rows: %d", nrow(distribution)),
    sprintf("Heatmap rows: %d", nrow(heatmap)),
    sprintf("Heatmap observed range: %.3f to %.3f", min(heatmap$z_score), max(heatmap$z_score))
  )
  writeLines(report_lines, file.path(qa_dir, "data_validation.txt"), useBytes = TRUE)

  if (length(failed)) {
    stop("Data validation failed: ", paste(failed, collapse = ", "))
  }

  invisible(list(
    checks = checks,
    trend = trend,
    distribution = distribution,
    heatmap = heatmap
  ))
}
