# Honest CosMx geometry. Pixel axes stay native (no x/y swap).
# Multi-FOV panels pack recorded fields into a tile grid so the axis
# box is filled with tissue. Each tile keeps its own 0.51 mm geometry.

fov_pixel_rects <- function(cells) {
  cells %>%
    dplyr::group_by(patient, fov) %>%
    dplyr::summarise(
      xmin = min(x),
      xmax = max(x),
      ymin = min(y),
      ymax = max(y),
      cx = mean(x),
      cy = mean(y),
      .groups = "drop"
    )
}

fov_rectangles <- function(cells, origin = NULL) {
  rects <- fov_pixel_rects(cells)
  ox <- if (is.null(origin)) min(rects$xmin) else origin[[1]]
  oy <- if (is.null(origin)) min(rects$ymin) else origin[[2]]
  rects %>%
    dplyr::mutate(
      xmin = (xmin - ox) * COSMX_UM_PER_PX,
      xmax = (xmax - ox) * COSMX_UM_PER_PX,
      ymin = (ymin - oy) * COSMX_UM_PER_PX,
      ymax = (ymax - oy) * COSMX_UM_PER_PX,
      cx = (cx - ox) * COSMX_UM_PER_PX,
      cy = (cy - oy) * COSMX_UM_PER_PX
    )
}

choose_pack_grid <- function(n, target_aspect = 0.62) {
  best <- list(ncol = max(1L, n), nrow = 1L)
  best_score <- Inf
  for (ncol in seq_len(max(1L, n))) {
    nrow <- max(1L, as.integer(ceiling(n / ncol)))
    leftover <- ncol * nrow - n
    asp <- nrow / ncol
    score <- leftover * 1.25 + 2.2 * abs(log(asp / target_aspect))
    if (score < best_score) {
      best_score <- score
      best <- list(ncol = as.integer(ncol), nrow = nrow)
    }
  }
  best
}

pack_layout <- function(rects, target_aspect = 0.62) {
  grid <- choose_pack_grid(nrow(rects), target_aspect)
  pitch <- (stats::median(pmax(rects$xmax - rects$xmin, rects$ymax - rects$ymin)) + 36) *
    COSMX_UM_PER_PX
  ordered <- rects[order(-rects$cy, rects$cx), , drop = FALSE]
  n <- nrow(ordered)
  ordered$col <- (seq_len(n) - 1L) %% grid$ncol
  ordered$row <- (seq_len(n) - 1L) %/% grid$ncol
  ordered$ox <- ordered$col * pitch
  ordered$oy <- (grid$nrow - 1L - ordered$row) * pitch
  ordered$pitch <- pitch
  ordered
}

pack_cells <- function(cells) {
  layout <- pack_layout(fov_pixel_rects(cells))
  cells %>%
    dplyr::left_join(
      layout %>% dplyr::select(patient, fov, xmin, ymin, ox, oy),
      by = c("patient", "fov")
    ) %>%
    dplyr::mutate(
      um_x = (x - xmin) * COSMX_UM_PER_PX + ox,
      um_y = (y - ymin) * COSMX_UM_PER_PX + oy
    )
}

pack_rects <- function(cells) {
  layout <- pack_layout(fov_pixel_rects(cells))
  layout %>%
    dplyr::mutate(
      x0 = ox,
      x1 = ox + (xmax - xmin) * COSMX_UM_PER_PX,
      y0 = oy,
      y1 = oy + (ymax - ymin) * COSMX_UM_PER_PX
    )
}

assign_fov <- function(pts, rects, pad_px = 80) {
  out <- pts
  if (!"fov" %in% names(out)) {
    out$fov <- NA_integer_
  }
  for (i in seq_len(nrow(rects))) {
    hit <- is.na(out$fov) &
      pts$x >= rects$xmin[i] - pad_px &
      pts$x <= rects$xmax[i] + pad_px &
      pts$y >= rects$ymin[i] - pad_px &
      pts$y <= rects$ymax[i] + pad_px
    out$fov[hit] <- rects$fov[i]
  }
  out[!is.na(out$fov), , drop = FALSE]
}

pack_points <- function(pts, cells) {
  rects <- fov_pixel_rects(cells)
  layout <- pack_layout(rects)
  pts <- assign_fov(pts, rects)
  pts %>%
    dplyr::left_join(
      layout %>% dplyr::select(fov, xmin, ymin, ox, oy),
      by = "fov"
    ) %>%
    dplyr::filter(!is.na(ox)) %>%
    dplyr::mutate(
      um_x = (x - xmin) * COSMX_UM_PER_PX + ox,
      um_y = (y - ymin) * COSMX_UM_PER_PX + oy
    )
}

fill_axes <- function(p, um_x, um_y, pad = 0.006) {
  xr <- range(um_x, na.rm = TRUE)
  yr <- range(um_y, na.rm = TRUE)
  dx <- max(diff(xr), 1e-3)
  dy <- max(diff(yr), 1e-3)
  p +
    coord_cartesian(
      xlim = xr + c(-1, 1) * pad * dx,
      ylim = yr + c(-1, 1) * pad * dy,
      expand = FALSE
    )
}

packed_aspect <- function(cells) {
  r <- pack_rects(cells)
  max(diff(range(c(r$y0, r$y1))), 1e-3) / max(diff(range(c(r$x0, r$x1))), 1e-3)
}

zoom_aspect <- function(cells, patient, fov) {
  raw <- cells[cells$patient == patient & cells$fov == fov, , drop = FALSE]
  um <- to_um(raw)
  max(diff(range(um$um_y)), 1e-3) / max(diff(range(um$um_x)), 1e-3)
}

row_fill <- function(plots, aspects, max_aspect = 0.30) {
  aspects <- pmax(as.numeric(aspects), 1e-3)
  widths <- (1 / aspects) / sum(1 / aspects)
  list(
    plot = patchwork::wrap_plots(plots, ncol = length(plots), widths = widths),
    aspect = min(widths[[1]] * aspects[[1]], max_aspect),
    widths = widths
  )
}

stack_spatial <- function(rows, guide_h = 0.07) {
  composed <- rows[[1]]$plot
  if (length(rows) > 1L) {
    for (i in seq.int(2L, length(rows))) {
      composed <- composed / rows[[i]]$plot
    }
  }
  composed <- composed / (patchwork::guide_area() + theme(plot.tag = element_blank()))
  hs <- c(vapply(rows, function(r) r$aspect, numeric(1)), guide_h)
  list(
    plot = composed + patchwork::plot_layout(heights = hs, guides = "collect") &
      theme(
        legend.position = "bottom",
        legend.justification = "center",
        # Collected guides sit side by side; stacked they push the last key off
        # the canvas.
        legend.box = "horizontal",
        legend.box.just = "center"
      ),
    heights = hs
  )
}

add_scalebar <- function(p, um_x, um_y) {
  L <- auto_scalebar(um_x, um_y)
  sb <- scalebar_xy(um_x, um_y, L)
  dy <- max(diff(range(um_y, na.rm = TRUE)), 1e-3)
  p +
    geom_segment(
      data = sb,
      aes(x = x, y = y, xend = xend, yend = yend),
      inherit.aes = FALSE,
      linewidth = 0.55,
      colour = "grey15"
    ) +
    annotate(
      "text",
      x = mean(c(sb$x, sb$xend)),
      y = sb$y - 0.055 * dy,
      label = scalebar_label(L),
      size = 2.9,
      family = TME_FONT,
      colour = "grey15"
    )
}

apply_cell_colour <- function(p, d, colour_by, point_size, show_key = TRUE) {
  if (colour_by %in% c("cancer", "fibroblast", "momacdc")) {
    key <- c(cancer = "Cancer.cells", fibroblast = "Fibroblast", momacdc = "MoMacDC")[[colour_by]]
    d$frac <- as.numeric(d$celltype == key)
    p +
      geom_point(
        data = d,
        aes(um_x, um_y, colour = frac),
        size = point_size,
        stroke = 0,
        alpha = 0.90
      ) +
      scale_fraction()
  } else if (colour_by == "type") {
    d$type <- factor(pretty_type(d$celltype), levels = names(TYPE_COL))
    p +
      geom_point(
        data = d,
        aes(um_x, um_y, colour = type),
        size = point_size,
        stroke = 0,
        alpha = 0.90
      ) +
      scale_colour_manual(
        values = TYPE_COL, drop = FALSE, name = NULL,
        # A figure that also stacks the eight types already prints this key; a
        # second copy in point form is the same eight labels twice.
        # Cells are drawn sub-point, so the key it does print needs its own size.
        guide = if (show_key) {
          guide_legend(override.aes = list(size = 1.8, alpha = 1))
        } else {
          "none"
        }
      )
  } else if (colour_by == "condition") {
    p +
      geom_point(
        data = d,
        aes(um_x, um_y, colour = condition),
        size = point_size,
        stroke = 0,
        alpha = 0.90
      ) +
      scale_colour_manual(
        values = c(COND_COL, `Ulcerated nodular` = oi("purple")),
        drop = TRUE, name = NULL
      ) +
      guides(colour = guide_legend(override.aes = list(size = 1.8, alpha = 1)))
  } else {
    stop(sprintf("unknown colour_by: %s", colour_by), call. = FALSE)
  }
}

tile_base <- function(rects) {
  ggplot() +
    geom_rect(
      data = rects,
      aes(xmin = x0, xmax = x1, ymin = y0, ymax = y1),
      inherit.aes = FALSE,
      fill = NA,
      colour = "grey50",
      linewidth = 0.22
    ) +
    labs(x = NULL, y = NULL) +
    theme_spatial()
}

cell_mosaic <- function(cells, colour_by, point_size = 0.28, show_key = TRUE) {
  packed <- pack_cells(cells)
  rects <- pack_rects(cells)
  um_x <- c(rects$x0, rects$x1)
  um_y <- c(rects$y0, rects$y1)
  p <- apply_cell_colour(tile_base(rects), packed, colour_by, point_size, show_key)
  fill_axes(add_scalebar(p, um_x, um_y), um_x, um_y)
}

cell_mosaic_slide <- function(cells, colour_by, point_size = 0.16) {
  origin <- c(min(cells$x), min(cells$y))
  um <- to_um(cells, origin = origin)
  rects <- fov_rectangles(cells, origin = origin) %>%
    dplyr::rename(x0 = xmin, x1 = xmax, y0 = ymin, y1 = ymax)
  p <- apply_cell_colour(tile_base(rects), um, colour_by, point_size)
  fill_axes(add_scalebar(p, um$um_x, um$um_y), um$um_x, um$um_y)
}

spot_on_tissue <- function(spots, colour_col, cells, point_size = 1.05, alpha = 0.95) {
  packed_c <- pack_cells(cells)
  packed_s <- pack_points(spots, cells)
  rects <- pack_rects(cells)
  um_x <- c(rects$x0, rects$x1)
  um_y <- c(rects$y0, rects$y1)
  p <- tile_base(rects) +
    geom_point(
      data = packed_c,
      aes(um_x, um_y),
      colour = "grey78",
      size = 0.11,
      alpha = 0.40,
      stroke = 0
    ) +
    geom_point(
      data = packed_s,
      aes(um_x, um_y, colour = .data[[colour_col]]),
      size = point_size,
      alpha = alpha,
      stroke = 0
    ) +
    scale_fraction()
  fill_axes(add_scalebar(p, um_x, um_y), um_x, um_y)
}

largest_fov <- function(cells, patient, condition = NULL) {
  d <- cells[cells$patient == patient, , drop = FALSE]
  if (!is.null(condition)) {
    d <- d[d$condition == condition, , drop = FALSE]
  }
  d %>%
    dplyr::count(fov, name = "n") %>%
    dplyr::slice_max(n, n = 1, with_ties = FALSE) %>%
    dplyr::pull(fov)
}

spot_centroid_in <- function(spots, cells) {
  xr <- range(cells$x)
  yr <- range(cells$y)
  spots %>% dplyr::filter(x >= xr[1], x <= xr[2], y >= yr[1], y <= yr[2])
}

fov_zoom <- function(cells, patient, fov, colour_by, point_size = 0.42) {
  raw <- cells[cells$patient == patient & cells$fov == fov, , drop = FALSE]
  um <- to_um(raw)
  p <- apply_cell_colour(
    ggplot() + labs(x = NULL, y = NULL) + theme_spatial(),
    um,
    colour_by,
    point_size
  )
  fill_axes(add_scalebar(p, um$um_x, um$um_y), um$um_x, um$um_y)
}

fov_zoom_with_spots <- function(cells, spots, patient, fov, colour_by) {
  raw <- cells[cells$patient == patient & cells$fov == fov, , drop = FALSE]
  origin <- c(min(raw$x), min(raw$y))
  um <- to_um(raw, origin = origin)
  sp <- to_um(spot_centroid_in(spots, raw), origin = origin)
  p <- apply_cell_colour(
    ggplot() + labs(x = NULL, y = NULL) + theme_spatial(),
    um,
    colour_by,
    0.34
  ) +
    geom_point(
      data = sp,
      aes(um_x, um_y),
      inherit.aes = FALSE,
      shape = 21,
      fill = NA,
      colour = "grey15",
      size = 2.0,
      stroke = 0.35
    )
  fill_axes(add_scalebar(p, um$um_x, um$um_y), um$um_x, um$um_y)
}
