#!/bin/bash
#Akshay Maheshwari, 9/06/2017
#Secure copies experiment analysis from each AWS instance that is active to local directory

EXPERIMENT_PATH="/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/"
SRC_PATH="/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/src/"

dateformat=$(date +"%y%m%d"_%H%M)
DATA_PATH="/Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/data/"$dateformat"/"
#BACKUP_PATH="s3://my-bucket/MyFolder"
KPATH="/Users/Akshay/Dropbox/code/akshay.pem"
KEEP_LOCALDATA=true; #Need to implement this conditional once have cloud storage setup.
RUN_ANALYSIS=false;
mkdir $DATA_PATH
mkdir $DATA_PATH"/analysis"
cp -r $EXPERIMENT_PATH/expt_* $DATA_PATH #Move all experiments into the data folder
cp $EXPERIMENT_PATH/output* $DATA_PATH #Move the output_list from experiment folder into data folder
cp $EXPERIMENT_PATH/translation* $DATA_PATH #Copy the smoldyn translation.txt to data folder
cp $SRC_PATH/smol_exptSetup* $DATA_PATH
rm -r $EXPERIMENT_PATH/expt*  #Clear the experiment folder
rm -r $EXPERIMENT_PATH/output*  #Clear the experiment folder

#aws s3 cp $DATA_PATH s3://akshays3backup/data/$dateformat/ --recursive

init=`aws ec2 describe-instance-status|grep -i ok` #list how many instances still running
sleep 2
while [ "${#init}" -ne "0" ]; #while any AWS instance is still running
do
	init=`aws ec2 describe-instance-status|grep -i ok` 
	for ip in `aws ec2 describe-instances | grep -i PublicIpAddress  | awk '{ print $2}' | cut -d',' -f1| sed -e 's/"//g'| tr . -` #for each ip that is running
	do		
		sleep 0.5
		if [ ! "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl smoldyn)" ]; #if smoldyn isn't running on the instance
		then
			./AWS_dlAnalysisStoreDataAutoShut_sub.sh $ip $KPATH $RUN_ANALYSIS $DATA_PATH &
		else 
			echo "Smoldyn still running on instance "$ip
		fi
	#sleep 10
	done
	echo "Current runtime..."$SECONDS"s."
	sleep 60 #If don't sleep here, instances that were recently closed will show up under describe-instances. So we wait for them to shut down.
done


	    		#if [ ! "$(ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f test -e ./translation/data/analysis/*[.pkl])" ];
	    		#if [ ! "$(ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com ls -d ./translation/data/pckldone)" ]; #If node analysis hasn't already been run (i.e., no analysis folder yet)
				#if [ ! "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl node_analysis)" ]; #If node analysis isn't already running


		    	#EXPERIMENT=$(ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f "ls translation | grep 'expt*'")

	    		#ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f python3 spaceballs/molhist_calc.py "$bins" "$radius" "$molposTS"
				#while [ "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl molhist_calc)" ]; 
			    #	do
			    #		echo "Molhist_calc running..."
			    		#16s. for expt0, expt1, expt 2 each; must be import causing slowdown
			    #		sleep 5;
			    #	done
			    #scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/spaceballs/data/analysis/*[.pkl] $DATA_PATH/analysis #Copy analysis from instance to local; could move this statement into if loop below if only want to dl data after finished

		    	#ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f aws s3 cp /home/ec2-user/spaceballs/data/ s3://akshays3backup/data/$dateformat/ --recursive
				
				#####S3 backup######
				#echo "Backing up on s3..."
		    	#while [ "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl s3)" ]; 
			    	#do
			    	#	sleep 2;
			    	#done
		    	
		    	
			    ### Transfer data locally###

#python3 -c "from simanalysis_methods import combinePkls; combinePkls('$DATA_PATH'+'/analysis')"

