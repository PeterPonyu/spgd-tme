# Draws Figure 12 of SPGD-TME, the independent KEEP-carcinoma board, from plotdata/.
# Rebound for the Supplementary bundle: scripts in render/, tables in
# plotdata/, output in figures/.
.args <- commandArgs(trailingOnly = FALSE)
.here <- dirname(normalizePath(sub("^--file=", "", .args[grep("^--file=", .args)])[1]))
root <- dirname(.here)
source(file.path(.here, "theme_tme.R"))
suppressMessages({
  library(ggplot2)
  library(patchwork)
  library(dplyr)
})

plotdir <- file.path(root, "plotdata")
figdir <- file.path(root, "figures")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

cos <- read.csv(file.path(plotdir, "F12_keep_cosine.csv"), stringsAsFactors = FALSE)
don <- read.csv(file.path(plotdir, "F12_donor_rmse.csv"), stringsAsFactors = FALSE)
scan <- read.csv(file.path(plotdir, "F12_neighbor_scan.csv"), stringsAsFactors = FALSE)
cos$decision <- factor(cos$decision, levels = c("ABSTAIN", "KEEP"))
keep_order <- unique(cos$substrate)
cos$substrate <- factor(cos$substrate, levels = keep_order)
don$edge <- factor(don$edge, levels = don$edge)
scan_order <- intersect(keep_order, unique(scan$library))
scan$library <- factor(scan$library, levels = scan_order)
scan$decision <- factor(scan$decision, levels = c("ABSTAIN", "KEEP"))
scan$designated <- as_flag(scan$designated)
tag_theme <- theme(plot.tag = element_text(size = TME_TAG_PT, family = TME_FONT, face = "bold"))

pA <- ggplot(cos, aes(substrate, cosine, fill = decision)) +
  geom_col(width = 0.62) +
  geom_hline(yintercept = 0.80, linewidth = 0.45, linetype = "22") +
  geom_text(
    aes(label = sprintf("%.3f", cosine)),
    vjust = -0.4, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_fill_manual(values = DECISION_COL, name = NULL) +
  scale_y_continuous(limits = c(0, 1.14), breaks = c(0, 0.25, 0.5, 0.75, 1), expand = expansion(mult = c(0, 0))) +
  labs(x = "Library", y = "Locked cosine") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

# One reported cosine summarises a whole neighborhood. Showing the scan is what
# separates a library whose malignant program is separable from most of its
# types from one where it is collinear with all of them.
pB <- ggplot(scan, aes(library, cosine)) +
  annotate(
    "rect",
    xmin = -Inf, xmax = Inf, ymin = 0.80, ymax = Inf,
    fill = oi("verm"), alpha = 0.09
  ) +
  geom_hline(yintercept = 0.80, linewidth = 0.45, linetype = "22") +
  # Seeded: an unseeded jitter redraws the scan differently on every render, so
  # the figure in the PDF would stop matching the one a rerun produces.
  geom_point(
    aes(fill = decision),
    position = position_jitter(width = 0.16, height = 0, seed = 20260827),
    size = 1.7, shape = 21, stroke = 0.2,
    colour = "grey25", alpha = 0.85
  ) +
  geom_point(
    data = scan[scan$designated, ],
    shape = 23, size = 2.6, stroke = 0.6, fill = "white", colour = "grey15"
  ) +
  # Same key as the collected bar legend; a second copy with a point glyph would
  # only repeat it.
  scale_fill_manual(values = DECISION_COL, guide = "none") +
  scale_y_continuous(limits = c(0, 1.0), breaks = c(0, 0.25, 0.5, 0.75, 1)) +
  labs(x = "Library", y = "Malignant\u2013neighbor cosine") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

pC <- ggplot(don, aes(edge, overall_rmse)) +
  geom_col(fill = oi("blue"), width = 0.62) +
  geom_text(
    aes(label = sprintf("%.4f", overall_rmse)),
    vjust = -0.35, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = "Directed edge", y = "Overall RMSE") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

pD <- ggplot(don, aes(edge, spot_pcc)) +
  geom_col(fill = oi("green"), width = 0.62) +
  geom_text(
    aes(label = sprintf("%.4f", spot_pcc)),
    vjust = 1.5, size = TME_VALUE_PT, family = TME_FONT, colour = "white"
  ) +
  scale_y_continuous(limits = c(0, 1.05), expand = expansion(mult = c(0, 0))) +
  labs(x = "Directed edge", y = "Spot-level PCC") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

pE <- ggplot(don, aes(edge, n_spots)) +
  geom_col(fill = oi("sky"), width = 0.62) +
  geom_text(
    aes(label = n_spots),
    vjust = -0.35, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.18))) +
  labs(x = "Directed edge", y = "Spots") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

refused_share <- scan %>%
  dplyr::group_by(library) %>%
  dplyr::summarise(
    n_neighbors = dplyr::n(),
    n_refused = sum(decision == "ABSTAIN"),
    share = 100 * n_refused / n_neighbors,
    call = dplyr::first(library_decision),
    .groups = "drop"
  )
pF <- ggplot(refused_share, aes(library, share, fill = call)) +
  geom_col(width = 0.62) +
  geom_text(
    aes(label = sprintf("%d/%d", n_refused, n_neighbors)),
    vjust = -0.35, size = TME_VALUE_PT, family = TME_FONT
  ) +
  scale_fill_manual(values = DECISION_COL, name = NULL) +
  scale_y_continuous(limits = c(0, 118), breaks = c(0, 50, 100), expand = expansion(mult = c(0, 0))) +
  labs(x = "Library", y = "Neighbors at or above cutoff (%)") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

tme_save(
  (pA | pB | pC) / (pD | pE | pF) +
    patchwork::plot_layout(guides = "collect") +
    plot_annotation(tag_levels = "A") &
    tag_theme &
    theme(legend.position = "bottom", legend.justification = "center"),
  "F12_keep", 11.2, 7.0, figdir
)
