#!/bin/bash
#Akshay Maheshwari, 9/02/2017
#Runs other scripts to automate pipeline from experiment set-up to analysis & figure production.

python3 /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/src/smol_exptSetup.py
sleep 2
sh AWS_start.sh
sleep 100
init=`aws ec2 describe-instance-status|grep -i initializing`
while [ "${#init}" -ne "0" ]; do
	init=`aws ec2 describe-instance-status|grep -i initializing`
	echo Instances are initializing..."$SECONDS"s.
	sleep 30
	done
sleep 120
sh AWS_scriptCopyRun.sh
echo "Simulation pipeline finished"
echo Total Runtime: "$SECONDS"s.


