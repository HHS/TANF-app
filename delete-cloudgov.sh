#!/bin/sh
#
# This deletes everything.  Don't use it!
# To actually get it to work, you need to set the
# YESIREALLYWANTTODOTHIS variable to something
#

if [ -z "$YESIREALLYWANTTODOTHIS" ] ; then
	echo "DANGER!  Not deleting unless you set the magic variable.  This deletes everything in your current space."
	exit 1
fi

cf delete tanf -r -f
cf delete-service tanf-db -f 
cf delete-service tanf-storage -f 
cf delete-service-key tanf-keys deployer -f
cf delete-service tanf-keys -f 

