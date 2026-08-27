# Independent KEEP-carcinoma board. Run from the SPGD-TME workbench root.
root <- normalizePath(file.path(getwd()))
if (!file.exists(file.path(root, "FIGURES.md"))) {
  stop("run from the SPGD-TME workbench root", call. = FALSE)
}
source(file.path(root, "manuscript/scripts/R/theme_tme.R"))
suppressMessages({
  library(ggplot2)
  library(patchwork)
  library(dplyr)
})

plotdir <- file.path(root, "data/plotdata")
figdir <- file.path(root, "manuscript/figs/rendered")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

cos <- read.csv(file.path(plotdir, "F12_keep_cosine.csv"), stringsAsFactors = FALSE)
don <- read.csv(file.path(plotdir, "F12_donor_rmse.csv"), stringsAsFactors = FALSE)
cos$decision <- factor(cos$decision, levels = c("ABSTAIN", "KEEP"))
keep_order <- unique(cos$substrate)
cos$substrate <- factor(cos$substrate, levels = keep_order)
don$edge <- factor(don$edge, levels = don$edge)
tag_theme <- theme(plot.tag = element_text(size = 12, family = TME_FONT, face = "bold"))

pA <- ggplot(cos, aes(substrate, cosine, fill = decision)) +
  geom_col(width = 0.62) +
  geom_hline(yintercept = 0.80, linewidth = 0.45, linetype = "22") +
  scale_fill_manual(values = c(ABSTAIN = oi("verm"), KEEP = oi("green"))) +
  scale_y_continuous(limits = c(0, 1.05), expand = expansion(mult = c(0, 0))) +
  labs(x = "Library", y = "Locked cosine") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

pB <- ggplot(cos, aes(decision, fill = decision)) +
  geom_bar(width = 0.55) +
  scale_fill_manual(values = c(ABSTAIN = oi("verm"), KEEP = oi("green")), guide = "none") +
  labs(x = "Native call", y = "Libraries") +
  theme_tme()

pC <- ggplot(don, aes(edge, overall_rmse)) +
  geom_col(fill = oi("blue"), width = 0.62) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.08))) +
  labs(x = "Directed edge", y = "Overall RMSE") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

pD <- ggplot(don, aes(edge, spot_pcc)) +
  geom_col(fill = oi("green"), width = 0.62) +
  scale_y_continuous(limits = c(0, 1.05), expand = expansion(mult = c(0, 0))) +
  labs(x = "Directed edge", y = "Spot-level PCC") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

pE <- ggplot(don, aes(edge, n_spots)) +
  geom_col(fill = oi("sky"), width = 0.62) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.08))) +
  labs(x = "Directed edge", y = "Spots") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

keep_only <- cos[cos$decision == "KEEP", ]
pF <- ggplot(keep_only, aes(substrate, cosine)) +
  geom_col(fill = oi("green"), width = 0.62) +
  geom_hline(yintercept = 0.80, linewidth = 0.45, linetype = "22") +
  scale_y_continuous(limits = c(0, 1.05), expand = expansion(mult = c(0, 0))) +
  labs(x = "KEEP carcinoma", y = "Locked cosine") +
  theme_tme() +
  theme(axis.text.x = element_text(angle = 28, hjust = 1))

tme_save(
  (pA | pB | pC) / (pD | pE | pF) + plot_annotation(tag_levels = "A") & tag_theme,
  "F12_keep", 11.2, 6.8, figdir
)
