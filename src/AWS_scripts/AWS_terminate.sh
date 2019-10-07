#!/bin/bash
# Atri Choksi February 28, 2017
#Shuts down all *running* AWS instances
IDS=$(aws ec2 describe-instances --filters  Name=tag:expts,Values=200xgr06 --query "Reservations[].Instances[].[InstanceId]" --output text | tr '\n' ' ')
#IDS=$(aws ec2 describe-instances --filters Name=tag:expts,Values=nano --query "Reservations[].Instances[].[InstanceId]" --output text | tr '\n' ' ')
aws ec2 terminate-instances --instance-ids ${IDS[@]:0:20000}