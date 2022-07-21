#!/bin/bash

#SBATCH --job-name=Net1A_farming
#SBATCH --time=120:00:00
#SBATCH --nodes=10
#SBATCH --ntasks=400
#SBATCH --mem-per-cpu=1048MB
#SBATCH --partition=computes_thin
#SBATCH -o SLURM_job_outputs_10_std/HistGB_Farming_10.out

cd ..
python3 DataFarmerMain_5.py 2500 400 csv
