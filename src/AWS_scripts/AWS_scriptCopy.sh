#!/bin/bash
#Akshay Maheshwari, 08/31/2017
#Secure copies all experiment scripts to each AWS instance that is active

EXPLIST_PATH="/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/expt_list.txt" #Experiment_list contains new-line separated names of parameter files for each experiment
KPATH="/Users/Akshay/Dropbox/code/akshay.pem"
ipArray=(`aws ec2 describe-instances | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -`)
i=0
while read p || [ -n "$p" ] #Or conditional needed to make sure last line not skipped in reading 
#for i in `aws ec2 describe-instances | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -`
do
	sleep 1
	./AWS_scriptCopy_sub.sh ${ipArray[$i]} $p $KPATH &
	#ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-${ipArray[$i]}.us-west-2.compute.amazonaws.com -f mkdir /home/ec2-user/translation/
	#sleep 0.1
    #scp -o StrictHostKeyChecking=no -i $KPATH -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/$p ec2-user@ec2-${ipArray[$i]}.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/
    #scp -o StrictHostKeyChecking=no -i $KPATH -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/translation.txt ec2-user@ec2-${ipArray[$i]}.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/
    #scp -o StrictHostKeyChecking=no -i $KPATH -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/src/analysis_utils.py ec2-user@ec2-${ipArray[$i]}.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/
    #scp -o StrictHostKeyChecking=no -i $KPATH -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/src/node_analysis.py ec2-user@ec2-${ipArray[$i]}.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/

    i=$((i+1))

#Ignores Host Key Checking to make simultaneous parallel execution possible without ssh warnings.
done < $EXPLIST_PATH
sleep 60;