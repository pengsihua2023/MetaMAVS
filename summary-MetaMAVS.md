# MetaMAVS — Project Summary

*A synthesis of the nine project decks in the repository root. MetaMAVS
(Metagenomic Multi-Agent Virus Surveillance) is a research-grade, LangGraph-based
multi-agent system for viral surveillance from wastewater, environmental, and
clinical metagenomic data.*

---

## 1. Why MetaMAVS (motivation)

Metagenomic viral surveillance is hard for four reasons the system is built to
address:

- **Complex, noisy data** — wastewater/environmental metagenomes mix host,
  bacteria, phage, and rare viral signals.
- **Many fragile manual steps** — QC → host removal → detection → taxonomy →
  abundance → novelty is easy to break and hard to reproduce.
- **Risk of over-claiming** — weak metagenomic hits can be mistaken for confirmed
  pathogens without careful flagging.
- **No coordination layer** — traditional pipelines lack decision logic, human
  review, and cross-step error handling.

## 2. What MetaMAVS is

A system that ingests metagenomic data, detects known & potential viral signals,
classifies them, tracks abundance trends, screens for novelty, assesses
epidemiological risk, and writes surveillance reports — orchestrated as a
**LangGraph state machine** (16 nodes, conditional routing, checkpointing,
human-in-the-loop).

- **Research-grade & scientifically cautious** — "detected signal", not
  "confirmed infection"; never overstates weak evidence.
- **Deterministic & key-free by default** — six nodes become NCBI-grounded LLM
  agents only when enabled; no cloud key is ever required to run.
- **Multi-agent, not a sequential script** — a StateGraph, not a flat pipeline.

### Design principles

- **State machine, not a script** — conditional routing, error diversion,
  human review, checkpointing.
- **One shared state** — every node returns a partial update; warnings/errors/log
  use add-reducers (append, never overwrite).
- **Framework dependency centralized** — only `graph.py` imports LangGraph; the
  16 nodes stay pure, testable functions.
- **Separation of concerns** — orchestration (LangGraph) · nodes (agents) ·
  utilities · data validation (pydantic).

## 3. Tool-integration philosophy

MetaMAVS started as an MVP (viral detection + classification) and is expanding
into a full molecular-epidemiology surveillance system. Bioinformatics tools are
integrated only if they are agent-friendly, judged on five criteria:

1. **Deterministic** — same input → same output (agents route on results).
2. **Fast, bounded runtime** — no hours/days-long, unpredictable calls.
3. **Self-contained** — "call once, get one answer", not a whole workflow engine.
4. **Machine-readable, actionable output** — a structured semantic verdict, not
   raw data needing expert interpretation.
5. **Fail-loud, not silent** — explicit errors on bad input.

By these criteria, BEAST2 (MCMC, non-reproducible, needs convergence checks),
IQ-TREE (unbounded ML search, no actionable verdict), and Nextstrain (a whole
Snakemake workflow — "orchestrator inside an orchestrator") are **not** suitable;
lightweight, single-call tools (e.g. Nextclade-style) are.

## 4. The workflow: from data to report

```
FASTQ → qc → host removal → viral detection → taxonomy → abundance →
   novel-virus screening → risk → human review → LLM narrative → report → END
```

The report is built in two clearly separated layers:

- **Deterministic chain computes the numbers.** Parsers turn tool outputs into
  normalized tables; taxonomy/abundance/risk agents compute summaries. The LLM
  never recomputes numbers.
- **`report_writer` (deterministic, no LLM) assembles `report.md`/`.html`**,
  embedding each agent's LLM output into its section. The LLM writes only the
  interpretation prose — not the report scaffold, and it reads computed summaries,
  never the raw tsv.

**Prompts (per LLM node):** a system prompt (role + hard scientific-caution
rules), a user prompt (the run's structured summaries as JSON, "use only this
data"), and a cached shared reference prefix.

## 5. The six AI agents

Six nodes become LLM agents when enabled. Shared trigger gate:
`llm.enabled AND llm_available() AND <this agent has real input>`; a `mode`
marker in state is the proof it fired. On the real Sapelo2 `Genome_72` run
(overall **High**, backend Gemma 4 E2B), **all six fired**:

| Agent | Analysed (input) | Inferred (result) |
|---|---|---|
| **qc** | FastQC: 3.3M reads, Q34.9 | ADEQUATE for sensitive detection |
| **taxonomy** | 18 GOTTCHA2 taxa + NCBI lineage | 3 phage / 4 pathogen-like / 1 control / 11 false-positive |
| **abundance** | 18-taxa RPM/trend (1 time point) | all stable = uninformative (single time point) |
| **novel_virus** | 29 CheckV contigs + RVDB homology | all < 64% identity → suspected-novel, per-candidate evidence |
| **risk** | taxonomy + trend + high-risk config | overall High; SARS-related & Norwalk = High |
| **narrative** | all structured summaries (JSON) | cautious public-health narrative (Gemma) |

Timing: qc/taxonomy/abundance/novel_virus/risk fire pre-review; the narrative
fires after human-review approval. `scripts/check_agents.py` verifies the count.

## 6. LLM backend: Claude → local Gemma 4 E2B

The inference backend was migrated from Anthropic Claude to a **local Gemma 4 E2B**
server (llama-server), selected by the `LLM_BACKEND` env var — the switch lives in
one centralized module, so all six agents keep their interface unchanged.

- **Default `gemma`** (local, free, private); **`claude`** for external/high-risk
  reports. Zero-code, reversible switch.
- **Quality comparison on the same real data:** identical risk verdict (both
  High); Claude is stronger on single-time-point honesty, methodological caveats,
  and data grounding; Gemma is reliable but more general — hence a **tiered
  policy**: Gemma for routine local runs, Claude when extra nuance matters.

## 7. HPC execution & fetched files (Sapelo2)

The controller runs locally and submits GOTTCHA2/FastQC/assembly+CheckV jobs to
UGA GACRC **Sapelo2** over SSH, polls, and fetches results with
`rsync --checksum`. For the single-sample `Genome_72` run it fetched **5 files**
(the complete real-data source): FastQC metrics, GOTTCHA2 tsv + lineage, CheckV
quality summary, and DIAMOND-vs-RVDB contig homology. The 8 `tables/*.csv` and
`report.md` all derive from these plus manifest metadata, NCBI lineage, and config.

## 8. Deployment plan & budget

A three-layer production architecture separates concerns:

| Layer | Role | Recommended |
|---|---|---|
| **AWS web** | domain/HTTPS/login, metadata, task status, calls Sapelo2 & GPU APIs, shows reports | EC2 t4g.large |
| **UGA Sapelo2 / Globus** | TB-scale sequencing data, Slurm bioinformatics pipelines, sends results back | /project, /scratch |
| **RunPod GPU inference** | local open-weight LLMs, multi-agent reasoning, report interpretation | A100 PCIe |

RunPod A100 ($1.39/hr) is far cheaper than AWS ($3.43/hr per GPU in 8× A100
batches). Budget: **~$5,551/year** (weekday GPU online) or **~$13,036/year** for
24/7 A100 service.

## 9. Status

- The deterministic Phase 1–3 pipeline runs key-free; the optional LLM layer is
  additive and degrades gracefully.
- **A full real Sapelo2 run fired all six AI agents** on `Genome_72`, with a
  Gemma-written report, RVDB-verified novelty, and 125+ passing tests.
- Migration, data-flow, agent-trigger, model-comparison, fetched-files, and
  deployment are documented in the repo (`docs/`) and the nine decks.

---

## Source decks (repository root)

| Deck | Covers | Summary section |
|---|---|---|
| `MetaMAVS_Team_Intro.pptx` | motivation, overview, principles | §1–2 |
| `Tools integration_0629.pptx` | tool-selection criteria, exclusions | §3 |
| `MetaMAVS_DataFlow_Prompts_EN.pptx` | data flow, prompts | §4 |
| `MetaMAVS_Agents_and_Report_EN.pptx` | agent triggers, report source | §4–5 |
| `MetaMAVS_Agent_IO_EN.pptx` | per-agent data & inference | §5 |
| `MetaMAVS_Migration_EN.pptx` | Claude → Gemma migration | §6 |
| `MetaMAVS_Gemma_vs_Claude_RealReport_EN.pptx` | model quality comparison | §6 |
| `MetaMAVS_Fetched_Files_EN.pptx` | HPC fetched files | §7 |
| `Deployment Plan-of-MetaMAVS.pptx` | 3-layer deployment, budget | §8 |
