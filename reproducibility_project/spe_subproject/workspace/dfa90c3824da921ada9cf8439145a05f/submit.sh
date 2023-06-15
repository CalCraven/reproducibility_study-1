#!/bin/bash
#PBS -N dfa90c3824da921ada9cf8439145a05f
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --time=00:05:00
#SBATCH --partition=short-std
#SBATCH --output=test_job_out.txt
#SBATCH --export=ALL

echo $SLURM_SUBMIT_DIR
cd $SLURM_SUBMIT_DIR
echo $infile $seed $T $P $rcut $tstep
module load lammps/5Jun2019
module load gcc/8.5.0
module load openmpi/gcc/8.5.0/4.1.2
mpirun -np 8 lmp -i $infile -var seed $seed -var T $T -var P $P -var rcut $rcut -var tstep $tstep
#lmp -in $infile -var seed $seed -var T $T -var P $P -var rcut $rcut -var tstep $tstep
