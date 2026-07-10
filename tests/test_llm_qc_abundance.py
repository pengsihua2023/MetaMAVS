"""Tests for the qc & abundance LLM-agent layers (mocked LLM)."""

from __future__ import annotations

import metamavs.agents.abundance_agent as ab_mod
import metamavs.agents.qc_agent as qc_mod
from metamavs.agents.qc_agent import llm_qc_assessment


def test_qc_llm_disabled_returns_none():
    assert llm_qc_assessment({"config": {"llm": {"enabled": False}}}, {"per_sample": [{"x": 1}]}) is None


def test_qc_llm_no_metrics_returns_none(monkeypatch):
    monkeypatch.setattr(qc_mod, "llm_available", lambda: True)
    assert llm_qc_assessment({"config": {"llm": {"enabled": True}}}, {"per_sample": []}) is None


def test_qc_llm_generates(monkeypatch):
    monkeypatch.setattr(qc_mod, "llm_available", lambda: True)
    monkeypatch.setattr(qc_mod, "generate", lambda *a, **k: "Depth is adequate; one sample borderline.")
    out = llm_qc_assessment({"config": {"llm": {"enabled": True}}},
                  {"per_sample": [{"sample_id": "s1", "mean_quality": 36, "total_reads": 2_000_000}]})
    assert "adequate" in out


def test_abundance_llm_interpretation(tmp_path, monkeypatch):
    (tmp_path / "tables").mkdir()
    (tmp_path / "intermediate").mkdir()
    import pandas as pd
    raw = tmp_path / "raw_viral_hits.csv"
    pd.DataFrame([
        {"sample_id": "s1", "taxon_name": "Norovirus", "family": "Caliciviridae", "taxid": 11983,
         "genome_length_kb": 7.6, "reads": 500, "confidence": 0.9, "tool": "gottcha2"},
        {"sample_id": "s2", "taxon_name": "Norovirus", "family": "Caliciviridae", "taxid": 11983,
         "genome_length_kb": 7.6, "reads": 1500, "confidence": 0.9, "tool": "gottcha2"},
    ]).to_csv(raw, index=False)
    state = {"run_dir": str(tmp_path), "raw_viral_hits_path": str(raw),
             "qc_summary": {"per_sample": [{"sample_id": "s1", "total_reads": 1_000_000},
                                            {"sample_id": "s2", "total_reads": 1_000_000}]},
             "config": {"llm": {"enabled": True}}}
    monkeypatch.setattr(ab_mod, "llm_available", lambda: True)
    monkeypatch.setattr(ab_mod, "generate", lambda *a, **k: "Norovirus rising across two timepoints; monitor.")
    out = ab_mod.abundance_analysis_agent_node(state)
    assert out["trend_summary"].get("mode") == "llm"
    assert "monitor" in out["trend_summary"]["llm_interpretation"]


def test_abundance_deterministic_when_disabled(tmp_path):
    (tmp_path / "tables").mkdir()
    (tmp_path / "intermediate").mkdir()
    import pandas as pd
    raw = tmp_path / "raw_viral_hits.csv"
    pd.DataFrame([{"sample_id": "s1", "taxon_name": "Norovirus", "family": "Caliciviridae",
                   "taxid": 11983, "genome_length_kb": 7.6, "reads": 500, "confidence": 0.9,
                   "tool": "gottcha2"}]).to_csv(raw, index=False)
    state = {"run_dir": str(tmp_path), "raw_viral_hits_path": str(raw),
             "qc_summary": {}, "config": {"llm": {"enabled": False}}}
    out = ab_mod.abundance_analysis_agent_node(state)
    assert "llm_interpretation" not in out["trend_summary"]
