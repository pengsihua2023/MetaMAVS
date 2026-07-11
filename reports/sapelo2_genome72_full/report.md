# MetaMAVS Surveillance Report: sapelo2_genome72_full

> _Research-grade metagenomic virus surveillance. Signals below are **detected sequence signals**, not confirmed infections. Confirmatory testing is required before any public-health action._

## 1. Project Summary

- **Project:** MetaMAVS
- **Run name:** sapelo2_genome72_full
- **Run id:** run_20260711_172021
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

The sample exhibits excellent metrics:
*   **Sequencing Depth:** Total reads (3.3M) is very high, ensuring high sensitivity for low-abundance viruses.
*   **Base Quality:** Mean quality (34.9) is high, minimizing noise.
*   **Status:** The sample passed all implicit quality checks.

No concerns regarding low depth, poor quality, or contamination were identified. This data provides a strong foundation for reliable viral signal detection.

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
- **Phage taxa:** 3
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

Based on this single-sample data, no temporal trend can be established, as stability from one point is uninformative. All detected viral taxa, including the top five identified, showed stable relative abundance (0.0% change).

This indicates that the environmental viral load for these specific agents was consistent at this time point. We cannot infer changes in transmission or case counts from this snapshot alone.

No genuine increases were observed to warrant immediate monitoring or repeat sampling. Further surveillance requires repeated sampling across multiple time points to establish a true trend.

## 7. Novel / Divergent Virus Candidates

| Candidate | Putative taxon | Reads | Confidence | Evidence |
| --- | --- | --- | --- | --- |
| NVC_001 | assembled viral contig k141_60867 | 0 | 0.629 | CheckV Medium-quality, completeness 63%, viral_genes 2; best known-virus hit QKU35076.1 at 34% (< 90%) -> divergent |
| NVC_002 | assembled viral contig k141_35521 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit QKU34530.1 at 39% (< 90%) -> divergent |
| NVC_003 | assembled viral contig k141_59450 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit AGE55605.1 at 29% (< 90%) -> divergent |
| NVC_004 | assembled viral contig k141_36112 | 0 | 0.638 | CheckV Medium-quality, completeness 64%, viral_genes 1; best known-virus hit AAU93529.1 at 50% (< 90%) -> divergent |
| NVC_005 | assembled viral contig k141_16451 | 0 | 0.538 | CheckV Medium-quality, completeness 54%, viral_genes 32; best known-virus hit QBP06533.1 at 51% (< 90%) -> divergent |
| NVC_006 | assembled viral contig k141_22743 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit ABY48142.1 at 42% (< 90%) -> divergent |
| NVC_007 | assembled viral contig k141_37566 | 0 | 0.806 | CheckV Medium-quality, completeness 81%, viral_genes 1; best known-virus hit QDH86641.1 at 60% (< 90%) -> divergent |
| NVC_008 | assembled viral contig k141_29885 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit QFG74328.1 at 43% (< 90%) -> divergent |
| NVC_009 | assembled viral contig k141_15535 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit QDY51995.1 at 31% (< 90%) -> divergent |
| NVC_010 | assembled viral contig k141_28011 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit AYV78014.1 at 31% (< 90%) -> divergent |
| NVC_011 | assembled viral contig k141_54234 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit AOP31334.1 at 64% (< 90%) -> divergent |
| NVC_012 | assembled viral contig k141_11267 | 0 | 0.913 | CheckV High-quality, completeness 91%, viral_genes 7; no known-virus protein hit -> suspected novel |
| NVC_013 | assembled viral contig k141_39673 | 0 | 0.557 | CheckV Medium-quality, completeness 56%, viral_genes 27; best known-virus hit YP_009254763.1 at 40% (< 90%) -> divergent |
| NVC_014 | assembled viral contig k141_33753 | 0 | 0.549 | CheckV Medium-quality, completeness 55%, viral_genes 1; best known-virus hit YP_009640107.1 at 32% (< 90%) -> divergent |
| NVC_015 | assembled viral contig k141_32511 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit QFG74471.1 at 42% (< 90%) -> divergent |
| NVC_016 | assembled viral contig k141_29538 | 0 | 0.881 | CheckV Medium-quality, completeness 88%, viral_genes 2; best known-virus hit AUI39789.1 at 40% (< 90%) -> divergent |
| NVC_017 | assembled viral contig k141_16042 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit AAD26531.1 at 44% (< 90%) -> divergent |
| NVC_018 | assembled viral contig k141_23319 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit QDY52166.1 at 42% (< 90%) -> divergent |
| NVC_019 | assembled viral contig k141_60635 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit ARF10911.1 at 33% (< 90%) -> divergent |
| NVC_020 | assembled viral contig k141_12395 | 0 | 0.538 | CheckV Medium-quality, completeness 54%, viral_genes 1; no known-virus protein hit -> suspected novel |
| NVC_021 | assembled viral contig k141_57350 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit AYV82314.1 at 33% (< 90%) -> divergent |
| NVC_022 | assembled viral contig k141_49244 | 0 | 0.635 | CheckV Medium-quality, completeness 64%, viral_genes 0; no known-virus protein hit -> suspected novel |
| NVC_023 | assembled viral contig k141_21386 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; best known-virus hit ARF12459.1 at 32% (< 90%) -> divergent |
| NVC_024 | assembled viral contig k141_55940 | 0 | 0.866 | CheckV Medium-quality, completeness 87%, viral_genes 2; best known-virus hit QKU34031.1 at 50% (< 90%) -> divergent |
| NVC_025 | assembled viral contig k141_45027 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 1; no known-virus protein hit -> suspected novel |
| NVC_026 | assembled viral contig k141_25320 | 0 | 0.799 | CheckV Medium-quality, completeness 80%, viral_genes 1; best known-virus hit QFG73724.1 at 35% (< 90%) -> divergent |
| NVC_027 | assembled viral contig k141_55512 | 0 | 0.516 | CheckV Medium-quality, completeness 52%, viral_genes 1; best known-virus hit AGE55605.1 at 31% (< 90%) -> divergent |
| NVC_028 | assembled viral contig k141_32030 | 0 | 0.88 | CheckV Medium-quality, completeness 88%, viral_genes 1; best known-virus hit WZO87221.1 at 46% (< 90%) -> divergent |
| NVC_029 | assembled viral contig k141_38332 | 0 | 1.0 | CheckV High-quality, completeness 100%, viral_genes 4; best known-virus hit AYV81995.1 at 36% (< 90%) -> divergent |

## 8. Epidemiological Risk Assessment

- **Overall risk:** High

| Taxon | Risk | Reads | Trend | Reasons |
| --- | --- | --- | --- | --- |
| Severe acute respiratory syndrome-related coronavirus | High | 37 | stable | [LLM] Matches the high-risk Betacoronavirus list with adequate read support (37 reads). Requires orthogonal confirmation. |
| Norwalk virus | High | 24 | stable | [LLM] Matches the high-risk pathogen list (Norovirus) with substantial read support (24 reads). Requires orthogonal confirmation. |
| Human mastadenovirus F | Medium | 64 | stable | [LLM] Substantial read support (64 reads) for a non-phage, non-pathogen virus, warranting a Medium risk assessment based on presence. |
| Human coronavirus 229E | Medium | 16 | stable | [LLM] Substantial read support (16 reads) for a non-high-risk pathogen, warranting a Medium risk assessment. |
| assembled viral contig k141_60867 | Medium | 0 | unknown | novel/divergent candidate; requires confirmatory characterisation |


**Normalization controls (not ranked as threats):** Pepper mild mottle virus (41 reads — Pepper mild mottle virus (PMMoV))

## AI-Assisted Interpretation

_Generated by gemma-4-E2B-it. Advisory only — the deterministic risk assessment above is authoritative; confirm all high-risk signals._

## Executive Summary
The wastewater metagenomic surveillance detected sequence signals consistent with several high-risk enteric and respiratory viruses in the sapelo2 location. Specifically, signals for Severe acute respiratory syndrome-related coronavirus and Norwalk virus were identified, warranting immediate follow-up. While the overall signal is high, all findings are detected sequence signals and require orthogonal confirmation before any public health action can be taken.

## Risk Interpretation
**High-Risk Signals:**
*   **Severe acute respiratory syndrome-related coronavirus:** A detected sequence signal consistent with a respiratory Betacoronavirus. Given the established faecal shedding and known public health relevance, this signal is flagged as high risk and requires immediate orthogonal confirmation.
*   **Norwalk virus:** A detected sequence signal consistent with a leading cause of viral gastroenteritis. This signal is also flagged as high risk and requires immediate orthogonal confirmation.

**Medium-Risk Signals:**
*   Signals for Human mastadenovirus F and Human coronavirus 229E were detected. These are not classified as high-risk pathogens, but their presence is noted.
*   An assembled viral contig was identified as a novel/divergent candidate; further characterization is required.

**Confidence:** The detected signals for the high-risk pathogens have sufficient read support to be considered significant, but they are not confirmed infections.

## Recommended Public-Health Actions
*   **Priority 1: Orthogonal Confirmation:** Immediately confirm the presence and identity of the Severe acute respiratory syndrome-related coronavirus and Norwalk virus using targeted RT-qPCR or amplicon sequencing assays.
*   **Priority 2: Novel Candidate Review:** Manually curate and verify the novel viral contigs identified to determine their potential significance.
*   **Priority 3: Contextual Integration:** Integrate these sequence signals with clinical and syndromic surveillance data before any public health action is considered.

## Caveats & Limitations
*   **Sequence Signal Only:** All findings represent detected viral genetic material in the wastewater; they do not confirm active infections, case counts, or outbreaks.
*   **Confirmation Required:** No public health action can be taken based on sequence reads alone. Orthogonal testing is mandatory for all High-risk detections.
*   **False Positives:** The analysis identified 11 flagged false positives, indicating the need for careful interpretation of all results.
*   **Data Limitations:** The absence of a signal does not prove the absence of the virus. The detection relies on the completeness of the reference database.

## 9. Human Review

- **Review required:** True
- **Decision:** approved
- **Approved for report:** True
- **Reviewer notes:** 6-agent run with RVDB novelty check

## 10. Recommended Follow-up Actions

- Confirm Severe acute respiratory syndrome-related coronavirus (High) with targeted RT-qPCR / amplicon sequencing
- Confirm Norwalk virus (High) with targeted RT-qPCR / amplicon sequencing
- Manually curate novel/divergent candidates; verify contigs with CheckV and phylogenetics

## 11. Warnings

- No host_reference configured; using placeholder path in generated commands
- 11 taxon(a) flagged as likely false positives / phage / low-confidence
- 29 novel/divergent viral candidate(s) require expert review

## 12. Reproducibility

- **MetaMAVS version:** 0.1.0
- **Config:** configs/sapelo2_config.yaml
- **Run directory:** reports/sapelo2_genome72_full
- **Generated (UTC):** 2026-07-11T20:43:44Z


---
_Generated by MetaMAVS. Detected signals require confirmatory testing._
