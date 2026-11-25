# Source this file in the R session that will run the figure.
# Set install = TRUE to repair the selected project or user library and recheck it.
check_figure_environment <- function(packages = NULL, install = FALSE,
                                     project = getwd(), repos = getOption("repos")) {
  project <- normalizePath(project, winslash = "/", mustWork = TRUE)
  active <- Sys.getenv("RENV_PROJECT")
  if (nzchar(active) && !identical(normalizePath(active, winslash = "/"), project))
    stop("This R session has a different renv project open. Open the requested project first.")
  locked <- nzchar(active)
  if (locked) {
    if (!requireNamespace("renv", quietly = TRUE))
      stop("The active project requires renv. Reopen it with its project profile enabled.")
    expected <- normalizePath(renv::paths$library(project = project), winslash = "/", mustWork = FALSE)
    if (!identical(normalizePath(.libPaths()[1], winslash = "/"), expected))
      stop("The active R library and renv project disagree. Reopen the target project's R session.")
  }
  lockfile <- file.path(project, "renv.lock")
  profile <- file.path(project, ".Rprofile")
  if (!locked && file.exists(profile)) {
    startup <- readLines(profile, warn = FALSE, encoding = "UTF-8")
    if (any(grepl("renv/activate[.]R", startup[!grepl("^\\s*#", startup)])))
      stop("Open this project with its renv profile enabled, then run this check again.")
  }
  if (is.null(packages)) {
    description <- file.path(project, "DESCRIPTION")
    if (!file.exists(description))
      stop("Supply packages = c(...) from the selected plotting script, or open its DESCRIPTION directory.")
    deps <- read.dcf(description, fields = c("Imports", "Depends"))[1, ]
    packages <- trimws(unlist(strsplit(deps[!is.na(deps)], ",", fixed = TRUE)))
  }
  # Respect version bounds in DESCRIPTION and exact project versions in renv.lock.
  syntax <- "^([A-Za-z][A-Za-z0-9.]*)\\s*(?:\\((>=|<=|==|>|<)\\s*([0-9][A-Za-z0-9.-]*)\\))?$"
  matches <- regmatches(packages, regexec(syntax, packages, perl = TRUE))
  if (any(lengths(matches) == 0L)) stop("Invalid dependency specification in packages or DESCRIPTION.")
  names_only <- vapply(matches, `[[`, character(1), 2L)
  lock <- if (locked && file.exists(lockfile)) renv::lockfile_read(lockfile) else NULL

  inspect <- function() {
    reasons <- vapply(matches, function(m) {
      name <- m[2]
      if (name == "R") {
        version <- as.character(getRversion())
      } else {
        if (!requireNamespace(name, quietly = TRUE)) return("missing or failed to load")
        version <- as.character(getNamespaceVersion(name))
      }
      if (length(m) >= 4L && nzchar(m[3])) {
        ok <- do.call(m[3], list(utils::compareVersion(version, m[4]), 0L))
        if (!ok) return(paste("requires", m[3], m[4], "loaded", version))
      }
      pinned <- lock$Packages[[name]]$Version
      if (!is.null(pinned) && utils::compareVersion(version, pinned) != 0L)
        return(paste("locked", pinned, "loaded", version))
      ""
    }, character(1), USE.NAMES = FALSE)
    stats::setNames(reasons[nzchar(reasons)], names_only[nzchar(reasons)])
  }

  issues <- inspect()
  if (install && length(issues)) {
    if ("R" %in% names(issues))
      stop("Check the required R version first: ", issues[["R"]])
    targets <- unique(names(issues))
    if (locked && !is.null(lock)) {
      absent <- setdiff(targets, names(lock$Packages))
      if (length(absent)) stop("Resolve dependencies missing from the project lockfile: ",
                               paste(absent, collapse = ", "))
      renv::restore(project = project, packages = targets, prompt = FALSE, clean = FALSE)
    } else {
      if (locked) {
        library <- .libPaths()[1]
      } else {
        user_lib <- strsplit(Sys.getenv("R_LIBS_USER"), .Platform$path.sep, fixed = TRUE)[[1]]
        if (!length(user_lib) || !nzchar(user_lib[1]))
          stop("Set R_LIBS_USER to a writable user library, restart R and repeat the check.")
        library <- path.expand(user_lib[1])
        if (!dir.exists(library)) dir.create(library, recursive = TRUE)
        .libPaths(c(library, .libPaths()))
      }
      if (file.access(library, 2L) != 0L) stop("R library is not writable: ", library)
      if (is.null(repos) || !length(repos)) repos <- c(CRAN = "https://cloud.r-project.org")
      repos[repos == "@CRAN@"] <- "https://cloud.r-project.org"
      utils::install.packages(targets, lib = library, repos = repos)
    }
    issues <- inspect()
  }
  result <- list(ready = !length(issues), r = as.character(getRversion()), project = project,
                 libraries = .libPaths(), active_renv = locked, package_issues = issues)
  if (length(issues)) {
    message(paste(names(issues), issues, sep = " — ", collapse = "\n"))
    if (install) stop("Setup still incomplete. Inspect installation diagnostics and recheck in a fresh project session.")
    message("Run check_figure_environment(install = TRUE) with the same project and package arguments to repair.")
  } else {
    message("R dependencies load in this session. Continue the figure task in ", project)
  }
  return(invisible(result))
}
