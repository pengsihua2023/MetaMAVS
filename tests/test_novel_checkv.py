"""CheckV contigs -> novel-virus candidates (real HPC-mode path)."""

from __future__ import annotations

from metamavs.agents.novel_virus_agent import novel_virus_screening_agent_node
from metamavs.agents.tool_output_parser_agent import tool_output_parser_agent_node
from metamavs.state import MetaMAVSState


def test_checkv_contigs_is_declared_in_state():
    # Must be a declared channel or LangGraph drops the parser's update, so
    # novel_virus never sees the CheckV contigs (integration regression guard).
    assert "checkv_contigs" in MetaMAVSState.__annotations__


def _novel_state(tmp_path, checkv_contigs, contig_homology=None):
    return {
        "config": {
            "execution": {"dry_run": True, "mode": "local"},
            "tools": {"assembly": {"enabled": True, "assembler": "megahit"},
                      "novel_virus_screening": {"enabled": True, "tools": ["checkv"],
                                                "novelty_min_pident": 90.0}},
            "llm": {"enabled": False},
        },
        "run_id": "t", "run_dir": str(tmp_path),
        "checkv_contigs": checkv_contigs,
        "contig_homology": contig_homology or {},
    }


def test_homology_splits_known_from_suspected_novel(tmp_path):
    from metamavs.parsers.contig_homology import parse_contig_homology
    contigs = [
        {"sample_id": "S1", "contig_id": "k1", "checkv_quality": "High-quality",
         "completeness": 95.0, "viral_genes": 9, "tool": "checkv"},   # known (95% hit)
        {"sample_id": "S1", "contig_id": "k2", "checkv_quality": "High-quality",
         "completeness": 88.0, "viral_genes": 7, "tool": "checkv"},   # divergent (55% hit)
        {"sample_id": "S1", "contig_id": "k3", "checkv_quality": "Medium-quality",
         "completeness": 60.0, "viral_genes": 4, "tool": "checkv"},   # no hit
    ]
    homology = {"k1": {"contig_id": "k1", "subject": "known|virusA", "pident": 95.0},
                "k2": {"contig_id": "k2", "subject": "known|virusB", "pident": 55.0}}
    out = novel_virus_screening_agent_node(_novel_state(tmp_path, contigs, homology))
    nv = out["novel_candidate_summary"]
    assert nv["novelty_checked"] is True
    assert nv["n_known_virus_filtered"] == 1          # k1 excluded (>=90%)
    assert nv["n_candidates"] == 2                    # k2 (divergent) + k3 (no hit)
    taxa = {c["putative_taxon"] for c in nv["candidates"]}
    assert "assembled viral contig k1" not in taxa
    assert "assembled viral contig k2" in taxa
    assert any("55%" in c["evidence"] for c in nv["candidates"])
    assert any("no known-virus" in c["evidence"] for c in nv["candidates"])


def test_no_homology_marks_novelty_unverified(tmp_path):
    contigs = [{"sample_id": "S1", "contig_id": "k1", "checkv_quality": "High-quality",
                "completeness": 91.0, "viral_genes": 7, "tool": "checkv"}]
    out = novel_virus_screening_agent_node(_novel_state(tmp_path, contigs))  # no homology
    nv = out["novel_candidate_summary"]
    assert nv["novelty_checked"] is False
    assert nv["n_candidates"] == 1
    assert any("NOT verified" in c["evidence"] for c in nv["candidates"])


def test_parse_contig_homology_best_hit(tmp_path):
    from metamavs.parsers.contig_homology import parse_contig_homology
    tsv = tmp_path / "S1.contig_homology.tsv"
    tsv.write_text(
        "k1\tvirusA\t80.0\t1e-40\t200\n"
        "k1\tvirusB\t95.0\t1e-60\t320\n"   # better bitscore -> best for k1
        "k2\tvirusC\t60.0\t1e-20\t120\n",
        encoding="utf-8",
    )
    r = parse_contig_homology(str(tsv), "S1")
    assert r["result"].ok
    best = {rec["contig_id"]: rec for rec in r["records"]}
    assert best["k1"]["subject"] == "virusB" and best["k1"]["pident"] == 95.0
    assert best["k2"]["subject"] == "virusC"


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
    assert "assembled viral contig k141_1" in names
    assert "assembled viral contig k141_3" in names
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
