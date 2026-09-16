# Shared ggplot2 theme for SPGD-TME figures. Tinos is required; silent
# font fallback is refused so later F3--F5 renders stay metric-stable.
suppressMessages({
  library(ggplot2)
  library(systemfonts)
  library(ragg)
})

.tme_required_font <- function() {
  fams <- unique(systemfonts::system_fonts()$family)
  if (!"Tinos" %in% fams) {
    stop("SPGD-TME rendering requires the Tinos font; refusing fallback.", call. = FALSE)
  }
  "Tinos"
}
TME_FONT <- .tme_required_font()
# Panels are printed six-up at \textwidth, so a 9/8 pt pair lands near 5 pt on
# the page. These sizes keep tick labels legible after that reduction.
TME_AXIS_PT <- 10.5
TME_TICK_PT <- 9.5
TME_VALUE_PT <- 3.2
TME_TAG_PT <- 13

# Okabe-Ito; used for substrate / pair keys, not for a method leaderboard.
.OI <- c(
  blue = "#0072B2", orange = "#E69F00", verm = "#D55E00", green = "#009E73",
  purple = "#CC79A7", sky = "#56B4E9", yellow = "#F0E442", black = "#000000",
  grey = "#999999"
)
oi <- function(k) unname(.OI[[k]])

SUBSTRATE_COL <- c(
  openST = oi("blue"),
  Xenium = oi("orange"),
  `Xenium FLEX` = oi("sky"),
  CosMx = oi("green")
)

PAIR_COL <- c(
  `A from B` = oi("blue"),
  `B from A` = oi("orange"),
  `D from C` = oi("green")
)

# Not the pair palette. Figure 11 prints a pair key and a condition key side by
# side, and two three-item keys in the same blue/orange/green read as one. This
# one also runs cool to warm, which the wound axis does and the pair set does not.
COND_COL <- c(
  Baseline = oi("sky"),
  Unwound = oi("purple"),
  Wound = oi("verm")
)

PATIENT_COL <- c(
  A = oi("blue"), B = oi("verm"), C = oi("green"), D = oi("purple")
)

DECISION_COL <- c(ABSTAIN = oi("verm"), KEEP = oi("green"))

TYPE_COL <- c(
  Cancer = oi("verm"), Endothelial = oi("sky"), Fibroblast = oi("orange"),
  Melanocyte = oi("yellow"), MoMacDC = oi("purple"), `Normal kerat.` = oi("green"),
  Pericyte = oi("blue"), `Plasma cell` = oi("grey")
)

pretty_pair <- function(x) {
  x <- gsub("_from_", " from ", x)
  x <- gsub("^A from B$", "A from B", x)
  x
}

pretty_substrate <- function(x) {
  out <- as.character(x)
  out[out == "openst"] <- "openST"
  out[out == "realgt"] <- "Xenium"
  out[out == "realgt2"] <- "Xenium FLEX"
  out[out == "realgt3"] <- "CosMx"
  out
}

pretty_type <- function(x) {
  map <- c(
    "Cancer.cells" = "Cancer",
    "Endothelial" = "Endothelial",
    "Fibroblast" = "Fibroblast",
    "Melanocyte" = "Melanocyte",
    "MoMacDC" = "MoMacDC",
    "Normal.Kerat" = "Normal kerat.",
    "Pericyte" = "Pericyte",
    "PlasmaCell" = "Plasma cell"
  )
  out <- unname(map[as.character(x)])
  ifelse(is.na(out), as.character(x), out)
}

pretty_step <- function(x) {
  map <- c(
    "extract_signature" = "Signature extraction",
    "signature_setup" = "Signature and spot setup",
    "specificity_weight" = "Specificity weights",
    "fit_gamma" = "Weighted fit",
    "platform_factor_fit" = "Platform factor fit",
    "self_gate" = "Platform self-gate",
    "platform_self_gate" = "Platform self-gate",
    "refuse" = "Reportability gate",
    "reportability_gate" = "Reportability gate",
    "poisson_fit" = "Poisson close",
    "poisson_close" = "Poisson close"
  )
  out <- unname(map[as.character(x)])
  ifelse(is.na(out), as.character(x), out)
}

as_flag <- function(x) {
  if (is.logical(x)) {
    return(x)
  }
  as.character(x) %in% c("True", "TRUE", "true", "1")
}

theme_tme <- function(base_size = 10) {
  theme_classic(base_size = TME_AXIS_PT, base_family = TME_FONT) +
    theme(
      axis.title = element_text(size = TME_AXIS_PT, face = "plain"),
      axis.text = element_text(size = TME_TICK_PT, face = "plain", colour = "black"),
      axis.line = element_line(linewidth = 0.4, colour = "black"),
      axis.ticks = element_line(linewidth = 0.4, colour = "black"),
      # Keys that need no title pass name = NULL; a colourbar has to say what it
      # encodes, so the title is not blanked here.
      legend.title = element_text(size = TME_TICK_PT, face = "plain"),
      legend.text = element_text(size = TME_TICK_PT, face = "plain"),
      legend.position = "top",
      legend.location = "plot",
      legend.direction = "horizontal",
      legend.justification = "center",
      legend.background = element_rect(fill = NA, colour = NA),
      legend.key = element_rect(fill = NA, colour = NA),
      legend.margin = margin(0, 0, 2, 0),
      plot.title = element_blank(),
      plot.subtitle = element_blank(),
      plot.tag = element_text(size = TME_TAG_PT, family = TME_FONT, face = "bold"),
      plot.caption = element_text(size = TME_TICK_PT, hjust = 0, colour = "grey20", margin = margin(6, 0, 0, 0)),
      strip.background = element_rect(fill = "grey94", colour = NA),
      strip.text = element_text(size = TME_TICK_PT, face = "plain", margin = margin(4, 6, 4, 6)),
      panel.grid.major = element_line(linewidth = 0.25, colour = "grey88"),
      panel.grid.minor = element_blank(),
      plot.margin = margin(8, 10, 8, 10)
    )
}

# CosMx export coordinates are pixels; locked conversion from donor_builder.
# Never swap x and y. Never stretch axes independently.
COSMX_UM_PER_PX <- 0.12028

to_um <- function(df, x = "x", y = "y", origin = NULL) {
  ox <- if (is.null(origin)) min(df[[x]], na.rm = TRUE) else origin[[1]]
  oy <- if (is.null(origin)) min(df[[y]], na.rm = TRUE) else origin[[2]]
  df$um_x <- (as.numeric(df[[x]]) - ox) * COSMX_UM_PER_PX
  df$um_y <- (as.numeric(df[[y]]) - oy) * COSMX_UM_PER_PX
  df
}

shared_origin <- function(...) {
  xs <- numeric(0)
  ys <- numeric(0)
  for (d in list(...)) {
    xs <- c(xs, as.numeric(d$x))
    ys <- c(ys, as.numeric(d$y))
  }
  c(min(xs, na.rm = TRUE), min(ys, na.rm = TRUE))
}

auto_scalebar <- function(um_x, um_y) {
  span <- max(diff(range(um_x, na.rm = TRUE)), diff(range(um_y, na.rm = TRUE)))
  if (span > 8000) {
    2000
  } else if (span > 3000) {
    1000
  } else if (span > 1200) {
    500
  } else {
    200
  }
}

# Back-compat name: translation to µm only.
prepare_spatial <- function(df, x = "x", y = "y") {
  to_um(df, x = x, y = y)
}

scalebar_xy <- function(um_x, um_y, length_um) {
  xmin <- min(um_x, na.rm = TRUE)
  xmax <- max(um_x, na.rm = TRUE)
  ymin <- min(um_y, na.rm = TRUE)
  ymax <- max(um_y, na.rm = TRUE)
  x0 <- xmin + 0.045 * (xmax - xmin)
  y0 <- ymin + 0.12 * (ymax - ymin)
  data.frame(x = x0, xend = x0 + length_um, y = y0, yend = y0)
}

scalebar_label <- function(length_um) {
  if (length_um >= 1000) {
    sprintf("%d mm", as.integer(round(length_um / 1000)))
  } else {
    sprintf("%d \u00b5m", as.integer(round(length_um)))
  }
}

# Every 0--1 face on this paper is the same quantity on the same scale, so they
# share one title and patchwork collects them into a single bar per figure.
# Which type each panel colours is stated in that panel's caption sentence.
OCCUPANCY_LAB <- "Type occupancy (0-1)"

scale_fraction <- function(name = OCCUPANCY_LAB) {
  scale_colour_viridis_c(
    option = "magma",
    limits = c(0, 1),
    breaks = c(0, 0.25, 0.5, 0.75, 1),
    begin = 0.08,
    end = 0.94,
    name = OCCUPANCY_LAB,
    guide = guide_colorbar(
      title.position = "left",
      title.vjust = 0.9,
      barwidth = unit(3.4, "cm"),
      barheight = unit(0.26, "cm"),
      ticks.linewidth = 0.2
    )
  )
}
# The collinearity sweep records the cosine at every t, so the refused stretch
# of a panel can be drawn from the same rows that carry the RMSE.
abstain_span <- function(d, c_star = 0.80) {
  refused <- d$t[d$cosine >= c_star]
  if (!length(refused)) {
    return(NULL)
  }
  min(refused)
}

abstain_layers <- function(d, c_star = 0.80) {
  onset <- abstain_span(d, c_star)
  if (is.null(onset)) {
    return(list())
  }
  list(
    annotate(
      "rect",
      xmin = onset, xmax = Inf, ymin = -Inf, ymax = Inf,
      fill = oi("verm"), alpha = 0.09
    ),
    annotate(
      "segment",
      x = onset, xend = onset, y = -Inf, yend = Inf,
      linetype = "22", linewidth = 0.45, colour = oi("verm")
    )
  )
}

theme_spatial <- function() {
  theme_tme() +
    theme(
      axis.text = element_blank(),
      axis.ticks = element_blank(),
      axis.line = element_blank(),
      panel.grid.major = element_blank(),
      panel.background = element_rect(fill = "white", colour = "grey70", linewidth = 0.30),
      # One collected bar per figure, so it has to carry its own title.
      legend.title = element_text(size = TME_TICK_PT, face = "plain", family = TME_FONT),
      legend.position = "bottom",
      legend.direction = "horizontal",
      legend.location = "plot",
      legend.justification = "center",
      legend.margin = margin(0, 0, 0, 0),
      legend.key.size = unit(0.28, "cm"),
      strip.background = element_rect(fill = "white", colour = NA),
      strip.text = element_text(size = TME_TICK_PT, face = "plain", margin = margin(1, 3, 1, 3)),
      plot.margin = margin(2, 3, 2, 3)
    )
}

tme_save <- function(plot, stem, w, h, figdir) {
  if (!dir.exists(figdir)) {
    stop(sprintf("SPGD-TME figure directory missing: %s", figdir), call. = FALSE)
  }
  png <- file.path(figdir, paste0(stem, ".png"))
  pdf <- file.path(figdir, paste0(stem, ".pdf"))
  ragg::agg_png(png, width = w, height = h, units = "in", res = 300, background = "white")
  print(plot)
  invisible(grDevices::dev.off())
  Cairo::CairoPDF(pdf, width = w, height = h, family = TME_FONT, version = "1.5")
  print(plot)
  invisible(grDevices::dev.off())
  cat("wrote", basename(png), "and", basename(pdf), "\n")
}
