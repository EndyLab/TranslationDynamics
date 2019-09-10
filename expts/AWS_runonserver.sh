mkdir "/home/ec2-user/translation/data"
mkdir "/home/ec2-user/translation/blahhh"
smoldyn /home/ec2-user/translation/translation.txt --define experiment=$2 -wtq
while [ "$( pgrep -fl smoldyn)" ]; #if smoldyn isn't running on the instance
do
	sleep 5
	echo "Smoldyn still running"
done
###### If further analysis, uncomment this
#python3 node_analysis.py
########
aws s3 cp "/home/ec2-user/translation/data/" s3://s3smoldyn/data/$1/ --recursive

echo "Finished experiment "$2
sudo poweroff #used to be sudo halt, which doesn't work sometimes (but does >95% time)