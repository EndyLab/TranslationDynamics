#!/bin/bash
#Akshay Maheshwari, 9/06/2017
#Secure copies experiment analysis from each AWS instance that is active to local directory

EXPERIMENT_PATH="/Users/Akshay/Dropbox/code/smoldyn-2.53-mac/pipeline/expts"
DATA_PATH="/Users/Akshay/Dropbox/code/smoldyn-2.53-mac/pipeline/data/170913_0528"
KPATH="/Users/Akshay/Dropbox/code/akshay.pem"
KEEP_LOCALDATA=true; #Need to implement this conditional once have cloud storage setup.

for ip in `aws ec2 describe-instances | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -` #for each ip that is running
do		
    scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/expts/data/analysis/*[.pkl] $DATA_PATH/analysis #Copy analysis from instance to local; could move this statement into if loop below if only want to dl data after finished

	ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f aws s3 cp /home/ec2-user/expts/data/ s3://akshays3backup/data/170913_0528/ --recursive
	echo "Backing up on s3..."
	while [ "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl s3)" ]; 
    	do
    		sleep 2;
    	done
    	
	if $KEEP_LOCALDATA ; then
		scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/expts/data/* $DATA_PATH #Copy data from instance to local; could move this statement into if loop below if only want to dl data after finished
	fi
		scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/expts/data/*Simtime* $DATA_PATH #Copy data from instance to local; could move this statement into if loop below if only want to dl data after finished
done

#python3 -c "from simanalysis_methods import combinePkls; combinePkls('$DATA_PATH'+'/analysis')"

