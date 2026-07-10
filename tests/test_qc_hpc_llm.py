"""QC LLM adequacy assessment fires on REAL FastQC data (HPC path)."""

from __future__ import annotations

import metamavs.agents.qc_agent as qc_agent
from metamavs.agents.qc_agent import llm_qc_assessment


def _state():
    return {"config": {"llm": {"enabled": True}}}


def _real_qc():
    return {"per_sample": [{"sample_id": "S1", "mean_quality": 36.0, "total_reads": 1_500_000}],
            "note": "Parsed from real FastQC output."}


def test_synthetic_qc_is_skipped(monkeypatch):
    monkeypatch.setattr(qc_agent, "llm_available", lambda: True)
    monkeypatch.setattr(qc_agent, "generate", lambda *a, **k: "should not be called")
    qc = {"per_sample": [{"sample_id": "S1"}], "note": "Metrics are synthetic placeholders in dry-run mode."}
    assert llm_qc_assessment(_state(), qc) is None


def test_real_qc_fires(monkeypatch):
    monkeypatch.setattr(qc_agent, "llm_available", lambda: True)
    monkeypatch.setattr(qc_agent, "generate", lambda *a, **k: "Adequate depth; proceed.")
    assert llm_qc_assessment(_state(), _real_qc()) == "Adequate depth; proceed."


def test_disabled_returns_none(monkeypatch):
    monkeypatch.setattr(qc_agent, "llm_available", lambda: True)
    monkeypatch.setattr(qc_agent, "generate", lambda *a, **k: "x")
    assert llm_qc_assessment({"config": {"llm": {"enabled": False}}}, _real_qc()) is None
