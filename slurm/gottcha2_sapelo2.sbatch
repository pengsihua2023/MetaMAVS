#!/usr/bin/env bash
# ============================================================================
# MetaMAVS — GOTTCHA2 viral detection on UGA GACRC Sapelo2 (real data)
# ----------------------------------------------------------------------------
# Standalone sbatch job that produces the REAL GOTTCHA2 tables MetaMAVS parses.
# Run this directly on a Sapelo2 login node with `sbatch`, OR let the MetaMAVS
# SSH controller submit an equivalent job (`metamavs run -c configs/sapelo2_config.yaml
# --execute`). Use this script when you want to run the heavy step by hand and
# then hand the .tsv outputs to the local Phase-B backend comparison.
#
# Edit the four >>> TODO <<< values, then:
#     sbatch slurm/gottcha2_sapelo2.sbatch
#
# GOTTCHA2's species minimap2 index is ~94 GB, so this needs a high-memory
# allocation (120G). Verify your partition's nodes actually provide it.
# ============================================================================
#SBATCH --job-name=mm_gottcha2
#SBATCH --partition=bahl_p               # >>> TODO: your partition (needs ~120G RAM) <<<
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

set -euo pipefail

# ---- Parameters (edit these) ------------------------------------------------
SAMPLE_ID="Genome_72"                    # >>> TODO: your sample id <<<
READ1="/scratch/sp96859/Meta-genome-data-analysis/Apptainer/data/short_reads/sample_72_0_01.fq.gz"  # >>> TODO <<<
READ2="/scratch/sp96859/Meta-genome-data-analysis/Apptainer/data/short_reads/sample_72_0_02.fq.gz"  # >>> TODO (empty for single-end) <<<
GOTTCHA2_DB="/scratch/sp96859/Meta-genome-data-analysis/Apptainer/databases/gottcha2_db/gottcha_db.species.fna"
GOTTCHA2_ENV_BIN="/home/sp96859/.conda/envs/gottcha2_env/bin"   # conda env with gottcha2.py on PATH
LEVEL="species"
THREADS="${SLURM_CPUS_PER_TASK:-16}"
OUTBASE="${SLURM_SUBMIT_DIR:-$PWD}/mm_gottcha2_${SAMPLE_ID}"

# ---- Environment ------------------------------------------------------------
# Prepend the env's bin to PATH (no `conda init` required on compute nodes).
export PATH="${GOTTCHA2_ENV_BIN}:$PATH"
command -v gottcha2.py >/dev/null 2>&1 || { echo "ERROR: gottcha2.py not on PATH" >&2; exit 127; }

WORK="${OUTBASE}/work"
RESULTS="${OUTBASE}/results"
mkdir -p "$WORK" "$RESULTS"

echo "[$(date '+%F %T')] host=$(hostname) sample=${SAMPLE_ID} threads=${THREADS}"
echo "[$(date '+%F %T')] db=${GOTTCHA2_DB}"

# ---- Run GOTTCHA2 -----------------------------------------------------------
# -i takes one (single-end) or two (paired-end) FASTQ files.
INPUTS=("$READ1")
[[ -n "${READ2}" ]] && INPUTS+=("$READ2")

gottcha2.py \
    -i "${INPUTS[@]}" \
    -d "${GOTTCHA2_DB}" \
    -l "${LEVEL}" \
    -t "${THREADS}" \
    -o "${WORK}/${SAMPLE_ID}.gottcha2" \
    -p "${SAMPLE_ID}"

# ---- Collect the two tables MetaMAVS parses ---------------------------------
cp "${WORK}/${SAMPLE_ID}.gottcha2/${SAMPLE_ID}.tsv"         "${RESULTS}/${SAMPLE_ID}.gottcha2.tsv"
cp "${WORK}/${SAMPLE_ID}.gottcha2/${SAMPLE_ID}.lineage.tsv" "${RESULTS}/${SAMPLE_ID}.gottcha2.lineage.tsv"

echo "[$(date '+%F %T')] DONE. Outputs:"
echo "  ${RESULTS}/${SAMPLE_ID}.gottcha2.tsv"
echo "  ${RESULTS}/${SAMPLE_ID}.gottcha2.lineage.tsv"
echo
echo "Next: copy these two .tsv files to your controller under"
echo "  reports/<run>/results/raw/gottcha2/  then run the local pipeline +"
echo "  scripts/compare_llm_backends.py (see docs/REAL_DATA_VALIDATION.md)."
