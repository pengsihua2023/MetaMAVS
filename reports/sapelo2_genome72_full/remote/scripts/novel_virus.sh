#!/usr/bin/env bash
#SBATCH --job-name=novel_virus
#SBATCH --partition=bahl_p
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=/scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/logs/novel_virus_%j.out
#SBATCH --error=/scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/logs/novel_virus_%j.err

set -euo pipefail

export PATH=/home/sp96859/.conda/envs/megahit_env/bin:/home/sp96859/.conda/envs/VirSorter2_new/bin:$HOME/.local/bin:$PATH
export CHECKVDB=/scratch/sp96859/Meta-genome-data-analysis/Apptainer/databases/checkv-db-v1.5

mkdir -p /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/results/novel_virus /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/work
megahit -1 /scratch/sp96859/Meta-genome-data-analysis/Apptainer/data/short_reads/sample_72_0_01.fq.gz -2 /scratch/sp96859/Meta-genome-data-analysis/Apptainer/data/short_reads/sample_72_0_02.fq.gz -o /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/work/Genome_72.assembly
checkv end_to_end /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/work/Genome_72.assembly/final.contigs.fa /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/work/Genome_72.checkv
cp /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/work/Genome_72.checkv/quality_summary.tsv /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/results/novel_virus/Genome_72.checkv_quality_summary.tsv
diamond blastx -q /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/work/Genome_72.assembly/final.contigs.fa -d /scratch/sp96859/Meta-genome-data-analysis/Apptainer/databases/RVDB/RVDB_prot_ref.dmnd -p 8 --outfmt 6 qseqid sseqid pident evalue bitscore --max-target-seqs 1 --evalue 1e-5 -o /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/results/novel_virus/Genome_72.contig_homology.tsv
