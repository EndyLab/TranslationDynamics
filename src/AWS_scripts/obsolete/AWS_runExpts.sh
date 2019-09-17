#!/bin/bash
#Akshay Maheshwari, 08/31/2017
#Executes one experiment for every running AWS instance. # of experiments is expected to be same as # of instances active.

EXPLIST_PATH="/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/expt_list.txt" #Experiment_list contains new-line separated names of parameter files for each experiment
ipArray=(`aws ec2 describe-instances | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -`)
KPATH="/Users/Akshay/Dropbox/code/akshay.pem"

i=0
sleep 5
while read p || [ -n "$p" ] #Or conditional needed to make sure last line not skipped in reading 
	do
		if [ ! "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-${ipArray[$i]}.us-west-2.compute.amazonaws.com -f pgrep -fl smoldyn)" ]; #if smoldyn isn't running on the instance
	    then
			ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-${ipArray[$i]}.us-west-2.compute.amazonaws.com -f mkdir "/home/ec2-user/translation/data"
			echo $p
			ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-${ipArray[$i]}.us-west-2.compute.amazonaws.com -f smoldyn /home/ec2-user/translation/translation.txt --define experiment=$p -wt
			#sleep 2
			#./AWS_runExpts_sub.sh ${ipArray[$i]} $p $KPATH  &

			#-t supresses graphics while -w supresses warnings from Smoldyn. Ignores Host Key Checking to make simultaneous parallel execution possible without ssh warnings.
			i=$((i+1))
		else
			echo "Already running on "$p
		fi
	done < $EXPLIST_PATH

echo Finished starting $i experiments