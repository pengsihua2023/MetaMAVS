"""Tests for NCBI Taxonomy lookup (network mocked — never hits NCBI)."""

from __future__ import annotations

import contextlib

import pandas as pd

import metamavs.taxonomy_db as tdb
from metamavs.agents.taxonomy_agent import taxonomy_classification_agent_node

_XML = b"""<?xml version="1.0"?>
<TaxaSet>
  <Taxon>
    <TaxId>10665</TaxId>
    <ScientificName>Tequatrovirus T4</ScientificName>
    <Rank>species</Rank>
    <Division>Phages</Division>
    <Lineage>Viruses; Duplodnaviria; Caudoviricetes; Straboviridae; Tequatrovirus</Lineage>
    <LineageEx>
      <Taxon><TaxId>10239</TaxId><ScientificName>Viruses</ScientificName><Rank>superkingdom</Rank></Taxon>
    </LineageEx>
  </Taxon>
  <Taxon>
    <TaxId>2697049</TaxId>
    <ScientificName>SARS-CoV-2</ScientificName>
    <Rank>species</Rank>
    <Division>Viruses</Division>
    <Lineage>Viruses; Riboviria; Nidovirales; Coronaviridae; Betacoronavirus</Lineage>
    <LineageEx>
      <Taxon><TaxId>10239</TaxId><ScientificName>Viruses</ScientificName><Rank>superkingdom</Rank></Taxon>
    </LineageEx>
  </Taxon>
</TaxaSet>"""


class _FakeResp:
    def __init__(self, data): self._data = data
    def read(self): return self._data
    def __enter__(self): return self
    def __exit__(self, *a): return False


def _patch_ok(monkeypatch):
    tdb._CACHE.clear()
    monkeypatch.setattr(tdb.urllib.request, "urlopen", lambda *a, **k: _FakeResp(_XML))


def test_fetch_lineages_parses_division_and_lineage(monkeypatch):
    _patch_ok(monkeypatch)
    res = tdb.fetch_lineages([10665, 2697049])
    assert res[10665]["is_phage"] is True
    assert res[10665]["division"] == "Phages"
    assert res[10665]["superkingdom"] == "Viruses"
    assert "Straboviridae" in res[10665]["lineage"]
    assert res[2697049]["is_phage"] is False
    assert res[2697049]["division"] == "Viruses"


def test_fetch_lineages_caches(monkeypatch):
    _patch_ok(monkeypatch)
    tdb.fetch_lineages([10665])
    calls = {"n": 0}
    def _count(*a, **k):
        calls["n"] += 1
        return _FakeResp(_XML)
    monkeypatch.setattr(tdb.urllib.request, "urlopen", _count)
    tdb.fetch_lineages([10665])           # cached -> no new request
    assert calls["n"] == 0


def test_fetch_lineages_network_failure_returns_empty(monkeypatch):
    tdb._CACHE.clear()
    def _boom(*a, **k):
        raise OSError("network down")
    monkeypatch.setattr(tdb.urllib.request, "urlopen", _boom)
    assert tdb.fetch_lineages([10665]) == {}


def test_taxonomy_agent_uses_ncbi_authoritative_phage(tmp_path, monkeypatch):
    (tmp_path / "tables").mkdir()
    (tmp_path / "intermediate").mkdir()
    cand = tmp_path / "candidate_viral_taxa.csv"
    # Name has NO "phage" keyword -> deterministic keyword matcher would miss it.
    pd.DataFrame([{"taxon_name": "Tequatrovirus T4", "family": "Straboviridae",
                   "taxid": 10665, "total_reads": 500, "max_confidence": 0.99}]).to_csv(cand, index=False)
    _patch_ok(monkeypatch)
    state = {"run_dir": str(tmp_path), "candidate_viral_taxa_path": str(cand),
             "config": {"ncbi": {"enabled": True, "email": "t@e.com"}, "llm": {"enabled": False}}}
    out = taxonomy_classification_agent_node(state)
    assert "ncbi" in out["taxonomy_summary"]["mode"]
    df = pd.read_csv(out["cleaned_taxonomy_table_path"])
    row = df.iloc[0]
    assert bool(row["is_phage"]) is True              # from NCBI Division=Phages, not the name
    assert row["ncbi_division"] == "Phages"
    assert "Straboviridae" in str(row["ncbi_lineage"])
