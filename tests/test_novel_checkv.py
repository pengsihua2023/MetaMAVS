"""CheckV contigs -> novel-virus candidates (real HPC-mode path)."""

from __future__ import annotations

from metamavs.agents.novel_virus_agent import novel_virus_screening_agent_node
from metamavs.agents.tool_output_parser_agent import tool_output_parser_agent_node
from metamavs.state import MetaMAVSState


def test_checkv_contigs_is_declared_in_state():
    # Must be a declared channel or LangGraph drops the parser's update, so
    # novel_virus never sees the CheckV contigs (integration regression guard).
    assert "checkv_contigs" in MetaMAVSState.__annotations__


def _novel_state(tmp_path, checkv_contigs):
    return {
        "config": {
            "execution": {"dry_run": True, "mode": "local"},
            "tools": {"assembly": {"enabled": True, "assembler": "megahit"},
                      "novel_virus_screening": {"enabled": True, "tools": ["checkv"]}},
            "llm": {"enabled": False},
        },
        "run_id": "t", "run_dir": str(tmp_path),
        "checkv_contigs": checkv_contigs,
    }


def test_good_checkv_contig_becomes_candidate(tmp_path):
    contigs = [
        {"sample_id": "S1", "contig_id": "k141_1", "checkv_quality": "High-quality",
         "completeness": 88.0, "viral_genes": 12, "tool": "checkv"},
        {"sample_id": "S1", "contig_id": "k141_2", "checkv_quality": "Low-quality",
         "completeness": 10.0, "viral_genes": 1, "tool": "checkv"},  # dropped
        {"sample_id": "S1", "contig_id": "k141_3", "checkv_quality": "Not-determined",
         "completeness": 62.0, "viral_genes": 4, "tool": "checkv"},  # kept via completeness>=50
    ]
    out = novel_virus_screening_agent_node(_novel_state(tmp_path, contigs))
    summary = out["novel_candidate_summary"]
    assert summary["n_candidates_from_checkv"] == 2
    assert summary["n_candidates"] == 2
    names = {c["putative_taxon"] for c in summary["candidates"]}
    assert "assembled contig k141_1" in names
    assert "assembled contig k141_3" in names
    assert "real CheckV contigs" in summary["note"]


def test_llm_candidate_list_is_capped(tmp_path, monkeypatch):
    import metamavs.agents.novel_virus_agent as nva
    seen = {}
    monkeypatch.setattr(nva, "llm_available", lambda: True)
    monkeypatch.setattr(nva, "build_novel_user", lambda cands: seen.setdefault("n", len(cands)) or "u")
    monkeypatch.setattr(nva, "generate_json", lambda *a, **k: {"assessments": []})
    contigs = [{"sample_id": "S1", "contig_id": f"k{i}", "checkv_quality": "High-quality",
                "completeness": 90.0 - i, "viral_genes": 5, "tool": "checkv"} for i in range(20)]
    st = _novel_state(tmp_path, contigs)
    st["config"]["llm"] = {"enabled": True}
    out = nva.novel_virus_screening_agent_node(st)
    assert seen["n"] <= nva._LLM_MAX_CANDIDATES         # only the top N go to the LLM
    assert out["novel_candidate_summary"]["n_candidates"] == 20   # table keeps all
    assert out["novel_candidate_summary"]["mode"] == "llm"


def test_no_checkv_contigs_is_unchanged(tmp_path):
    out = novel_virus_screening_agent_node(_novel_state(tmp_path, []))
    summary = out["novel_candidate_summary"]
    assert summary["n_candidates_from_checkv"] == 0
    assert "synthetic taxonomy" in summary["note"]


def test_parser_stores_checkv_contigs(tmp_path):
    tsv = tmp_path / "S1.checkv_quality_summary.tsv"
    tsv.write_text(
        "contig_id\tcheckv_quality\tcompleteness\tviral_genes\n"
        "k141_1\tHigh-quality\t88.0\t12\n"
        "k141_2\tComplete\t100.0\t20\n",
        encoding="utf-8",
    )
    for sub in ("tables", "intermediate", "results"):
        (tmp_path / sub).mkdir(parents=True, exist_ok=True)
    state = {
        "run_id": "t", "run_dir": str(tmp_path),
        "synced_manifest": {"downloaded": [{"local_path": str(tsv), "ok": True}]},
    }
    out = tool_output_parser_agent_node(state)
    assert "checkv_contigs" in out
    assert len(out["checkv_contigs"]) == 2
    assert out["checkv_contigs"][0]["checkv_quality"] == "High-quality"
