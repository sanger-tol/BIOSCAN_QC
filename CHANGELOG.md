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

### Planned

- Stop codons in the main sequence (decided 5 Nov 2026): (1) use a stop-free secondary from the same species (within 2%, 5+ reads) if one exists; (2) otherwise apply BIP's frame correction (missing base = N, extra homopolymer base deleted, ends not trimmed); (3) if BIP cannot correct it, flag as possible NUMT. BIP runs only on flagged sequences with 5+ reads; length is a flag only; corrected PASS sequences are replaced on BOLD. Tested on batches 10, 18 and 43: no PASS/ON_HOLD changes, 131 sequences corrected, ampliseq confirmed all 31 corrections it could check.
- Stop-codon frame correction with BIP (Barcode Inference Pipeline, Centre for Biodiversity Genomics, https://github.com/cbg-innov/BIP, Apache License 2.0) on flagged sequences only, before QC. Replaces `StopCodonRemove_v1.Rmd`, which only flagged stop codons, took hours per batch and caused duplicate rows.
- Write the QC version and git commit into each batch's output (`qc_version.txt`).
- Write every specimen with a reason, including those removed before categories are assigned.
- Repeat plates (`_rpt`, e.g. FRBX_025_rpt in batch 3) are dropped; find and fix the step.
- Check the strongest secondary sequence, not the second row by `Contig_ID`.
- Write categories 13–16 (FAILED / EXCLUDED) from the QC script itself; renumber the internal "13 = no_category" check.
- Category 8: decide whether the salvage should require 50 or more reads, as Table 1 in the README says.
- README: update Usage, Input and Output sections to the current script; correct the description of the mosquito step (2.6) and step 2.7.
