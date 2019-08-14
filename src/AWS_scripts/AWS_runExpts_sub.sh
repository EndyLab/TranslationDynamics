ssh -o StrictHostKeyChecking=no -i $3 ec2-user@ec2-$1.us-west-2.compute.amazonaws.com -f mkdir "/home/ec2-user/translation/data"

echo $2
ssh -o StrictHostKeyChecking=no -i $3 ec2-user@ec2-$1.us-west-2.compute.amazonaws.com -f smoldyn /home/ec2-user/translation/translation.txt --define experiment=$2 -twq
