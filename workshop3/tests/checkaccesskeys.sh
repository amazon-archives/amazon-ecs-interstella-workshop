#!/bin/bash

ACCESSKEYS=$(grep -EHn '[A-Z0-9]{20}' *)
SECRETKEYS=$(grep -EHn '[A-Za-z0-9/\+=]{40}' *)
STATUS=0
if [ ! -z "$ACCESSKEYS" ]; then
  echo "WARNING: Access Keys Detected:"
  echo "$ACCESSKEYS" | awk -F ':' '{print "File:", $1, "| Line:",$2}'
  # We would typically put some sort of notification function here. Maybe send out an SNS notification to a security alias.
  STATUS=1
else
  echo "No access keys detected"
fi
if [ ! -z "$SECRETKEYS" ]; then
  echo "WARNING: Secret Keys Detected"
  echo "$SECRETKEYS" | awk -F ':' '{print "File:", $1, "| Line:",$2}'
  # We would typically put some sort of notification function here. Maybe send out an SNS notification to a security alias.
  STATUS=1
else
  echo "No secret keys detected"
fi

exit $STATUS