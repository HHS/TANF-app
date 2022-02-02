
#!/bin/sh


# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME=${2}

update()
{
    cd product-updates || exit

    if [ "$1" = "rolling" ] ; then
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGHOSTNAME" --no-route -f manifest.yml --strategy rolling || exit 1
    else
        cf push "$CGHOSTNAME" --no-route -f manifest.yml
    fi

    cf map-route "$CGHOSTNAME" app.cloud.gov --hostname "${CGHOSTNAME}"
}

if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    update 'rolling'
else
    update
fi
