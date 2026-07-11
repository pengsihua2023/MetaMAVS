#!/usr/bin/env python3
"""Report which of the six MetaMAVS LLM agents fired in a run.

Reads a run's saved state and checks each agent's ``mode`` / assessment marker.
Before approval only 5 agents can have fired (``paused_state.json``); the 6th
(narrative) fires after ``metamavs review --approve`` (``state.json``). This
script auto-selects whichever state file exists.

Usage:
    python scripts/check_agents.py [--run-dir reports/sapelo2_genome72_full]
"""

from __future__ import annotations

import argparse
import json
import os
import sys


def _load_state(run_dir: str) -> tuple[dict, str]:
    for name in ("state.json", "paused_state.json"):  # prefer final state
        path = os.path.join(run_dir, name)
        if os.path.exists(path):
            return json.loads(open(path).read()), name
    print(f"ERROR: no state.json / paused_state.json in {run_dir}", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-dir", default="reports/sapelo2_genome72_full",
                    help="Run directory containing state.json / paused_state.json.")
    args = ap.parse_args()

    s, src = _load_state(args.run_dir)
    mark = lambda x: "✅ fired" if x else "❌ not fired"

    qc = s.get("qc_summary") or {}
    tax = s.get("taxonomy_summary") or {}
    tr = s.get("trend_summary") or {}
    nv = s.get("novel_candidate_summary") or {}
    rs = s.get("risk_summary") or {}
    na = s.get("llm_narrative") or {}
    post_approval = src == "state.json" and na.get("status") == "ok"

    print(f"# source: {src}   run: {args.run_dir}\n")
    print(f"1. qc          : {mark(bool(qc.get('llm_assessment')))}   note={qc.get('note')!r}")
    print(f"2. taxonomy    : {mark(tax.get('mode') in ('llm', 'llm+ncbi'))}   mode={tax.get('mode')}")
    print(f"3. abundance   : {mark(tr.get('mode') == 'llm')}   mode={tr.get('mode')}")
    print(f"4. novel_virus : {mark(nv.get('mode') == 'llm')}   "
          f"n={nv.get('n_candidates')} from_checkv={nv.get('n_candidates_from_checkv')} "
          f"known_filtered={nv.get('n_known_virus_filtered')} novelty_checked={nv.get('novelty_checked')}")
    print(f"5. risk        : {mark(rs.get('mode') == 'llm')}   overall={rs.get('overall_risk')}")
    if post_approval:
        print(f"6. narrative   : {mark(na.get('status') == 'ok')}   model={na.get('model')}")
    else:
        print("6. narrative   : ⏳ fires after `metamavs review --approve`")

    fired = sum([
        bool(qc.get("llm_assessment")),
        tax.get("mode") in ("llm", "llm+ncbi"),
        tr.get("mode") == "llm",
        nv.get("mode") == "llm",
        rs.get("mode") == "llm",
        na.get("status") == "ok",
    ])
    total = 6 if post_approval else 5
    print(f"\n=> {fired} agent(s) fired ({'post-approval' if post_approval else 'pre-approval; 5 checkable'}).")
    if nv.get("note"):
        print(f"   novel_virus: {nv.get('note')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
