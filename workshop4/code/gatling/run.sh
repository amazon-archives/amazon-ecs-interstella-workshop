#! /bin/sh

simulation=$1
s3bucket=$2

#ls -R | grep ":$" | sed -e 's/:$//' -e 's/[^-][^\/]*\//--/g' -e 's/^/   /' -e 's/-/|/'
#ls -l user-files/simulations/interstella/advancedSim.scala
#ls -l user-files/simulations/interstella/basicSim.scala
#pwd

## Invoke gatling
gatling.sh -s $simulation
## Copy results back up to s3 bucket
aws s3 cp results s3://$s3bucket --recursive