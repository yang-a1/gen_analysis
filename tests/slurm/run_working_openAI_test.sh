#!/bin/bash



source /home/$USER/.bashrc
wait

# this implements proxy settings for the slurm job
source /etc/profile.d/http_proxy.sh

conda activate gen_analysis
wait

python working_openAI_test.py

