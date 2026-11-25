required_packages <- c(
  "ggplot2", "patchwork", "ggdist", "ggrepel", "colorspace",
  "ragg", "svglite", "readxl", "scales", "farver", "systemfonts",
  "viridisLite", "jsonlite"
)
missing_packages <- required_packages[
  !vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)
]
if (length(missing_packages)) {
  stop(
    "Missing packages: ", paste(missing_packages, collapse = ", "),
    ". From this project, run source(\"scripts/check_r_project.R\") and ",
    "check_figure_environment(install = TRUE). After it reports ready, rerun source(\"R/run_example.R\")."
  )
}

source("R/figure_config.R")
source("R/figure_style.R")
source("R/generate_example_data.R")
source("R/validate_example.R")
source("R/render_example_figure.R")
source("R/qa_palette.R")
source("R/palette_system.R")

cfg <- figure_config()

font_match <- systemfonts::match_fonts(cfg$font_family)
if (!nrow(font_match) || !nzchar(font_match$path[1])) {
  stop("Configured font is unavailable: ", cfg$font_family)
}
installed_fonts <- systemfonts::system_fonts()
font_rows <- installed_fonts[installed_fonts$path == font_match$path[1] &
                               installed_fonts$index == font_match$index[1], , drop = FALSE]
if (!nrow(font_rows) || !any(tolower(font_rows$family) == tolower(cfg$font_family))) {
  warning("Requested font '", cfg$font_family, "' resolved to a different or unidentified family: ",
          font_match$path[1], ". Check the final exported glyphs and font embedding.")
}

input_status <- prepare_example_data(cfg)
message(if (input_status == "created") "Generated the example inputs." else "Reusing the saved example inputs.")
validated <- validate_example_data(cfg)
built <- build_example_figure(cfg, inputs = validated)
export_example_figure(built, cfg)
palette_qa <- run_palette_qa(cfg)
palette_system_qa <- audit_palette_system("output/qa", cfg$font_family)

cat(
  "Draft exports written; scientific, visual and export acceptance remains pending.\n",
  sprintf("Canvas: %g x %g mm\n", cfg$width_mm, cfg$height_mm),
  sprintf("Font: %s (%s)\n", cfg$font_family, font_match$path[1]),
  sprintf("Rows: trend=%d, distribution=%d, heatmap=%d\n",
    nrow(validated$trend), nrow(validated$distribution), nrow(validated$heatmap)
  ),
  sprintf(
    "Palette minimum Delta E (original/deutan/protan/tritan/grayscale): %s\n",
    paste(formatC(
      palette_qa$minimum_pairwise_delta_e_2000,
      format = "f",
      digits = 1
    ), collapse = "/")
  ),
  sprintf("Cividis lightness path broadly monotonic: %s\n",
    palette_system_qa$sequential_monotonic),
  sep = ""
)
