"""Tests for high-risk pathogen matching (taxid + name aliases)."""

from __future__ import annotations

from metamavs.pathogens import match_high_risk

CONFIG = ["SARS-CoV-2", "Influenza A virus", "Influenza B virus", "Norovirus", "Enterovirus"]


def test_match_sars_by_full_name():
    # GOTTCHA2's full name must map to the configured "SARS-CoV-2".
    assert match_high_risk("Severe acute respiratory syndrome-related coronavirus", 694009, CONFIG) == "SARS-CoV-2"


def test_match_sars_by_taxid_even_if_name_unusual():
    assert match_high_risk("some odd coronavirus label", 2697049, CONFIG) == "SARS-CoV-2"


def test_match_norovirus_via_norwalk():
    assert match_high_risk("Norwalk virus", 11983, CONFIG) == "Norovirus"


def test_match_influenza():
    assert match_high_risk("Influenza A virus", 11320, CONFIG) == "Influenza A virus"


def test_enterovirus_aliases():
    assert match_high_risk("Coxsackievirus B3", 0, CONFIG) == "Enterovirus"


def test_non_pathogen_returns_none():
    assert match_high_risk("Escherichia phage T4", 10665, CONFIG) is None
    assert match_high_risk("Pepper mild mottle virus", 12239, CONFIG) is None


def test_literal_fallback_for_custom_entry():
    # A custom config entry not in the alias DB still matches by substring.
    assert match_high_risk("Monkeypox virus strain X", 0, ["Monkeypox virus"]) == "Monkeypox virus"


def test_only_considers_configured_pathogens():
    # SARS not in the configured list -> not matched.
    assert match_high_risk("Severe acute respiratory syndrome-related coronavirus", 694009, ["Norovirus"]) is None
