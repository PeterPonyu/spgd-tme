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

f3_sum <- cell_sum
f3_sum$patient <- factor(gsub("^Patient", "", f3_sum$patient), levels = c("A", "B", "C", "D"))
f3_sum$condition <- factor(
  gsub("_", " ", f3_sum$condition),
  levels = c("Baseline", "Ulcerated nodular", "Unwound", "Wound")
)
f3_fill <- c(
  "Ulcerated nodular" = oi("purple"), Baseline = oi("blue"),
  Unwound = oi("orange"), Wound = oi("green")
)
clong <- f3_sum %>%
  tidyr::pivot_longer(
    c("cancer_fraction", "fibroblast_fraction", "momacdc_fraction"),
    names_to = "metric", values_to = "value"
  ) %>%
  mutate(metric = recode(
    metric,
    cancer_fraction = "Cancer",
    fibroblast_fraction = "Fibroblast",
    momacdc_fraction = "MoMacDC"
  ))

g3a <- cell_mosaic(pa, "cancer")
g3b <- cell_mosaic(pb, "cancer")
g3c <- cell_mosaic(pc, "cancer")
g3d <- cell_mosaic(pd, "cancer")
g3e <- ggplot(clong, aes(patient, value, fill = condition)) +
  geom_col(position = position_dodge(0.78), width = 0.72) +
  facet_wrap(~metric, ncol = 3, scales = "free_y") +
  scale_fill_manual(values = f3_fill) +
  labs(x = "Patient", y = "Typed-cell fraction") +
  theme_tme()
g3f <- ggplot(f3_sum, aes(patient, n_cells, fill = condition)) +
  geom_col(position = position_dodge(0.78), width = 0.72) +
  scale_fill_manual(values = f3_fill) +
  labs(x = "Patient", y = "Typed cells") +
  theme_tme()
f3 <- stack_spatial(list(
  row_fill(list(g3a, g3b), c(packed_aspect(pa), packed_aspect(pb))),
  row_fill(list(g3c, g3d), c(packed_aspect(pc), packed_aspect(pd))),
  row_fill(list(g3e, g3f), c(0.36, 0.36))
))
f3_tag <- theme(
  plot.tag = element_text(size = 11, family = TME_FONT, face = "bold"),
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
cond_spots$condition <- factor(cond_spots$condition, levels = c("Baseline", "Unwound", "Wound"))
cond_spots$type <- factor(pretty_type(cond_spots$type), levels = rev(unique(pretty_type(cond_spots$type))))
wF <- ggplot(cond_spots, aes(type, mean, fill = condition)) +
  geom_col(position = position_dodge(0.78), width = 0.72) +
  coord_flip() +
  scale_fill_manual(values = COND_COL) +
  labs(x = NULL, y = "Mean truth fraction") +
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
kE <- ggplot(refuse, aes(substrate, cosine, fill = decision)) +
  geom_col(width = 0.62) +
  geom_hline(yintercept = 0.80, linewidth = 0.45, linetype = "22") +
  scale_fill_manual(values = c(ABSTAIN = oi("verm"), KEEP = oi("green"))) +
  labs(x = NULL, y = "Cosine") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))
kF <- ggplot(refuse, aes(decision, fill = decision)) +
  geom_bar(width = 0.55) +
  scale_fill_manual(values = c(ABSTAIN = oi("verm"), KEEP = oi("green")), guide = "none") +
  labs(x = "Native call", y = "Substrates") +
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
  scale_colour_manual(values = c(computed = oi("blue"), locked = oi("orange"))) +
  labs(x = "Directed transfer", y = "Metric") +
  theme_tme()
dB <- ggplot(donor[!is.na(donor$RMSE), ], aes(pair, RMSE, fill = source)) +
  geom_col(width = 0.62) +
  geom_text(
    aes(label = sprintf("%.4f", RMSE)),
    vjust = -0.35,
    size = 2.6,
    family = TME_FONT
  ) +
  scale_fill_manual(values = c(computed = oi("blue"), locked = oi("orange")), guide = "none") +
  scale_y_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = "Directed transfer", y = "Overall RMSE") +
  theme_tme()
dC <- ggplot(donor[!is.na(donor$PCC_spot), ], aes(pair, PCC_spot, fill = source)) +
  geom_col(width = 0.62) +
  geom_text(
    aes(label = sprintf("%.4f", PCC_spot)),
    vjust = -0.35,
    size = 2.6,
    family = TME_FONT
  ) +
  scale_fill_manual(values = c(computed = oi("blue"), locked = oi("orange")), guide = "none") +
  scale_y_continuous(limits = c(0, 1.12), expand = expansion(mult = c(0, 0))) +
  labs(x = "Directed transfer", y = "Spot PCC") +
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
      plot.tag = element_text(size = 11, family = TME_FONT, face = "bold", hjust = 0, vjust = 1),
      plot.tag.position = "topleft"
    ),
  "F8_donor", 11.2, 11.2 * sum(f8$heights) + 0.40, figdir
)
## F8_donor end

myelo$pair <- factor(pretty_pair(myelo$pair), levels = pair_levels)
f9_occ <- function(p, name) {
  p +
    scale_colour_viridis_c(
      option = "magma",
      limits = c(0, 1),
      breaks = c(0, 0.5, 1),
      begin = 0.08,
      end = 0.94,
      name = name,
      guide = guide_colorbar(
        title.position = "top",
        title.hjust = 0.5,
        barwidth = unit(2.6, "cm"),
        barheight = unit(0.22, "cm"),
        ticks.linewidth = 0.2
      )
    ) +
    theme(
      legend.title = element_text(size = TME_TICK_PT, face = "plain", family = TME_FONT)
    )
}
mA <- ggplot(myelo, aes(pair, mean)) +
  geom_col(fill = oi("purple"), width = 0.55) +
  geom_text(
    aes(label = sprintf("%.4f", mean)),
    vjust = -0.35,
    size = 2.6,
    family = TME_FONT,
    fontface = "plain"
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = "Pair", y = "MoMacDC mean truth fraction") +
  theme_tme()
mB <- f9_occ(
  spot_on_tissue(maps_a, "MoMacDC", pa, point_size = 4.20, alpha = 1.00),
  "MoMacDC occupancy"
)
mC <- f9_occ(
  spot_on_tissue(maps_d, "MoMacDC", pd, point_size = 1.75, alpha = 0.90),
  "MoMacDC occupancy"
)
mD <- f9_occ(
  fov_zoom(cells, "PatientA", fov_a, "momacdc", point_size = 2.40),
  "MoMacDC occupancy"
)
mE <- f9_occ(
  fov_zoom(cells, "PatientD", fov_wnd, "momacdc", point_size = 1.90),
  "MoMacDC occupancy"
)
mF <- f9_occ(
  spot_on_tissue(maps_a, "Fibroblast", pa, point_size = 4.20, alpha = 1.00),
  "Fibroblast occupancy"
)
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
      plot.tag = element_text(size = 11, family = TME_FONT, face = "bold", hjust = 0, vjust = 1),
      plot.tag.position = "topleft",
      legend.title = element_text(size = TME_TICK_PT, face = "plain", family = TME_FONT)
    ),
  "F9_myeloid", 11.2, 11.2 * sum(f9$heights) + 0.40, figdir
)

}

floor$pair <- factor(pretty_pair(floor$pair), levels = pair_levels)
floor$type <- factor(pretty_type(floor$type), levels = rev(unique(pretty_type(floor$type))))
cond_spots$condition <- factor(cond_spots$condition, levels = c("Baseline", "Unwound", "Wound"))
cond_spots$type <- factor(pretty_type(cond_spots$type), levels = rev(unique(pretty_type(cond_spots$type))))
myelo$pair <- factor(pretty_pair(myelo$pair), levels = pair_levels)
p9a <- ggplot(floor, aes(type, mean, fill = pair)) +
  geom_col(position = position_dodge(0.78), width = 0.72) +
  coord_flip() +
  scale_fill_manual(values = PAIR_COL) +
  labs(x = "Type", y = "Mean truth fraction") +
  theme_tme()
fB <- ggplot(cond_spots, aes(type, mean, fill = condition)) +
  geom_col(position = position_dodge(0.78), width = 0.72) +
  coord_flip() +
  scale_fill_manual(values = COND_COL) +
  labs(x = NULL, y = "Wound-axis fraction") +
  theme_tme()
fC <- ggplot(myelo, aes(pair, mean)) +
  geom_col(fill = oi("purple"), width = 0.55) +
  geom_text(
    aes(label = sprintf("%.4f", mean)),
    vjust = -0.35,
    size = 2.6,
    family = TME_FONT,
    fontface = "plain"
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = NULL, y = "MoMacDC") +
  theme_tme()
fD <- spot_on_tissue(maps_a, "Cancer.cells", pa, point_size = 2.85)
fE <- spot_on_tissue(maps_b, "Cancer.cells", pb, point_size = 2.60)
fF <- spot_on_tissue(maps_d, "Cancer.cells", pd, point_size = 2.90)
f11 <- stack_spatial(list(
  row_fill(list(p9a, fB, fC), c(0.55, 0.55, 0.40)),
  row_fill(list(fD, fE, fF), c(packed_aspect(pa), packed_aspect(pb), packed_aspect(pd)))
))
f11_tag <- theme(
  plot.tag = element_text(size = 11, family = TME_FONT, face = "bold", hjust = 0, vjust = 1),
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
