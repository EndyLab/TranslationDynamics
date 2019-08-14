
KPATH="/Users/Akshay/Dropbox/code/akshay.pem"
ssh -o StrictHostKeyChecking=no -i $3 ec2-user@ec2-$1.us-west-2.compute.amazonaws.com -f mkdir /home/ec2-user/translation
scp -o StrictHostKeyChecking=no -i $3 -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/$2 ec2-user@ec2-$1.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/
scp -o StrictHostKeyChecking=no -i $3 -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/translation.txt ec2-user@ec2-$1.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/
scp -o StrictHostKeyChecking=no -i $3 -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/expts/AWS_runonserver.sh ec2-user@ec2-$1.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/
scp -o StrictHostKeyChecking=no -i $3 -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/src/node_analysis.py ec2-user@ec2-$1.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/
scp -o StrictHostKeyChecking=no -i $3 -r /Users/Akshay/Dropbox/Life/EndyLab/Research/TranslationDynamics/src/analysis_utils.py ec2-user@ec2-$1.us-west-2.compute.amazonaws.com:/home/ec2-user/translation/

sleep 0.2
ssh -o StrictHostKeyChecking=no -i $3 ec2-user@ec2-$1.us-west-2.compute.amazonaws.com -f sh /home/ec2-user/translation/AWS_runonserver.sh $4 $2
