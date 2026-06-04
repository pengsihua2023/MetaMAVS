#!/usr/bin/env bash
#SBATCH --job-name=gottcha2
#SBATCH --partition=bahl_p
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=120G
#SBATCH --time=12:00:00
#SBATCH --output=/scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/logs/gottcha2_%j.out
#SBATCH --error=/scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/logs/gottcha2_%j.err

set -euo pipefail

export PATH=/home/sp96859/.conda/envs/gottcha2_env/bin:$PATH

mkdir -p /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/results/viral_detection /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/work
gottcha2.py -i /scratch/sp96859/Meta-genome-data-analysis/Apptainer/data/short_reads/llnl_66ce4dde_R1.fastq.gz /scratch/sp96859/Meta-genome-data-analysis/Apptainer/data/short_reads/llnl_66ce4dde_R2.fastq.gz -d /scratch/sp96859/Meta-genome-data-analysis/Apptainer/databases/gottcha2_db/gottcha_db.species.fna -l species -t 8 -o /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/work/llnl_66ce4dde.gottcha2 -p llnl_66ce4dde
cp /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/work/llnl_66ce4dde.gottcha2/llnl_66ce4dde.tsv /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/results/viral_detection/llnl_66ce4dde.gottcha2.tsv
cp /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/work/llnl_66ce4dde.gottcha2/llnl_66ce4dde.lineage.tsv /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260604_172046/results/viral_detection/llnl_66ce4dde.gottcha2.lineage.tsv
