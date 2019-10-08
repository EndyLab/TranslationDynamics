#!/bin/bash
#Akshay Maheshwari, 08/31/2017
#Initiates $COUNT number of AWS instances of type $TYPE using the AMI image $AMI
sleep 4
AMI=ami-05100a02b85c5e455
KNAME=akshay
SID=sg-10dd6576
TYPE=t3.nano #t3.nano 
EXPLIST_PATH="/Users/Akshay/Documents/TranslationDynamics/expts/expt_list.txt"
COUNT=$(($(wc -l < $EXPLIST_PATH))) #counts number of lines in experiment_list then adds 1 (since bash doesn't count last line)
REGION=us-west-1
echo "Starting $COUNT instances of $TYPE..."
#echo aws ec2 run-instances --image-id $AMI
echo $(( COUNT%901 ))
sleep 5

aws ec2 run-instances --tag-specifications 'ResourceType=instance,Tags=[{Key=expts,Value=crowded-gr3-200x-lowdiff}]' --image-id $AMI --instance-type $TYPE --key-name $KNAME --security-group-ids $SID --count $(( COUNT%901 )) --region $REGION --iam-instance-profile Name="EC2toS3" --instance-initiated-shutdown-behavior=terminate
if [ $COUNT -gt 900 ]; then
	echo 900
	sleep 180
	aws ec2 run-instances --tag-specifications 'ResourceType=instance,Tags=[{Key=expts,Value=crowded-gr3-200x-lowdiff}]' --image-id $AMI --instance-type $TYPE --key-name $KNAME --security-group-ids $SID --count 900 --region $REGION --iam-instance-profile Name="EC2toS3" --instance-initiated-shutdown-behavior=terminate 
fi

echo "Done starting"

#--instance-market-options '{"MarketType":"spot","SpotOptions": {"MaxPrice": "0.002", "InstanceInterruptionBehavior": "hibernate"}}'