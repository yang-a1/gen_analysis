#!/bin/bash



# source /etc/profile.d/http_proxy.sh
source /home/$USER/.bashrc
# unset HTTPCORE_PROXY
# unset HTTPX_PROXY
# unset HTTP_PROXY
# unset FTP_PROXY
# unset NO_PROXY
# unset HTTPS_PROXY
# unset RSYNC_PROXY




# export HTTPCORE_PROXY=http://proxy1.arc-ts.umich.edu:3128/
# export HTTPX_PROXY=http://proxy1.arc-ts.umich.edu:3128/
# export HTTP_PROXY=http://proxy1.arc-ts.umich.edu:3128/
# export FTP_PROXY=http://proxy1.arc-ts.umich.edu:3128/
# export NO_PROXY=localhost,127.0.0.1,.localdomain,.umich.edu,ime240-4-1-hs
# export HTTPS_PROXY=http://proxy1.arc-ts.umich.edu:3128/
# export RSYNC_PROXY=proxy1.arc-ts.umich.edu:3128





wait
conda activate gen_analysis
echo $http_proxy
echo $https_proxy
echo $ftp_proxy
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $HTTPX_PROXY
echo $HTTPCORE_PROXY
echo "conmpleted proxy setup"
source /etc/profile.d/http_proxy.sh
python working_openAI_test.py

