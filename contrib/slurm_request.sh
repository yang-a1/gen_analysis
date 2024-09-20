#!/bin/bash


#source ~/.bashrc
# alternative is source /home/$USER/.bashrc


# modifications to /home/$USER/.bashrc are required.  comment out the lines below from .bashrc

# if [ $? -eq 0 ]; then
#    eval "$__conda_setup"
# else
# fi
# unset __conda_setup

# end of lines for .bashrc modification




# set your tempfile directory for the run.  Needs to have enough memory.  Default scratch
#export TMPDIR=//scratch/margit_root/margit0



#sbatch       --account=margit0
#sbatch       --partition=standard
#sbatch       -c 1
#sbatch       --nodes=1
#sbatch       --mem-per-cpu=7g
#sbatch       --time=00-00:02:00




source /home/$USER/.bashrc
# source /etc/profile.d/http_proxy.sh
srun bash run_working_openAI_test.sh
