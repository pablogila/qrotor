#!/bin/bash                                                          
#SBATCH --partition=general
#SBATCH --qos=test
#SBATCH --job-name=QRotor-test
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=00:10:00
#SBATCH --mem=24000

module purge
module load ase

python3 convergence_calc.py
