generate_example_data <- function(cfg, data_dir = "data") {
  dir.create(data_dir, recursive = TRUE, showWarnings = FALSE)
  set.seed(cfg$seed)

  days <- c(0, 7, 14, 21, 28)
  groups <- cfg$group_levels
  n_per_cell <- 8L

  design <- expand.grid(
    day = days,
    group = groups,
    replicate = seq_len(n_per_cell),
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
  design$group <- factor(design$group, levels = groups)

  mean_response <- with(
    design,
    50 +
      ifelse(group == "Control", 0.06 * day,
        ifelse(group == "Treatment A", 0.34 * day, 0.52 * day)
      )
  )
  group_sd <- with(
    design,
    ifelse(group == "Control", 4.5,
      ifelse(group == "Treatment A", 5.0, 5.4)
    )
  )
  design$response <- round(stats::rnorm(nrow(design), mean_response, group_sd), 3)
  design$response_unit <- "a.u."
  design$is_simulated <- TRUE
  design$simulation_seed <- cfg$seed
  design$group <- as.character(design$group)

  trend <- design[, c(
    "day", "group", "replicate", "response", "response_unit",
    "is_simulated", "simulation_seed"
  )]
  distribution <- trend[trend$day == max(days), ]

  features <- sprintf("Marker %02d", seq_len(10))
  conditions <- c(
    "Control_D7", "TreatmentA_D7", "TreatmentB_D7",
    "Control_D28", "TreatmentA_D28", "TreatmentB_D28"
  )
  heatmap <- expand.grid(
    feature = features,
    condition = conditions,
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
  feature_index <- match(heatmap$feature, features)
  condition_index <- match(heatmap$condition, conditions)
  time_effect <- ifelse(grepl("D28$", heatmap$condition), 0.35, -0.10)
  treatment_effect <- ifelse(grepl("TreatmentA", heatmap$condition), 0.45,
    ifelse(grepl("TreatmentB", heatmap$condition), 0.85, -0.20)
  )
  signed_pattern <- sin(feature_index * 0.85) + cos(condition_index * 0.70)
  heatmap$z_score <- round(
    0.55 * signed_pattern + time_effect + treatment_effect +
      stats::rnorm(nrow(heatmap), 0, 0.22),
    3
  )
  heatmap$unit <- "z-score"
  heatmap$is_simulated <- TRUE
  heatmap$simulation_seed <- cfg$seed

  utils::write.csv(
    trend,
    file.path(data_dir, "simulated_trend.csv"),
    row.names = FALSE,
    na = ""
  )
  utils::write.csv(
    distribution,
    file.path(data_dir, "simulated_distribution.csv"),
    row.names = FALSE,
    na = ""
  )
  utils::write.csv(
    heatmap,
    file.path(data_dir, "simulated_heatmap.csv"),
    row.names = FALSE,
    na = ""
  )

  dictionary <- data.frame(
    dataset = c(
      rep("simulated_trend.csv", 7),
      rep("simulated_distribution.csv", 7),
      rep("simulated_heatmap.csv", 6)
    ),
    variable = c(
      "day", "group", "replicate", "response", "response_unit",
      "is_simulated", "simulation_seed",
      "day", "group", "replicate", "response", "response_unit",
      "is_simulated", "simulation_seed",
      "feature", "condition", "z_score", "unit", "is_simulated",
      "simulation_seed"
    ),
    type = c(
      "integer", "ordered category", "integer", "numeric", "text",
      "logical", "integer",
      "integer", "ordered category", "integer", "numeric", "text",
      "logical", "integer",
      "ordered category", "ordered category", "numeric", "text",
      "logical", "integer"
    ),
    unit = c(
      "day", "none", "none", "a.u.", "none", "none", "none",
      "day", "none", "none", "a.u.", "none", "none", "none",
      "none", "none", "z-score", "none", "none", "none"
    ),
    description = c(
      "Measurement time after the simulated intervention",
      "Experimental group; preserve the declared order",
      "Independent simulated observation identifier within each group and day",
      "Simulated response value",
      "Unit for response",
      "Explicit simulation flag",
      "Random seed used to generate the dataset",
      "Measurement time after the simulated intervention",
      "Experimental group; preserve the declared order",
      "Independent simulated observation identifier within each group and day",
      "Simulated response value at day 28",
      "Unit for response",
      "Explicit simulation flag",
      "Random seed used to generate the dataset",
      "Simulated marker identifier",
      "Group-time combination",
      "Simulated standardized marker response",
      "Unit for z_score",
      "Explicit simulation flag",
      "Random seed used to generate the dataset"
    ),
    stringsAsFactors = FALSE
  )
  utils::write.csv(
    dictionary,
    file.path(data_dir, "simulated_data_dictionary.csv"),
    row.names = FALSE,
    na = ""
  )

  invisible(list(
    trend = trend,
    distribution = distribution,
    heatmap = heatmap,
    dictionary = dictionary
  ))
}

# The normal figure entrypoint initializes an empty project only. On a revision,
# use the existing input tables, including data written by previous scaffold versions.
prepare_example_data <- function(cfg, data_dir = "data") {
  filenames <- paste0("simulated_", c("trend", "distribution", "heatmap", "data_dictionary"), ".csv")
  inputs <- file.path(data_dir, filenames)
  present <- file.exists(inputs)
  if (all(present)) return(invisible("reused"))
  formats <- c("pdf", "svg", "png", "tiff")
  prior_run <- c(file.path(cfg$output_dirs$qa, c("export_manifest.csv", "data_validation.txt")),
                 file.path(unlist(cfg$output_dirs[formats]), paste0("academic_figure_example.", formats)),
                 file.path(cfg$output_dirs$previews, "academic_figure_example_preview.png"))
  if (any(present) || any(file.exists(prior_run))) {
    stop("Incomplete example input set. Restore the missing files for this revision: ",
         paste(filenames[!present], collapse = ", "), ". Start a new scaffold for a separate simulation.")
  }

  dir.create(data_dir, recursive = TRUE, showWarnings = FALSE)
  # A fixed staging directory prevents two new runs from mixing different seeds.
  staging <- file.path(data_dir, ".initializing-simulated-inputs")
  if (!dir.create(staging, showWarnings = FALSE)) {
    stop("Cannot initialize example inputs in ", staging,
         ". Check write access and whether another run is already initializing this project.")
  }
  on.exit(unlink(staging, recursive = TRUE), add = TRUE)
  # A concurrent first run can finish between the existence check and mkdir.
  if (all(file.exists(inputs))) return(invisible("reused"))
  if (any(file.exists(inputs))) stop("Example inputs changed during initialization. Retry with the saved set.")
  generate_example_data(cfg, staging)
  published <- character()
  for (i in seq_along(inputs)) {
    if (file.exists(inputs[i]) || !file.rename(file.path(staging, filenames[i]), inputs[i])) {
      unlink(published)
      stop("Could not install the new example input set at ", inputs[i])
    }
    published <- c(published, inputs[i])
  }
  invisible("created")
}
