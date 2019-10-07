#!/bin/bash
#Akshay Maheshwari, 08/31/2017
#Secure copies all experiment scripts to each AWS instance that is active

EXPLIST_PATH="/Users/Akshay/Documents/TranslationDynamics/expts/expt_list.txt" #Experiment_list contains new-line separated names of parameter files for each experiment
KPATH="/Users/Akshay/Dropbox/code/akshay.pem"
REGION=us-west-1
ipArray=(`aws --region us-west-1 ec2 describe-instances --filters "Name=availability-zone,Values=us-west-1b" "Name=tag:expts,Values=spottest" | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -`)
i=0
dateformat=$(date +"%y%m%d"_%H%M)

DATA_PATH="/Users/Akshay/Documents/TranslationDynamics/data/"$dateformat"/"
EXPERIMENT_PATH="/Users/Akshay/Documents/TranslationDynamics/expts/"
SRC_PATH="/Users/Akshay/Documents/TranslationDynamics/src/"

mkdir $DATA_PATH

while read p || [ -n "$p" ] #Or conditional needed to make sure last line not skipped in reading 
#for i in `aws ec2 describe-instances | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -`
do
	sleep 2
	./AWS_scriptCopy_sub.sh ${ipArray[$i]} $p $KPATH $dateformat &
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
cp -r $EXPERIMENT_PATH/expt_* $DATA_PATH #Move all experiments into the data folder
cp $EXPERIMENT_PATH/output* $DATA_PATH #Move the output_list from experiment folder into data folder
cp $EXPERIMENT_PATH/translation* $DATA_PATH #Copy the smoldyn translation.txt to data folder
cp $SRC_PATH/smol_exptSetup* $DATA_PATH
rm -r $EXPERIMENT_PATH/expt*  #Clear the experiment folder
rm -r $EXPERIMENT_PATH/output*  #Clear the experiment folder

#aws s3 cp --recursive $EXPERIMENT_PATH/expt_* s3://s3smoldyn/data/$dateformat/ 
#aws s3 cp --recursive $EXPERIMENT_PATH/expt_* s3://s3smoldyn/data/$dateformat/ 