"""Tests for the LLM-as-agent taxonomy & risk paths (with safety-rail clamps)."""

from __future__ import annotations

import pandas as pd

import metamavs.agents.risk_assessment_agent as risk_mod
import metamavs.agents.taxonomy_agent as tax_mod
from metamavs.agents.risk_assessment_agent import _clamp_llm_risk, risk_assessment_agent_node
from metamavs.agents.taxonomy_agent import taxonomy_classification_agent_node


# ---- safety-rail clamp -----------------------------------------------------
def test_clamp_phage_pinned_low_even_if_llm_says_critical():
    assert _clamp_llm_risk("Critical", is_phage=True, flagged=False, is_known=False) == "Low"


def test_clamp_false_positive_pinned_low():
    assert _clamp_llm_risk("High", is_phage=False, flagged=True, is_known=False) == "Low"


def test_clamp_known_pathogen_floored_at_high():
    # LLM tries to downgrade a configured high-risk pathogen -> floored to High.
    assert _clamp_llm_risk("Low", is_phage=False, flagged=False, is_known=True) == "High"
    # LLM may still escalate above the floor.
    assert _clamp_llm_risk("Critical", is_phage=False, flagged=False, is_known=True) == "Critical"


def test_clamp_middle_ground_trusts_llm():
    assert _clamp_llm_risk("Medium", is_phage=False, flagged=False, is_known=False) == "Medium"


# ---- taxonomy LLM augmentation (union: only adds caution) -------------------
def _candidates_csv(tmp_path):
    p = tmp_path / "candidate_viral_taxa.csv"
    pd.DataFrame([
        {"taxon_name": "Mystery virus X", "family": "unclassified", "taxid": 0,
         "total_reads": 800, "max_confidence": 0.9},  # deterministic: not phage, not FP
    ]).to_csv(p, index=False)
    return p


def test_taxonomy_llm_adds_phage_flag(tmp_path, monkeypatch):
    (tmp_path / "tables").mkdir()
    (tmp_path / "intermediate").mkdir()
    cand = _candidates_csv(tmp_path)
    state = {"run_dir": str(tmp_path), "candidate_viral_taxa_path": str(cand),
             "config": {"llm": {"enabled": True}}}
    monkeypatch.setattr(tax_mod, "llm_available", lambda: True)
    monkeypatch.setattr(tax_mod, "generate_json", lambda *a, **k: {
        "taxa": [{"taxon_name": "Mystery virus X", "category": "phage",
                  "is_phage": True, "false_positive": False, "rationale": "LLM: looks like a phage"}]})
    out = taxonomy_classification_agent_node(state)
    assert out["taxonomy_summary"]["mode"] == "llm"
    df = pd.read_csv(out["cleaned_taxonomy_table_path"])
    row = df[df["taxon_name"] == "Mystery virus X"].iloc[0]
    assert bool(row["is_phage"]) is True                 # LLM added the phage flag
    assert "phage" in str(row["llm_rationale"]).lower()


# ---- risk LLM path with clamping -------------------------------------------
def test_risk_llm_used_with_reasoning_and_clamp(tmp_path, monkeypatch):
    (tmp_path / "tables").mkdir()
    (tmp_path / "intermediate").mkdir()
    tax = tmp_path / "cleaned_taxonomy_table.csv"
    pd.DataFrame([
        {"taxon_name": "SARS-CoV-2", "taxid": 2697049, "total_reads": 600,
         "is_phage": False, "false_positive_flag": False},
        {"taxon_name": "Random virus Y", "taxid": 0, "total_reads": 700,
         "is_phage": False, "false_positive_flag": False},
    ]).to_csv(tax, index=False)
    state = {"run_dir": str(tmp_path), "cleaned_taxonomy_table_path": str(tax),
             "config": {"risk": {"high_risk_pathogens": ["SARS-CoV-2"]}, "llm": {"enabled": True}}}
    monkeypatch.setattr(risk_mod, "llm_available", lambda: True)
    # LLM under-calls SARS (Low) and calls Random virus Medium.
    monkeypatch.setattr(risk_mod, "generate_json", lambda *a, **k: {"assessments": [
        {"taxon_name": "SARS-CoV-2", "risk_level": "Low", "reasoning": "LLM thinks low"},
        {"taxon_name": "Random virus Y", "risk_level": "Medium", "reasoning": "moderate support"},
    ]})
    out = risk_assessment_agent_node(state)
    assert out["risk_summary"]["mode"] == "llm"
    rows = {r["taxon_name"]: r for r in out["risk_summary"]["top_risks"]}
    # SARS clamped UP to High despite LLM saying Low (safety rail).
    assert rows["SARS-CoV-2"]["risk_level"] == "High"
    assert "safety rails" in rows["SARS-CoV-2"]["reasons"]
    # Middle-ground taxon keeps the LLM's call + reasoning.
    assert rows["Random virus Y"]["risk_level"] == "Medium"
    assert "[LLM]" in rows["Random virus Y"]["reasons"]


def test_risk_deterministic_when_llm_disabled(tmp_path):
    (tmp_path / "tables").mkdir()
    (tmp_path / "intermediate").mkdir()
    tax = tmp_path / "cleaned_taxonomy_table.csv"
    pd.DataFrame([{"taxon_name": "SARS-CoV-2", "taxid": 2697049, "total_reads": 600,
                   "is_phage": False, "false_positive_flag": False}]).to_csv(tax, index=False)
    state = {"run_dir": str(tmp_path), "cleaned_taxonomy_table_path": str(tax),
             "config": {"risk": {"high_risk_pathogens": ["SARS-CoV-2"]}, "llm": {"enabled": False}}}
    out = risk_assessment_agent_node(state)
    assert out["risk_summary"]["mode"] == "deterministic"
    assert out["risk_summary"]["overall_risk"] == "High"
