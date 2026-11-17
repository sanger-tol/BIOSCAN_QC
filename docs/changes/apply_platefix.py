"""
Apply the plate-assignment fix to QCBioscan_rerun.Rmd (dev branch of sanger-tol/BIOSCAN_QC).

    python3 apply_platefix.py QCBioscan_rerun.Rmd            # edits the file in place
    python3 apply_platefix.py QCBioscan_rerun.Rmd out.Rmd    # writes a patched copy

Each edit must match the script exactly (the stated number of times) or nothing is written.
See docs/changes/plate_assignment_fix.md for what each edit does and why.
"""
import sys

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else src
t = open(src).read()
if "partner_plate_from_label" in t:
    sys.exit("Already patched: nothing to do.")


def sub(old, new, count=1):
    global t
    n = t.count(old)
    if n != count:
        sys.exit(f"Expected {count} match(es), found {n}; file left unchanged:\n{old[:120]!r}")
    t = t.replace(old, new)


# 1. Report title carries the batch (batch_no is exported by the run script before rendering)
sub('title: "BIOSCAN QC Report"',
    'title: "`r paste(\'BIOSCAN QC Report:\', Sys.getenv(\'batch_no\'))`"')

# 2. Plate boxplot colours: fixed order instead of a random shuffle on every run
sub('subgroup <- sample(pastel_colors_small)',
    'subgroup <- pastel_colors_small')

# 3. Stats table: real partner plate for random SQPP controls; flag internal lab controls;
#    write the plate given to every well
sub('''    partner_plate = str_extract(Label2, "^[^_]+_[^_]+"),
    plate_number = str_extract(Label2, "(?<=_)[^_]+(?=_)"),
    sample_type = ifelse(grepl("CONTROL", Label, ignore.case = TRUE), "control", "sample")
  )''', '''    partner_plate_from_label = str_extract(Label2, "^[^_]+_[^_]+"),
    # Random controls carry an SQPP code in their label (CONTROL_NEG_SQPP-100479-I_F9);
    # mBRAVE's Sample.Plate.ID gives their real partner plate (e.g. NHMG_270).
    partner_plate = ifelse(grepl("^SQPP", Label2) & grepl("^[A-Za-z]+_[0-9]+$", Sample.Plate.ID),
                           Sample.Plate.ID, partner_plate_from_label),
    plate_number = str_extract(Label2, "(?<=_)[^_]+(?=_)"),
    # Whole plates of lab controls (Group "DNAP CONTROLS") have no partner plate; flagged for reference
    internal_control = grepl("DNAP", Group, ignore.case = TRUE),
    sample_type = ifelse(grepl("CONTROL", Label, ignore.case = TRUE), "control", "sample")
  )
plate_lookup <- stats_table_comb %>% dplyr::select(Label, partner_plate, internal_control) %>%
  dplyr::distinct(Label, .keep_all = TRUE)
write.csv(stats_table_comb %>% dplyr::select(Label, Group, Sample.Plate.ID, partner_plate_from_label, partner_plate,
                                             plate_column, plate_row, internal_control, sample_type),
          file = paste(output_path, "plate_assignment_", batch_no, ".csv", sep = ""), row.names = FALSE)''')

# 4. Sequence table: the same real plate for SQPP controls, so the negative-control contamination
#    search compares them with the samples on their own plate. partner_group is used only for the
#    outline colour in the contamination heatmaps.
sub('qc_AM$Sample.Plate.ID <- paste(qc_AM$partner_plate, qc_AM$plate_number, sep = "_")',
    '''qc_AM$Sample.Plate.ID <- paste(qc_AM$partner_plate, qc_AM$plate_number, sep = "_")
sqpp_rows <- grepl("SQPP", qc_AM$pid) & qc_AM$pid %in% plate_lookup$Label
qc_AM$Sample.Plate.ID[sqpp_rows] <- plate_lookup$partner_plate[match(qc_AM$pid[sqpp_rows], plate_lookup$Label)]
qc_AM$partner_group <- qc_AM$partner_plate
qc_AM$partner_group[sqpp_rows] <- sub("_.*", "", qc_AM$Sample.Plate.ID[sqpp_rows])''')

# 5. Contamination heatmaps (partner and UMI): outline colour by partner, not by SQPP code
sub('aes(fill = rep_count_primary, color = partner_plate), linewidth = 1)',
    'aes(fill = rep_count_primary, color = partner_group), linewidth = 1)', count=2)

# 5b. partner_group is for the plots only: drop it before qc_AM feeds the sample tables and output CSVs
sub('qc_tsv_no_cont <- qc_AM %>% filter(!(str_detect(pid, "CONTROL")))',
    '''qc_AM$partner_group <- NULL  # plot-only column; keeps the output CSVs unchanged
qc_tsv_no_cont <- qc_AM %>% filter(!(str_detect(pid, "CONTROL")))''')

# (Whole plates of lab controls, Group "DNAP CONTROLS", stay in the per-plate heatmaps: they are
#  real 96-well blank plates, e.g. SQPP_42666-42669 in batch10. They are flagged in plate_assignment.)

# 6. Category heatmaps: skip plates with nothing to draw
sub('''    group_data <- statsDF %>% filter(Sample.Plate.ID == plate)
    plot <- ggplot(group_data''',
    '''    group_data <- statsDF %>% filter(Sample.Plate.ID == plate)
    if (nrow(group_data) == 0) next
    plot <- ggplot(group_data''')

open(dst, "w").write(t)
print(f"Patched: {dst}")
