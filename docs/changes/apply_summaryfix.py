"""
Fix the summary text and tables in the QC HTML report (QCBioscan_rerun.Rmd, dev branch).

    python3 apply_summaryfix.py QCBioscan_rerun.Rmd            # edits the file in place
    python3 apply_summaryfix.py QCBioscan_rerun.Rmd out.Rmd    # writes a patched copy

Each edit must match the script exactly (the stated number of times) or nothing is written.
Only the HTML report changes; no output CSV is affected.
See docs/changes/report_summary_fix.md.
"""
import re
import sys

src = sys.argv[1]
dst = sys.argv[2] if len(sys.argv) > 2 else src
t = open(src).read()
if "list_or_none <- function" in t:
    sys.exit("Already patched: nothing to do.")


def sub(old, new, count=1):
    # line ends may carry trailing spaces in the Rmd: allow them when matching
    global t
    pat = re.compile("[ \t]*\n".join(re.escape(x) for x in old.split("\n")))
    n = len(pat.findall(t))
    if n != count:
        sys.exit(f"Expected {count} match(es), found {n}; file left unchanged:\n{old[:160]!r}")
    t = pat.sub(lambda m: new, t)


# 0. Helpers used by the fixes below
sub('batch_no <- env_list$batch_no\n',
    '''batch_no <- env_list$batch_no

# Report helpers: "none" for an empty list, 0 for a missing count
list_or_none <- function(x, sep = ", ") { x <- x[!is.na(x)]; if (length(x) == 0) "none" else paste(x, collapse = sep) }
zero_if_na <- function(x) { x <- unname(x); if (length(x) == 0 || is.na(x)) 0 else x }
''')

# 1. Category summary table: count category, description and decision together.
#    The old code tallied categories and descriptions separately and joined the two tallies on the
#    COUNT (merge(..., by = "Freq")), so categories with the same number of specimens were crossed
#    and duplicated (batch43_0: categories 5/12 and 10/11).
# 2. Use the decision names used everywhere else: PASS (stored as YES in the CSVs) and ON_HOLD (was "NO").
# 3. Replace the two "% OF SAMPLES EXCLUDED" lines with counts and percentages that say what they are.
sub('''summary1 <- table(qc_tsv_arthropod_primary$category) %>% as.data.frame()
summary2 <- table(qc_tsv_arthropod_primary$category_explanation) %>% as.data.frame()
summary_merge <- merge(summary2,summary1, by = "Freq")
summary_merge <- summary_merge %>%
  mutate(Decision = case_when(
    Var1.y %in% c(1:8) ~ "YES",
    Var1.y %in% c(9:12) ~ "NO",
    Var1.y == 13 ~ "no_category"
  ))
colnames(summary_merge) <- c("Number of samples", "Description", "Category", "Decision")
''', '''# One row per category: count category, description and decision together
decision_label <- function(x) dplyr::recode(x, "YES" = "PASS", .default = x)  # CSVs keep "YES"
summary_merge <- qc_tsv_arthropod_primary %>%
  dplyr::ungroup() %>%  # the table is still grouped by pid from an earlier step
  dplyr::count(category, category_explanation, category_decision) %>%
  dplyr::mutate(category_decision = decision_label(category_decision)) %>%
  dplyr::select(n, category_explanation, category, category_decision)
colnames(summary_merge) <- c("Number of samples", "Description", "Category", "Decision")
''')

sub('''knitr::kable(table(qc_tsv_arthropod_primary$category_decision) %>% as.data.frame(),
             col.names = c("Decision category", "Number of samples"), format = "html") %>%''',
    '''knitr::kable(qc_tsv_arthropod_primary %>% dplyr::ungroup() %>% dplyr::count(Decision = decision_label(category_decision)),
             col.names = c("Decision", "Number of samples"), format = "html") %>%''')

sub('''cat(paste(100-(nrow(qc_tsv_arthropod_primary)*100/total_sample_number), "% OF SAMPLES EXCLUDED [all samples]"))
cat(paste(100-(nrow((qc_tsv_arthropod_primary %>% filter(category_decision == "YES")))*100/total_sample_number), "% OF SAMPLES EXCLUDED [only approved samples]"))''',
    '''n_retained <- nrow(qc_tsv_arthropod_primary)
n_pass <- nrow(qc_tsv_arthropod_primary %>% filter(category_decision == "YES"))
pct <- function(x) paste0(round(100 * x / total_sample_number, 1), "%")
cat(paste0("Samples in this batch (excluding controls): ", total_sample_number,
           "\\nGiven a category: ", n_retained, " (", pct(n_retained), ")",
           "\\n    PASS: ", n_pass, " (", pct(n_pass), ")",
           "\\n    ON_HOLD: ", n_retained - n_pass, " (", pct(n_retained - n_pass), ")",
           "\\nNot given a category (FAILED or EXCLUDED earlier in the QC): ",
           total_sample_number - n_retained, " (", pct(total_sample_number - n_retained), ")\\n"))''')

# 4. "none" / 0 instead of empty lists, NA and NaN
sub('''      "\\nPlates:", paste(c(empty_n_cont %>% filter(Count > 29) %>% pull(Sample.Plate.ID),
                           lysate_n_cont %>% filter(Count > 29) %>% pull(Sample.Plate.ID)), collapse = ", ")''',
    '''      "\\nPlates:", list_or_none(c(empty_n_cont %>% filter(Count > 29) %>% pull(Sample.Plate.ID),
                           lysate_n_cont %>% filter(Count > 29) %>% pull(Sample.Plate.ID)))''')

sub('''cat(paste("Plates where the 75th percentile of the data is lower than expected mean read count (dark grey):\\n\\n", paste(low_read_plates, collapse = "\\n"),"\\n"),''',
    '''cat(paste("Plates where the 75th percentile of the data is lower than expected mean read count (dark grey):\\n\\n", list_or_none(low_read_plates, sep = "\\n"),"\\n"),''')

sub('''    paste("\\n\\nPlates where all samples have 0 reads:", paste(sample_stats %>%
  dplyr::group_by(Sample.Plate.ID) %>%
  dplyr::filter(all(Count == 0)) %>%
  dplyr::pull(Sample.Plate.ID) %>%
  unique(), collapse = ", "),
  "Plates where all samples have 5 of fewer reads:", paste(sample_stats %>%
  dplyr::group_by(Sample.Plate.ID) %>%
  dplyr::filter(all(Count < 5)) %>%
  dplyr::pull(Sample.Plate.ID) %>%
  unique(), collapse = ", ")''',
    '''    paste("\\n\\nPlates where all samples have 0 reads:", list_or_none(sample_stats %>%
  dplyr::group_by(Sample.Plate.ID) %>%
  dplyr::filter(all(Count == 0)) %>%
  dplyr::pull(Sample.Plate.ID) %>%
  unique()),
  "\\nPlates where all samples have fewer than 5 reads:", list_or_none(sample_stats %>%
  dplyr::group_by(Sample.Plate.ID) %>%
  dplyr::filter(all(Count < 5)) %>%
  dplyr::pull(Sample.Plate.ID) %>%
  unique())''')

sub('''  paste("Plates where the 75th percentile of the data is lower than expected mean read count (dark grey):", paste(low_read_UMI, collapse = ", ")),''',
    '''  paste("Plates where the 75th percentile of the data is lower than expected mean read count (dark grey):", list_or_none(low_read_UMI)),''')

sub('''cat(paste("Number of samples with positive control OTU as primary sequence:", p_cont_contamination_tab["primary"]),
    paste("\\nNumber of samples with positive control OTU as secondary sequence:", p_cont_contamination_tab["secondary"]),''',
    '''cat(paste("Number of samples with positive control OTU as primary sequence:", zero_if_na(p_cont_contamination_tab["primary"])),
    paste("\\nNumber of samples with positive control OTU as secondary sequence:", zero_if_na(p_cont_contamination_tab["secondary"])),''')

none_pc = '"none (no positive control sequences found in other samples)"'
sub('''"\\nRead count mean of all positive control sequences in other samples:", mean(p_cont_contamination$rep_count_primary),''',
    f'''"\\nRead count mean of all positive control sequences in other samples:", if (nrow(p_cont_contamination) == 0) {none_pc} else mean(p_cont_contamination$rep_count_primary),''')
sub('''"\\nRead count median of all positive control sequences in other samples:", median(p_cont_contamination$rep_count_primary)''',
    f'''"\\nRead count median of all positive control sequences in other samples:", if (nrow(p_cont_contamination) == 0) {none_pc} else median(p_cont_contamination$rep_count_primary)''')

open(dst, "w").write(t)
print(f"Patched: {dst}")
