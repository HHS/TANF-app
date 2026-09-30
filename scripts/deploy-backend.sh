#!/bin/bash

##############################
# Global Variable Decls
##############################

# The deployment strategy you wish to employ ( rolling update or setting up a new environment)
DEPLOY_STRATEGY=${1}

#The application name  defined via the manifest yml for the frontend
CGHOSTNAME_FRONTEND=${2}
CGAPPNAME_FRONTEND="tdp-frontend-$CGHOSTNAME_FRONTEND"
CGAPPNAME_BACKEND=${3}
CF_SPACE=${4}
DEPLOY_COMPONENT=${5:-all}

if [[ ! "$DEPLOY_COMPONENT" =~ ^(all|backend|celery)$ ]]; then
  echo "DEPLOY_COMPONENT must be one of: all, backend, celery"
  exit 1
fi

# The cloud.gov space defined via environment variable (e.g., "tanf-dev", "tanf-staging")
env=${CF_SPACE#tanf-}
backend_app_name=${CGAPPNAME_BACKEND#tdp-backend-}

CGAPPNAME_CELERY="tdp-celery-${backend_app_name}"

echo DEPLOY_STRATEGY: "$DEPLOY_STRATEGY"
echo BACKEND_HOST: "$CGAPPNAME_BACKEND"
echo CELERY_APPNAME: "$CGAPPNAME_CELERY"
echo CF_SPACE: "$CF_SPACE"
echo env: "$env"
echo backend_app_name: "$backend_app_name"


##############################
# Function Decls
##############################

set_cf_envs()
{
  var_list=(
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
  "ADMIN_FRONTEND_BASE_URL"
  "LOGGING_LEVEL"
  "JWT_KEY"
  "SENDGRID_API_KEY"
  "OFA_READ_ONLY_PASSWORD"
  "OFA_ADMIN_READ_ONLY_PASSWORD"
  "KEYCLOAK_AUTH_PERCENTAGE"
  "KEYCLOAK_ADMIN_CLIENT_SECRET"
  "KEYCLOAK_DJANGO_CLIENT_SECRET"
  "KEYCLOAK_TDP_ADMIN_REALM"
  "KEYCLOAK_TDP_ADMIN_CLIENT_ID"
  "KEYCLOAK_TDP_ADMIN_CLIENT_SECRET"
  "KEYCLOAK_BROWSER_URL"
  "KEYCLOAK_SERVER_URL"
  "KEYCLOAK_SYNC_ENABLED"
  )

  APP=$1

  echo "Setting environment variables for $APP"

  for var_name in "${var_list[@]}"; do
    # Intentionally unsetting variable if empty
    if [[ -z "${!var_name}" ]]; then
        echo "WARNING: Empty value for $var_name. It will now be unset."
        cf_cmd="cf unset-env $APP $var_name ${!var_name}"
        $cf_cmd
        continue
    elif [[ ("$CF_SPACE" = "tanf-staging") ]]; then
        var_value=${!var_name}
        staging_var="STAGING_$var_name"
        if [[ "${!staging_var}" ]]; then
          var_value=${!staging_var}
        fi
        cf_cmd="cf set-env $APP $var_name ${var_value}"
    else
      cf_cmd="cf set-env $APP $var_name ${!var_name}"
    fi

    echo "Setting var : $var_name"
    $cf_cmd
  done

  set_alloy_envs "$APP"
}

# Helper method to generate JWT cert and keys for new environment
generate_jwt_cert()
{
    APP=$1
    echo "regenerating JWT cert/key"
    yes 'XX' | openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes -sha256
    cf set-env "$CGAPPNAME_BACKEND" JWT_CERT "$(cat cert.pem)"
    cf set-env "$CGAPPNAME_BACKEND" JWT_KEY "$(cat key.pem)"
}

set_alloy_envs() {
  echo "Setting alloy for $APP"

  pushd plg/alloy || exit

  if [ "$APP" = "$CGAPPNAME_BACKEND" ] ; then
    cf set-env "$APP" ALLOY_SYSTEM_NAME "django-system-$backend_app_name"
    cf set-env "$APP" ALLOY_BACKEND_NAME "backend-$backend_app_name"
  elif [ "$APP" = "$CGAPPNAME_CELERY" ] ; then
    cf set-env "$APP" ALLOY_SYSTEM_NAME "celery-system-$backend_app_name"
    cf set-env "$APP" ALLOY_BACKEND_NAME "celery-$backend_app_name"
  else
    echo "Can't set alloy, unknown app"
  fi

  popd || exit
}

add_service_bindings() {
    COMPONENT=$1

    if [[ "$COMPONENT" == "all" || "$COMPONENT" == "backend" ]]; then
      yq eval -i ".applications[0].services[0] = \"tdp-db-${env}\"" ./tdrs-backend/manifest.buildpack.yml
      yq eval -i ".applications[0].services[1] = \"tdp-staticfiles-${env}\"" ./tdrs-backend/manifest.buildpack.yml
      yq eval -i ".applications[0].services[2] = \"tdp-datafiles-${env}\"" ./tdrs-backend/manifest.buildpack.yml
      yq eval -i ".applications[0].services[3] = \"tdp-redis-${env}\"" ./tdrs-backend/manifest.buildpack.yml
    fi

    if [[ "$COMPONENT" == "all" || "$COMPONENT" == "celery" ]]; then
      yq eval -i ".applications[0].services[0] = \"tdp-db-${env}\"" ./tdrs-backend/manifest.celery.yml
      yq eval -i ".applications[0].services[1] = \"tdp-staticfiles-${env}\"" ./tdrs-backend/manifest.celery.yml
      yq eval -i ".applications[0].services[2] = \"tdp-datafiles-${env}\"" ./tdrs-backend/manifest.celery.yml
      yq eval -i ".applications[0].services[3] = \"tdp-redis-${env}\"" ./tdrs-backend/manifest.celery.yml
    fi
}

update_backend()
{
    APP=$1
    STRATEGY=$2

    echo "Deploying $APP with strategy $STRATEGY"

    cd tdrs-backend || exit

    if [ "$APP" = "$CGAPPNAME_BACKEND" ] ; then
      MANIFEST="manifest.buildpack.yml"
    elif [ "$APP" = "$CGAPPNAME_CELERY" ] ; then
      MANIFEST="manifest.celery.yml"
    else
      echo "Unknown app"
      exit
    fi

    args=("$APP")
    args+=("--no-route")
    args+=("-f")
    args+=("$MANIFEST")
    args+=("-t")
    args+=("180")

    if [[ "$APP" = "$CGAPPNAME_CELERY" && "$CF_SPACE" = "tanf-prod" ]]; then
      args+=("-m")
      args+=("2G")
    fi

    if [ "$STRATEGY" = "rolling" ] ; then
        set_cf_envs "$APP"
        # Do a zero downtime deploy.  This requires enough memory for
        # two apps to exist in the org/space at one time.
        args+=("--strategy")
        args+=("rolling")
        cf push "${args[@]}" || exit 1
    else
        cf push "${args[@]}"

        # set up JWT key if needed
        if cf e "$APP" | grep -q JWT_KEY ; then
            echo jwt cert already created
        else
            generate_jwt_cert "$APP"
        fi

        set_cf_envs "$APP"

        cf unset-env "$APP" "AV_SCAN_URL"

        if [ "$CF_SPACE" = "tanf-prod" ]; then
          cf set-env "$APP" AV_SCAN_URL "http://tanf-prod-clamav-rest.apps.internal:9000/scan"
        else
          # Add environment varilables for clamav
          cf set-env "$APP" AV_SCAN_URL "http://tdp-clamav-nginx-$env.apps.internal:9000/scan"

          # Add variable for dev/staging apps to know their DB name. Prod uses default AWS name.
          cf unset-env "$APP" "APP_DB_NAME"
          cf set-env "$APP" "APP_DB_NAME" "tdp_db_$backend_app_name"
        fi
    fi

    cf set-env "$APP" CGAPPNAME_BACKEND "$CGAPPNAME_BACKEND"
    cf restage "$APP"

    cd ..
}

update_backend_network()
{
    echo "Setting backend network"
    cf map-route "$CGAPPNAME_BACKEND" apps.internal --hostname "$CGAPPNAME_BACKEND"
    cf map-route "$CGAPPNAME_CELERY" apps.internal --hostname "$CGAPPNAME_CELERY"

    # Add network policy to allow frontend to access backend
    cf add-network-policy "$CGAPPNAME_FRONTEND" "$CGAPPNAME_BACKEND" --protocol tcp --port 8080

    if [ "$CF_SPACE" = "tanf-prod" ]; then
      # Add network policy to allow backend to access tanf-prod services
      cf add-network-policy "$CGAPPNAME_BACKEND" clamav-rest --protocol tcp --port 9000
    else
      cf add-network-policy "$CGAPPNAME_BACKEND" "tdp-clamav-nginx-$env" --protocol tcp --port 9000
    fi
}

##############################
# Main script body
##############################

# Determine the appropriate BASE_URL for the deployed instance based on the
# provided Cloud.gov App Name
DEFAULT_ROUTE="https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov"
if [ -n "$BASE_URL" ]; then
  # Use Shell Parameter Expansion to replace localhost in the URL
  BASE_URL="${BASE_URL//http:\/\/localhost:8080/$DEFAULT_ROUTE}"
elif [ "$CF_SPACE" = "tanf-prod" ]; then
  # Keep the base url set explicitly for production.
  BASE_URL="https://tanfdata.acf.hhs.gov/v1"
elif [ "$CF_SPACE" = "tanf-staging" ]; then
  # use .acf.hss.gov domain for develop and staging.
  BASE_URL="https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov/v1"
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
  FRONTEND_BASE_URL="https://$CGHOSTNAME_FRONTEND.tanfdata.acf.hhs.gov"
else
  # Default to the route formed with the cloud.gov env for the lower environments.
  FRONTEND_BASE_URL="$DEFAULT_FRONTEND_ROUTE"
fi

load_backend_secret_key()
{
  BACKEND_GUID=$(cf app "$CGAPPNAME_BACKEND" --guid || true)
  if [[ "$BACKEND_GUID" == "FAILED" ]]; then
    return
  fi

  DJANGO_SECRET_KEY=$(cf curl "/v3/apps/$BACKEND_GUID/env" | jq -r '.environment_variables.DJANGO_SECRET_KEY // empty')
}

CONFIGURED_DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY:-}
DJANGO_SECRET_KEY=
load_backend_secret_key

if [[ -z "$DJANGO_SECRET_KEY" ]]; then
  DJANGO_SECRET_KEY=$CONFIGURED_DJANGO_SECRET_KEY
fi

if [[ -z "${DJANGO_SECRET_KEY:-}" && "$DEPLOY_COMPONENT" == "celery" ]]; then
  for _ in {1..60}; do
    echo "Waiting for the backend to publish its shared DJANGO_SECRET_KEY."
    sleep 10
    load_backend_secret_key
    if [[ -n "${DJANGO_SECRET_KEY:-}" ]]; then
      break
    fi
  done
fi

if [[ -z "${DJANGO_SECRET_KEY:-}" && "$DEPLOY_COMPONENT" == "celery" ]]; then
  echo "Backend DJANGO_SECRET_KEY is unavailable; Celery cannot be deployed safely."
  exit 1
fi

if [[ -z "${DJANGO_SECRET_KEY:-}" ]]; then
  DJANGO_SECRET_KEY=$(python3 -c "from secrets import token_urlsafe; print(token_urlsafe(50))")
fi

# These variables are read indirectly by set_cf_envs.
# shellcheck disable=SC2034
DJANGO_SETTINGS_MODULE="tdpservice.settings.cloudgov"
# shellcheck disable=SC2034
if [ "$CF_SPACE" = "tanf-prod" ]; then
  DJANGO_CONFIGURATION="Production"
elif [ "$CF_SPACE" = "tanf-staging" ]; then
  DJANGO_CONFIGURATION="Staging"
else
  DJANGO_CONFIGURATION="Development"
  DJANGO_DEBUG="Yes"
fi


#### there's an env var + binding race condition that prevents initial deploys

CELERY_DEPLOY_STRATEGY=$DEPLOY_STRATEGY

APP_GUID=$(cf app "$CGAPPNAME_BACKEND" --guid || true)
CELERY_GUID=$(cf app "$CGAPPNAME_CELERY" --guid || true)

if [[ $DEPLOY_STRATEGY == 'rolling' ]]; then
  if [[ $APP_GUID == 'FAILED' ]]; then
    DEPLOY_STRATEGY='initial'
  else
    DEPLOY_STRATEGY='rolling'
  fi

  if [[ $CELERY_GUID == 'FAILED' ]]; then
    CELERY_DEPLOY_STRATEGY='initial'
  else
    CELERY_DEPLOY_STRATEGY='rolling'
  fi
fi

if [[ $DEPLOY_STRATEGY == 'rebuild' && ( "$DEPLOY_COMPONENT" == "all" || "$DEPLOY_COMPONENT" == "backend" ) ]]; then
  # You want to redeploy the instance under the same name
  # Delete the existing app (with out deleting the services)
  # and perform the initial deployment strategy.
  cf delete "$CGAPPNAME_BACKEND" -r -f
fi

if [[ $DEPLOY_STRATEGY == 'rebuild' && ( "$DEPLOY_COMPONENT" == "all" || "$DEPLOY_COMPONENT" == "celery" ) ]]; then
  cf delete "$CGAPPNAME_CELERY" -r -f
fi

add_service_bindings "$DEPLOY_COMPONENT"

if [[ "$DEPLOY_COMPONENT" == "all" || "$DEPLOY_COMPONENT" == "backend" ]]; then
  if [[ $DEPLOY_STRATEGY == 'rebuild' ]]; then
    update_backend "$CGAPPNAME_BACKEND" 'initial'
  else
    update_backend "$CGAPPNAME_BACKEND" "$DEPLOY_STRATEGY"
  fi
fi

if [[ "$DEPLOY_COMPONENT" == "all" || "$DEPLOY_COMPONENT" == "celery" ]]; then
  if [[ $CELERY_DEPLOY_STRATEGY == 'rebuild' ]]; then
    update_backend "$CGAPPNAME_CELERY" 'initial'
  else
    update_backend "$CGAPPNAME_CELERY" "$CELERY_DEPLOY_STRATEGY"
  fi
fi

if [[ "$DEPLOY_COMPONENT" == "all" ]]; then
  update_backend_network
fi
