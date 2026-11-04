# Changelog

## Unreleased (branch `dev`, to become version 3.0)

Changes to `QCBioscan_rerun.Rmd`, the script used for the February 2026 rerun (`qc_reports_rerun_Feb2026`).

### Done

- Synced with the copy run on the farm (colour palette for up to 20 partners in the plots).
- **Category 8 restored.** The salvage step looked for `category_decision == "NO"`, but categories 9–12 have been labelled `"ON_HOLD"` since V1, so no specimen was ever salvaged to category 8. It now looks for `"ON_HOLD"`.
- **Report card wording.** Categories 4 and 5 were written as "A single sequence present", although they have minor secondary sequences; they now use the same wording as categories 6 and 7. Category 8 uses the wording already on the portal ("Multiple sequences present but all differ by <2%; one sequence is dominant (>50 reads)").

### Planned

- Stop-codon frame correction with BIP (Barcode Inference Pipeline, Centre for Biodiversity Genomics, https://github.com/cbg-innov/BIP, Apache License 2.0) on flagged sequences only, before QC. Replaces `StopCodonRemove_v1.Rmd`, which only flagged stop codons, took hours per batch and caused duplicate rows.
- Write the QC version and git commit into each batch's output (`qc_version.txt`).
- Write every specimen with a reason, including those removed before categories are assigned.
- Repeat plates (`_rpt`, e.g. FRBX_025_rpt in batch 3) are dropped; find and fix the step.
- Check the strongest secondary sequence, not the second row by `Contig_ID`.
- Read-count thresholds (5 reads): decision pending (Rule A or Rule B).
- Category 8: decide whether the salvage should require 50 or more reads, as Table 1 in the README says.
- README Table 1: make the thresholds and category 12 wording match the code; correct the description of the mosquito step (2.6).
