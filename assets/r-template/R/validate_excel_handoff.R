project_root <- normalizePath(".", winslash = "/", mustWork = TRUE)
workbook_path <- file.path(
  project_root,
  "output", "spreadsheet", "simulated_academic_figure_data.xlsx"
)
qa_dir <- file.path(project_root, "output", "qa")
report_path <- file.path(qa_dir, "excel_roundtrip.txt")
dir.create(qa_dir, recursive = TRUE, showWarnings = FALSE)

if (!requireNamespace("readxl", quietly = TRUE)) {
  stop("Missing package 'readxl'. Run renv::restore() from the project root.")
}

if (!file.exists(workbook_path)) {
  stop("Workbook not found: ", workbook_path)
}

readxl_path <- find.package("readxl")
readxl_resolved_path <- normalizePath(
  readxl_path,
  winslash = "/",
  mustWork = TRUE
)
renv_library_root <- normalizePath(
  file.path(project_root, "renv", "library"),
  winslash = "/",
  mustWork = TRUE
)
active_library <- normalizePath(
  .libPaths()[1],
  winslash = "/",
  mustWork = TRUE
)
project_readxl_path <- file.path(active_library, "readxl")

expected_sheets <- c(
  "Metadata", "Levels", "Trend", "Distribution", "Heatmap", "Dictionary"
)
expected_rows <- c(
  Metadata = 10L,
  Levels = 9L,
  Trend = 120L,
  Distribution = 24L,
  Heatmap = 60L,
  Dictionary = 20L
)
expected_columns <- list(
  Metadata = c("Field", "Value"),
  Levels = c(
    "variable", "level", "order", "display_label", "color_hex",
    "R_shape", "R_linetype"
  ),
  Trend = c(
    "day", "group", "replicate", "response", "response_unit",
    "is_simulated", "simulation_seed"
  ),
  Distribution = c(
    "day", "group", "replicate", "response", "response_unit",
    "is_simulated", "simulation_seed"
  ),
  Heatmap = c(
    "feature", "condition", "z_score", "unit", "is_simulated",
    "simulation_seed"
  ),
  Dictionary = c("dataset", "variable", "type", "unit", "description")
)

group_levels <- c("Control", "Treatment A", "Treatment B")
condition_levels <- c(
  "Control_D7", "TreatmentA_D7", "TreatmentB_D7",
  "Control_D28", "TreatmentA_D28", "TreatmentB_D28"
)
feature_levels <- sprintf("Marker %02d", seq_len(10L))
simulation_seed <- 20261009
numeric_tolerance <- 1e-12

checks <- list()
details <- list()

add_check <- function(name, result, detail = "") {
  checks[[name]] <<- isTRUE(result)
  details[[name]] <<- as.character(detail)
  invisible(result)
}

is_integerish <- function(x, allow_na = FALSE, tolerance = 1e-9) {
  if (!is.numeric(x)) {
    return(FALSE)
  }
  if (!allow_na && anyNA(x)) {
    return(FALSE)
  }
  values <- x[!is.na(x)]
  all(is.finite(values)) && all(abs(values - round(values)) <= tolerance)
}

has_at_most_three_decimals <- function(x, tolerance = 1e-9) {
  is.numeric(x) && !anyNA(x) && all(is.finite(x)) &&
    all(abs(x * 1000 - round(x * 1000)) <= tolerance)
}

compare_data_frames <- function(actual, expected, tolerance = numeric_tolerance) {
  actual <- as.data.frame(actual, stringsAsFactors = FALSE, check.names = FALSE)
  expected <- as.data.frame(expected, stringsAsFactors = FALSE, check.names = FALSE)

  if (!identical(names(actual), names(expected))) {
    return(list(ok = FALSE, detail = "column names or order differ"))
  }
  if (nrow(actual) != nrow(expected)) {
    return(list(
      ok = FALSE,
      detail = sprintf("row count differs: workbook=%d csv=%d", nrow(actual), nrow(expected))
    ))
  }

  failures <- character()
  max_numeric_difference <- 0
  for (column_name in names(expected)) {
    actual_column <- actual[[column_name]]
    expected_column <- expected[[column_name]]

    if (is.numeric(expected_column) || is.integer(expected_column)) {
      if (!is.numeric(actual_column)) {
        failures <- c(failures, sprintf("%s is not numeric", column_name))
        next
      }
      same_missing <- identical(is.na(actual_column), is.na(expected_column))
      difference <- abs(as.numeric(actual_column) - as.numeric(expected_column))
      finite_difference <- difference[is.finite(difference)]
      column_max <- if (length(finite_difference)) max(finite_difference) else 0
      max_numeric_difference <- max(max_numeric_difference, column_max)
      if (!same_missing || any(difference > tolerance, na.rm = TRUE)) {
        failures <- c(
          failures,
          sprintf("%s differs (max abs diff %.3g)", column_name, column_max)
        )
      }
    } else if (is.logical(expected_column)) {
      if (!is.logical(actual_column) || !identical(actual_column, expected_column)) {
        failures <- c(failures, sprintf("%s logical values differ", column_name))
      }
    } else {
      if (!identical(as.character(actual_column), as.character(expected_column))) {
        failures <- c(failures, sprintf("%s text values differ", column_name))
      }
    }
  }

  list(
    ok = !length(failures),
    detail = if (length(failures)) {
      paste(failures, collapse = "; ")
    } else {
      sprintf("exact row order; max numeric abs diff %.3g", max_numeric_difference)
    }
  )
}

sheet_names <- readxl::excel_sheets(workbook_path)
add_check(
  "six_sheets_in_expected_order",
  identical(sheet_names, expected_sheets),
  paste(sheet_names, collapse = ", ")
)

workbook <- stats::setNames(
  lapply(expected_sheets, function(sheet_name) {
    as.data.frame(
      readxl::read_excel(workbook_path, sheet = sheet_name),
      stringsAsFactors = FALSE,
      check.names = FALSE
    )
  }),
  expected_sheets
)

add_check(
  "readxl_loaded_from_project_renv",
  startsWith(active_library, paste0(renv_library_root, "/")) &&
    file.exists(project_readxl_path) &&
    identical(
      normalizePath(project_readxl_path, winslash = "/", mustWork = TRUE),
      readxl_resolved_path
    ),
  sprintf("project link=%s; resolved cache=%s", project_readxl_path, readxl_resolved_path)
)

for (sheet_name in expected_sheets) {
  data <- workbook[[sheet_name]]
  add_check(
    paste0("rows_", tolower(sheet_name)),
    nrow(data) == expected_rows[[sheet_name]],
    sprintf("observed=%d expected=%d", nrow(data), expected_rows[[sheet_name]])
  )
  add_check(
    paste0("columns_", tolower(sheet_name)),
    identical(names(data), expected_columns[[sheet_name]]),
    paste(names(data), collapse = ", ")
  )
}

metadata <- stats::setNames(workbook$Metadata$Value, workbook$Metadata$Field)
add_check(
  "metadata_simulated_status",
  identical(
    unname(metadata[["Status"]]),
    "SIMULATED DATA - not a real scientific result"
  ),
  unname(metadata[["Status"]])
)
add_check(
  "metadata_seed",
  identical(as.numeric(metadata[["Random seed"]]), simulation_seed),
  unname(metadata[["Random seed"]])
)
add_check(
  "metadata_group_order",
  identical(
    unname(metadata[["Group order"]]),
    paste(group_levels, collapse = " | ")
  ),
  unname(metadata[["Group order"]])
)
add_check(
  "metadata_precision_statement",
  grepl("three decimals", metadata[["Precision"]], fixed = TRUE),
  unname(metadata[["Precision"]])
)

group_rows <- workbook$Levels$variable == "group"
condition_rows <- workbook$Levels$variable == "condition"
add_check(
  "levels_group_order",
  identical(workbook$Levels$level[group_rows], group_levels) &&
    identical(as.integer(workbook$Levels$order[group_rows]), seq_along(group_levels)),
  paste(workbook$Levels$level[group_rows], collapse = " | ")
)
add_check(
  "levels_condition_order",
  identical(workbook$Levels$level[condition_rows], condition_levels) &&
    identical(
      as.integer(workbook$Levels$order[condition_rows]),
      seq_along(condition_levels)
    ),
  paste(workbook$Levels$level[condition_rows], collapse = " | ")
)
add_check(
  "data_group_order",
  identical(unique(workbook$Trend$group), group_levels) &&
    identical(unique(workbook$Distribution$group), group_levels),
  paste(unique(workbook$Trend$group), collapse = " | ")
)
add_check(
  "data_heatmap_level_order",
  identical(unique(workbook$Heatmap$feature), feature_levels) &&
    identical(unique(workbook$Heatmap$condition), condition_levels),
  sprintf(
    "features=%s; conditions=%s",
    paste(unique(workbook$Heatmap$feature), collapse = " | "),
    paste(unique(workbook$Heatmap$condition), collapse = " | ")
  )
)

scientific_sheets <- c("Trend", "Distribution", "Heatmap")
add_check(
  "simulation_flags_logical_true",
  all(vapply(scientific_sheets, function(sheet_name) {
    flag <- workbook[[sheet_name]]$is_simulated
    is.logical(flag) && !anyNA(flag) && all(flag)
  }, logical(1))),
  "Trend, Distribution, and Heatmap are logical TRUE"
)
add_check(
  "simulation_seeds_numeric_and_match",
  all(vapply(scientific_sheets, function(sheet_name) {
    seed <- workbook[[sheet_name]]$simulation_seed
    is_integerish(seed) && all(seed == simulation_seed)
  }, logical(1))),
  as.character(simulation_seed)
)

add_check(
  "trend_numeric_types",
  all(vapply(
    workbook$Trend[c("day", "replicate", "response", "simulation_seed")],
    is.numeric,
    logical(1)
  )),
  paste(
    vapply(
      workbook$Trend[c("day", "replicate", "response", "simulation_seed")],
      function(x) class(x)[1],
      character(1)
    ),
    collapse = ", "
  )
)
add_check(
  "distribution_numeric_types",
  all(vapply(
    workbook$Distribution[c("day", "replicate", "response", "simulation_seed")],
    is.numeric,
    logical(1)
  )),
  paste(
    vapply(
      workbook$Distribution[c("day", "replicate", "response", "simulation_seed")],
      function(x) class(x)[1],
      character(1)
    ),
    collapse = ", "
  )
)
add_check(
  "heatmap_numeric_types",
  all(vapply(
    workbook$Heatmap[c("z_score", "simulation_seed")],
    is.numeric,
    logical(1)
  )),
  paste(
    vapply(
      workbook$Heatmap[c("z_score", "simulation_seed")],
      function(x) class(x)[1],
      character(1)
    ),
    collapse = ", "
  )
)
add_check(
  "integer_semantics",
  is_integerish(workbook$Levels$order) &&
    is_integerish(workbook$Levels$R_shape, allow_na = TRUE) &&
    is_integerish(workbook$Trend$day) &&
    is_integerish(workbook$Trend$replicate) &&
    is_integerish(workbook$Trend$simulation_seed) &&
    is_integerish(workbook$Distribution$day) &&
    is_integerish(workbook$Distribution$replicate) &&
    is_integerish(workbook$Distribution$simulation_seed) &&
    is_integerish(workbook$Heatmap$simulation_seed),
  "order, shape, day, replicate, and seed columns contain whole numeric values"
)
add_check(
  "three_decimal_precision",
  has_at_most_three_decimals(workbook$Trend$response) &&
    has_at_most_three_decimals(workbook$Distribution$response) &&
    has_at_most_three_decimals(workbook$Heatmap$z_score),
  "response and z_score values are representable at three decimal places"
)
add_check(
  "scientific_data_no_missing_values",
  !anyNA(workbook$Trend) &&
    !anyNA(workbook$Distribution) &&
    !anyNA(workbook$Heatmap),
  "Trend, Distribution, and Heatmap"
)

csv_map <- c(
  Trend = "simulated_trend.csv",
  Distribution = "simulated_distribution.csv",
  Heatmap = "simulated_heatmap.csv",
  Dictionary = "simulated_data_dictionary.csv"
)
roundtrip_summaries <- character()
for (sheet_name in names(csv_map)) {
  csv_path <- file.path(project_root, "data", csv_map[[sheet_name]])
  csv_data <- utils::read.csv(
    csv_path,
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
  comparison <- compare_data_frames(workbook[[sheet_name]], csv_data)
  check_name <- paste0("csv_roundtrip_", tolower(sheet_name))
  add_check(check_name, comparison$ok, comparison$detail)
  roundtrip_summaries <- c(
    roundtrip_summaries,
    sprintf("%s: %s", sheet_name, comparison$detail)
  )
}

check_status <- ifelse(unlist(checks, use.names = FALSE), "PASS", "FAIL")
check_names <- names(checks)
failed <- check_names[check_status == "FAIL"]
detail_width <- max(nchar(check_names))
check_lines <- sprintf(
  paste0("%-", detail_width, "s  %s  %s"),
  check_names,
  check_status,
  unlist(details[check_names], use.names = FALSE)
)

report_lines <- c(
  "Excel handoff round-trip validation",
  sprintf("Run date: %s", format(Sys.time(), "%Y-%m-%d %H:%M:%S %Z")),
  sprintf("Workbook: %s", workbook_path),
  sprintf("R: %s", R.version.string),
  sprintf("readxl: %s", as.character(utils::packageVersion("readxl"))),
  sprintf("readxl project package link: %s", project_readxl_path),
  sprintf("readxl resolved cache path: %s", readxl_resolved_path),
  "",
  check_lines,
  "",
  "Observed data rows:",
  sprintf(
    "  %s: %d",
    expected_sheets,
    vapply(workbook[expected_sheets], nrow, integer(1))
  ),
  "",
  "CSV round-trip details:",
  paste0("  ", roundtrip_summaries),
  "",
  sprintf(
    "Overall result: %s (%d/%d checks passed)",
    if (length(failed)) "FAIL" else "PASS",
    sum(check_status == "PASS"),
    length(check_status)
  )
)

if (length(failed)) {
  report_lines <- c(
    report_lines,
    sprintf("Failed checks: %s", paste(failed, collapse = ", "))
  )
}

writeLines(report_lines, report_path, useBytes = TRUE)
cat(paste(report_lines, collapse = "\n"), "\n", sep = "")

if (length(failed)) {
  stop(
    "Excel handoff validation failed: ",
    paste(failed, collapse = ", "),
    call. = FALSE
  )
}

invisible(list(checks = checks, workbook = workbook, report_path = report_path))
