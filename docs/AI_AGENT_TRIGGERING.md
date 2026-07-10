# How the four AI agents were triggered (Genome_72 run)

MetaMAVS has **six** optional LLM agents. In the real Sapelo2 `Genome_72` run,
**four** of them fired — **taxonomy, abundance, risk, and narrative** — because
they operate on the real GOTTCHA2 data chain. The other two (`qc`,
`novel_virus`) were skipped because their wet-lab steps weren't run on the
cluster, so their inputs were synthetic placeholders and a caution guard
short-circuited the LLM call.

This document explains the trigger process for the four that fired.

---

## The shared trigger pattern

Every LLM agent is **optional and additive**. Each guards its LLM call with the
same three base conditions, then adds one data-availability condition of its own:

```
llm.enabled == true          # config: llm.enabled
AND llm_available()          # backend reachable (Gemma server up, or Claude key)
AND <this agent has real input to interpret>
```

- `llm.enabled` — from the config (`llm: { enabled: true }` in
  `configs/sapelo2_config.yaml`).
- `llm_available()` — `metamavs/llm/client.py`; for `LLM_BACKEND=gemma` it is
  true when the `openai` SDK is importable (local server assumed up).
- The per-agent data condition is what distinguishes "fired" from "skipped."

If any condition is false the agent returns a clean no-op and the deterministic
result stands — the workflow never fails.

When an agent's LLM path runs, it stamps a **`mode`** marker in its summary
(e.g. `llm`, `llm+ncbi`) — that marker is the authoritative evidence that it
fired, visible in `state.json`.

---

## 1. taxonomy — classification

- **Node:** `metamavs/agents/taxonomy_agent.py`
- **Trigger (`:41`):**
  ```python
  if not llm_cfg.get("enabled") or not llm_available() or not candidates:
      return {}                        # skip: no candidate taxa to classify
  data = generate_json(TAXONOMY_SYSTEM, build_taxonomy_user(candidates, lineages),
                       cached_prefix=SHARED_REFERENCE, **resolve_params(llm_cfg, "taxonomy"))
  if not data or "taxa" not in data:   # skip: malformed reply → deterministic
      return {}
  ```
- **Data condition:** `candidates` — the parsed viral taxa from the GOTTCHA2 tsv.
  The real run had 20 taxa, so the condition held.
- **What the LLM does:** classify each taxon as phage / pathogen / false-positive
  / uncertain (NCBI-lineage-grounded), and flag review concerns. It may only
  *add* caution — it never overrides the deterministic labels.
- **Marker in this run:** `taxonomy_summary.mode = "llm+ncbi"`; log line
  `Taxonomy (llm+ncbi): 20 taxa, 8 flagged (3 phage)`. **→ fired.**

## 2. abundance — trend interpretation

- **Node:** `metamavs/agents/abundance_agent.py`
- **Trigger (`:133`):**
  ```python
  if trends and llm_cfg.get("enabled") and llm_available():
      txt = generate(ABUNDANCE_SYSTEM, build_abundance_user(trend_summary, n_samples),
                     cached_prefix=SHARED_REFERENCE, **resolve_params(llm_cfg, "abundance"))
      if txt:
          trend_summary["llm_interpretation"] = txt
          trend_summary["mode"] = "llm"
  ```
- **Data condition:** `trends` — the RPM-normalised abundance/trend table
  (computed deterministically upstream). Non-empty here.
- **What the LLM does:** write an epidemiological interpretation of the abundance
  trends (increases, stability, cross-sample context).
- **Marker in this run:** `trend_summary.mode = "llm"`, `llm_interpretation`
  present; log `Abundance: LLM trend interpretation generated`. **→ fired.**

## 3. risk — per-taxon risk reasoning

- **Node:** `metamavs/agents/risk_assessment_agent.py`
- **Trigger (`:48`):**
  ```python
  if not llm_cfg.get("enabled") or not llm_available() or not evidence:
      return {}                        # skip: no risk evidence
  data = generate_json(RISK_SYSTEM, build_risk_user(evidence),
                       cached_prefix=SHARED_REFERENCE, **resolve_params(llm_cfg, "risk_assessment"))
  if not data or "assessments" not in data:
      return {}
  ```
- **Data condition:** `evidence` — the per-taxon risk evidence (taxonomy label,
  reads, trend, pathogen match) built deterministically. Present here.
- **Safety rail:** the LLM may only *raise* caution. Deterministic rules pin
  phages/false-positives Low and floor configured high-risk pathogens at High;
  the LLM adds reasoning, it does not lower a deterministic verdict.
- **Marker in this run:** `risk_summary.mode = "llm"`; every `top_risks[i].reasons`
  begins with `[LLM] …` (e.g. "[LLM] Matches the high-risk pathogen list
  (Betacoronavirus) …"). **→ fired.**

## 4. narrative — llm_interpretation (the report's AI section)

- **Node:** `metamavs/agents/llm_interpretation_agent.py`
- **Trigger (`:30`, `:35`):**
  ```python
  if not llm_cfg.get("enabled"):       # → status "disabled"
      return {...}
  if not llm_available():              # → status "no_key"
      return {...}
  narrative = generate(SYSTEM_PROMPT, build_user_prompt(state),
                       cached_prefix=SHARED_REFERENCE, **resolve_params(llm_cfg, "llm_interpretation"))
  ```
- **Data condition:** none beyond enabled + available — it always has the whole
  run state to summarise. (Runs after human review is approved.)
- **What the LLM does:** write the public-health narrative
  (`## AI-Assisted Interpretation`) that `report_writer` embeds. See
  [`DATA_FLOW_AND_PROMPTS.md`](DATA_FLOW_AND_PROMPTS.md).
- **Marker in this run:** `llm_narrative.status = "ok"`, `model = "gemma-4-E2B-it"`;
  log `Generating LLM surveillance narrative` → `LLM ok (gemma:…)`. **→ fired.**

---

## Order in the graph

```
… → taxonomy_agent → abundance_agent → novel_virus_agent → risk_assessment_agent
     → human_review (approve) → llm_interpretation → report_writer → END
```

`taxonomy`, `abundance`, `risk` fire during the main pass (before the review
pause); `llm_interpretation` fires after approval, right before the report is
written. Each is independent — one skipping never blocks the others.

---

## Why the other two didn't fire (for contrast)

| Agent | Data condition | This run | Result |
|---|---|---|---|
| `qc` | real QC metrics (note not "synthetic") | QC tools off; `note` = "…synthetic placeholders…" | guard skips (`qc_agent.py:_llm_qc`) |
| `novel_virus` | real assembly candidates | assembly off; `n_candidates = 0`, synthetic | skipped |

Both are gated so the LLM never interprets placeholder data — consistent with the
"do not invent metrics / do not overstate" caution rules. To make all six fire,
run QC (`fastqc`/`fastp`) and assembly + novel screening as real steps in
`hpc.steps`.

---

## Evidence summary (from `reports/sapelo2_genome72/state.json`)

| Agent | Marker | Fired |
|---|---|---|
| taxonomy | `taxonomy_summary.mode = llm+ncbi` | ✅ |
| abundance | `trend_summary.mode = llm` | ✅ |
| risk | `risk_summary.mode = llm`, `[LLM]` in reasons | ✅ |
| narrative | `llm_narrative.status = ok`, model gemma-4-E2B-it | ✅ |
| qc | `qc_summary.llm_assessment = None` | ❌ |
| novel_virus | `novel_candidate_summary.mode = deterministic` | ❌ |
