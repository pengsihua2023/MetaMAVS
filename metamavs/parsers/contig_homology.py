"""Parse DIAMOND blastx of assembled contigs vs a known-virus protein DB.

Reduces outfmt-6 alignments to the single BEST hit per contig (highest bitscore),
used by novel_virus screening to separate known viruses (strong protein hit) from
suspected-novel contigs (no/weak hit).

Expected outfmt 6 columns: qseqid sseqid pident evalue bitscore
(the order emitted by jobgen's diamond command).
"""

from __future__ import annotations

from typing import Any

from .base import make_result, read_lines


def parse_contig_homology(path: str, sample_id: str | None = None) -> dict[str, Any]:
    """Best known-virus hit per contig -> records [{contig_id, subject, pident, evalue}]."""

    try:
        best: dict[str, dict[str, Any]] = {}
        for line in read_lines(path):
            if not line.strip() or line.startswith("#"):
                continue
            f = line.split("\t")
            if len(f) < 5:
                continue
            qseqid, sseqid = f[0], f[1]
            try:
                pident = float(f[2]); evalue = float(f[3]); bitscore = float(f[4])
            except ValueError:
                continue
            cur = best.get(qseqid)
            if cur is None or bitscore > cur["_bitscore"]:
                best[qseqid] = {"contig_id": qseqid, "subject": sseqid, "pident": pident,
                                "evalue": evalue, "_bitscore": bitscore, "tool": "contig_homology"}
        records = [{k: v for k, v in r.items() if k != "_bitscore"} for r in best.values()]
        return {"result": make_result("contig_homology", sample_id, parsed_table_path=path,
                                      n_records=len(records)), "records": records}
    except Exception as exc:
        return {"result": make_result("contig_homology", sample_id, ok=False,
                                      warnings=[f"contig_homology parse failed: {exc}"]), "records": []}
