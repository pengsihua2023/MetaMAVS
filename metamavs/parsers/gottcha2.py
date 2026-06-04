"""Parse a GOTTCHA2 summary TSV into viral-hit rows.

GOTTCHA2 v2 writes a tab-separated summary (commonly ``<prefix>.tsv``) with a
header that includes at least LEVEL, NAME, TAXID and a read-count column. Column
names vary slightly across versions, so we resolve them case-insensitively and
degrade gracefully on anything unexpected.
"""

from __future__ import annotations

from typing import Any

from .base import make_result, read_lines
from .kraken2 import _family_for

_READ_COLS = ("READ_COUNT", "READ_COUNTS", "READS", "ROLLUP_READ_COUNT", "TOTAL_BP_MAPPED")


def parse_gottcha2(path: str, sample_id: str | None = None) -> dict[str, Any]:
    """Species-level GOTTCHA2 rows -> raw_viral_hits schema (tool='gottcha2')."""

    try:
        lines = read_lines(path)
        if not lines:
            return {"result": make_result("gottcha2", sample_id, n_records=0), "records": []}
        header = [h.strip().upper() for h in lines[0].split("\t")]
        idx = {h: i for i, h in enumerate(header)}
        lvl_i = idx.get("LEVEL")
        name_i = idx.get("NAME")
        taxid_i = idx.get("TAXID")
        reads_i = next((idx[c] for c in _READ_COLS if c in idx), None)
        if name_i is None or reads_i is None:
            return {"result": make_result("gottcha2", sample_id, ok=False,
                                          warnings=["gottcha2: missing NAME/READ_COUNT columns"]), "records": []}
        records: list[dict[str, Any]] = []
        for line in lines[1:]:
            f = line.split("\t")
            if len(f) <= max(name_i, reads_i):
                continue
            if lvl_i is not None and lvl_i < len(f) and f[lvl_i].strip().lower() != "species":
                continue
            try:
                reads = int(float(f[reads_i]))
            except ValueError:
                continue
            name = f[name_i].strip()
            if reads <= 0 or not name:
                continue
            try:
                taxid = int(f[taxid_i]) if taxid_i is not None and taxid_i < len(f) and f[taxid_i] else 0
            except ValueError:
                taxid = 0
            records.append({
                "sample_id": sample_id, "taxon_name": name, "family": _family_for(name),
                "taxid": taxid, "genome_length_kb": 0.0, "reads": reads,
                "confidence": 0.9, "tool": "gottcha2",
            })
        return {"result": make_result("gottcha2", sample_id, parsed_table_path=path, n_records=len(records)),
                "records": records}
    except Exception as exc:
        return {"result": make_result("gottcha2", sample_id, ok=False, warnings=[f"gottcha2 parse failed: {exc}"]),
                "records": []}
