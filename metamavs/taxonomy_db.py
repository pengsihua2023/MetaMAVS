"""NCBI Taxonomy lookup (E-utilities efetch) — verified lineage for taxids.

Grounds the taxonomy/risk LLM agents in authoritative data instead of model
memory. Optional and fully defensive: disabled by default, one batched HTTP
request, in-process cache, and any network/parse failure returns ``{}`` so the
pipeline degrades to deterministic + memory-based behaviour.

Runs on the LOCAL controller (which has internet); the HPC compute path is
untouched.
"""

from __future__ import annotations

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from .utils.logging_utils import get_logger

logger = get_logger("taxonomy_db")

_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
_CACHE: dict[int, dict] = {}


def _parse_taxon(taxon: ET.Element) -> dict:
    name = taxon.findtext("ScientificName", "")
    rank = taxon.findtext("Rank", "")
    division = taxon.findtext("Division", "")
    lineage = taxon.findtext("Lineage", "")
    superkingdom = ""
    for t in taxon.findall("./LineageEx/Taxon"):
        if t.findtext("Rank", "") == "superkingdom":
            superkingdom = t.findtext("ScientificName", "")
            break
    return {
        "ncbi_name": name,
        "rank": rank,
        "division": division,           # e.g. "Phages", "Viruses", "Bacteria"
        "superkingdom": superkingdom,    # e.g. "Viruses"
        "lineage": lineage,
        "is_phage": division.strip().lower() == "phages",
        "is_viral": superkingdom.strip().lower() in {"viruses", "viroids"} or "virus" in division.lower(),
    }


def fetch_lineages(
    taxids: list[int], *, api_key: str | None = None, email: str | None = None, timeout_s: int = 15
) -> dict[int, dict]:
    """Return {taxid: lineage_info} from NCBI Taxonomy. ``{}`` on any failure.

    Batches all (positive, uncached) taxids into a single efetch request.
    """

    want = sorted({int(t) for t in taxids if int(t or 0) > 0})
    missing = [t for t in want if t not in _CACHE]

    if missing:
        params = {"db": "taxonomy", "id": ",".join(str(t) for t in missing),
                  "retmode": "xml", "tool": "MetaMAVS"}
        if email:
            params["email"] = email
        if api_key:
            params["api_key"] = api_key
        url = f"{_EFETCH}?{urllib.parse.urlencode(params)}"
        try:
            with urllib.request.urlopen(url, timeout=timeout_s) as resp:  # noqa: S310 - fixed NCBI host
                root = ET.fromstring(resp.read())
            found = 0
            for taxon in root.findall("Taxon"):
                try:
                    tid = int(taxon.findtext("TaxId", "0") or 0)
                except ValueError:
                    continue
                if tid:
                    _CACHE[tid] = _parse_taxon(taxon)
                    found += 1
            logger.info("NCBI Taxonomy: fetched %d/%d lineage(s)", found, len(missing))
        except Exception as exc:  # network, timeout, XML, etc.
            logger.warning("NCBI Taxonomy lookup failed (%s) — using memory/deterministic only", exc)
            return {}

    return {t: _CACHE[t] for t in want if t in _CACHE}
