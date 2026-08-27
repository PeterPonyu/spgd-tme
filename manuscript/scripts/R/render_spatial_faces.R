# Spatial data faces. Cells and spots stay in the CosMx pixel frame.

pa <- cells[cells$patient == "PatientA", ]
pb <- cells[cells$patient == "PatientB", ]
pc <- cells[cells$patient == "PatientC", ]
pd <- cells[cells$patient == "PatientD", ]
fov_a <- largest_fov(cells, "PatientA")
fov_b <- largest_fov(cells, "PatientB")
fov_c <- largest_fov(cells, "PatientC")
fov_base <- largest_fov(cells, "PatientD", "Baseline")
fov_wnd <- largest_fov(cells, "PatientD", "Wound")

if (!identical(Sys.getenv("TME_RENDER_ONLY"), "F11")) {

# The cohort is an eight-type simplex, so the cell-level faces report the whole
# composition rather than the three coordinates the wound axis moves.
occ <- cell_occ
occ$patient <- factor(gsub("^Patient", "", occ$patient), levels = c("A", "B", "C", "D"))
occ$condition <- factor(
  gsub("_", " ", occ$condition),
  levels = c("Ulcerated nodular", "Baseline", "Unwound", "Wound")
)
occ$type <- factor(pretty_type(occ$type), levels = names(TYPE_COL))
type_counts <- occ %>%
  dplyr::group_by(patient, type) %>%
  dplyr::summarise(n_cells = sum(n_cells), .groups = "drop")

# F3 has no spot-level panel to justify an occupancy bar, so the fields are
# coloured by the same eight types the composition panel stacks and take their
# key from that panel instead of printing a second copy of it.
g3a <- cell_mosaic(pa, "type", show_key = FALSE)
g3b <- cell_mosaic(pb, "type", show_key = FALSE)
g3c <- cell_mosaic(pc, "type", show_key = FALSE)
g3d <- cell_mosaic(pd, "type", show_key = FALSE)
g3e <- ggplot(occ, aes(patient, fraction, fill = type)) +
  geom_col(width = 0.72) +
  facet_grid(~condition, scales = "free_x", space = "free_x") +
  scale_fill_manual(values = TYPE_COL, name = NULL) +
  # No y limits: the stacked top lands on 1 within floating point, and a hard
  # limit censors the segment that carries it.
  scale_y_continuous(breaks = c(0, 0.5, 1), expand = expansion(mult = c(0, 0.02))) +
  guides(fill = guide_legend(nrow = 2, byrow = TRUE)) +
  labs(x = "Patient", y = "Typed-cell fraction") +
  theme_tme()
floor_note <- data.frame(
  type = factor(levels(type_counts$type)[1], levels = levels(type_counts$type)),
  n_cells = 50
)
g3f <- ggplot(type_counts, aes(type, n_cells, colour = patient)) +
  geom_hline(yintercept = 50, linetype = "22", linewidth = 0.45, colour = oi("verm")) +
  geom_text(
    data = floor_note, aes(type, n_cells, label = "50-cell reference floor"),
    inherit.aes = FALSE, hjust = 0, vjust = -0.6,
    size = TME_VALUE_PT, family = TME_FONT, colour = oi("verm")
  ) +
  geom_point(position = position_dodge(0.62), size = 1.9) +
  scale_colour_manual(values = PATIENT_COL, name = NULL) +
  scale_y_log10(
    labels = function(v) format(v, big.mark = ",", scientific = FALSE, trim = TRUE)
  ) +
  labs(x = NULL, y = "Typed cells per donor") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 35, hjust = 1))
f3 <- stack_spatial(
  list(
    row_fill(list(g3a, g3b), c(packed_aspect(pa), packed_aspect(pb))),
    row_fill(list(g3c, g3d), c(packed_aspect(pc), packed_aspect(pd))),
    row_fill(list(g3e, g3f), c(0.38, 0.38))
  ),
  guide_h = 0.11
)
f3_tag <- theme(
  plot.tag = element_text(size = TME_TAG_PT, family = TME_FONT, face = "bold"),
  plot.tag.position = "topleft",
  plot.margin = margin(6, 4, 4, 6)
)
tme_save(
  f3$plot + plot_annotation(tag_levels = "A") & f3_tag,
  "F3_cohort", 11.2, 11.2 * sum(f3$heights) + 0.40, figdir
)
if (identical(Sys.getenv("TME_RENDER_ONLY"), "F3")) {
  quit(save = "no")
}

uA <- cell_mosaic(pa, "type", point_size = 0.28)
uB <- cell_mosaic(pb, "cancer", point_size = 0.22)
uC <- fov_zoom_with_spots(cells, maps_a, "PatientA", fov_a, "type")
uD <- fov_zoom(cells, "PatientB", fov_b, "cancer")
uE <- spot_on_tissue(maps_a, "Cancer.cells", pa, point_size = 1.05)
uF <- spot_on_tissue(maps_b, "Cancer.cells", pb, point_size = 1.00)
f4 <- stack_spatial(list(
  row_fill(list(uA, uB), c(packed_aspect(pa), packed_aspect(pb))),
  row_fill(
    list(uC, uD),
    c(zoom_aspect(cells, "PatientA", fov_a), zoom_aspect(cells, "PatientB", fov_b)),
    max_aspect = 0.22
  ),
  row_fill(list(uE, uF), c(packed_aspect(pa), packed_aspect(pb)))
))
tme_save(
  f4$plot + plot_annotation(tag_levels = "A") & tag_theme,
  "F4_ulcerated", 11.2, 11.2 * sum(f4$heights) + 0.40, figdir
)

wA <- cell_mosaic(pd, "condition", point_size = 0.20)
wB <- fov_zoom(cells, "PatientD", fov_base, "cancer")
wC <- fov_zoom(cells, "PatientD", fov_wnd, "cancer")
wD <- spot_on_tissue(maps_d, "Cancer.cells", pd, point_size = 0.95)
wE <- spot_on_tissue(maps_d, "Fibroblast", pd, point_size = 0.95)
# Each of the 3261 spots carries its own truth vector and the condition of the
# field it sits in, so the wound axis is three distributions, not three means.
spot_cond$condition <- factor(spot_cond$condition, levels = c("Baseline", "Unwound", "Wound"))
wound_n <- spot_cond %>%
  dplyr::count(condition, name = "n")
wound_lab <- stats::setNames(
  sprintf("%s\n(n=%d)", wound_n$condition, wound_n$n),
  as.character(wound_n$condition)
)
wound_long <- spot_cond %>%
  tidyr::pivot_longer(
    c("Cancer.cells", "Fibroblast", "MoMacDC"),
    names_to = "type", values_to = "truth"
  ) %>%
  mutate(type = factor(pretty_type(type), levels = c("Cancer", "Fibroblast", "MoMacDC")))
wound_dodge <- position_dodge(width = 0.80)
wF <- ggplot(wound_long, aes(condition, truth, fill = type)) +
  geom_violin(
    position = wound_dodge, scale = "width", width = 0.72,
    linewidth = 0.25, colour = "grey35"
  ) +
  geom_boxplot(
    position = wound_dodge, width = 0.13, outlier.shape = NA,
    linewidth = 0.25, fill = "white", colour = "grey25"
  ) +
  stat_summary(
    fun = mean, geom = "point", position = wound_dodge,
    shape = 23, size = 1.4, fill = "white", colour = "grey15", stroke = 0.4
  ) +
  scale_fill_manual(values = TYPE_COL, name = NULL) +
  scale_x_discrete(labels = wound_lab) +
  scale_y_continuous(breaks = c(0, 0.5, 1), expand = expansion(mult = c(0.02, 0.04))) +
  labs(x = NULL, y = "Per-spot truth fraction") +
  theme_tme()
f5 <- stack_spatial(list(
  row_fill(
    list(wA, wB, wC),
    c(packed_aspect(pd), zoom_aspect(cells, "PatientD", fov_base), zoom_aspect(cells, "PatientD", fov_wnd))
  ),
  row_fill(list(wD, wE, wF), c(packed_aspect(pd), packed_aspect(pd), 0.55))
))
tme_save(
  f5$plot + plot_annotation(tag_levels = "A") & tag_theme,
  "F5_wound", 11.2, 11.2 * sum(f5$heights) + 0.40, figdir
)

kA <- cell_mosaic(pc, "cancer", point_size = 0.16)
kB <- spot_on_tissue(keep_cmp, "tumor_truth", pc, point_size = 0.70)
kC <- spot_on_tissue(keep_cmp, "tumor_hat", pc, point_size = 0.70)
kD <- fov_zoom(cells, "PatientC", fov_c, "cancer")
# The reported column is 5686 paired numbers; the two maps above show where they
# sit, and these two faces show how well they agree.
keep_rmse <- sqrt(mean((keep_cmp$tumor_hat - keep_cmp$tumor_truth)^2))
keep_pcc <- stats::cor(keep_cmp$tumor_hat, keep_cmp$tumor_truth)
kE <- ggplot(keep_cmp, aes(tumor_truth, tumor_hat)) +
  geom_abline(slope = 1, intercept = 0, linetype = "22", linewidth = 0.45, colour = "grey35") +
  geom_point(size = 0.45, alpha = 0.22, colour = oi("green"), stroke = 0) +
  annotate(
    "label",
    x = 0.02, y = 1.0, hjust = 0, vjust = 1,
    label = sprintf(
      "n = %d\nRMSE = %.4f\nr = %.4f", nrow(keep_cmp), keep_rmse, keep_pcc
    ),
    size = TME_VALUE_PT, family = TME_FONT,
    fill = "white", alpha = 0.75, lineheight = 1.05
  ) +
  scale_x_continuous(limits = c(0, 1), breaks = c(0, 0.5, 1)) +
  scale_y_continuous(limits = c(0, 1), breaks = c(0, 0.5, 1)) +
  labs(x = "Locked tumor truth", y = "Estimated tumor fraction") +
  theme_tme()
keep_ecdf <- rbind(
  data.frame(series = "Locked truth", value = keep_cmp$tumor_truth),
  data.frame(series = "Protocol estimate", value = keep_cmp$tumor_hat)
)
kF <- ggplot(keep_ecdf, aes(value, colour = series)) +
  stat_ecdf(linewidth = 0.7, pad = FALSE) +
  geom_hline(yintercept = 0.5, linetype = "22", linewidth = 0.35, colour = "grey55") +
  scale_colour_manual(
    values = c(`Locked truth` = oi("grey"), `Protocol estimate` = oi("green")),
    name = NULL
  ) +
  scale_x_continuous(limits = c(0, 1), breaks = c(0, 0.5, 1)) +
  scale_y_continuous(limits = c(0, 1), breaks = c(0, 0.5, 1)) +
  labs(x = "Tumor fraction", y = "Cumulative share of spots") +
  theme_tme()
f6 <- stack_spatial(list(
  row_fill(list(kA, kB, kC), c(packed_aspect(pc), packed_aspect(pc), packed_aspect(pc))),
  row_fill(list(kD, kE, kF), c(zoom_aspect(cells, "PatientC", fov_c), 0.42, 0.42))
))
tme_save(
  f6$plot + plot_annotation(tag_levels = "A") & tag_theme,
  "F6_keep", 11.2, 11.2 * sum(f6$heights) + 0.40, figdir
)

## F8_donor start
donor$pair <- factor(pretty_pair(donor$pair), levels = pair_levels)
donor$source <- factor(donor$source, levels = c("computed", "locked"))
dlong <- donor %>%
  tidyr::pivot_longer(
    c("RMSE", "PCC_type", "PCC_spot", "tumor_rmse"),
    names_to = "metric", values_to = "value"
  ) %>%
  mutate(metric = factor(
    metric,
    levels = c("RMSE", "tumor_rmse", "PCC_type", "PCC_spot"),
    labels = c("Overall RMSE", "Tumor RMSE", "Type PCC", "Spot PCC")
  ))
dA <- ggplot(dlong[!is.na(dlong$value), ], aes(pair, value, colour = source)) +
  geom_point(size = 3.2, stroke = 0.8) +
  facet_wrap(~metric, scales = "free_y", ncol = 2) +
  scale_colour_manual(values = c(computed = oi("blue"), locked = oi("orange")), name = NULL) +
  labs(x = "Directed transfer", y = "Metric") +
  theme_tme()
# Panel A already faces all four metrics on all four edges. Redrawing two of
# them as bars says nothing new, so B and C carry the truth the metrics are
# computed against instead: how tumor mass is spread over spots, and how the
# three tracked types divide each edge's simplex.
spot_truth <- dplyr::bind_rows(
  data.frame(pair = "A from B", maps_a[, c("Cancer.cells", "Fibroblast", "MoMacDC")]),
  data.frame(pair = "B from A", maps_b[, c("Cancer.cells", "Fibroblast", "MoMacDC")]),
  data.frame(pair = "D from C", maps_d[, c("Cancer.cells", "Fibroblast", "MoMacDC")])
)
spot_truth$pair <- factor(spot_truth$pair, levels = pair_levels)
computed_col <- PAIR_COL[c("A from B", "B from A", "D from C")]
pure_note <- spot_truth %>%
  dplyr::group_by(pair) %>%
  dplyr::summarise(pure = mean(Cancer.cells == 1), .groups = "drop")
dB <- ggplot(spot_truth, aes(Cancer.cells, colour = pair)) +
  stat_ecdf(geom = "step", linewidth = 0.75, pad = FALSE) +
  # The label sits at the height of each curve's final jump, which is exactly the
  # share of spots that are pure tumor, and names its own edge so the panel needs
  # no separate colour key.
  geom_text(
    data = pure_note,
    aes(x = 0.97, y = 1 - pure, label = sprintf("%s, %.0f%% pure tumor", pair, 100 * pure), colour = pair),
    inherit.aes = FALSE, hjust = 1, vjust = -0.55,
    size = TME_VALUE_PT, family = TME_FONT, show.legend = FALSE
  ) +
  scale_colour_manual(values = computed_col, guide = "none") +
  scale_x_continuous(limits = c(0, 1), breaks = c(0, 0.25, 0.5, 0.75, 1)) +
  scale_y_continuous(limits = c(0, 1.04), breaks = c(0, 0.25, 0.5, 0.75, 1)) +
  labs(x = "Spot tumor truth", y = "Share of spots at or below") +
  theme_tme()
simplex_mean <- spot_truth %>%
  dplyr::group_by(pair) %>%
  dplyr::summarise(
    Cancer = mean(Cancer.cells), Fibroblast = mean(Fibroblast),
    MoMacDC = mean(MoMacDC), .groups = "drop"
  ) %>%
  dplyr::mutate(`Other five types` = 1 - Cancer - Fibroblast - MoMacDC) %>%
  tidyr::pivot_longer(-pair, names_to = "type", values_to = "share") %>%
  dplyr::mutate(type = factor(type, levels = c("Cancer", "Fibroblast", "MoMacDC", "Other five types")))
dC <- ggplot(simplex_mean, aes(pair, share, fill = type)) +
  geom_col(width = 0.62) +
  geom_text(
    data = simplex_mean[simplex_mean$share > 0.06, ],
    # Fibroblast is the one light fill in this key; white on it does not read.
    aes(label = sprintf("%.3f", share), colour = type),
    position = position_stack(vjust = 0.5),
    size = TME_VALUE_PT, family = TME_FONT, show.legend = FALSE
  ) +
  scale_colour_manual(
    values = c(
      Cancer = "white", Fibroblast = "grey10", MoMacDC = "white",
      `Other five types` = "white"
    ),
    guide = "none"
  ) +
  scale_fill_manual(
    values = c(
      Cancer = TYPE_COL[["Cancer"]], Fibroblast = TYPE_COL[["Fibroblast"]],
      MoMacDC = TYPE_COL[["MoMacDC"]], `Other five types` = "grey55"
    ),
    name = NULL
  ) +
  guides(fill = guide_legend(nrow = 2, byrow = TRUE)) +
  scale_y_continuous(breaks = c(0, 0.5, 1), expand = expansion(mult = c(0, 0.02))) +
  labs(x = "Directed transfer", y = "Mean spot occupancy") +
  theme_tme()
dD <- spot_on_tissue(maps_b, "Cancer.cells", pb, point_size = 1.00)
dE <- spot_on_tissue(maps_d, "Cancer.cells", pd, point_size = 0.95)
dF <- spot_on_tissue(maps_a, "Cancer.cells", pa, point_size = 2.40, alpha = 1.00)
f8 <- stack_spatial(list(
  row_fill(list(dA), 0.46),
  row_fill(list(dB, dC), c(0.36, 0.36)),
  row_fill(list(dD, dE, dF), c(packed_aspect(pb), packed_aspect(pd), packed_aspect(pa)))
))
tme_save(
  f8$plot +
    plot_annotation(tag_levels = "A") &
    theme(
      plot.tag = element_text(size = TME_TAG_PT, family = TME_FONT, face = "bold", hjust = 0, vjust = 1),
      plot.tag.position = "topleft"
    ),
  "F8_donor", 11.2, 11.2 * sum(f8$heights) + 0.40, figdir
)
## F8_donor end

myelo$pair <- factor(pretty_pair(myelo$pair), levels = pair_levels)
# Three means say nothing about a zero-inflated axis: over half these spots hold
# no myeloid cell at all. The step curve carries the whole per-spot distribution
# and marks where each edge's mean falls inside it.
momac <- spot_truth[, c("pair", "MoMacDC")]
# The mean and the empty share come from the tracked occupancy table, not from a
# recount of the maps, so the marked values are the ones the prose reports.
momac_mark <- myelo %>%
  dplyr::transmute(pair, m = mean, empty = zero_rate)
momac_mark$at <- vapply(
  seq_len(nrow(momac_mark)),
  function(i) mean(momac$MoMacDC[momac$pair == momac_mark$pair[i]] <= momac_mark$m[i]),
  numeric(1)
)
mA <- ggplot(momac, aes(MoMacDC, colour = pair)) +
  stat_ecdf(geom = "step", linewidth = 0.75, pad = FALSE) +
  geom_point(
    data = momac_mark, aes(m, at, colour = pair),
    inherit.aes = FALSE, size = 2.3, shape = 18, show.legend = FALSE
  ) +
  # Naming the edge on its own curve is what lets this panel drop the colour key
  # a fourth legend row would otherwise cost the figure.
  geom_text(
    data = momac_mark,
    aes(x = 0.97, y = empty, label = sprintf("%s, %.0f%% empty", pair, 100 * empty), colour = pair),
    inherit.aes = FALSE, hjust = 1, vjust = -0.55,
    size = TME_VALUE_PT, family = TME_FONT, show.legend = FALSE
  ) +
  scale_colour_manual(values = computed_col, guide = "none") +
  scale_x_continuous(limits = c(0, 1), breaks = c(0, 0.25, 0.5, 0.75, 1)) +
  scale_y_continuous(limits = c(0, 1.04), breaks = c(0, 0.25, 0.5, 0.75, 1)) +
  labs(x = "Spot MoMacDC truth", y = "Share of spots at or below") +
  theme_tme()
mB <- spot_on_tissue(maps_a, "MoMacDC", pa, point_size = 4.20, alpha = 1.00)
mC <- spot_on_tissue(maps_d, "MoMacDC", pd, point_size = 1.75, alpha = 0.90)
mD <- fov_zoom(cells, "PatientA", fov_a, "momacdc", point_size = 2.40)
mE <- fov_zoom(cells, "PatientD", fov_wnd, "momacdc", point_size = 1.90)
mF <- spot_on_tissue(maps_a, "Fibroblast", pa, point_size = 4.20, alpha = 1.00)
f9 <- stack_spatial(
  list(
    row_fill(list(mA, mB, mC), c(0.42, packed_aspect(pa), packed_aspect(pd))),
    row_fill(
      list(mD, mE, mF),
      c(zoom_aspect(cells, "PatientA", fov_a), zoom_aspect(cells, "PatientD", fov_wnd), packed_aspect(pa))
    )
  ),
  guide_h = 0.12
)
tme_save(
  f9$plot +
    plot_annotation(tag_levels = "A") &
    theme(
      plot.tag = element_text(size = TME_TAG_PT, family = TME_FONT, face = "bold", hjust = 0, vjust = 1),
      plot.tag.position = "topleft",
      legend.title = element_text(size = TME_TICK_PT, face = "plain", family = TME_FONT)
    ),
  "F9_myeloid", 11.2, 11.2 * sum(f9$heights) + 0.40, figdir
)

}

floor$pair <- factor(pretty_pair(floor$pair), levels = pair_levels)
floor$type <- factor(pretty_type(floor$type), levels = rev(unique(pretty_type(floor$type))))
floor$present <- 1 - floor$zero_rate
cond_spots$condition <- factor(cond_spots$condition, levels = c("Baseline", "Unwound", "Wound"))
cond_spots$type <- factor(pretty_type(cond_spots$type), levels = rev(unique(pretty_type(cond_spots$type))))
# Three bar panels over the same eight types: only the leftmost needs to name
# them, and repeating the names costs the other two a third of their width.
share_type_axis <- theme(
  axis.text.y = element_blank(),
  axis.ticks.y = element_blank()
)
fA <- ggplot(floor, aes(type, mean, fill = pair)) +
  geom_col(position = position_dodge(0.78), width = 0.72) +
  coord_flip() +
  scale_fill_manual(values = PAIR_COL, name = NULL) +
  scale_y_continuous(breaks = c(0, 0.25, 0.5, 0.75)) +
  labs(x = NULL, y = "Mean spot occupancy") +
  theme_tme()
# A mean near zero can be a type spread thinly over every spot or a type absent
# from most of them, and Type PCC averages those two cases differently. This is
# the second reading the mean cannot give.
fB <- ggplot(floor, aes(type, present, fill = pair)) +
  geom_col(position = position_dodge(0.78), width = 0.72) +
  coord_flip() +
  scale_fill_manual(values = PAIR_COL, name = NULL) +
  scale_y_continuous(limits = c(0, 1), breaks = c(0, 0.25, 0.5, 0.75, 1)) +
  labs(x = NULL, y = "Share of spots holding the type") +
  theme_tme() +
  share_type_axis
fC <- ggplot(cond_spots, aes(type, mean, fill = condition)) +
  geom_col(position = position_dodge(0.78), width = 0.72) +
  coord_flip() +
  scale_fill_manual(values = COND_COL, name = NULL) +
  scale_y_continuous(breaks = c(0, 0.25, 0.5, 0.75)) +
  labs(x = NULL, y = "Mean spot occupancy, wound axis") +
  theme_tme() +
  share_type_axis
# The three donors pack to aspects of 0.40, 0.50, and 0.57, so widths drawn from
# each footprint leave the row ragged and pull the leftmost field away from the
# panel above it. One shared view box makes the three the same size; the padding
# lands outside the tissue and the micrometre scale is untouched.
field_aspect <- exp(mean(log(c(packed_aspect(pa), packed_aspect(pb), packed_aspect(pd)))))
fD <- spot_on_tissue(maps_a, "Cancer.cells", pa, point_size = 2.85, target_aspect = field_aspect)
fE <- spot_on_tissue(maps_b, "Cancer.cells", pb, point_size = 2.60, target_aspect = field_aspect)
fF <- spot_on_tissue(maps_d, "Cancer.cells", pd, point_size = 2.90, target_aspect = field_aspect)
f11 <- stack_spatial(list(
  row_fill(list(fA, fB, fC), c(0.52, 0.52, 0.52)),
  row_fill(list(fD, fE, fF), c(field_aspect, field_aspect, field_aspect))
))
f11_tag <- theme(
  plot.tag = element_text(size = TME_TAG_PT, family = TME_FONT, face = "bold", hjust = 0, vjust = 1),
  plot.tag.position = "topleft",
  plot.title = element_text(
    hjust = 0.5, face = "plain", family = TME_FONT, size = TME_AXIS_PT
  ),
  plot.margin = margin(6, 4, 4, 6)
)
tme_save(
  f11$plot + plot_annotation(tag_levels = "A") & f11_tag,
  "F11_floor", 11.2, 11.2 * sum(f11$heights) + 0.40, figdir
)
