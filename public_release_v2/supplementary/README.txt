SPGD-TME Supplementary Material
===============================

Two locked operators report mixed-spot TME composition on CosMx carcinomas

This bundle is the material the Data availability statement names. It holds every
number the figures and tables plot, the frozen constants those numbers were
produced under, and the scripts that turn one into the other. It holds no
sequencing data: the libraries are public and are cited by repository accession in
the manuscript, and the reference matrices they yield are named here by content
hash rather than redistributed under their source licences.

Contents
--------

  plotdata/    one table per panel; the values the figures and tables plot
  locks/       the constants frozen before any sweep, and the input hashes
  render/      the scripts that draw every figure and write every table body
  SHA256SUMS.txt

Reproducing a figure or a table
-------------------------------

Run these from the directory this file sits in. Nothing outside the bundle is
needed and nothing outside it is written.

  Figures 2-11   Rscript render/render_disk_faces.R
  Figure 12      Rscript render/render_F12_keep.R
                 both read plotdata/ and write one PDF and one PNG per figure
                 into figures/
  Figure 1       drawn in the manuscript source as a TikZ picture, not from data
  Tables 1-3     python3 render/generate_tables.py
                 reads plotdata/T1_materials.csv, T2_timing.csv and
                 T3_donor_matrix.csv, writes the TeX table bodies into tables/

R needs ggplot2, patchwork, dplyr, tidyr, ragg and Cairo.

Locks
-----

  locks/c_star.json             the frozen malignant-neighbour cosine cutoff
  locks/type_pairs.json         the malignant-neighbour type pair per substrate
  locks/cd_lock.json            the donor split
  locks/f6_protocol.json        the reportability protocol constants
  locks/donor_pair_STATUS.json  which donor pairs were built, and from what
  locks/materials_sha256.tsv    SHA-256 of every locked input, keyed by the name
                                Table 1 prints for it

Where each file belongs
-----------------------

The render reads plotdata/ as one set, so no file is private to one figure. The
prefix below is the stage that emitted the file, and for tables it is also the
printed table number. For figures it is not: the stages were numbered as they
were written and the figures were renumbered afterwards, so F9_type_floor.csv is
the reference floor that prints as Figure 11 and F10_myeloid_occupancy.csv is the
myeloid axis that prints as Figure 9. To go from a printed panel to its numbers,
run the commands above and read figures/ beside the submitted figure.

  Emit stage F2
    plotdata/F2D_A_from_B_truth_maps.csv
    plotdata/F2D_B_from_A_truth_maps.csv
    plotdata/F2_condition_cell_summary.csv
    plotdata/F2_donor_edges.csv
    plotdata/F2_native_refuse.csv
    plotdata/F2_pair_cards.csv
    plotdata/F2_truth_mass.csv
    plotdata/F2_xenium_flex_cosine.csv
  Emit stage F3
    plotdata/F3_collinearity_sweep.csv
    plotdata/F3_fulln_part_cosmx.csv
    plotdata/F3_fulln_part_openst.csv
    plotdata/F3_fulln_part_xenium.csv
    plotdata/F3_part_cosmx.csv
    plotdata/F3_part_openst.csv
    plotdata/F3_part_xenium.csv
    plotdata/F3_pi_fulln_cosmx.csv
    plotdata/F3_pi_t0_cosmx.csv
    plotdata/F3_pi_t0_openst.csv
    plotdata/F3_pi_t0_xenium.csv
    plotdata/F3_t0_bootstrap.csv
    plotdata/F3_t0_fulln.csv
  Emit stage F4
    plotdata/F4_keep_spatial.csv
    plotdata/F4_keep_spatial_fulln.csv
    plotdata/F4_keep_spatial_fulln_compare.csv
    plotdata/F4_keep_spatial_fulln_summary.csv
    plotdata/F4_keep_spatial_summary.csv
    plotdata/F4_refusal.csv
  Emit stage F5
    plotdata/F5_donor_transfer.csv
    plotdata/F5_part_A_from_B.csv
    plotdata/F5_part_B_from_A.csv
    plotdata/F5_part_D_from_C.csv
  Emit stage F9
    plotdata/F9_D_from_C_spot_condition.csv
    plotdata/F9_D_from_C_truth_maps.csv
    plotdata/F9_condition_occupancy.csv
    plotdata/F9_condition_spot_truth.csv
    plotdata/F9_type_floor.csv
  Emit stage F10
    plotdata/F10_myeloid_occupancy.csv
  Emit stage F12
    plotdata/F12_crc_cosine_probe.json
    plotdata/F12_donor_rmse.csv
    plotdata/F12_he_liver_cosine_probe.json
    plotdata/F12_he_nsclc_cosine_probe.json
    plotdata/F12_he_nsclc_t0_donor.json
    plotdata/F12_keep_cosine.csv
    plotdata/F12_neighbor_scan.csv
    plotdata/F12_pdac_cosine_probe.json
  Table 1
    plotdata/T1_materials.csv
  Table 2
    plotdata/T2_timing.csv
  Table 3
    plotdata/T3_donor_matrix.csv
  Shared inputs
    plotdata/cells_spatial.csv.gz
    plotdata/timing_probe.csv
    plotdata/timing_probe_three_substrates.csv
