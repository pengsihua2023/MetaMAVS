# The six AI agents: what each analysed and inferred (Genome_72)

Grounded in the real Sapelo2 run `reports/sapelo2_genome72_full` (single sample
`Genome_72`, sapelo2, GOTTCHA2 + FastQC + megahit/CheckV + RVDB, overall risk
**High**). For each of the six LLM agents: the **input data** it analysed and its
**inference result**. Backend: local Gemma 4 E2B.

> Recall the division of labour: each agent runs an LLM only to *interpret* the
> deterministically-computed data — it never recomputes the numbers. The
> deterministic `report_writer` then embeds these outputs into `report.md`.

---

## 1. qc — data-adequacy assessment

- **Input:** the real per-sample FastQC metrics —
  `total_reads = 3,326,783`, `mean_quality = 34.9`, `mean_read_length = 150`,
  `qc_status = pass`.
- **Inference:** QC is **ADEQUATE** for sensitive viral detection. Depth (3.3M
  reads) is very high → high sensitivity for low-abundance viruses; mean quality
  34.9 is high → low noise; no concerns flagged.

## 2. taxonomy — classification of detected taxa

- **Input:** 18 candidate viral taxa from GOTTCHA2 (name, taxid, reads,
  confidence) + verified **NCBI Taxonomy** lineage per taxid.
- **Inference (`mode = llm+ncbi`):** each taxon classified into phage / pathogen /
  false-positive / uncertain. Result: **18 taxa → 3 phage, 4 pathogen-like,
  1 control, 11 flagged** as likely false positives (low reads/confidence). The
  LLM may only add caution; it never overrides the deterministic labels.

## 3. abundance — trend interpretation

- **Input:** the RPM abundance/trend table for 18 taxa. Top by mean RPM:
  Human mastadenovirus F (19.2), Obolenskvirus AP22 (16.5), Phikzvirus phiKZ
  (15.9), Pepper mild mottle virus (12.3), SARS-related coronavirus (11.1) — all
  `trend = stable`.
- **Inference:** *"Based on this single-sample data, no temporal trend can be
  established; stability from one point is uninformative. All taxa showed stable
  relative abundance (0.0% change)… we cannot infer changes in transmission or
  case counts."* (Correctly flags the single-time-point limitation.)

## 4. novel_virus — novel/divergent candidate assessment

- **Input:** 29 CheckV-quality assembled contigs (High/Medium/Complete or
  completeness ≥ 50%) **cross-checked against RVDB** by DIAMOND blastx. All 29 had
  best known-virus protein hits **< 64 % identity** (0 excluded as known at
  ≥ 90 %) → all retained as suspected-novel.
- **Inference (`mode = llm`):** per-candidate assessment, e.g. NVC_002 — *"high
  quality assembled contig (100 % completeness)… significant divergence (39 %
  identity) from known viruses indicates a novel lineage or highly divergent
  relative. Given zero read support, this signal is weak and prone to being an
  assembly artefact."* (Notes both the divergence and the weak read support.)

## 5. risk — per-taxon epidemiological risk

- **Input:** cleaned taxonomy (labels/flags) + abundance trend + configured
  high-risk pathogen list + NCBI lineage.
- **Inference (`mode = llm`, overall = High):** counts Low 13 / Medium 31 /
  High 2 / Critical 0. Two **High**:
  - *SARS-related coronavirus* (37 reads): "matches the high-risk Betacoronavirus
    list with adequate read support."
  - *Norwalk virus* (24 reads): "matches the high-risk pathogen list (Norovirus)
    with substantial read support."
  Deterministic rails floor configured high-risk pathogens at High; the LLM adds
  the `[LLM]` reasoning per taxon.

## 6. narrative — public-health surveillance narrative

- **Input:** the whole run's structured summaries (risk, taxonomy, abundance,
  novel, sample metadata) rendered to JSON — *not* the raw files.
- **Inference (`llm_narrative`, model `gemma-4-E2B-it`):** a cautious Markdown
  narrative — *"detected sequence signals consistent with several high-risk
  enteric and respiratory viruses in sapelo2… SARS-related coronavirus and Norwalk
  virus were identified, warranting…"* — with Executive Summary / Risk
  Interpretation / Recommended Actions / Caveats, framed as "detected sequence
  signals", not confirmed infections. This text becomes the report's
  `## AI-Assisted Interpretation` section.

---

## Summary table

| Agent | Analysed (input) | Inferred (result) |
|---|---|---|
| qc | FastQC: 3.3M reads, Q34.9 | ADEQUATE for sensitive detection; no concerns |
| taxonomy | 18 GOTTCHA2 taxa + NCBI lineage | 3 phage / 4 pathogen-like / 1 control / 11 false-positive |
| abundance | 18-taxa RPM/trend (1 time point) | all stable = uninformative (single time point) |
| novel_virus | 29 CheckV contigs + RVDB homology | all < 64 % identity → suspected-novel; each caveated |
| risk | taxonomy + trend + high-risk config | overall High; SARS-CoV-related & Norwalk = High |
| narrative | all structured summaries (JSON) | cautious public-health narrative (Gemma) |

All six ran on the **same real Genome_72 data**; each interpreted its slice, and
`report_writer` assembled the results into `report.md`.
