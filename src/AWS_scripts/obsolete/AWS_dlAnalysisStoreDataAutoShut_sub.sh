KPATH=$2
ip=$1
RUN_ANALYSIS=$3
DATA_PATH=$4

while [ "$(ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com ls ./translation/data/analysis | grep pkl |wc -c)" -eq 0 ] && $RUN_ANALYSIS; #If there isn't a pkl file in the analysis folder already
do
	if [ ! "$(ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl node_analysis)" ];
	then
	    echo "Analysis starting..."
	    ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f python3 ./translation/node_analysis.py
		echo "$( ssh -o StrictHostKeyChecking=no -i $KPATH ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com -f pgrep -fl node_analysis)" 
		#sleep 0.1
	else ##(if no pkl but node_analysis is active)
		echo "Analysis still running..." 
		sleep 5
	fi
done
 #If there is a pkl file in the analysis folder
if $RUN_ANALYSIS; then
	scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/data/analysis/*[.pkl] $DATA_PATH/analysis #Copy analysis from instance to local; could move this statement into if loop below if only want to dl data after finished
fi

if $KEEP_LOCALDATA ; then
	scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/data/* $DATA_PATH #Copy data from instance to local; could move this statement into if loop below if only want to dl data after finished
else
	scp -o StrictHostKeyChecking=no -i $KPATH -r ec2-user@ec2-$ip.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/data/*Simtime* $DATA_PATH #Only copy simtime anyway since smaller file.
fi

ip=$(echo $ip| tr - .)
echo "Smoldyn finished running...shutting down instance "$ip
instance=`aws ec2 describe-instances --filter Name=ip-address,Values=$ip| grep -i .InstanceId| awk '{print $2}'| cut -d',' -f1| sed -e 's/"//g'` #get the instance id for that instance
aws ec2 terminate-instances --instance-ids $instance; #terminate that instance

