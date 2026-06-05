"""Curated domain reference context for the LLM agents (literature grounding).

``SHARED_REFERENCE`` is a static, factual reference on wastewater/environmental
viral surveillance. It is injected as the **cached** prefix of every LLM agent's
system prompt, so the model's judgement is grounded in documented principles AND
the (now >1024-token) prefix actually engages Anthropic prompt caching, giving
cross-agent cache hits within a run.

``PATHOGEN_REFERENCE`` holds short, per-pathogen reference snippets that are
woven into the *user* prompt only when that pathogen is actually detected
(literature-aware, per-detection).

These are concise, widely-documented facts — not a substitute for primary
literature, and the model is instructed to treat them as background only.
"""

from __future__ import annotations

SHARED_REFERENCE = """\
# Reference: Wastewater / environmental viral metagenomic surveillance

## What the data is
Wastewater-based epidemiology (WBE) detects viral nucleic acids shed by a
contributing population into sewage or the environment. A metagenomic detection
is a POPULATION-LEVEL sequence signal: it indicates presence and approximate
relative abundance of viral genetic material in the sample, NOT individual
infections, case counts, severity, or active transmission. Confirmed
epidemiological conclusions require orthogonal assays and clinical/epidemiologic
context.

## Signal strength and confidence
- Read support scales (very roughly) with environmental abundance and assay
  sensitivity, modulated by genome size, shedding magnitude, and decay in transit.
- Low read counts (~<10) are weak/uncertain and prone to false positives from
  database artefacts, conserved regions, index hopping, or low-complexity hits.
- A single time point cannot establish a temporal trend; "stable" from one
  sample is uninformative. Trends require repeated sampling at the same site.
- k-mer/marker classifiers (Kraken2, GOTTCHA2) can mis-assign at low coverage;
  species-level calls with reasonable breadth-of-coverage are more reliable than
  read count alone.

## Controls and normalization
- Pepper mild mottle virus (PMMoV) is a plant virus and the most widely used
  faecal-load NORMALIZATION marker — it confirms faecal input and enables
  inter-sample comparison. It is NOT a human/animal pathogen and must not be
  ranked as a threat.
- crAssphage and other bacteriophages are environmental/faecal indicators, not
  human pathogens; report them separately.

## High-risk pathogen context (for surveillance prioritisation)
- SARS-CoV-2 (Betacoronavirus): respiratory pathogen, well-documented faecal
  shedding; WBE is an established early-warning tool.
- Influenza A/B: respiratory; environmental signals are weaker and seasonal.
- Norovirus / Sapovirus (Caliciviridae): leading causes of viral
  gastroenteritis; abundantly shed in stool; common and often high in wastewater.
- Enteroviruses (incl. poliovirus, EV-D68, coxsackie/echo): enteric, robustly
  shed; poliovirus environmental surveillance underpins global eradication.
- Hepatitis A virus: enteric, faecal-oral; outbreak-relevant.

## Additional surveillance targets (context)
- Respiratory syncytial virus (RSV) and human metapneumovirus: respiratory,
  seasonal; environmental signals are weaker than enteric viruses.
- Measles virus: respiratory/highly transmissible; any signal is notable but
  environmental detection is uncommon and warrants careful confirmation.
- Hepatitis E virus: enteric, zoonotic potential; relevant in some settings.
- Mpox (monkeypox) virus: detection in wastewater has been used as a
  complementary signal during outbreaks; interpret cautiously.

## Decay, transport and sampling caveats
- RNA viruses degrade faster than DNA viruses in sewer transit; non-enveloped
  enteric viruses (noro, entero, HAV, adeno) are more stable than enveloped
  respiratory viruses, biasing relative recovery.
- Composite (24 h) samples better represent the contributing population than
  grab samples; flow and dilution (rain/industrial input) affect concentrations
  and motivate normalization (e.g. to PMMoV).
- Inhibitors, extraction efficiency, and concentration method (e.g.
  ultrafiltration, PEG) all affect yield; recovery controls are recommended.

## Sequencing / classification caveats
- Reference-database completeness bounds what can be detected; absence of a
  signal is not evidence of absence.
- Closely related taxa can cross-map; strain- or subtype-level claims from short
  reads are unreliable. Protein-level search (e.g. DIAMOND vs RVDB) can recover
  divergent viruses that nucleotide methods miss.
- Coverage breadth and evenness are stronger evidence than raw read count for a
  true positive.

## Confirmation hierarchy for actionable detections
1. Re-test the same sample/extract with a targeted, validated RT-qPCR assay.
2. Amplicon or targeted-capture sequencing to verify identity and (where
   possible) lineage.
3. Repeat sampling across time points to establish a genuine trend.
4. Integrate with clinical/syndromic surveillance before any public-health action.

## Interpretation principles (always apply)
- Use "detected sequence signal", never "confirmed infection/outbreak".
- Do not over-claim from weak signals; explicitly flag low reads/low confidence.
- Separate environmental phages and normalization controls from pathogens.
- Recommend orthogonal confirmation (targeted RT-qPCR / amplicon sequencing)
  for any High/Critical detection before action.
- Never provide clinical diagnosis or outbreak confirmation from reads alone.
"""

# Per-pathogen reference snippets, matched by name patterns so full taxonomic
# names (e.g. "Severe acute respiratory syndrome-related coronavirus") still hit.
PATHOGEN_REFERENCE: dict[str, dict] = {
    "SARS-CoV-2": {
        "patterns": ["sars-cov-2", "severe acute respiratory syndrome"],
        "text": "SARS-CoV-2: respiratory Betacoronavirus; documented faecal shedding; WBE is an established early-warning signal.",
    },
    "Norovirus": {
        "patterns": ["norovirus", "norwalk"],
        "text": "Norovirus (Norwalk virus): leading cause of viral gastroenteritis; very high faecal shedding; common in wastewater.",
    },
    "Sapovirus": {
        "patterns": ["sapovirus", "sapporo"],
        "text": "Sapovirus (Sapporo virus): calicivirus causing gastroenteritis; faecally shed.",
    },
    "Influenza A virus": {
        "patterns": ["influenza a"],
        "text": "Influenza A: respiratory; environmental signals weaker/seasonal; subtype not inferable from reads.",
    },
    "Influenza B virus": {
        "patterns": ["influenza b"],
        "text": "Influenza B: respiratory; seasonal.",
    },
    "Enterovirus": {
        "patterns": ["enterovirus", "coxsackie", "echovirus", "poliovirus", "rhinovirus"],
        "text": "Enteroviruses (poliovirus, EV-D68, coxsackie/echo): enteric, robustly shed; basis of poliovirus environmental surveillance.",
    },
    "Hepatitis A virus": {
        "patterns": ["hepatovirus a", "hepatitis a"],
        "text": "Hepatitis A virus: enteric, faecal-oral; outbreak-relevant.",
    },
    "Adenovirus": {
        "patterns": ["adenovirus", "mastadenovirus"],
        "text": "Human adenovirus (enteric types e.g. F): faecally shed; common wastewater detection.",
    },
}


def pathogen_snippets(names: list[str]) -> list[str]:
    """Return reference snippets for detected taxa, matched by name patterns."""

    out: list[str] = []
    seen: set[str] = set()
    for name in names:
        low = (name or "").lower()
        for canon, entry in PATHOGEN_REFERENCE.items():
            if canon in seen:
                continue
            if any(p in low for p in entry["patterns"]):
                out.append(entry["text"])
                seen.add(canon)
    return out
