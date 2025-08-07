#! /usr/bin/env bash

#partition - defq, bigmem and xtreme
#SBATCH --job-name=nf-sra
#SBATCH --ntasks=1
#SBATCH --partition=defq
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=24:00:00
#SBATCH -o slurm.%A.o
#SBATCH -e slurm.%A.e

module load java
module load nextflow

nextflow run down_sra.nf -c ./down_sra_conf/run.config -resume -profile slurm

module unload java
module unload nextflow