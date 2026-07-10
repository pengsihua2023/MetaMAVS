# Running the full MetaMAVS pipeline on Sapelo2 (end-to-end)

This guide runs the **entire** MetaMAVS workflow in SSH-controller mode
(**Path A1**): one command submits the GOTTCHA2 job to UGA GACRC **Sapelo2**,
polls it, downloads the results, parses them, runs the taxonomy / abundance /
risk / LLM agents, and produces the final **virus detection report**.

You only run three commands: `remote-check`, `run --execute`, `review`.

---

## How it works

The **controller runs on your local machine** (this WSL host) — not on Sapelo2.
It reaches out to the cluster over SSH for the heavy step and does everything
else locally.

```
  Local controller (WSL)                         Sapelo2 (HPC)
  ┌───────────────────────────────┐   SSH    ┌──────────────────────┐
  │ metamavs run --execute        │ ───────► │ submit GOTTCHA2 job   │
  │  • submit + poll (every 60s)  │ ◄─────── │ run on compute node   │
  │  • download .tsv              │  .tsv    └──────────────────────┘
  │  • parse → taxonomy/abundance │
  │  • risk + LLM interpretation  │  (local Gemma 4 E2B, free)
  │  • pause at human review      │
  └───────────────────────────────┘
            │  metamavs review --approve
            ▼
     report.md / report.html   ← final virus detection report
```

---

## Prerequisites

The **local controller** must have all of:

- **SSH access to Sapelo2** (`sp96859@sapelo2.gacrc.uga.edu`) with Duo 2FA.
- **Internet** — NCBI Taxonomy grounding is on (`ncbi.enabled: true`).
- **An LLM backend:**
  - *Gemma (default, free, local):* a `llama-server` on
    `http://localhost:8080/v1` started with `--jinja`.
  - *Claude (optional, paid):* `ANTHROPIC_API_KEY` in `.env`, and
    `export LLM_BACKEND=claude`.
- The Python env installed: `pip install -e ".[llm]"`.

On the **cluster side**, the config (`configs/sapelo2_config.yaml`) already
points at the real GOTTCHA2 conda env and database; the manifest
(`data/sapelo2_manifest.csv`) already lists the real `Genome_72` FASTQ paths.

> ⚠️ The GOTTCHA2 job takes **hours** and `run --execute` **blocks while
> polling** (up to 24 h). Always run it inside `tmux`/`screen` so a disconnect
> doesn't kill the controller. This step submits a **real cluster job**.

---

## Step 0 — Local setup

```bash
cd /mnt/d/claude-code-project/MetaMAVS

# Confirm the local Gemma server is up (used to write the report, free)
curl -s http://localhost:8080/v1/models >/dev/null && echo "gemma server OK" \
  || echo "!! start llama-server first"

# Choose the LLM backend. Default is gemma (free, local).
export LLM_BACKEND=gemma
# For a Claude-written report instead (paid), use:
# export LLM_BACKEND=claude     # requires ANTHROPIC_API_KEY in .env
```

## Step 1 — HPC readiness check (triggers Duo once)

```bash
.venv/bin/metamavs remote-check --config configs/sapelo2_config.yaml
```

- The first connection prompts for **Duo** (push / passcode); SSH ControlMaster
  reuses it for the rest of the run.
- It verifies SSH connectivity, the scheduler, `remote_base`, and the conda env.
- Proceed only when **every check is `[OK ]`**. Fix any `[FAIL]` first (usually a
  path or conda-env issue).

## Step 2 — Run end-to-end (inside tmux)

```bash
tmux new -s metamavs                 # persistent session (survives disconnects)
cd /mnt/d/claude-code-project/MetaMAVS
export LLM_BACKEND=gemma             # tmux is a fresh shell — set it again

.venv/bin/metamavs run --config configs/sapelo2_config.yaml --execute
```

This automatically: submits GOTTCHA2 → polls every 60 s → downloads the `.tsv` →
parses it into real tables → runs taxonomy / abundance / risk / LLM → then
**pauses and exits** at the human-review checkpoint (`human_review.mode: pause`,
triggered by the High-risk detections).

Detach/reattach without stopping it:

```
Ctrl-b  then  d          # detach, leave it running
tmux attach -t metamavs  # come back
```

Monitor the cluster job from another terminal (optional):

```bash
ssh sp96859@sapelo2.gacrc.uga.edu 'squeue -u sp96859'
```

## Step 3 — Human review → generate the final report

```bash
.venv/bin/metamavs review --run-dir reports/sapelo2_genome72 --approve
```

It prints the detection summary (overall risk, top detections); approving
generates the report. Omit `--approve` to see it first and be prompted `[y/N]`.

## Step 4 — Get the virus detection report

```bash
ls -lh reports/sapelo2_genome72/report.md reports/sapelo2_genome72/report.html

# Open the HTML report in Windows:
explorer.exe "$(wslpath -w reports/sapelo2_genome72/report.html)"
```

Run directory layout:

```
reports/sapelo2_genome72/
  report.md / report.html        ← final virus detection report
  state.json                     ← full state (reuse for backend comparison)
  results/raw/gottcha2/*.tsv     ← the real GOTTCHA2 results fetched back
  tables/  intermediate/  logs/  commands/  remote/
```

---

## Optional — compare LLM backends on this real run

After Step 4 you have real results in `state.json`. Re-run only the LLM layer
under each backend (no cluster access needed) and diff the narratives:

```bash
python scripts/compare_llm_backends.py \
    --state reports/sapelo2_genome72/state.json \
    --backends gemma,claude \
    --outdir reports/llm_backend_comparison
```

See `docs/REAL_DATA_VALIDATION.md` for the acceptance criteria.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `run` sits polling for a long time | Normal — GOTTCHA2 is slow. `squeue` shows `R` while it runs; it only times out after 24 h (`max_wait_s`). |
| Duo prompts repeatedly | ControlMaster isn't active. Check `ssh_control: true`, `ssh_control_path: ~/.ssh/mm-sapelo2`, and that the dir is writable. |
| Controller died mid-run | The cluster job keeps running; `remote/jobs.json` records it, so re-running `run --execute` **re-attaches** instead of resubmitting. |
| Want a Claude-written report | `export LLM_BACKEND=claude` (+ key in `.env`), then repeat Steps 2–3. |
| `OUT_OF_MEMORY` on the job | `bahl_p` node lacked RAM. Raise `hpc.step_resources.gottcha2.mem` or use a highmem partition. |
| `gottcha2.py: command not found` on the job | Fix `hpc.step_env.gottcha2` PATH / conda env in the config. |

---

## Command summary

```bash
cd /mnt/d/claude-code-project/MetaMAVS
export LLM_BACKEND=gemma

.venv/bin/metamavs remote-check --config configs/sapelo2_config.yaml   # 1. check (Duo)
tmux new -s metamavs
.venv/bin/metamavs run     --config configs/sapelo2_config.yaml --execute   # 2. run (hours)
.venv/bin/metamavs review  --run-dir reports/sapelo2_genome72 --approve     # 3. report
```
