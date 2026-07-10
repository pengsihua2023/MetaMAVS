# Real-Data Validation: Gemma vs Claude on Sapelo2 results

This runbook validates the **migrated inference layer** (Claude → local Gemma
4 E2B) on **real** metagenomic data from UGA GACRC **Sapelo2**, rather than the
synthetic dry-run fixtures used during migration.

The core idea: the heavy bioinformatics (GOTTCHA2, a ~12 h high-memory job)
runs **once** on the cluster and produces real taxonomy/abundance/risk tables.
The LLM interpretation layer is then re-run **locally** under each backend on
those exact same real inputs — cheap, repeatable, and requires no cluster access.

```
  Phase A (once, on Sapelo2)                 Phase B (repeat, local)
  ┌────────────────────────┐                 ┌───────────────────────────┐
  │ GOTTCHA2 on real FASTQ │  real .tsv  →   │ LLM_BACKEND=gemma  ─┐      │
  │ (SLURM / SSH)          │                 │ LLM_BACKEND=claude ─┴─ diff│
  └────────────────────────┘                 └───────────────────────────┘
```

---

## Prerequisites

- **Phase A:** a Sapelo2 account; the GOTTCHA2 conda env; the species GOTTCHA2
  DB (~94 GB minimap2 index → a ~120 G RAM partition); real paired/single FASTQ.
- **Phase B (gemma):** local `llama-server` on `http://localhost:8080/v1` started
  with `--jinja`, plus `pip install -e ".[llm]"` (installs `openai`).
- **Phase B (claude, optional):** `ANTHROPIC_API_KEY` in `.env` (paid). The
  harness runs Gemma-only and skips Claude gracefully if the key/SDK is absent.

Start the local Gemma server (example):

```bash
./build/bin/llama-server -hf ggml-org/gemma-4-E2B-it-GGUF:Q8_0 \
    --host 127.0.0.1 --port 8080 --jinja
curl -s http://localhost:8080/v1/models   # expect HTTP 200 + model list
```

---

## Phase A — produce REAL results on Sapelo2

Pick **one** of the two paths. Both yield the two files MetaMAVS parses:
`<SAMPLE>.gottcha2.tsv` and `<SAMPLE>.gottcha2.lineage.tsv`.

### Path A1 — MetaMAVS SSH controller (recommended, end-to-end)

The controller submits the GOTTCHA2 job over SSH (ControlMaster reuses one Duo
auth), polls it, downloads the `.tsv`, parses it locally, and runs the full
graph. Edit the two TODO paths in `configs/sapelo2_config.yaml` first
(`gottcha2_db` and the manifest's FASTQ), then:

```bash
metamavs run --config configs/sapelo2_config.yaml --execute
# human_review.mode=pause → approve the checkpoint when prompted:
metamavs review --run-dir reports/sapelo2_genome72
```

This writes `reports/sapelo2_genome72/state.json` — the input Phase B needs.

### Path A2 — standalone sbatch (run the heavy step by hand)

Use `slurm/gottcha2_sapelo2.sbatch` when you'd rather submit GOTTCHA2 yourself.
Edit the four `>>> TODO <<<` values (sample id, READ1/READ2, DB, env bin), then
on a Sapelo2 login node:

```bash
sbatch slurm/gottcha2_sapelo2.sbatch
```

When it finishes, copy the two `.tsv` outputs back to the controller under the
run's raw results directory and run the local pipeline to parse them into
`state.json`:

```bash
mkdir -p reports/sapelo2_genome72/results/raw/gottcha2
scp <user>@sapelo2:.../mm_gottcha2_<SAMPLE>/results/<SAMPLE>.gottcha2*.tsv \
    reports/sapelo2_genome72/results/raw/gottcha2/
# then let MetaMAVS parse the downloaded results into state.json
metamavs run --config configs/sapelo2_config.yaml --execute
```

**Acceptance (Phase A):** `state.json` exists and its `risk_summary.top_risks`
lists real taxa with real read counts (e.g. SARS-related coronavirus, Norwalk
virus), not the synthetic dry-run catalogue.

---

## Phase B — compare both backends on the SAME real results

No cluster access needed. The harness loads the completed run's `state.json`
(real tables) and re-runs only the LLM interpretation node under each backend:

```bash
python scripts/compare_llm_backends.py \
    --state reports/sapelo2_genome72/state.json \
    --backends gemma,claude \
    --outdir reports/llm_backend_comparison
```

Outputs:

```
reports/llm_backend_comparison/
  gemma/intermediate/llm_narrative.md
  claude/intermediate/llm_narrative.md
  comparison_summary.json          # status/model/words/elapsed per backend
```

Side-by-side review:

```bash
diff -y --width=200 \
  reports/llm_backend_comparison/gemma/intermediate/llm_narrative.md \
  reports/llm_backend_comparison/claude/intermediate/llm_narrative.md | less
```

---

## What to judge (acceptance criteria, Phase B)

Both backends must operate on identical real inputs. Judge quality on:

| Dimension | Pass condition |
|---|---|
| **Verdict parity** | Same `overall_risk`; same taxa flagged High/Critical. A downgrade of a real High pathogen is a **fail**. |
| **Factual grounding** | Narrative reflects the real taxa, read counts, site and date — no invented pathogens or numbers. |
| **Scientific caution** | "detected sequence signal" not "confirmed infection"; phages separated; confirmatory testing recommended for High. |
| **Single-time-point honesty** | If only one sample/time point, no spurious temporal/trend claims. |
| **Format validity** | For the JSON agents (taxonomy/novel/risk) the reply parses; for narrative, Markdown is well-formed. |
| **Latency** | Acceptable for the workflow (local Gemma is typically comparable to or faster than the Claude round-trip). |

**Decision rule:** if Gemma matches on verdict parity + grounding + caution, keep
`LLM_BACKEND=gemma` as default. Reserve `LLM_BACKEND=claude` for external reports
or high-risk events where the extra epidemiological nuance is worth the API cost.
The switch is zero-code and fully reversible.

---

## Reference: observed run (Genome_72, real Sapelo2 GOTTCHA2)

Real input `reports/sapelo2_genome72/state.json` — `overall_risk=High`, real top
taxa SARS-related coronavirus (52 reads) and Norwalk virus (26 reads). Both
backends produced an `ok` narrative from these real tables; both preserved the
High verdict and the scientific-caution framing. Claude additionally anchored to
run specifics (site, collection date, single-time-point caveat) and gave slightly
richer per-taxon reasoning; Gemma was correct and cautious but more general —
consistent with the migration comparison. This confirms Gemma is a viable local
default on real data, with Claude available for cases needing extra nuance.

A full side-by-side of the two **final reports** on this real run (excerpts,
per-taxon reasoning, caveats) is in
[`GEMMA_VS_CLAUDE_REAL_REPORT.md`](GEMMA_VS_CLAUDE_REAL_REPORT.md).
