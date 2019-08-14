#!/bin/bash
#Akshay Maheshwari, 9/02/2017
#Runs other scripts to automate pipeline from experiment set-up to analysis & figure production.

python3 /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/src/smol_exptSetup.py
sh AWS_start.sh
sleep 60
init=`aws ec2 describe-instance-status|grep -i initializing`
while [ "${#init}" -ne "0" ]; do
	init=`aws ec2 describe-instance-status|grep -i initializing`
	echo Instances are initializing..."$SECONDS"s.
	sleep 10
	done
sh AWS_scriptCopy.sh
sh AWS_runExpts.sh
sh AWS_dlAnalysisStoreDataAutoShut.sh
echo "Simulation pipeline finished"
echo Total Runtime: "$SECONDS"s.


