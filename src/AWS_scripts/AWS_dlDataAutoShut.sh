#!/bin/bash
#Akshay Maheshwari, 09/02/2017
#Secure copies experiment analysis from each AWS instance that is active to local directory
EXPERIMENT_PATH="/Users/Akshay/Dropbox/code/smoldyn-2.53-mac/pipeline/expts"
dateformat=$(date +"%y%m%d"_%H%M)
DATA_PATH="/Users/Akshay/Dropbox/code/smoldyn-2.53-mac/pipeline/data/"$dateformat"/"
KPATH="/Users/Akshay/Dropbox/code/akshay.pem"

mkdir $DATA_PATH
cp -r $EXPERIMENT_PATH $DATA_PATH #Copy all experiments into the data folder
cp $EXPERIMENT_PATH/[output]* $DATA_PATH #Move the output_list from experiment folder into data folder
rm -r $EXPERIMENT_PATH/[expt]*  #Clear the experiment folder
rm -r $EXPERIMENT_PATH/[output]*  #Clear the experiment folder

init=`aws ec2 describe-instance-status|grep -i ok` #list how many instances still running
while [ "${#init}" -ne "0" ]; #while any AWS instance is still running
do
	init=`aws ec2 describe-instance-status|grep -i ok` 
	for ip in `aws ec2 describe-instances | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -` #for each ip that is running
	do
	    scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/expts/data/* $DATA_PATH #Copy data from instance to local; could move this statement into if loop below if only want to dl data after finished
	    if [ ! "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl smoldyn)" ]; #if smoldyn isn't running on the instance
	    then  
	    	ip=$(echo $ip| tr - .)
	    	echo "Smoldyn finished running...shutting down instance "$ip
	    	instance=`aws ec2 describe-instances --filter Name=ip-address,Values=$ip| grep -i .InstanceId| awk '{print $2}'| cut -d',' -f1| sed -e 's/"//g'` #get the instance id for that instance
	    	aws ec2 terminate-instances --instance-ids $instance; #terminate that instance
	    else 
	    	echo "Smoldyn still running on instance "$ip
	    fi
	done
	sleep 60
done
