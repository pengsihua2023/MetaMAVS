"""Parse a GOTTCHA2 summary TSV into VIRAL hit rows.

GOTTCHA2's RefSeq database profiles all organisms, so its summary lists bacteria,
archaea and viruses alike. For viral surveillance we keep only taxa whose lineage
sits under the *Viruses* superkingdom. The lineage is read from the sibling
``<prefix>.gottcha2.lineage.tsv`` (downloaded next to the summary). If that file
is absent we keep all species and warn (so the parser still degrades gracefully).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import make_result, read_lines
from .kraken2 import _family_for

_READ_COLS = ("READ_COUNT", "READ_COUNTS", "READS", "ROLLUP_READ_COUNT")


def _viral_species_taxids(lineage_path: Path) -> set[int]:
    """Taxids of species whose lineage superkingdom is Viruses.

    lineage.tsv rows: <score> then repeating (rank, taxid, name) tuples from
    superkingdom down to species.
    """

    viral: set[int] = set()
    for line in read_lines(str(lineage_path)):
        f = line.split("\t")
        if len(f) < 4 or f[1].strip().lower() != "superkingdom":
            continue
        if f[3].strip().lower() not in ("viruses", "virus"):
            continue
        for i in range(1, len(f) - 2, 3):
            if f[i].strip().lower() == "species":
                try:
                    viral.add(int(f[i + 1]))
                except ValueError:
                    pass
    return viral


def parse_gottcha2(path: str, sample_id: str | None = None) -> dict[str, Any]:
    """Viral species-level GOTTCHA2 rows -> raw_viral_hits schema (tool='gottcha2')."""

    try:
        p = str(path)
        suffix = ".gottcha2.tsv"
        lineage_path = Path(p[: -len(suffix)] + ".gottcha2.lineage.tsv") if p.endswith(suffix) else None
        has_lineage = lineage_path is not None and lineage_path.exists()
        viral_taxids = _viral_species_taxids(lineage_path) if has_lineage and lineage_path else set()
        warnings: list[str] = []
        if not has_lineage:
            warnings.append("gottcha2: no sibling lineage.tsv -> viral-lineage filter skipped")

        lines = read_lines(path)
        if not lines:
            return {"result": make_result("gottcha2", sample_id, n_records=0, warnings=warnings), "records": []}
        header = [h.strip().upper() for h in lines[0].split("\t")]
        idx = {h: i for i, h in enumerate(header)}
        lvl_i, name_i, taxid_i = idx.get("LEVEL"), idx.get("NAME"), idx.get("TAXID")
        reads_i = next((idx[c] for c in _READ_COLS if c in idx), None)
        if name_i is None or reads_i is None:
            return {"result": make_result("gottcha2", sample_id, ok=False,
                                          warnings=warnings + ["gottcha2: missing NAME/READ_COUNT columns"]),
                    "records": []}

        records: list[dict[str, Any]] = []
        for line in lines[1:]:
            f = line.split("\t")
            if len(f) <= max(name_i, reads_i):
                continue
            if lvl_i is not None and lvl_i < len(f) and f[lvl_i].strip().lower() != "species":
                continue
            try:
                taxid = int(f[taxid_i]) if taxid_i is not None and taxid_i < len(f) and f[taxid_i] else 0
            except ValueError:
                taxid = 0
            if has_lineage and taxid not in viral_taxids:
                continue  # not viral -> drop (bacteria/archaea)
            try:
                reads = int(float(f[reads_i]))
            except ValueError:
                continue
            name = f[name_i].strip()
            if reads <= 0 or not name:
                continue
            records.append({
                "sample_id": sample_id, "taxon_name": name, "family": _family_for(name),
                "taxid": taxid, "genome_length_kb": 0.0, "reads": reads,
                "confidence": 0.9, "tool": "gottcha2",
            })
        return {"result": make_result("gottcha2", sample_id, parsed_table_path=path,
                                      n_records=len(records), warnings=warnings),
                "records": records}
    except Exception as exc:
        return {"result": make_result("gottcha2", sample_id, ok=False, warnings=[f"gottcha2 parse failed: {exc}"]),
                "records": []}
