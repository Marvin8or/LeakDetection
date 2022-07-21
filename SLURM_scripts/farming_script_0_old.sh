#!/bin/bash

#SBATCH --job-name=Net1A_farming
#SBATCH --time=120:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=40
#SBATCH --mem-per-cpu=1048MB
#SBATCH --partition=computes_thin
#SBATCH -o SLURM_job_outputs_0_std/HistGB_Farming_0_old.out

cd ..
python3 DataFarmerOld.py 500 40

