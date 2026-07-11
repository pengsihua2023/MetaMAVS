# Files fetched from the HPC (single-sample run: Genome_72)

For the full Sapelo2 run (QC + GOTTCHA2 + assembly/CheckV + RVDB homology), the
controller fetched **5 files** back from the cluster — the complete real-data
source for every downstream table and the report. `synced_manifest.json` reports
`complete: true` (no missing outputs).

Transfer: `result_sync_agent` pulls each job's declared `output_files` with
`rsync -avz --partial --checksum` over the reused SSH ControlMaster connection.
Only these final result files are fetched; large intermediates (MEGAHIT assembly
dir, CheckV work dir, the ~94 GB GOTTCHA2 index) stay on the cluster.

## The 5 files

| File | Size | From job / tool | Local dir | Feeds |
|---|---|---|---|---|
| `Genome_72.fastqc_data.txt` | 16 KB | qc — **FastQC** | `results/raw/qc/` | QC metrics → `qc` agent (data-adequacy) |
| `Genome_72.gottcha2.tsv` | 19 KB | gottcha2 — **GOTTCHA2** | `results/raw/gottcha2/` | viral hits → the main analysis chain |
| `Genome_72.gottcha2.lineage.tsv` | 11 KB | gottcha2 — **GOTTCHA2** | `results/raw/gottcha2/` | lineage (keep only *Viruses* superkingdom) |
| `Genome_72.checkv_quality_summary.tsv` | 5.7 MB | novel_virus — **CheckV** | `results/raw/novel_virus/` | per-contig quality → novel candidates |
| `Genome_72.contig_homology.tsv` | 311 KB | novel_virus — **DIAMOND vs RVDB** | `results/raw/novel_virus/` | best known-virus hit → novelty check |

## Per-file detail

1. **`Genome_72.fastqc_data.txt`** — FastQC's extracted per-sample metrics (mean
   quality, total reads, adapter %, read length). Parsed by `parse_fastqc` →
   `qc_summary`; drives the QC LLM data-adequacy note.

2. **`Genome_72.gottcha2.tsv`** — GOTTCHA2 species-level profile (name, taxid,
   read counts). Parsed by `parse_gottcha2` → `raw_viral_hits` after filtering to
   viral taxa; the root of the detection → taxonomy → abundance → risk chain.

3. **`Genome_72.gottcha2.lineage.tsv`** — sibling lineage table used to keep only
   contigs/taxa whose superkingdom is *Viruses* (drops bacteria/archaea). Optional
   quality filter — the pipeline degrades gracefully without it.

4. **`Genome_72.checkv_quality_summary.tsv`** — CheckV per-contig assessment
   (~61k rows: checkv_quality, completeness, viral_genes). Parsed →
   `checkv_contigs`; High/Medium/Complete-quality contigs become novel candidates.

5. **`Genome_72.contig_homology.tsv`** — DIAMOND blastx of assembled contigs vs
   the RVDB known-virus protein DB (best hit per contig: subject, pident, evalue).
   Parsed → `contig_homology`; a candidate matching a known virus at ≥ 90% pident
   is reported as a known assembled genome, otherwise "suspected novel".

## Why only these five

Each SLURM job declares its `output_files`; `result_sync` fetches exactly those.
The set is the **minimal parseable result** for the three enabled steps (qc,
gottcha2, novel_virus). Everything downstream — the 8 `tables/*.csv` and
`report.md` — is derived from these 5 files plus the manifest metadata, verified
NCBI Taxonomy lineage, and the config.

> Note: a GOTTCHA2-only run fetches just the 2 GOTTCHA2 files; enabling QC and
> novel-virus screening adds the FastQC, CheckV, and RVDB-homology files.
