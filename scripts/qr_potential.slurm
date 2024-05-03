#!/bin/bash                                                          
#SBATCH --partition=general
#SBATCH --qos=regular
#SBATCH --job-name=qr_potential
#SBATCH --cpus-per-task=16
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=03:00:00
#SBATCH --mem=1000G

module load Python

python3 qr_potential.py
