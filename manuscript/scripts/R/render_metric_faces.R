# Non-spatial data faces. Assumes plot tables and helpers are in the parent frame.

collect_bottom <- function(p) {
  p + patchwork::plot_layout(guides = "collect") +
    plot_annotation(tag_levels = "A") &
    tag_theme &
    theme(legend.position = "bottom", legend.justification = "center")
}

## F2_hero start
pA <- ggplot(cards, aes(pair, n_spots)) +
  geom_col(fill = oi("blue"), width = 0.62) +
  geom_text(
    aes(label = n_spots),
    vjust = -0.35, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.16))) +
  labs(x = "Donor pair", y = "Spots") +
  theme_tme()
pB <- ggplot(mass, aes(type, pair, fill = mean)) +
  geom_tile(colour = "white", linewidth = 0.3) +
  geom_text(
    aes(label = sprintf("%.2f", mean), colour = mean > 0.45),
    size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_fill_gradient(low = "white", high = oi("verm"), name = "Mean occupancy") +
  scale_colour_manual(values = c(`FALSE` = "grey20", `TRUE` = "white"), guide = "none") +
  labs(x = "Type", y = "Pair") +
  theme_tme() +
  theme(
    axis.text.x = element_text(angle = 35, hjust = 1),
    panel.grid.major = element_blank()
  )
pC <- ggplot(refuse, aes(substrate, cosine, fill = decision)) +
  geom_col(width = 0.62) +
  geom_hline(yintercept = 0.80, linewidth = 0.45, linetype = "22") +
  geom_text(
    aes(label = sprintf("%.3f", cosine)),
    vjust = 1.5, size = TME_VALUE_PT, family = TME_FONT, colour = "white"
  ) +
  scale_fill_manual(
    values = DECISION_COL, limits = names(DECISION_COL), drop = FALSE, name = NULL
  ) +
  scale_y_continuous(limits = c(0, 1.05), expand = expansion(mult = c(0, 0))) +
  labs(x = "Library", y = "Locked cosine") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))
# Every mixed spot carries its own truth vector, so the pair is a distribution
# and not the three means the rest of the board reports.
spot_truth <- rbind(
  data.frame(pair = "A from B", tumor = maps_a$Cancer.cells),
  data.frame(pair = "B from A", tumor = maps_b$Cancer.cells),
  data.frame(pair = "D from C", tumor = maps_d$Cancer.cells)
)
spot_truth$pair <- factor(spot_truth$pair, levels = intersect(pair_levels, spot_truth$pair))
spot_truth_n <- spot_truth %>%
  dplyr::group_by(pair) %>%
  dplyr::summarise(n = dplyr::n(), med = stats::median(tumor), .groups = "drop")
pD <- ggplot(spot_truth, aes(pair, tumor, fill = pair)) +
  geom_violin(width = 0.86, linewidth = 0.3, colour = "grey35", scale = "width") +
  geom_boxplot(width = 0.16, outlier.shape = NA, linewidth = 0.3, fill = "white") +
  geom_text(
    data = spot_truth_n, aes(pair, 1.06, label = sprintf("n=%d", n)),
    inherit.aes = FALSE, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_fill_manual(values = PAIR_COL, guide = "none") +
  scale_y_continuous(limits = c(0, 1.12), breaks = c(0, 0.25, 0.5, 0.75, 1)) +
  labs(x = "Donor pair", y = "Per-spot tumor truth") +
  theme_tme()
occupied <- mass
occupied$pair <- droplevels(occupied$pair)
occupied$occupied <- 100 * (1 - occupied$zero_rate)
pE <- ggplot(occupied, aes(type, occupied, fill = pair)) +
  geom_col(position = position_dodge(0.78), width = 0.70) +
  coord_flip() +
  scale_fill_manual(values = PAIR_COL, name = NULL) +
  scale_y_continuous(limits = c(0, 100), expand = expansion(mult = c(0, 0.02))) +
  labs(x = NULL, y = "Spots occupied (%)") +
  theme_tme()
pF <- ggplot(cards, aes(pair, approx_um)) +
  geom_col(fill = oi("sky"), width = 0.62) +
  geom_text(
    aes(label = sprintf("%.0f cells", median_cells)),
    vjust = -0.35, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.16))) +
  labs(x = "Donor pair", y = "Spot diameter (µm)") +
  theme_tme()
tme_save(collect_bottom((pA | pB | pC) / (pD | pE | pF)), "F2_hero", 11.0, 7.0, figdir)
## F2_hero end

sweep$substrate <- factor(pretty_substrate(sweep$substrate), levels = sub_levels)
boot$substrate <- factor(pretty_substrate(boot$substrate), levels = sub_levels)
fulln$substrate <- factor(pretty_substrate(fulln$substrate), levels = sub_levels)
refusal <- refusal[!is.na(refusal$substrate), ]
refusal$substrate <- factor(pretty_substrate(refusal$substrate), levels = sub_levels)
refusal$refused <- as_flag(refusal$refused)
sweep$decision <- ifelse(as_flag(sweep$abstain), "ABSTAIN", "KEEP")

## F7_dose start
# The manipulated variable is t; the bootstrap interval and the full-n point are
# the same t = 0 setting scored two other ways, so they belong on this axis.
dose_one <- function(sub) {
  d <- sweep[sweep$substrate == sub, ]
  b <- boot[boot$substrate == sub, ]
  fn <- fulln[fulln$substrate == sub, ]
  col <- unname(SUBSTRATE_COL[[sub]])
  ggplot(d, aes(t, tumor_rmse)) +
    abstain_layers(d) +
    geom_line(colour = col, linewidth = 0.7) +
    geom_point(colour = col, size = 1.8) +
    geom_errorbar(
      data = b, aes(x = 0, ymin = ci95_lo, ymax = ci95_hi),
      inherit.aes = FALSE, width = 0.045, linewidth = 0.5, colour = "grey20"
    ) +
    geom_point(
      data = fn, aes(x = 0, y = tumor_rmse),
      inherit.aes = FALSE, shape = 21, size = 2.5, stroke = 0.7,
      fill = "white", colour = "grey15"
    ) +
    scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.10))) +
    labs(x = "Interpolation fraction t", y = "Ungated tumor RMSE") +
    theme_tme()
}
# The cutoff is stated in cosine, so the gate decision is legible only when the
# same sweep is read in that coordinate.
gate_one <- function(sub, show_key = FALSE) {
  d <- sweep[sweep$substrate == sub, ]
  native <- d[d$t == min(d$t), ]
  ggplot(d, aes(cosine, tumor_rmse)) +
    annotate(
      "rect",
      xmin = 0.80, xmax = Inf, ymin = -Inf, ymax = Inf,
      fill = oi("verm"), alpha = 0.09
    ) +
    geom_vline(xintercept = 0.80, linetype = "22", linewidth = 0.45, colour = oi("verm")) +
    geom_path(
      colour = "grey55", linewidth = 0.5,
      arrow = arrow(length = unit(0.14, "cm"), type = "closed")
    ) +
    geom_point(aes(fill = decision), shape = 21, size = 2.3, stroke = 0.4, colour = "grey25") +
    geom_point(
      data = native, shape = 23, size = 3.0, stroke = 0.6,
      fill = "white", colour = "grey15"
    ) +
    # Only the panel that carries both calls draws the key; the other two would
    # emit a second copy of it with a half-empty glyph.
    scale_fill_manual(
      values = DECISION_COL, limits = names(DECISION_COL), drop = FALSE,
      name = NULL, guide = if (show_key) "legend" else "none"
    ) +
    scale_y_continuous(limits = c(0, NA), expand = expansion(mult = c(0, 0.12))) +
    labs(x = "Malignant\u2013neighbor cosine", y = "Tumor RMSE") +
    theme_tme()
}
tme_save(
  collect_bottom(
    (dose_one("openST") | dose_one("Xenium") | dose_one("CosMx")) /
      (gate_one("openST") | gate_one("Xenium") | gate_one("CosMx", show_key = TRUE))
  ),
  "F7_dose", 10.8, 7.0, figdir
)
## F7_dose end

## F10_eval start
eA <- ggplot(boot, aes(substrate, tumor_rmse, fill = substrate)) +
  geom_col(width = 0.62) +
  geom_errorbar(aes(ymin = ci95_lo, ymax = ci95_hi), width = 0.15) +
  scale_fill_manual(values = SUBSTRATE_COL, guide = "none") +
  labs(x = NULL, y = "t = 0 tumor RMSE") +
  theme_tme()
eB <- ggplot(fulln, aes(substrate, tumor_rmse, fill = substrate)) +
  geom_col(width = 0.62) +
  geom_text(
    aes(label = sprintf("n=%d", n_spots)),
    vjust = -0.35, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_fill_manual(values = SUBSTRATE_COL, guide = "none") +
  scale_y_continuous(expand = expansion(mult = c(0, 0.16))) +
  labs(x = NULL, y = "Full-n tumor RMSE") +
  theme_tme()
# One of these four edges is the recorded close rather than a computed transfer.
# Drawing all four in one colour reads as four results of the same kind.
eC_d <- donor[!is.na(donor$RMSE), ]
eC <- ggplot(eC_d, aes(pair, RMSE, fill = source)) +
  geom_col(width = 0.62) +
  geom_text(
    aes(label = sprintf("%.4f", RMSE)),
    vjust = -0.35, size = TME_VALUE_PT, family = TME_FONT
  ) +
  geom_text(
    data = eC_d[eC_d$source == "locked", ],
    aes(label = "locked"), y = 0, vjust = -0.9,
    size = TME_VALUE_PT, family = TME_FONT, colour = "white"
  ) +
  scale_fill_manual(
    values = c(computed = oi("blue"), locked = oi("orange")), guide = "none"
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = NULL, y = "Donor RMSE") +
  theme_tme()
timing <- timing[timing$step != "build_total", , drop = FALSE]
timing$step <- factor(pretty_step(timing$step), levels = rev(pretty_step(timing$step)))
# The self-gate is the largest stage of the current build, so on a shared
# vertical axis the other steps flatten. Laid on its side each step gets a
# full-width label and prints its own seconds.
eD <- ggplot(timing, aes(step, seconds)) +
  geom_col(fill = oi("orange"), width = 0.66) +
  geom_text(
    aes(label = ifelse(seconds >= 0.01, sprintf("%.2f s", seconds), "<0.01 s")),
    hjust = -0.12, size = TME_VALUE_PT, family = TME_FONT
  ) +
  coord_flip(clip = "off") +
  scale_y_continuous(expand = expansion(mult = c(0, 0.30))) +
  labs(x = NULL, y = "Seconds, one openST pass") +
  theme_tme()
# Distance to the cutoff, not the cosine itself: the cosine board is already the
# hero figure, and what the board needs is how much headroom each call has.
refuse$margin <- refuse$c_star - refuse$cosine
eE <- ggplot(refuse, aes(substrate, margin, fill = decision)) +
  geom_col(width = 0.62) +
  geom_hline(yintercept = 0, linewidth = 0.4, colour = "grey20") +
  geom_text(
    aes(label = sprintf("%+.2f", margin), vjust = ifelse(margin >= 0, -0.35, 1.25)),
    size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_fill_manual(values = DECISION_COL, name = NULL) +
  scale_y_continuous(expand = expansion(mult = c(0.18, 0.18))) +
  labs(x = NULL, y = "Cutoff margin") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))
# Pseudobulk agreement is the third score each computed edge carries; without it
# the board reads a whole-simplex RMSE with nothing to cross-check it.
eF <- ggplot(donor[!is.na(donor$pseudobulk_jsd), ], aes(pair, pseudobulk_jsd)) +
  geom_col(fill = oi("purple"), width = 0.62) +
  geom_text(
    aes(label = sprintf("%.4f", pseudobulk_jsd)),
    vjust = -0.35, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = NULL, y = "Pseudobulk JSD") +
  theme_tme()
# patchwork aligns axis titles down a column, so A's title was pushed out to
# clear the six step names on D and ended up floating a label's width from the
# axis it names. Freeing the label, not the space, moves A's title back against
# its own tick marks while both panels keep their shared left edge.
tme_save(
  collect_bottom(
    (patchwork::free(eA, type = "label", side = "l") | eB | eC) / (eD | eE | eF)
  ),
  "F10_eval", 11.2, 7.0, figdir
)
## F10_eval end
