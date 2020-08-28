#!/bin/sh
#
# This deletes everything.  Don't use it!
# To actually get it to work, you need to set the
# YESIREALLYWANTTODOTHIS variable to something
#

CGHOSTNAME_BACKEND=${1}
CGHOSTNAME_FRONTEND=${2}
YESIREALLYWANTTODOTHIS=${3}

if [ -z "$YESIREALLYWANTTODOTHIS" ] ; then
	echo "DANGER!  Not deleting unless you set the magic variable.  This deletes everything in your current space."
	exit 1
fi

cf delete $CGHOSTNAME_BACKEND -r -f
cf delete $CGHOSTNAME_FRONTEND -r -f
cf delete-service db-raft -f 
cf delete-service-key tdp-app-keys deployer -f
cf delete-service tdp-app-keys -f 

