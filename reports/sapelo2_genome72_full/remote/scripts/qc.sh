#!/usr/bin/env bash
#SBATCH --job-name=qc
#SBATCH --partition=bahl_p
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=02:00:00
#SBATCH --output=/scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/logs/qc_%j.out
#SBATCH --error=/scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/logs/qc_%j.err

set -euo pipefail

export PATH=/home/sp96859/.conda/envs/gottcha2_env/bin:$PATH

mkdir -p /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/results/qc
fastqc --extract -t 8 -o /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/results/qc /scratch/sp96859/Meta-genome-data-analysis/Apptainer/data/short_reads/sample_72_0_01.fq.gz /scratch/sp96859/Meta-genome-data-analysis/Apptainer/data/short_reads/sample_72_0_02.fq.gz
cp /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/results/qc/sample_72_0_01_fastqc/fastqc_data.txt /scratch/sp96859/Meta-genome-data-analysis/Apptainer/Meta_MAVS/metamavs/run_20260711_172021/results/qc/Genome_72.fastqc_data.txt
