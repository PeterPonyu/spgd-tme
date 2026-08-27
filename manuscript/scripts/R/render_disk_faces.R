# RTX orchestrator. Run from the SPGD-TME workbench root.
# Spatial geometry lives in spatial_geom.R. Metric and spatial faces are split.

root <- normalizePath(file.path(getwd()))
if (!file.exists(file.path(root, "FIGURES.md"))) {
  stop("run from the SPGD-TME workbench root", call. = FALSE)
}
source(file.path(root, "manuscript/scripts/R/theme_tme.R"))
source(file.path(root, "manuscript/scripts/R/spatial_geom.R"))

suppressMessages({
  library(ggplot2)
  library(patchwork)
  library(dplyr)
  library(tidyr)
})

plotdir <- file.path(root, "data/plotdata")
figdir <- file.path(root, "manuscript/figs/rendered")
dir.create(figdir, recursive = TRUE, showWarnings = FALSE)

pair_levels <- c("A from B", "B from A", "C from D", "D from C")
sub_levels <- c("openST", "Xenium", "CosMx")
refuse_levels <- c("openST", "Xenium", "Xenium FLEX", "CosMx")

cards <- read.csv(file.path(plotdir, "F2_pair_cards.csv"), stringsAsFactors = FALSE)
mass <- read.csv(file.path(plotdir, "F2_truth_mass.csv"), stringsAsFactors = FALSE)
refuse <- read.csv(file.path(plotdir, "F2_native_refuse.csv"), stringsAsFactors = FALSE)
orth <- read.csv(file.path(plotdir, "F2_realgt2_cosine.csv"), stringsAsFactors = FALSE)
orth <- orth[, c("substrate", "malignant", "neighbor", "cosine", "c_star", "decision")]
refuse <- rbind(refuse, orth)
edges <- read.csv(file.path(plotdir, "F2_donor_edges.csv"), stringsAsFactors = FALSE)
maps_a <- read.csv(file.path(plotdir, "F2D_A_from_B_truth_maps.csv"), stringsAsFactors = FALSE)
maps_b <- read.csv(file.path(plotdir, "F2D_B_from_A_truth_maps.csv"), stringsAsFactors = FALSE)
maps_d <- read.csv(file.path(plotdir, "F9_D_from_C_truth_maps.csv"), stringsAsFactors = FALSE)
floor <- read.csv(file.path(plotdir, "F9_type_floor.csv"), stringsAsFactors = FALSE)
cond_spots <- read.csv(file.path(plotdir, "F9_condition_spot_truth.csv"), stringsAsFactors = FALSE)
spot_cond <- read.csv(file.path(plotdir, "F9_D_from_C_spot_condition.csv"), stringsAsFactors = FALSE)
cell_occ <- read.csv(file.path(plotdir, "F9_condition_occupancy.csv"), stringsAsFactors = FALSE)
myelo <- read.csv(file.path(plotdir, "F10_myeloid_occupancy.csv"), stringsAsFactors = FALSE)
sweep <- read.csv(file.path(plotdir, "F3_collinearity_sweep.csv"), stringsAsFactors = FALSE)
boot <- read.csv(file.path(plotdir, "F3_t0_bootstrap.csv"), stringsAsFactors = FALSE)
fulln <- read.csv(file.path(plotdir, "F3_t0_fulln.csv"), stringsAsFactors = FALSE)
refusal <- read.csv(file.path(plotdir, "F4_refusal.csv"), stringsAsFactors = FALSE)
donor <- read.csv(file.path(plotdir, "F5_donor_transfer.csv"), stringsAsFactors = FALSE)
keep_cmp <- read.csv(file.path(plotdir, "F4_keep_spatial_fulln_compare.csv"), stringsAsFactors = FALSE)
cells <- read.csv(gzfile(file.path(plotdir, "cells_spatial.csv.gz")), stringsAsFactors = FALSE)
cell_sum <- read.csv(file.path(plotdir, "F2_condition_cell_summary.csv"), stringsAsFactors = FALSE)
timing <- read.csv(file.path(plotdir, "T2_timing.csv"), stringsAsFactors = FALSE)

cards$pair <- factor(pretty_pair(cards$pair), levels = pair_levels)
mass$pair <- factor(pretty_pair(mass$pair), levels = pair_levels)
mass$type <- factor(pretty_type(mass$type), levels = unique(pretty_type(mass$type)))
refuse$substrate <- factor(pretty_substrate(refuse$substrate), levels = refuse_levels)
refuse$decision <- factor(refuse$decision, levels = c("ABSTAIN", "KEEP"))
edges$pair <- factor(pretty_pair(edges$pair), levels = pair_levels)
edge_available <- edges[!is.na(as.numeric(edges$n_spots)) & edges$source == "q1_truth", ]
donor$pair <- factor(pretty_pair(donor$pair), levels = pair_levels)

tag_theme <- theme(plot.tag = element_text(size = TME_TAG_PT, family = TME_FONT, face = "bold"))

if (!identical(Sys.getenv("TME_RENDER_ONLY"), "F11")) {
  source(file.path(root, "manuscript/scripts/R/render_metric_faces.R"))
}
source(file.path(root, "manuscript/scripts/R/render_spatial_faces.R"))
