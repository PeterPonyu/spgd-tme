# Non-spatial data faces. Assumes plot tables and helpers are in the parent frame.

pA <- ggplot(cards, aes(pair, n_spots)) +
  geom_col(fill = oi("blue"), width = 0.62) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.08))) +
  labs(x = "Donor pair", y = "Spots") +
  theme_tme()
pB <- ggplot(mass, aes(type, pair, fill = mean)) +
  geom_tile(colour = "white", linewidth = 0.3) +
  scale_fill_gradient(low = "white", high = oi("verm"), name = NULL) +
  labs(x = "Type", y = "Pair") +
  theme_tme() +
  theme(
    axis.text.x = element_text(angle = 35, hjust = 1),
    legend.position = "right",
    legend.direction = "vertical",
    panel.grid.major = element_blank()
  )
pC <- ggplot(refuse, aes(substrate, cosine, fill = decision)) +
  geom_col(width = 0.62) +
  geom_hline(yintercept = 0.80, linewidth = 0.45, linetype = "22") +
  scale_fill_manual(values = c(ABSTAIN = oi("verm"), KEEP = oi("green"))) +
  scale_y_continuous(limits = c(0, 1.05), expand = expansion(mult = c(0, 0))) +
  labs(x = "Substrate", y = "Locked cosine") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))
pD <- ggplot(edge_available, aes(pair, as.numeric(n_spots))) +
  geom_col(fill = oi("blue"), width = 0.62) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.12))) +
  labs(x = "Directed edge", y = "Spots") +
  theme_tme()
pE <- ggplot(refuse, aes(decision, fill = decision)) +
  geom_bar(width = 0.55) +
  scale_fill_manual(values = c(ABSTAIN = oi("verm"), KEEP = oi("green")), guide = "none") +
  labs(x = "Native call", y = "Substrates") +
  theme_tme()
pF <- ggplot(cards, aes(pair, approx_um)) +
  geom_col(fill = oi("sky"), width = 0.62) +
  labs(x = "Donor pair", y = "Spot diameter (µm)") +
  theme_tme()
tme_save((pA | pB | pC) / (pD | pE | pF) + plot_annotation(tag_levels = "A") & tag_theme, "F2_hero", 11.0, 6.6, figdir)

sweep$substrate <- factor(pretty_substrate(sweep$substrate), levels = sub_levels)
boot$substrate <- factor(pretty_substrate(boot$substrate), levels = sub_levels)
fulln$substrate <- factor(pretty_substrate(fulln$substrate), levels = sub_levels)
refusal <- refusal[!is.na(refusal$substrate), ]
refusal$substrate <- factor(pretty_substrate(refusal$substrate), levels = sub_levels)
refusal$refused <- as_flag(refusal$refused)
dose_one <- function(sub) {
  ggplot(sweep[sweep$substrate == sub, ], aes(t, tumor_rmse)) +
    geom_line(colour = unname(SUBSTRATE_COL[[sub]]), linewidth = 0.7) +
    geom_point(colour = unname(SUBSTRATE_COL[[sub]]), size = 1.8) +
    labs(x = "t", y = "Ungated RMSE") +
    theme_tme()
}
ref_one <- function(sub) {
  d <- refusal[refusal$substrate == sub, ]
  k <- d[!d$refused, ]
  ggplot(d, aes(t, rmse_gate_off)) +
    geom_line(colour = oi("grey"), linewidth = 0.65) +
    geom_point(colour = oi("grey"), size = 1.6) +
    geom_point(
      data = k, aes(t, rmse_gate_on), shape = 21, size = 2.6, stroke = 0.8,
      fill = "white", colour = oi("green"), inherit.aes = FALSE
    ) +
    labs(x = "t", y = "Tumor RMSE") +
    theme_tme()
}
tme_save(
  (dose_one("openST") | dose_one("Xenium") | dose_one("CosMx")) /
    (ref_one("openST") | ref_one("Xenium") | ref_one("CosMx")) +
    plot_annotation(tag_levels = "A") & tag_theme,
  "F7_dose", 10.8, 6.8, figdir
)

boot$substrate <- factor(pretty_substrate(boot$substrate), levels = sub_levels)
fulln$substrate <- factor(pretty_substrate(fulln$substrate), levels = sub_levels)
eA <- ggplot(boot, aes(substrate, tumor_rmse, fill = substrate)) +
  geom_col(width = 0.62) +
  geom_errorbar(aes(ymin = ci95_lo, ymax = ci95_hi), width = 0.15) +
  scale_fill_manual(values = SUBSTRATE_COL, guide = "none") +
  labs(x = NULL, y = "t = 0 tumor RMSE") +
  theme_tme()
eB <- ggplot(fulln, aes(substrate, tumor_rmse, fill = substrate)) +
  geom_col(width = 0.62) +
  scale_fill_manual(values = SUBSTRATE_COL, guide = "none") +
  labs(x = NULL, y = "Full-n tumor RMSE") +
  theme_tme()
eC <- ggplot(donor[!is.na(donor$RMSE), ], aes(pair, RMSE)) +
  geom_col(fill = oi("blue"), width = 0.62) +
  labs(x = NULL, y = "Donor RMSE") +
  theme_tme()
timing$step <- factor(timing$step, levels = timing$step)
eD <- ggplot(timing, aes(step, seconds)) +
  geom_col(fill = oi("orange"), width = 0.62) +
  labs(x = NULL, y = "Seconds") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))
eE <- ggplot(refuse, aes(substrate, cosine)) +
  geom_col(aes(fill = decision), width = 0.62) +
  geom_hline(yintercept = 0.80, linetype = "22") +
  scale_fill_manual(values = c(ABSTAIN = oi("verm"), KEEP = oi("green"))) +
  labs(x = NULL, y = "Native cosine") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))
eF <- ggplot(cards, aes(pair, n_spots)) +
  geom_col(fill = oi("sky"), width = 0.62) +
  labs(x = NULL, y = "Spots") +
  theme_tme()
tme_save((eA | eB | eC) / (eD | eE | eF) + plot_annotation(tag_levels = "A") & tag_theme, "F10_eval", 11.2, 6.8, figdir)
