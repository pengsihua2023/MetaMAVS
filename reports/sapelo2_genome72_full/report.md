# MetaMAVS Surveillance Report: sapelo2_genome72_full

> _Research-grade metagenomic virus surveillance. Signals below are **detected sequence signals**, not confirmed infections. Confirmatory testing is required before any public-health action._

## 1. Project Summary

- **Project:** MetaMAVS
- **Run name:** sapelo2_genome72_full
- **Run id:** run_20260710_234706
- **Mode:** execution
- **Overall risk:** High

## 2. Sample Summary

- **Number of samples:** 1
- **Sequencing type:** paired_end
- **Locations:** sapelo2
- **Collection dates:** 2025-12-02

## 3. Quality Control

- **Passed:** 1
- **Failed:** 0

| Sample | Mean Q | Total reads | Adapter % | QC |
| --- | --- | --- | --- | --- |
| Genome_72 | 34.9 | 3326783 | - | pass |


_AI QC note:_ The QC metrics for "Genome_72" are **ADEQUATE** for sensitive viral detection.

The sample exhibits extremely high sequencing depth (3.3M reads), which maximizes sensitivity for low-abundance viruses. The mean quality score (34.9) is high, and the read length (150) is sufficient. The "pass" status indicates no immediate issues with adapter contamination or overall sequencing quality.

**Recommendation:** Proceed with analysis. No re-sequencing is warranted based on these metrics.

## 4. Host Read Removal

- **Tool:** minimap2
- **Host reference:** /path/to/host/reference

| Sample | Host read % | Non-host reads |
| --- | --- | --- |
| Genome_72 | 85.0 | 300000 |

## 5. Viral Detection & Taxonomy

- **Detection tools:** gottcha2
- **Candidate taxa:** 18
- **Flagged (phage/FP/low-conf):** 11
- **Phage taxa:** 4
- **Pathogen-like taxa:** 4

## 6. Abundance Trends

| Taxon | Mean RPM | First RPM | Last RPM | % change | Trend |
| --- | --- | --- | --- | --- | --- |
| Human mastadenovirus F | 19.24 | 19.24 | 19.24 | 0.0 | stable |
| Obolenskvirus AP22 | 16.53 | 16.53 | 16.53 | 0.0 | stable |
| Phikzvirus phiKZ | 15.93 | 15.93 | 15.93 | 0.0 | stable |
| Pepper mild mottle virus | 12.32 | 12.32 | 12.32 | 0.0 | stable |
| Severe acute respiratory syndrome-related coronavirus | 11.12 | 11.12 | 11.12 | 0.0 | stable |


_AI trend interpretation:_

Based on this single-sample data, no epidemiological trend or conclusion regarding an outbreak can be established. Abundance reflects the current environmental viral load, not case counts.

All observed taxa, including the top signal, Human mastadenovirus F (19.24 RPM) and the Severe acute respiratory syndrome-related coronavirus (11.12 RPM), show a "stable" trend. This stability is uninformative, and a single time point cannot establish a temporal pattern.

To determine if these signals represent a genuine increase or decrease, **repeated sampling across multiple time points is essential.** We recommend repeat sampling to establish a reliable trend before any public health action is considered.

## 7. Novel / Divergent Virus Candidates

| Candidate | Putative taxon | Reads | Confidence | Evidence |
| --- | --- | --- | --- | --- |
| NVC_001 | assembled contig k141_8205 | 0 | 0.913 | CheckV High-quality, completeness 91%, viral_genes 7 |
| NVC_002 | assembled contig k141_22106 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_003 | assembled contig k141_27848 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_004 | assembled contig k141_54255 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_005 | assembled contig k141_14489 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_006 | assembled contig k141_50456 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_007 | assembled contig k141_22755 | 0 | 0.88 | CheckV Medium-quality, completeness 88%, viral_genes 1 |
| NVC_008 | assembled contig k141_59057 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_009 | assembled contig k141_45707 | 0 | 0.881 | CheckV Medium-quality, completeness 88%, viral_genes 2 |
| NVC_010 | assembled contig k141_56208 | 0 | 0.629 | CheckV Medium-quality, completeness 63%, viral_genes 2 |
| NVC_011 | assembled contig k141_25606 | 0 | 0.638 | CheckV Medium-quality, completeness 64%, viral_genes 1 |
| NVC_012 | assembled contig k141_19319 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_013 | assembled contig k141_33897 | 0 | 0.635 | CheckV Medium-quality, completeness 64%, viral_genes 0 |
| NVC_014 | assembled contig k141_29873 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_015 | assembled contig k141_45317 | 0 | 0.557 | CheckV Medium-quality, completeness 56%, viral_genes 27 |
| NVC_016 | assembled contig k141_52976 | 0 | 0.866 | CheckV Medium-quality, completeness 87%, viral_genes 2 |
| NVC_017 | assembled contig k141_34455 | 0 | 0.516 | CheckV Medium-quality, completeness 52%, viral_genes 1 |
| NVC_018 | assembled contig k141_42526 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_019 | assembled contig k141_61025 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_020 | assembled contig k141_20091 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_021 | assembled contig k141_18586 | 0 | 0.538 | CheckV Medium-quality, completeness 54%, viral_genes 1 |
| NVC_022 | assembled contig k141_54479 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 4 |
| NVC_023 | assembled contig k141_36833 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_024 | assembled contig k141_21054 | 0 | 0.538 | CheckV Medium-quality, completeness 54%, viral_genes 32 |
| NVC_025 | assembled contig k141_45003 | 0 | 0.549 | CheckV Medium-quality, completeness 55%, viral_genes 1 |
| NVC_026 | assembled contig k141_30034 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |
| NVC_027 | assembled contig k141_61067 | 0 | 0.806 | CheckV Medium-quality, completeness 81%, viral_genes 1 |
| NVC_028 | assembled contig k141_30128 | 0 | 0.799 | CheckV Medium-quality, completeness 80%, viral_genes 1 |
| NVC_029 | assembled contig k141_61293 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1 |

## 8. Epidemiological Risk Assessment

- **Overall risk:** High

| Taxon | Risk | Reads | Trend | Reasons |
| --- | --- | --- | --- | --- |
| Severe acute respiratory syndrome-related coronavirus | High | 37 | stable | [LLM] Matches the high-risk pathogen list (Betacoronavirus) and has adequate read support (37 reads), warranting a High risk assessment for surveillance prioritization. |
| Norwalk virus | High | 24 | stable | [LLM] Matches the high-risk pathogen list (Norovirus) and has substantial read support (24 reads), indicating a significant environmental signal. |
| Human mastadenovirus F | Medium | 64 | stable | [LLM] Non-pathogen virus with substantial read support (64 reads). Classified as Medium risk based on substantial signal, though it does not match the high-risk pathogen list. |
| Human coronavirus 229E | Medium | 16 | stable | [LLM] Non-pathogen virus with moderate read support (16 reads). Classified as Medium risk based on signal strength. |
| assembled contig k141_8205 | Medium | 0 | unknown | novel/divergent candidate; requires confirmatory characterisation |


**Normalization controls (not ranked as threats):** Pepper mild mottle virus (41 reads — Pepper mild mottle virus (PMMoV))

## AI-Assisted Interpretation

_Generated by gemma-4-E2B-it. Advisory only — the deterministic risk assessment above is authoritative; confirm all high-risk signals._

## Executive Summary
The wastewater metagenomic surveillance of the Sapelo 2 site detected a high-risk viral signal, including sequences matching SARS-CoV-2 and Norwalk virus. These detections represent sequence signals in the environment, not confirmed infections or outbreaks. While the signal strength for the primary pathogens is substantial, orthogonal confirmation is required before any public health action. Other non-pathogenic viruses and novel candidates were also identified.

## Risk Interpretation
**Severe acute respiratory syndrome-related coronavirus (High Risk):** A detected sequence signal was found with 37 reads. This pathogen is a known respiratory virus with documented faecal shedding, warranting high surveillance prioritization.
**Norwalk virus (High Risk):** A significant signal was detected with 24 reads. This virus is a leading cause of gastroenteritis and is commonly shed in wastewater.
**Human mastadenovirus F (Medium Risk):** A substantial signal (64 reads) was detected. This is classified as a non-pathogen virus, but its high read count indicates a significant environmental presence.
**Human coronavirus 229E (Medium Risk):** A moderate signal (16 reads) was detected.
**Novel Candidates:** Several novel contigs were identified; these require further characterization to determine their biological significance.

## Recommended Public-Health Actions
*   **Priority Confirmation:** Immediately confirm the detection of the Severe acute respiratory syndrome-related coronavirus and Norwalk virus using targeted RT-qPCR or amplicon sequencing.
*   **Contextual Analysis:** Integrate these sequence signals with clinical and syndromic surveillance data before any public-health action is taken.
*   **Curate Novel Sequences:** Manually curate and verify novel contigs to assess their potential relevance.

## Caveats & Limitations
*   **Signal vs. Confirmation:** All findings are detected sequence signals, not confirmed infections or outbreaks.
*   **Read Count:** While the top signals have adequate read support, low read counts (<10) are prone to uncertainty, and all results must be treated cautiously.
*   **False Positives:** The analysis identified 11 potential false positives, emphasizing the need for orthogonal confirmation.
*   **Data Scope:** This analysis is based solely on metagenomic reads; clinical diagnosis or outbreak confirmation cannot be made from this data alone.
*   **Phages:** Environmental bacteriophages were detected (4 taxa); these are environmental indicators and are not considered human or animal pathogens.

## 9. Human Review

- **Review required:** True
- **Decision:** approved
- **Approved for report:** True
- **Reviewer notes:** Offline 6-agent regeneration from real Sapelo2 HPC results (all tools run).

## 10. Recommended Follow-up Actions

- Confirm Severe acute respiratory syndrome-related coronavirus (High) with targeted RT-qPCR / amplicon sequencing
- Confirm Norwalk virus (High) with targeted RT-qPCR / amplicon sequencing
- Manually curate novel/divergent candidates; verify contigs with CheckV and phylogenetics

## 11. Warnings

- 29 novel/divergent viral candidate(s) require expert review

## 12. Reproducibility

- **MetaMAVS version:** 0.1.0
- **Config:** configs/sapelo2_config.yaml
- **Run directory:** reports/sapelo2_genome72_full
- **Generated (UTC):** 2026-07-11T16:16:20Z


---
_Generated by MetaMAVS. Detected signals require confirmatory testing._
