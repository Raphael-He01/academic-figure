# From the academic-figure directory, source this file in RStudio and call
# render_model_examples("my-previews"). Both inputs are deterministic simulations.
render_model_examples <- function(out_dir, components = "assets/r-template/R") {
  if (file.exists(out_dir)) stop("Choose a new output directory")
  source(file.path(components, "plot_state_mass.R"), local = TRUE)
  source(file.path(components, "plot_sample_atlas.R"), local = TRUE)
  if (!all(vapply(c("ggplot2", "ragg", "svglite"), requireNamespace,
                  logical(1), quietly = TRUE))) stop("Requires ggplot2, ragg and svglite")

  title_style <- ggplot2::theme(
    plot.title.position = "plot", plot.caption.position = "plot",
    plot.title = ggplot2::element_text(size = 16, face = "bold", colour = "#233542"),
    plot.subtitle = ggplot2::element_text(size = 9.5, colour = "#4B5D64",
                                          margin = ggplot2::margin(b = 12)),
    plot.caption = ggplot2::element_text(size = 8, hjust = 0, colour = "#45545C",
                                         margin = ggplot2::margin(t = 10)),
    plot.margin = ggplot2::margin(11, 14, 10, 12),
    legend.position = "bottom", legend.box = "vertical")
  times <- 0:40
  # Two branches follow equal normal-quantile grids with known weights.
  # Omitting step 24 creates a genuinely unavailable distribution.
  z <- qnorm((seq_len(100) - 0.5) / 100)
  particles <- do.call(rbind, lapply(setdiff(times, 24L), function(t) {
    separation <- 0.12 + 1.5 * plogis((t - 13) / 3)
    share <- 0.2 + 0.55 * t / 40
    data.frame(time = t, particle = seq_len(200),
               state = c(-separation + .33 * z, separation + .37 * z),
               weight = rep(c(1 - share, share) / 100, each = 100))
  }))
  mass <- state_mass_table(particles, times, seq(-3, 3, by = .2))
  observed <- mass$summary$n > 0
  stopifnot(all(mass$summary$n[observed] == 200L),
            all(mass$summary$below_range[observed] + mass$summary$above_range[observed] == 0),
            all(abs(tapply(mass$cells$mass, mass$cells$time, sum)[observed] - 1) < 1e-12))
  field <- plot_state_mass(mass, high = "#426D80", mass_max = .25) +
    ggplot2::labs(title = "One state distribution splits into two branches",
                  subtitle = "Simulated state samples  |  200 weighted particles per available step",
                  x = "Time step", y = "State value",
                  caption = "Each cell gives probability in a 0.2-unit state bin.\nThe crossed column marks step 24, where no distribution was supplied.") +
    title_style + ggplot2::guides(fill = ggplot2::guide_colourbar(title.position = "top",
                  barwidth = grid::unit(45, "mm"), barheight = grid::unit(3, "mm")))

  # Deviations from a 20 degree C reference at four times of day.
  ids <- sprintf("S%02d", 1:16)
  zones <- rep(c("Sheltered", "Open"), each = 8)
  phases <- c("Dawn", "Midday", "Afternoon", "Dusk")
  values <- matrix(NA_real_, length(ids), length(phases),
                   dimnames = list(ids, phases))
  offsets <- c(-1.2, -.85, -.5, -.1, .25, .55, .9, 1.25)
  for (i in seq_along(ids)) {
    profile <- if (zones[i] == "Open") c(-2.4, 1.9, 3.4, -.4) else c(-.6, .6, 1.2, .1)
    values[i, ] <- round(profile + offsets[(i - 1) %% 8 + 1] * c(.45, .9, .8, .5), 2)
  }
  values["S02", "Midday"] <- NA_real_
  values["S15", "Dusk"] <- NA_real_
  values["S04", "Dusk"] <- 0
  samples <- data.frame(sample_id = ids, values, check.names = FALSE)
  annotation <- data.frame(sample_id = rev(ids), group = rev(zones))
  # Representative among fully observed profiles in each group, by total L1 distance.
  medoids <- vapply(unique(zones), function(g) {
    x <- values[zones == g & complete.cases(values), , drop = FALSE]
    rownames(x)[which.min(rowSums(as.matrix(dist(x, method = "manhattan"))))]
  }, character(1))
  atlas <- plot_sample_atlas(samples, annotation, phases,
                             group_colours = c(Sheltered = "#C289A0", Open = "#527F94"),
                             value_label = "Temperature offset (°C)", medoid_ids = medoids,
                             midpoint = 0, limits = c(-5, 5), group_label = "Exposure") +
    ggplot2::guides(colour = ggplot2::guide_legend(order = 1),
                    shape = ggplot2::guide_legend(order = 2),
                    fill = ggplot2::guide_colourbar(order = 3)) +
    ggplot2::labs(title = "Open sites have a stronger afternoon peak",
                  subtitle = "Simulated temperature offsets from 20 °C  |  16 sites at four times of day",
                  caption = "Triangles identify the most central complete profile within each exposure group\nby total absolute distance. Crosses mark missing measurements.") +
    title_style

  if (!dir.create(out_dir, recursive = TRUE)) stop("Could not create output directory")
  save_plot <- function(p, stem, height) {
    for (format in c("svg", "png")) {
      device <- if (format == "svg") svglite::svglite else ragg::agg_png
      ggplot2::ggsave(file.path(out_dir, paste0(stem, ".", format)), plot = p,
                      device = device, width = 190, height = height, units = "mm",
                      dpi = 220, bg = "white")
    }
  }
  save_plot(field, "state-mass", 118)
  save_plot(atlas, "sample-atlas", 129)
  write.csv(mass$summary, file.path(out_dir, "mass-summary.csv"), row.names = FALSE, na = "")
  write.csv(atlas$data, file.path(out_dir, "atlas-cells.csv"), row.names = FALSE, na = "")
  invisible(list(state = field, atlas = atlas))
}
