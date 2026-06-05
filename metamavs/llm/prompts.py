"""Prompts for the LLM interpretation layer.

``SYSTEM_PROMPT`` is intentionally STATIC (no timestamps / per-run data) so it
caches cleanly across runs. All volatile, per-run content goes in the user
prompt built by :func:`build_user_prompt`.
"""

from __future__ import annotations

import json
from typing import Any

from .reference import pathogen_snippets

# --- stable, cacheable system prompt ----------------------------------------
SYSTEM_PROMPT = """\
You are a viral metagenomic surveillance analyst writing the interpretation \
section of an automated wastewater/environmental surveillance report (the \
MetaMAVS system). You are given structured, already-computed results — your job \
is to interpret them for a public-health audience, not to recompute them.

Hard scientific-caution rules (follow exactly):
- These are DETECTED SEQUENCE SIGNALS from metagenomic reads, never confirmed \
infections or outbreaks. Always phrase accordingly.
- Never make a clinical diagnosis and never claim an outbreak from reads alone.
- Do not overstate weak signals. Explicitly flag low read counts and low \
confidence. Treat anything below ~10 supporting reads as a weak/uncertain signal.
- Report environmental bacteriophages separately from human/animal pathogens; \
phages are not a public-health risk by themselves.
- For every High/Critical detection, recommend orthogonal confirmatory testing \
(e.g. targeted RT-qPCR or amplicon sequencing) before any action.
- Be transparent and concise. Do not invent taxa, numbers, or trends not present \
in the provided data.

Write in Markdown. Use these sections, in order, and nothing else:
## Executive Summary  (3-5 sentences)
## Risk Interpretation  (per High/Critical taxon: what it is, why flagged, caveats)
## Recommended Public-Health Actions  (bulleted, prioritised, confirmatory-first)
## Caveats & Limitations  (bulleted)
Keep the whole thing under ~450 words.\
"""


# --- taxonomy interpretation (LLM agent) ------------------------------------
TAXONOMY_SYSTEM = """\
You are a viral taxonomy curator for wastewater/environmental metagenomic \
surveillance. For each candidate taxon you are given (name, family, taxid, \
total supporting reads, max classification confidence), classify it into exactly \
one category and flag review concerns.

Rules:
- "phage": bacteriophages / environmental phages (e.g. names containing phage, \
crassphage, *viridae bacteriophage). Not a human/animal pathogen.
- "false_positive": likely spurious — very low reads (<10), very low confidence \
(<0.3), low-complexity/fragmentary hits, or common contaminants.
- "pathogen": a plausible human/animal viral pathogen with reasonable support.
- "uncertain": unclassified/divergent or otherwise ambiguous.
Be conservative; when unsure prefer "uncertain" over "pathogen". You may only \
ADD caution — never claim confirmation.

Respond with JSON ONLY, no prose:
{"taxa":[{"taxon_name": str, "category": "phage|false_positive|pathogen|uncertain", \
"is_phage": bool, "false_positive": bool, "rationale": str}]}\
"""


def build_taxonomy_user(candidates: list[dict[str, Any]], lineages: dict[int, dict] | None = None) -> str:
    lineages = lineages or {}
    rows = []
    for c in candidates:
        tid = int(c.get("taxid", 0) or 0)
        row = {"taxon_name": c.get("taxon_name"), "family": c.get("family"), "taxid": tid,
               "total_reads": int(c.get("total_reads", 0) or 0),
               "max_confidence": float(c.get("max_confidence", 0.0) or 0.0)}
        lin = lineages.get(tid)
        if lin:  # verified NCBI Taxonomy facts — prefer these over prior knowledge
            row["ncbi_division"] = lin.get("division")
            row["ncbi_superkingdom"] = lin.get("superkingdom")
            row["ncbi_lineage"] = lin.get("lineage")
        rows.append(row)
    note = ("\n\nWhere present, ncbi_* fields are AUTHORITATIVE NCBI Taxonomy facts — "
            "trust them over prior knowledge (division 'Phages' => bacteriophage)." if lineages else "")
    return ("Classify these candidate viral taxa. Use only this data.\n\n```json\n"
            + json.dumps(rows, indent=2, default=str) + "\n```" + note)


# --- risk assessment (LLM agent) --------------------------------------------
RISK_SYSTEM = """\
You are an epidemiological risk analyst for viral wastewater surveillance. For \
each taxon you are given (name, supporting reads, whether it is a phage, whether \
it was flagged a likely false positive, abundance trend, and whether it matches \
the configured high-risk pathogen list), assign a risk level and explain why.

Risk levels: "Low", "Medium", "High", "Critical".
Rules (follow exactly — these are signals, not confirmed infections):
- Environmental phages → always "Low".
- Likely-false-positive / very low read (<10) signals → "Low" (do not over-claim).
- A taxon matching the configured high-risk pathogen list with adequate support \
(>=10 reads) → at least "High"; "Critical" only if ALSO sharply increasing.
- Non-phage, non-pathogen viruses → "Medium" if substantial support, else "Low".
- Never exceed the evidence; recommend confirmatory testing for High/Critical.

Respond with JSON ONLY, no prose:
{"assessments":[{"taxon_name": str, "risk_level": "Low|Medium|High|Critical", \
"reasoning": str}], "overall_reasoning": str}\
"""


def build_risk_user(evidence: list[dict[str, Any]]) -> str:
    snippets = pathogen_snippets([str(e.get("taxon_name", "")) for e in evidence])
    ref = ("\n\nReference notes for detected taxa (background only):\n- " + "\n- ".join(snippets)) if snippets else ""
    return ("Assess epidemiological risk for these taxa. Use only this data.\n\n```json\n"
            + json.dumps(evidence, indent=2, default=str) + "\n```" + ref)


# --- novel/divergent virus candidate interpretation (LLM agent) -------------
NOVEL_SYSTEM = """\
You are a virologist assessing NOVEL or DIVERGENT viral candidates from \
metagenomic assembly/screening of wastewater/environmental samples. For each \
candidate (putative taxon, family hint, supporting reads, classification \
confidence, evidence) give a brief, cautious assessment: what viral group it may \
belong to, how confident the evidence is, plausibility of being a genuine novel \
virus vs artefact/chimera, and the recommended characterisation steps \
(e.g. contig curation, CheckV completeness, ORF/RdRp search, phylogenetics).

Be conservative — these are uncertain signals, not discoveries. Do not name a \
specific new species or claim novelty as fact.

Respond with JSON ONLY:
{"candidates":[{"candidate_id": str, "assessment": str, "confidence": "low|medium|high", \
"recommended_steps": [str]}], "summary": str}\
"""


def build_novel_user(candidates: list[dict[str, Any]]) -> str:
    return ("Assess these novel/divergent viral candidates. Use only this data.\n\n```json\n"
            + json.dumps(candidates, indent=2, default=str) + "\n```")


def build_user_prompt(state: dict[str, Any]) -> str:
    """Render the per-run structured results into a compact prompt."""

    cfg = state.get("config", {}) or {}
    project = cfg.get("project", {}) or {}
    risk = state.get("risk_summary", {}) or {}
    tax = state.get("taxonomy_summary", {}) or {}
    sample = state.get("sample_summary", {}) or {}
    novel = state.get("novel_candidate_summary", {}) or {}
    vd = state.get("viral_detection_summary", {}) or {}

    payload = {
        "run_name": project.get("run_name", ""),
        "samples": {
            "n": sample.get("n_samples", 0),
            "locations": sample.get("locations", []),
            "collection_dates": sample.get("collection_dates", []),
            "type": "wastewater/environmental metagenome",
        },
        "detection_tools": vd.get("tools", []),
        "overall_risk": risk.get("overall_risk", "Low"),
        "risk_level_counts": risk.get("counts", {}),
        "top_risk_taxa": risk.get("top_risks", []),  # name, risk_level, total_reads, trend, reasons
        "taxonomy": {
            "n_taxa": tax.get("n_taxa", 0),
            "n_phage": tax.get("n_phage", 0),
            "n_flagged_false_positive": tax.get("n_flagged", 0),
        },
        "novel_candidates": novel.get("n_candidates", 0),
        "recommended_actions_deterministic": state.get("recommended_followup_actions", []),
    }
    names = [str(t.get("taxon_name", "")) for t in risk.get("top_risks", [])]
    snippets = pathogen_snippets(names)
    ref = ("\n\nReference notes for detected taxa (background only):\n- " + "\n- ".join(snippets)) if snippets else ""
    return (
        "Interpret the following MetaMAVS surveillance results. Use only this data.\n\n"
        "```json\n" + json.dumps(payload, indent=2, default=str) + "\n```" + ref
    )
