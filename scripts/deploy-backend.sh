#!/bin/sh

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_BACKEND=${2}

echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
echo BACKEND_HOST: "$CGHOSTNAME_BACKEND"

#Helper method to generate JWT cert and keys for new environment
generate_jwt_cert() 
{
    echo "regenerating JWT cert/key"
    yes 'XX' | openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -sha256
    cf set-env "$CGHOSTNAME_BACKEND" JWT_CERT "$(cat cert.pem)"
    cf set-env "$CGHOSTNAME_BACKEND" JWT_KEY "$(cat key.pem)"
}

update_backend()
{
    cd tdrs-backend || exit
    if [ "$1" = "rolling" ] ; then
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGHOSTNAME_BACKEND" --no-route -f manifest.buildpack.yml  --strategy rolling || exit 1
    else
        cf push "$CGHOSTNAME_BACKEND" --no-route -f manifest.buildpack.yml
        # set up JWT key if needed
        if cf e "$CGHOSTNAME_BACKEND" | grep -q JWT_KEY ; then
            echo jwt cert already created
        else
            generate_jwt_cert
        fi
    fi
    cf map-route "$CGHOSTNAME_BACKEND" app.cloud.gov --hostname "$CGHOSTNAME_BACKEND"
    cd ..
}

strip() {
    # Usage: strip "string" "pattern"
    printf '%s\n' "${1##$2}"
}

bind_backend_to_services() {
    #The cloud.gov space defined via environment variable (e.g., "tanf-dev", "tanf-staging")
    env=$(strip $CF_SPACE "tanf-")

    cf bind-service "$CGHOSTNAME_BACKEND" "tdp-staticfiles-${env}"
    cf bind-service "$CGHOSTNAME_BACKEND" "tdp-datafiles-${env}"
    cf bind-service "$CGHOSTNAME_BACKEND" "tdp-db-${env}"

    bash ./scripts/set-backend-env-vars.sh "$CGHOSTNAME_BACKEND" "$CF_SPACE"

    cf restage "$CGHOSTNAME_BACKEND"
}


if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    # perform a rolling update for the backend and frontend deployments if
    # specified, otherwise perform a normal deployment
    update_backend 'rolling'
elif [ "$DEPLOY_STRATEGY" = "bind" ] ; then
    # Bind the services the application depends on, update the environment
    # variables and restage the app.
    bind_backend_to_services
elif [ "$DEPLOY_STRATEGY" = "initial" ]; then
    # There is no app with this name, and the services need to be bound to it
    # for it to work. the app will fail to start once, have the services bind,
    # and then get restaged.
    update_backend
    bind_backend_to_services
elif [ "$DEPLOY_STRATEGY" = "rebuild" ]; then
    # You want to redeploy the instance under the same name
    # Delete the existing app (with out deleting the services)
    # and perform the initial deployment strategy.
    cf delete "$CGHOSTNAME_BACKEND" -r -f
    update_backend
    bind_backend_to_services
else
    # No changes to deployment config, just deploy the changes and restart
    update_backend
fi
