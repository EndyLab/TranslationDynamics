#!/bin/bash
#Akshay Maheshwari, 8/13/2019
#Secure copies experiment analysis from each AWS instance that is active to local directory

KPATH="/Users/Akshay/Dropbox/code/akshay.pem"
DATA_PATH="/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/data/190903_1848/"


for ip in `aws ec2 describe-instances | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -` #for each ip that is running
do		
	if [ ! "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl smoldyn)" ]; #if smoldyn isn't running on the instance
    then
		ip=$(echo $ip| tr - .)
		scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/data/* $DATA_PATH #Copy data from instance to local; could move this statement into if loop below if only want to dl data after finished

		echo "Smoldyn finished running...shutting down instanc "$ip
		instance=`aws ec2 describe-instances --filter Name=ip-address,Values=$ip| grep -i .InstanceId| awk '{print $2}'| cut -d',' -f1| sed -e 's/"//g'` #get the instance id for that instance
		aws ec2 terminate-instances --instance-ids $instance; #terminate that instance
	else 
    	echo "Smoldyn still running on instance "$ip
    fi	
done
