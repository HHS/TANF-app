
#!/bin/sh


# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_LIVE_COMMS=${2}

update_livecomms()
{
    cd live-comms || exit

    if [ "$1" = "rolling" ] ; then
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGHOSTNAME_LIVE_COMMS" --no-route -f manifest.yml --strategy rolling || exit 1
    else
        cf push "$CGHOSTNAME_LIVE_COMMS" --no-route -f manifest.yml
    fi

    cf map-route "$CGHOSTNAME_LIVE_COMMS" app.cloud.gov --hostname "${CGHOSTNAME_LIVE_COMMS}"
}

# perform a rolling update for the backend and frontend deployments if
# specified, otherwise perform a normal deployment
if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    update_livecomms 'rolling'
else
    update_livecomms
fi
