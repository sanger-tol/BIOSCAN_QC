# Changelog

## Unreleased (branch `dev`, to become version 3.0)

Changes to `QCBioscan_rerun.Rmd`, the script used for the February 2026 rerun (`qc_reports_rerun_Feb2026`).

### Done

- Synced with the copy run on the farm (colour palette for up to 20 partners in the plots).
- **Category 8 restored.** The salvage step looked for `category_decision == "NO"`, but categories 9–12 have been labelled `"ON_HOLD"` since V1, so no specimen was ever salvaged to category 8. It now looks for `"ON_HOLD"`.
- **Report card wording.** Categories 4 and 5 were written as "A single sequence present", although they have minor secondary sequences; they now use the same wording as categories 6 and 7. Category 8 uses the wording already on the portal ("Multiple sequences present but all differ by <2%; one sequence is dominant (>50 reads)").

- **Category 3 includes 5 reads** (`>= 5`), as README Table 1 always said; a single sequence with exactly 5 reads was falling into category 11 (ON_HOLD). Category 9 uses `> 5` like category 10. Rule: a sequence needs 5 or more reads to count; a secondary with 5 or fewer reads is minor.
- **Wording:** "5 or fewer reads" for minor secondaries (categories 4–7, explanations and report card); "5 to 49 reads" for low reads; categories 11 and 12 described as the code assigns them.
- **README:** spelling fixed; section 1.6 refers to the positive control; Table 1 rewritten with ON_HOLD (9–12), FAILED (13–15) and EXCLUDED (16) and their report card descriptions.
- **Random controls on their real plates.** Controls labelled with an SQPP code (`CONTROL_NEG_SQPP-83235-A_E1`) now get their partner plate from mBRAVE's `Sample Plate ID`. This removes the fake one-well "SQPP" plates and the gaps they left in the plate heatmaps, and the negative-control contamination search now compares these controls with the samples on their own plate. Whole plates of lab negative controls (DNAP CONTROLS) are still drawn, as before. Each run writes `plate_assignment_<batch>.csv`. QC outputs unchanged (all CSVs identical on batch43_0). Details and before/after figures: `docs/changes/plate_assignment_fix.md`.
- **Report labelled with the batch.** The title is "BIOSCAN QC Report: <batch>". Run scripts should pass `output_file = paste0("QCBioscan_rerun_", batch_no, ".html")` so each file is named after its batch.
- **Fixed plot colours.** Plate boxplot colours are no longer shuffled at random on each run.
- **Category summary table fixed.** It joined the per-category and per-description tallies on the count, so categories with the same number of specimens were crossed and duplicated (batch43_0: categories 5/12 and 10/11; PASS rows summed to 1,901 instead of 1,895). It now counts category, description and decision together. Categories in the CSVs were never affected.
- **Report wording.** Decisions shown as PASS and ON_HOLD (was YES/NO); the two "% OF SAMPLES EXCLUDED" lines replaced with counts and percentages for PASS, ON_HOLD and not categorised; "none" or 0 instead of blank, NA or NaN; "5 of fewer" corrected to "fewer than 5". HTML only. Details: `docs/changes/report_summary_fix.md`.

### Planned

- Stop codons in the main sequence (proposed 18 Nov 2026, replacing the 5 Nov order; for the team to agree): (1) BIP frame correction on flagged sequences with 5+ reads, BIP's own 327K reference only (missing base = N, extra homopolymer base deleted, ends not trimmed, 1-3 edits, result must be stop-free); (1b, if agreed) also BIP's non-homopolymer 'check' edits, marked separately; (2) only if BIP cannot fix the main sequence: a stop-free secondary from the same species/BIN with 5+ reads that matches a reference at least as well as the main; (3) otherwise flag as possible NUMT (not PASS as it is). Length is a flag only; corrected PASS sequences are replaced on BOLD; FACE historic specimens are reported separately. Evidence (batches 10, 18, 43): 554 of 14,595 PASS specimens in batches 10 and 18 have a stop codon in the main sequence, all on BOLD with it; 340 are FACE. Of the other 214, BIP corrects 72, 'check' edits up to 45 more, a stop-free secondary 3 more; about 94 left to flag (139 without 'check' edits). Ampliseq (batch 43) confirmed 31 of 40 homopolymer corrections and 8 of 8 judgeable 'check' edits, none contradicted. Secondary second, not first: in wells checked on BOLD the main sequence was usually the species' known haplotype with one slip that BIP fixes, while the stop-free secondary (2.5-4.5% away) matched nothing closely (likely a NUMT). A BIOSCAN-supplemented BIP reference corrected only 4 more and is not used (decided 17 Nov). Not counting stop-codon secondaries against ON_HOLD specimens would free only 9 of 1,302 (same BIN or within 5%), so no change proposed. Test folders on the farm: bip_qc_test, bip_ref_test, step1_test, check_edits_test.
- Stop-codon frame correction with BIP (Barcode Inference Pipeline, Centre for Biodiversity Genomics, https://github.com/cbg-innov/BIP, Apache License 2.0) on flagged sequences only, before QC. Replaces `StopCodonRemove_v1.Rmd`, which only flagged stop codons, took hours per batch and caused duplicate rows.
- Write the QC version and git commit into each batch's output (`qc_version.txt`).
- Write every specimen with a reason, including those removed before categories are assigned.
- Repeat plates (`_rpt`, e.g. FRBX_025_rpt in batch 3) are dropped; find and fix the step.
- Check the strongest secondary sequence, not the second row by `Contig_ID`.
- Write categories 13–16 (FAILED / EXCLUDED) from the QC script itself; renumber the internal "13 = no_category" check.
- Category 8: decide whether the salvage should require 50 or more reads, as Table 1 in the README says.
- README: update Usage, Input and Output sections to the current script; correct the description of the mosquito step (2.6) and step 2.7.
