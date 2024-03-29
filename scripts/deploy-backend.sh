#!/bin/bash

##############################
# Global Variable Decls 
##############################

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGAPPNAME_FRONTEND=${2}
CGAPPNAME_BACKEND=${3}
CGAPPNAME_KIBANA=${4}
CGAPPNAME_PROXY=${5}
CF_SPACE=${6}

strip() {
    # Usage: strip "string" "pattern"
    printf '%s\n' "${1##$2}"
}
# The cloud.gov space defined via environment variable (e.g., "tanf-dev", "tanf-staging")
env=$(strip $CF_SPACE "tanf-")
backend_app_name=$(echo $CGAPPNAME_BACKEND | cut -d"-" -f3)

# Update the Kibana and Elastic proxy names to include the environment
CGAPPNAME_KIBANA="${CGAPPNAME_KIBANA}-${backend_app_name}"
CGAPPNAME_PROXY="${CGAPPNAME_PROXY}-${backend_app_name}"

echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
echo BACKEND_HOST: "$CGAPPNAME_BACKEND"
echo KIBANA_HOST: "$CGAPPNAME_KIBANA"
echo ELASTIC_PROXY_HOST: "$CGAPPNAME_PROXY"
echo CF_SPACE: "$CF_SPACE"
echo env: "$env"
echo backend_app_name: "$backend_app_name"


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
  "BASE_URL"
  "CLAMAV_NEEDED"
  "CYPRESS_TOKEN"
  "DJANGO_CONFIGURATION"
  "DJANGO_DEBUG"
  "DJANGO_SECRET_KEY"
  "DJANGO_SETTINGS_MODULE"
  "DJANGO_SU_NAME"
  "FRONTEND_BASE_URL"
  "KIBANA_BASE_URL"
  "LOGGING_LEVEL"
  "REDIS_URI"
  "JWT_KEY"
  "STAGING_JWT_KEY"
  )

  echo "Setting environment variables for $CGAPPNAME_BACKEND"

  for var_name in ${var_list[@]}; do
    # Intentionally unsetting variable if empty
    if [[ -z "${!var_name}" ]]; then
        echo "WARNING: Empty value for $var_name. It will now be unset."
        cf_cmd="cf unset-env $CGAPPNAME_BACKEND $var_name ${!var_name}"
        $cf_cmd
        continue
    elif [[ ("$var_name" =~ "STAGING_") && ("$CF_SPACE" = "tanf-staging") ]]; then
        sed_var_name=$(echo "$var_name" | sed -e 's@STAGING_@@g')
        cf_cmd="cf set-env $CGAPPNAME_BACKEND $sed_var_name ${!var_name}"
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

update_kibana()
{
  cd tdrs-backend || exit

  # Run template evaluation on manifest
  yq eval -i ".applications[0].services[0] = \"es-${backend_app_name}\""  manifest.proxy.yml
  yq eval -i ".applications[0].env.CGAPPNAME_PROXY = \"${CGAPPNAME_PROXY}\""  manifest.kibana.yml

  if [ "$1" = "rolling" ] ; then
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGAPPNAME_PROXY" --no-route -f manifest.proxy.yml -t 180 --strategy rolling || exit 1
        cf push "$CGAPPNAME_KIBANA" --no-route -f manifest.kibana.yml -t 180 --strategy rolling || exit 1
    else
        cf push "$CGAPPNAME_PROXY" --no-route -f manifest.proxy.yml -t 180
        cf push "$CGAPPNAME_KIBANA" --no-route -f manifest.kibana.yml -t 180
    fi
    
    cf map-route "$CGAPPNAME_PROXY" apps.internal --hostname "$CGAPPNAME_PROXY"
    cf map-route "$CGAPPNAME_KIBANA" apps.internal --hostname "$CGAPPNAME_KIBANA"

    # Add network policy allowing Kibana to talk to the proxy and to allow the backend to talk to Kibana
    cf add-network-policy "$CGAPPNAME_KIBANA" "$CGAPPNAME_PROXY" --protocol tcp --port 8080
    cf add-network-policy "$CGAPPNAME_BACKEND" "$CGAPPNAME_KIBANA" --protocol tcp --port 5601
    cf add-network-policy "$CGAPPNAME_FRONTEND" "$CGAPPNAME_KIBANA" --protocol tcp --port 5601
    cf add-network-policy "$CGAPPNAME_KIBANA" "$CGAPPNAME_FRONTEND" --protocol tcp --port 80

    cd ..
}

update_backend()
{
    cd tdrs-backend || exit
    cf unset-env "$CGAPPNAME_BACKEND" "AV_SCAN_URL"
    
    if [ "$CF_SPACE" = "tanf-prod" ]; then
      cf set-env "$CGAPPNAME_BACKEND" AV_SCAN_URL "http://tanf-prod-clamav-rest.apps.internal:9000/scan/"
    else
      # Add environment varilables for clamav
      cf set-env "$CGAPPNAME_BACKEND" AV_SCAN_URL "http://tdp-clamav-nginx-$env.apps.internal:9000/scan/"
    fi

    if [ "$1" = "rolling" ] ; then
        set_cf_envs
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        cf push "$CGAPPNAME_BACKEND" --no-route -f manifest.buildpack.yml -t 180 --strategy rolling || exit 1
    else
        cf push "$CGAPPNAME_BACKEND" --no-route -f manifest.buildpack.yml -t 180
        # set up JWT key if needed
        if cf e "$CGAPPNAME_BACKEND" | grep -q JWT_KEY ; then
            echo jwt cert already created
        else
            generate_jwt_cert
        fi
    fi

    set_cf_envs
    
    cf map-route "$CGAPPNAME_BACKEND" apps.internal --hostname "$CGAPPNAME_BACKEND"

    # Add network policy to allow frontend to access backend
    cf add-network-policy "$CGAPPNAME_FRONTEND" "$CGAPPNAME_BACKEND" --protocol tcp --port 8080
    
    if [ "$CF_SPACE" = "tanf-prod" ]; then
      # Add network policy to allow backend to access tanf-prod services
      cf add-network-policy "$CGAPPNAME_BACKEND" clamav-rest --protocol tcp --port 9000
    else
      cf add-network-policy "$CGAPPNAME_BACKEND" tdp-clamav-nginx-$env --protocol tcp --port 9000
    fi

    cd ..
}

bind_backend_to_services() {
    echo "Binding services to app: $CGAPPNAME_BACKEND"

    if [ "$CGAPPNAME_BACKEND" = "tdp-backend-develop" ]; then
      # TODO: this is technical debt, we should either make staging mimic tanf-dev 
      #       or make unique services for all apps but we have a services limit
      #       Introducing technical debt for release 3.0.0 specifically.
      env="develop"
    fi

    cf bind-service "$CGAPPNAME_BACKEND" "tdp-staticfiles-${env}"
    cf bind-service "$CGAPPNAME_BACKEND" "tdp-datafiles-${env}"
    cf bind-service "$CGAPPNAME_BACKEND" "tdp-db-${env}"
    
    # The below command is different because they cannot be shared like the 3 above services
    cf bind-service "$CGAPPNAME_BACKEND" "es-${backend_app_name}"
    
    set_cf_envs

    echo "Restarting app: $CGAPPNAME_BACKEND"
    cf restage "$CGAPPNAME_BACKEND"

}

##############################
# Main script body
##############################

# Determine the appropriate BASE_URL for the deployed instance based on the
# provided Cloud.gov App Name
DEFAULT_ROUTE="https://$CGAPPNAME_FRONTEND.app.cloud.gov"
if [ -n "$BASE_URL" ]; then
  # Use Shell Parameter Expansion to replace localhost in the URL
  BASE_URL="${BASE_URL//http:\/\/localhost:8080/$DEFAULT_ROUTE}"
elif [ "$CF_SPACE" = "tanf-prod" ]; then
  # Keep the base url set explicitly for production.
  BASE_URL="https://tanfdata.acf.hhs.gov/v1"
elif [ "$CF_SPACE" = "tanf-staging" ]; then
  # use .acf.hss.gov domain for develop and staging.
  BASE_URL="https://$CGAPPNAME_FRONTEND.acf.hhs.gov/v1"
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
elif [ "$CF_SPACE" = "tanf-staging" ]; then
   # use .acf.hss.gov domain for develop and staging.
  FRONTEND_BASE_URL="https://$CGAPPNAME_FRONTEND.acf.hhs.gov"
else
  # Default to the route formed with the cloud.gov env for the lower environments.
  FRONTEND_BASE_URL="$DEFAULT_FRONTEND_ROUTE"
fi

KIBANA_BASE_URL="http://$CGAPPNAME_KIBANA.apps.internal"

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
  DJANGO_DEBUG="Yes"
  CYPRESS_TOKEN=$CYPRESS_TOKEN
fi

if [ "$DEPLOY_STRATEGY" = "rolling" ] ; then
    # Perform a rolling update for the backend and frontend deployments if
    # specified, otherwise perform a normal deployment
    update_backend 'rolling'
    update_kibana 'rolling'
elif [ "$DEPLOY_STRATEGY" = "bind" ] ; then
    # Bind the services the application depends on and restage the app.
    bind_backend_to_services
elif [ "$DEPLOY_STRATEGY" = "initial" ]; then
    # There is no app with this name, and the services need to be bound to it
    # for it to work. the app will fail to start once, have the services bind,
    # and then get restaged.
    update_backend
    update_kibana
    bind_backend_to_services
elif [ "$DEPLOY_STRATEGY" = "rebuild" ]; then
    # You want to redeploy the instance under the same name
    # Delete the existing app (with out deleting the services)
    # and perform the initial deployment strategy.
    cf delete "$CGAPPNAME_BACKEND" -r -f
    cf delete "$CGAPPNAME_KIBANA" -r -f
    cf delete "$CGAPPNAME_PROXY" -r -f
    update_backend
    update_kibana
    bind_backend_to_services
else
    # No changes to deployment config, just deploy the changes and restart
    update_backend
    update_kibana
fi
