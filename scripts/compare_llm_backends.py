#!/usr/bin/env python3
"""Compare LLM backends (Gemma vs Claude) on REAL MetaMAVS results.

This is the Phase-B validation harness: it does NOT re-run any bioinformatics
tool and never touches the HPC cluster. It loads a *completed* run's saved
``state.json`` (which already holds the REAL parsed taxonomy / abundance / risk
tables from a Sapelo2 GOTTCHA2 run) and re-runs only the LLM interpretation
layer under each backend, so the two narratives are produced from the exact same
real inputs. Outputs are written side by side for review.

Usage
-----
    # default: reuse the cached real Sapelo2 run, compare both backends
    python scripts/compare_llm_backends.py

    # explicit
    python scripts/compare_llm_backends.py \
        --state reports/sapelo2_genome72/state.json \
        --backends gemma,claude \
        --outdir reports/llm_backend_comparison

Requirements
------------
- gemma: a local llama-server on http://localhost:8080/v1 (--jinja) + `openai`.
- claude: ANTHROPIC_API_KEY in .env (paid) + `anthropic`. Skipped gracefully if
  the key/SDK is absent, so the harness still runs Gemma-only.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def _run_one(state: dict, backend: str, outdir: Path) -> dict:
    """Run the LLM interpretation node under one backend; return a result dict."""

    os.environ["LLM_BACKEND"] = backend  # read fresh by llm.client._backend()

    # Import lazily and AFTER setting the env so availability reflects the backend.
    from metamavs.llm import llm_available
    from metamavs.agents.llm_interpretation_agent import llm_interpretation_agent_node

    if not llm_available():
        return {"backend": backend, "status": "unavailable",
                "note": "backend SDK/key/server not available — skipped"}

    st = copy.deepcopy(state)
    bdir = outdir / backend
    (bdir / "intermediate").mkdir(parents=True, exist_ok=True)
    st["run_dir"] = str(bdir)

    t0 = time.time()
    out = llm_interpretation_agent_node(st)
    elapsed = time.time() - t0

    narrative = (out.get("llm_narrative") or {})
    text = narrative.get("text", "")
    md = bdir / "intermediate" / "llm_narrative.md"
    if text:
        md.write_text(text, encoding="utf-8")
    return {
        "backend": backend,
        "status": narrative.get("status"),
        "model": narrative.get("model"),
        "elapsed_s": round(elapsed, 1),
        "words": len(text.split()) if text else 0,
        "chars": len(text),
        "narrative_path": str(md) if text else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", default="reports/sapelo2_genome72/state.json",
                    help="Path to a completed run's state.json (REAL results).")
    ap.add_argument("--backends", default="gemma,claude",
                    help="Comma-separated backends to compare (default: gemma,claude).")
    ap.add_argument("--outdir", default="reports/llm_backend_comparison",
                    help="Where to write per-backend narratives + summary.")
    args = ap.parse_args()

    state_path = (REPO / args.state) if not Path(args.state).is_absolute() else Path(args.state)
    if not state_path.exists():
        print(f"ERROR: state file not found: {state_path}", file=sys.stderr)
        print("Run the real Sapelo2 pipeline first (see docs/REAL_DATA_VALIDATION.md).",
              file=sys.stderr)
        return 2

    state = json.loads(state_path.read_text())
    # Force the LLM layer on regardless of what the saved config said.
    state.setdefault("config", {}).setdefault("llm", {})["enabled"] = True

    outdir = (REPO / args.outdir) if not Path(args.outdir).is_absolute() else Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    backends = [b.strip().lower() for b in args.backends.split(",") if b.strip()]
    rs = state.get("risk_summary", {})
    print(f"Real input: {state_path}")
    print(f"  overall_risk={rs.get('overall_risk')}  "
          f"n_taxa={state.get('taxonomy_summary', {}).get('n_taxa')}  "
          f"top={[t.get('taxon_name') for t in (rs.get('top_risks') or [])[:3]]}")
    print(f"Backends: {backends}\n")

    results = []
    for b in backends:
        print(f"[{b}] generating narrative on real data ...")
        r = _run_one(state, b, outdir)
        results.append(r)
        print(f"    -> status={r.get('status')} model={r.get('model')} "
              f"words={r.get('words')} elapsed={r.get('elapsed_s')}s")

    summary = {
        "state": str(state_path),
        "overall_risk": rs.get("overall_risk"),
        "top_risks": [t.get("taxon_name") for t in (rs.get("top_risks") or [])[:5]],
        "results": results,
    }
    (outdir / "comparison_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nWrote {outdir/'comparison_summary.json'}")
    for r in results:
        if r.get("narrative_path"):
            print(f"  {r['backend']:7s} narrative: {r['narrative_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
