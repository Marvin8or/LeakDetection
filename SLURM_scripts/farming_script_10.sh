#!/bin/bash

#SBATCH --job-name=Net1A_farming
#SBATCH --time=72:00:00
#SBATCH --nodes=10
#SBATCH --ntasks=480
#SBATCH --partition=computes_thin
#SBATCH -o SLURM_job_outputs_10_std/HistGB_Farming_10.out

cd ..
python3 DataFarmerMain_10.py 2084 480
