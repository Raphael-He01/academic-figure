# Copy into a project, configure source/units/range above, and run saved code in RStudio.
stopifnot(Sys.getenv('RSTUDIO') == '1')
for (pkg in c('ggplot2', 'mapproj', 'maps', 'jsonlite', 'ragg', 'svglite')) {
  if (!requireNamespace(pkg, quietly = TRUE)) stop('Missing R package: ', pkg)
}
library(ggplot2)
cfg <- list(width_mm = 183, height_mm = 112, dpi = 300, font = 'Helvetica',
            value_min = 0, value_max = 1, legend_title = 'Value ([unit])',
            title = 'Global point locations', subtitle = '[source and period]',
            footer = 'Mollweide projection  |  [base map source]',
            land = '#E0E7E7', shore = '#BAC8CA', ocean = '#F6FAFA', graticule = '#D9E4E5')
labels <- unlist(cfg[c('legend_title', 'subtitle', 'footer')])
if (length(labels) != 3L || anyNA(labels) || any(!nzchar(trimws(labels))) ||
    any(grepl('\\[(unit|source and period|base map source)\\]', labels))) {
  warning('Incomplete map labels. The figure will be marked DRAFT.')
  cfg$title <- paste('DRAFT  | ', cfg$title)
}
dir.create('output', showWarnings = FALSE)

# Pre-existing public-domain Natural Earth 1:110m land, no internet required to run.
earth <- jsonlite::fromJSON('data/ne_110m_land.geojson', simplifyVector = FALSE)
stopifnot(identical(earth$type, 'FeatureCollection'), length(earth$features) > 0)
project <- function(lon, lat) {
  q <- mapproj::mapproject(lon, lat, projection = 'mollweide', orientation = c(90, 0, 0))
  data.frame(x = q$x, y = q$y)
}
land <- do.call(rbind, lapply(seq_along(earth$features), function(i) {
  g <- earth$features[[i]]$geometry
  if (!identical(g$type, 'Polygon')) stop('Unsupported geometry: ', g$type)
  do.call(rbind, lapply(seq_along(g$coordinates), function(j) {
    ll <- do.call(rbind, lapply(g$coordinates[[j]], function(v) as.numeric(unlist(v))))
    xy <- project(ll[, 1], ll[, 2])
    data.frame(xy, polygon = i, ring = j)
  }))
}))
stopifnot(all(is.finite(land$x)), all(is.finite(land$y)))

# Supply a CSV with unique id, longitude, latitude and value; no values are invented.
sites <- read.csv('data/sites.csv', stringsAsFactors = FALSE)
required <- c('id', 'longitude', 'latitude', 'value')
if (!all(required %in% names(sites))) stop('sites.csv must contain: ', paste(required, collapse = ', '))
if (anyNA(sites[required]) || anyDuplicated(sites$id) || any(!nzchar(as.character(sites$id)))) stop('Missing or duplicate site data')
if (!all(is.finite(sites$longitude) & sites$longitude >= -180 & sites$longitude <= 180 & is.finite(sites$latitude) & sites$latitude >= -90 & sites$latitude <= 90 & is.finite(sites$value))) stop('Invalid coordinates or values')
if (any(sites$value < cfg$value_min | sites$value > cfg$value_max)) stop('Values outside the configured colour limits; adjust them explicitly')
sites <- cbind(sites, project(sites$longitude, sites$latitude))
stopifnot(all(is.finite(sites$x)), all(is.finite(sites$y)))

lat_lines <- do.call(rbind, lapply(c(-60, -30, 0, 30, 60), function(lat) {
  cbind(project(seq(-180, 180, 2), rep(lat, 181)), line = paste0('lat',lat))
}))
lon_lines <- do.call(rbind, lapply(seq(-120, 120, 60), function(lon) {
  cbind(project(rep(lon, 179), seq(-89, 89)), line = paste0('lon',lon))
}))
outline <- rbind(project(rep(-180, 181), seq(-90, 90)), project(rep(180, 181), seq(90, -90)))
figure <- ggplot() +
  geom_polygon(data = outline, aes(x, y), fill = cfg$ocean, colour = '#BAC8CA', linewidth = .28) +
  geom_path(data = lat_lines, aes(x, y, group = line), colour = cfg$graticule, linewidth = .20) +
  geom_path(data = lon_lines, aes(x, y, group = line), colour = cfg$graticule, linewidth = .20) +
  geom_polygon(data = land, aes(x, y, group = polygon, subgroup = ring), rule = 'evenodd',
               fill = cfg$land, colour = cfg$shore, linewidth = .16) +
  geom_point(data = sites, aes(x, y, colour = value), size = 1.65, alpha = .86, stroke = 0) +
  scale_colour_viridis_c(option = 'C', limits = c(cfg$value_min, cfg$value_max), name = cfg$legend_title) +
  guides(colour = guide_colourbar(title.position = 'top', barwidth = grid::unit(72, 'mm'),
                                  barheight = grid::unit(3, 'mm'))) +
  coord_fixed(xlim = c(-2.08, 2.08), ylim = c(-1.06, 1.06), expand = FALSE, clip = 'off') +
  labs(title = cfg$title, subtitle = cfg$subtitle, caption = cfg$footer) +
  theme_void(base_family = cfg$font, base_size = 8) +
  theme(plot.title = element_text(size = 13, face = 'bold', colour = '#213640', margin = margin(b = 5)),
        plot.subtitle = element_text(size = 8, colour = '#596A72', margin = margin(b = 5)),
        plot.caption = element_text(size = 7, colour = '#596A72', hjust = 0, margin = margin(t = 4)),
        plot.margin = margin(9, 12, 8, 12), legend.position = 'bottom',
        legend.title = element_text(size = 8), legend.text = element_text(size = 7),
        legend.margin = margin(t = 3, b = 0))
w <- cfg$width_mm / 25.4; h <- cfg$height_mm / 25.4
grDevices::quartz(type = 'pdf', file = 'output/global-sites.pdf', width = w, height = h, family = cfg$font)
print(figure); grDevices::dev.off()
svglite::svglite('output/global-sites.svg', width = w, height = h, bg = 'white')
print(figure); grDevices::dev.off()
ragg::agg_png('output/global-sites.png', width = cfg$width_mm, height = cfg$height_mm, units = 'mm', res = cfg$dpi, background = 'white')
print(figure); grDevices::dev.off()
print(figure)
cat('GLOBAL_MAP_TEMPLATE_COMPLETE: ', nrow(sites), ' input sites; RStudio = ', Sys.getenv('RSTUDIO'), '\n', sep = '')
