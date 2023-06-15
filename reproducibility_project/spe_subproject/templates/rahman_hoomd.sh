{% extends "slurm.sh" %}

{% block header %}
{% set gpus = operations|map(attribute='directives.ngpu')|sum %}
    {{- super () -}}

#SBATCH --nodes=1
#SBATCH --partition=short-tesla
#SBATCH --time=00:30:00
#SBATCH --gres gpu:1
#SBATCH --mail-type=ALL
#SBATCH --mail-user=co.d.quach@vanderbilt.edu
#SBATCH -o output-%j.log
#SBATCH -e error-%j.log

#module load anaconda/3.9
echo "running a script"
echo "running a 3.11 script"
module load hoomd/single/4.0.0tesla

export MOSDEF_PYTHON=~/.conda/envs/hoomd3.11.0.craven76/bin/python
conda activate hoomd3.11.0.craven76
echo $(conda env list)


{% endblock header %}

{% block body %}
    {{- super () -}}


{% endblock body %}
