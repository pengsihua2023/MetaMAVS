"""High-risk pathogen matching by taxid + name aliases.

Real classifiers (GOTTCHA2, Kraken2, …) report full taxonomic names that rarely
match a short config label literally — e.g. GOTTCHA2 calls SARS-CoV-2
"Severe acute respiratory syndrome-related coronavirus", and Norovirus
"Norwalk virus". This module maps each canonical high-risk pathogen to a set of
NCBI taxids and lowercase name patterns so detections are correctly flagged.

``match_high_risk`` is config-driven: it only considers pathogens listed in the
user's ``risk.high_risk_pathogens``. For a listed pathogen we use its alias
entry (taxids + patterns) when known, and always fall back to a literal
substring check so custom/unknown entries still work.
"""

from __future__ import annotations

# canonical name -> {"taxids": {...}, "patterns": [lowercase substrings]}
PATHOGEN_ALIASES: dict[str, dict] = {
    "sars-cov-2": {
        "taxids": {2697049, 694009},  # SARS-CoV-2; SARS-related coronavirus (species)
        "patterns": [
            "sars-cov-2", "sars cov 2", "sars coronavirus 2",
            "severe acute respiratory syndrome coronavirus 2",
            "severe acute respiratory syndrome-related coronavirus",
            "severe acute respiratory syndrome related coronavirus",
        ],
    },
    "influenza a virus": {
        "taxids": {11320},
        "patterns": ["influenza a virus", "influenza a "],
    },
    "influenza b virus": {
        "taxids": {11520},
        "patterns": ["influenza b virus", "influenza b "],
    },
    "norovirus": {
        "taxids": {11983, 142786},  # Norwalk virus; Norovirus (genus)
        "patterns": ["norovirus", "norwalk virus"],
    },
    "enterovirus": {
        "taxids": {12059},  # Enterovirus (genus)
        "patterns": [
            "enterovirus", "coxsackievirus", "echovirus", "poliovirus", "rhinovirus",
        ],
    },
}


def match_high_risk(taxon_name: str, taxid: int, configured: list[str]) -> str | None:
    """Return the configured high-risk pathogen this taxon matches, or None.

    Matching order, per configured pathogen:
      1. taxid is in the pathogen's known taxid set;
      2. taxon name contains one of the pathogen's known name patterns;
      3. literal substring fallback (so custom config entries still match).
    """

    name_l = (taxon_name or "").lower()
    try:
        tid = int(taxid)
    except (TypeError, ValueError):
        tid = 0

    for p in configured:
        entry = PATHOGEN_ALIASES.get(p.lower())
        if entry:
            if tid and tid in entry["taxids"]:
                return p
            if any(pat in name_l for pat in entry["patterns"]):
                return p
        if p.lower() in name_l:  # backward-compatible literal fallback
            return p
    return None
