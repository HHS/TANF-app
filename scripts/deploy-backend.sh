#!/bin/bash

##############################
# Global Variable Decls 
##############################

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGAPPNAME_BACKEND=${2}
CF_SPACE=${3}

strip() {
    # Usage: strip "string" "pattern"
    printf '%s\n' "${1##$2}"
}
# The cloud.gov space defined via environment variable (e.g., "tanf-dev", "tanf-staging")
env=$(strip $CF_SPACE "tanf-")


echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
echo BACKEND_HOST: "$CGAPPNAME_BACKEND"
echo CF_SPACE: "$CF_SPACE"
echo env: "$env"


##############################
# Function Decls
##############################

set_cf_envs()
{
  var_list=(
  "ACFTITAN_HOST"
  "ACFTITAN_KEY"
  "ACFTITAN_USERNAME"
  "AMS_CLIENT_ID"
  "AMS_CLIENT_SECRET"
  "AMS_CONFIGURATION_ENDPOINT"
  "AV_SCAN_URL"
  "BASE_URL"
  "CLAMAV_NEEDED"
  "DJANGO_CONFIGURATION"
  "DJANGO_SECRET_KEY"
  "DJANGO_SETTINGS_MODULE"
  "DJANGO_SU_NAME"
  "FRONTEND_BASE_URL"
  "PROD_JWT_CERT"
  "PROD_JWT_KEY"
  "LOGGING_LEVEL"
  "PROD_ACR_VALUES"
  "PROD_OIDC_OP_AUTHORIZATION_ENDPOINT"
  "PROD_CLIENT_ASSERTION_TYPE"
  "PROD_OIDC_RP_CLIENT_ID"
  "PROD_OIDC_OP_ISSUER"
  "PROD_OIDC_OP_JWKS_ENDPOINT"
  "PROD_OIDC_OP_LOGOUT_ENDPOINT"
  "PROD_OIDC_OP_TOKEN_ENDPOINT"
  "REDIS_URI"
  )

  for var_name in ${var_list[@]}; do
    # Intentionally not setting variable if empty
    if [[ -z "${!var_name}" ]]; then
        echo "WARNING: Empty value for $var_name. It will now be unset."
        cf_cmd="cf unset-env $CGAPPNAME_BACKEND $var_name ${!var_name}"
        $cf_cmd
        continue
    fi

    if [[ "$var_name" =~ "PROD_" ]] && [[ "$CF_SPACE" = "tanf-prod" ]]; then
        prod_var_name=$(echo $var_name | sed -e 's/PROD_//g')
        cf_cmd="cf set-env $CGAPPNAME_BACKEND $prod_var_name ${!var_name}"
    else
    
        cf_cmd="cf set-env $CGAPPNAME_BACKEND $var_name ${!var_name}"
    fi
    
    echo "Setting var : $var_name"
    $cf_cmd
  done

}

# Helper method to generate JWT cert and keys for new environment
generate_jwt_cert() 
{
    echo "regenerating JWT cert/key"
    yes 'XX' | openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -sha256
    cf set-env "$CGAPPNAME_BACKEND" JWT_CERT "$(cat cert.pem)"
    cf set-env "$CGAPPNAME_BACKEND" JWT_KEY "$(cat key.pem)"
}

update_backend()
{
    cd tdrs-backend || exit
    if [ "$1" = "rolling" ] ; then
        set_cf_envs

        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGAPPNAME_BACKEND" --no-route -f manifest.buildpack.yml  --strategy rolling || exit 1
    else
        cf push "$CGAPPNAME_BACKEND" --no-route -f manifest.buildpack.yml
        # set up JWT key if needed
        if cf e "$CGAPPNAME_BACKEND" | grep -q JWT_KEY ; then
            echo jwt cert already created
        else
            generate_jwt_cert
        fi
    fi

    set_cf_envs

    if [ "$CF_SPACE" = "tanf-prod" ]; then
        cf map-route tdp-backend-prod api-tanfdata.acf.hhs.gov
    else
        cf map-route "$CGAPPNAME_BACKEND" app.cloud.gov --hostname "$CGAPPNAME_BACKEND"
    fi

    cd ..
}

bind_backend_to_services() {
    cf bind-service "$CGAPPNAME_BACKEND" "tdp-staticfiles-${env}"
    cf bind-service "$CGAPPNAME_BACKEND" "tdp-datafiles-${env}"
    cf bind-service "$CGAPPNAME_BACKEND" "tdp-db-${env}"
    set_cf_envs
    cf restage "$CGAPPNAME_BACKEND"
}

##############################
# Main script body
##############################

# Determine the appropriate BASE_URL for the deployed instance based on the
# provided Cloud.gov App Name
DEFAULT_ROUTE="https://$CGAPPNAME_BACKEND.app.cloud.gov"
if [ -n "$BASE_URL" ]; then
  # Use Shell Parameter Expansion to replace localhost in the URL
  BASE_URL="${BASE_URL//http:\/\/localhost:8080/$DEFAULT_ROUTE}"
elif [ "$CF_SPACE" = "tanf-prod" ]; then
  # Keep the base url set explicitly for production.
  BASE_URL="https://api-tanfdata.acf.hhs.gov/v1"
else
  # Default to the route formed with the cloud.gov env for the lower environments.
  BASE_URL="$DEFAULT_ROUTE/v1"
fi

DEFAULT_FRONTEND_ROUTE="${DEFAULT_ROUTE//backend/frontend}"
if [ -n "$FRONTEND_BASE_URL" ]; then
  FRONTEND_BASE_URL="${FRONTEND_BASE_URL//http:\/\/localhost:3000/$DEFAULT_FRONTEND_ROUTE}"
elif [ "$CF_SPACE" = "tanf-prod" ]; then
  # Keep the base url set explicitly for production.
  FRONTEND_BASE_URL="https://tanfdata.acf.hhs.gov"
else
  # Default to the route formed with the cloud.gov env for the lower environments.
  FRONTEND_BASE_URL="$DEFAULT_FRONTEND_ROUTE"
fi

# Dynamically generate a new DJANGO_SECRET_KEY
DJANGO_SECRET_KEY=$(python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))")

# Dynamically set DJANGO_CONFIGURATION based on Cloud.gov Space
DJANGO_SETTINGS_MODULE="tdpservice.settings.cloudgov"
if [ "$CF_SPACE" = "tanf-prod" ]; then
  DJANGO_CONFIGURATION="Production"
elif [ "$CF_SPACE" = "tanf-staging" ]; then
  DJANGO_CONFIGURATION="Staging"
else
  DJANGO_CONFIGURATION="Development"
fi

if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    # Perform a rolling update for the backend and frontend deployments if
    # specified, otherwise perform a normal deployment
    update_backend 'rolling'
elif [ "$DEPLOY_STRATEGY" = "bind" ] ; then
    # Bind the services the application depends on and restage the app.
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
    cf delete "$CGAPPNAME_BACKEND" -r -f
    update_backend
    bind_backend_to_services
else
    # No changes to deployment config, just deploy the changes and restart
    update_backend
fi
