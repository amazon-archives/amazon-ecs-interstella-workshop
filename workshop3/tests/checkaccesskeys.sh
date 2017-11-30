#!/bin/bash

ACCESSKEYS=$(grep -REHnw '[A-Z0-9]{20}' *)
SECRETKEYS=$(grep -REHnw '[A-Za-z0-9/\+=]{40}' *)

# By default, grep will show the output of the pattern matches, but since we don't want to log our access or secret keys anywhere, we're stripping them out before logging anything.

STATUS=0
if [ ! -z "$ACCESSKEYS" ]; then
  echo "ERROR: Access Keys Detected:"
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
  # Not setting a status here because a lot of things can match this regex. Git commit IDs for example.
else
  echo "No secret keys detected"
fi

exit $STATUS
