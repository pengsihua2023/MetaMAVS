"""Tests for the LLM literature/reference context."""

from __future__ import annotations

from metamavs.llm.reference import SHARED_REFERENCE, pathogen_snippets
from metamavs.llm.prompts import build_risk_user


def test_shared_reference_large_enough_to_cache():
    # Needs to exceed Anthropic's ~1024-token cache minimum to engage caching.
    assert len(SHARED_REFERENCE) // 4 > 1024
    low = SHARED_REFERENCE.lower()
    assert "pmmov" in low and "normalization" in low
    assert "detected sequence signal" in low
    assert "confirm" in low


def test_pathogen_snippets_match_full_taxonomic_names():
    snippets = pathogen_snippets([
        "Severe acute respiratory syndrome-related coronavirus",
        "Norwalk virus", "Enterovirus C", "Sapporo virus", "Human mastadenovirus F",
    ])
    joined = " ".join(snippets).lower()
    assert "sars-cov-2" in joined
    assert "norovirus" in joined
    assert "enterovirus" in joined
    assert "sapovirus" in joined
    assert "adenovirus" in joined


def test_pathogen_snippets_deduplicate():
    # Two enterovirus species -> one enterovirus snippet.
    snippets = pathogen_snippets(["Enterovirus C", "Enterovirus D"])
    assert len(snippets) == 1


def test_risk_user_prompt_weaves_in_reference():
    prompt = build_risk_user([{"taxon_name": "Norwalk virus", "total_reads": 26}])
    assert "Reference notes" in prompt
    assert "Norovirus" in prompt
