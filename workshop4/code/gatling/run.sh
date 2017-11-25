#! /bin/sh

#simulation=$1
#s3bucket=$2
## Invoke gatling
gatling.sh -s advanced.SimulationA
## Copy results back up to s3 bucket
aws s3 cp results s3://gatlingloadtestresult --recursive