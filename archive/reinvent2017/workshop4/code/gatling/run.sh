#! /bin/sh

# Invoke gatling
gatling.sh -s advancedSim
# Copy results back up to s3 bucket
aws s3 cp results s3://(insert S3 bucket name) --recursive