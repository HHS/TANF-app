#!/bin/bash
set -e

DEV_BACKEND_APPS=("tdp-backend-raft" "tdp-backend-qasp" "tdp-backend-a11y")
DEV_CELERY_APPS=("tdp-celery-raft" "tdp-celery-qasp" "tdp-celery-a11y")
STAGING_BACKEND_APPS=("tdp-backend-develop" "tdp-backend-staging")
STAGING_CELERY_APPS=("tdp-celery-develop" "tdp-celery-staging")
PROD_BACKEND="tdp-backend-prod"
PROD_CELERY="tdp-celery-prod"

PUBLIC_DOMAIN="app.cloud.gov"

# Environment variables that must be set in the deployer's shell.
# These are injected into the CF app's environment via the manifest.
REQUIRED_ENV_VARS=(
    "KEYCLOAK_ADMIN"              # Admin console username
    "KEYCLOAK_ADMIN_PASSWORD"     # Admin console password
    "KC_TDP_DJANGO_CLIENT_SECRET" # tdp-django client secret (realm config)
    "LOGIN_GOV_JWT_KEY"           # Login.gov RSA private key (PEM or base64)
    "CF_DOCKER_PASSWORD"          # Docker registry password/token (used by cf push)
)
OPTIONAL_ENV_VARS=(
    "KC_TDP_GRAFANA_CLIENT_SECRET" # tdp-grafana client secret (realm config)
    "KC_GRAFANA_REDIRECT_URI"      # Grafana OAuth redirect URI (e.g. https://tdp-grafana.app.cloud.gov/login/generic_oauth)
    "KC_GRAFANA_WEB_ORIGIN"        # Grafana web origin (e.g. https://tdp-grafana.app.cloud.gov)
    "KC_GRAFANA_POST_LOGOUT_URI"   # Grafana post-logout redirect URI (e.g. https://tdp-grafana.app.cloud.gov/*)
    "LOGIN_GOV_ACR_VALUES"         # Login.gov identity assurance level
)

help() {
    echo "Deploy Keycloak to the Cloud Foundry space you're currently authenticated in."
    echo ""
    echo "Syntax: deploy.sh [-h] -d <rds_service_name> -p <public_hostname> -i <docker_image> -u <docker_username>"
    echo ""
    echo "Options:"
    echo "  h     Print this help message."
    echo "  d     The Cloud Foundry service name of the RDS instance (e.g. tdp-keycloak-db-dev)."
    echo "  p     The public hostname for Keycloak (e.g. tdp-keycloak-dev)."
    echo "        This will create a public route at <hostname>.${PUBLIC_DOMAIN}"
    echo "        and set KC_HOSTNAME so Keycloak generates correct redirect URIs."
    echo "  i     The Docker image URI for Keycloak (e.g. ghcr.io/hhs/tdp-keycloak:latest)."
    echo "  u     Docker registry username. Password must be set via CF_DOCKER_PASSWORD env var."
    echo ""
    echo "Required environment variables (must be set in your shell):"
    for var in "${REQUIRED_ENV_VARS[@]}"; do
        echo "  $var"
    done
    echo ""
    echo "Optional environment variables:"
    for var in "${OPTIONAL_ENV_VARS[@]}"; do
        echo "  $var"
    done
    echo ""
    echo "Example:"
    echo "  ./deploy.sh -d tdp-keycloak-db-dev -p tdp-keycloak-dev -i ghcr.io/hhs/tdp-keycloak:latest -u myuser"
    echo ""
}

check_required_env_vars() {
    local missing=()
    for var in "${REQUIRED_ENV_VARS[@]}"; do
        if [ -z "${!var:-}" ]; then
            missing+=("$var")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        echo "Error: the following required environment variables are not set:"
        for var in "${missing[@]}"; do
            echo "  $var"
        done
        echo ""
        echo "Set them in your shell before running this script."
        popd
        exit 1
    fi
}

inject_env_vars() {
    local manifest="$1"
    # Env vars used by cf push itself, not by the Keycloak app
    local skip_vars=("CF_DOCKER_PASSWORD")

    for var in "${REQUIRED_ENV_VARS[@]}" "${OPTIONAL_ENV_VARS[@]}"; do
        if [[ " ${skip_vars[*]} " =~ " ${var} " ]]; then
            continue
        fi
        if [ -n "${!var:-}" ]; then
            # Use yq strenv() to safely handle values with special characters
            export "$var"
            yq eval -i ".applications[0].env.$var = strenv($var)" "$manifest"
        fi
    done
}

deploy_keycloak() {
    local db_service="$1"
    local public_hostname="$2"
    local docker_image="$3"
    local docker_username="$4"
    local public_url="https://${public_hostname}.${PUBLIC_DOMAIN}"

    MANIFEST=manifest.tmp.yml
    cp manifest.yml $MANIFEST

    yq eval -i ".applications[0].services[0] = \"${db_service}\"" $MANIFEST
    yq eval -i ".applications[0].env.KC_HOSTNAME = \"${public_url}\"" $MANIFEST
    yq eval -i ".applications[0].docker.image = \"${docker_image}\"" $MANIFEST
    inject_env_vars $MANIFEST

    CF_DOCKER_PASSWORD="$CF_DOCKER_PASSWORD" cf push --no-route -f $MANIFEST -t 180 --strategy rolling --docker-image "$docker_image" --docker-username "$docker_username"

    # Internal route for server-to-server communication (backend/celery -> keycloak)
    cf map-route keycloak apps.internal --hostname keycloak

    # Public route for browser redirects and admin console access
    cf map-route keycloak "$PUBLIC_DOMAIN" --hostname "$public_hostname"

    rm $MANIFEST
}

configure_keycloak_idps() {
    echo "Running IdP configuration task..."
    cf run-task keycloak \
        --command "export SKIP_KEYCLOAK_WAIT=true KEYCLOAK_URL=http://keycloak.apps.internal:8080 KEYCLOAK_MANAGEMENT_URL=http://keycloak.apps.internal:8080 && /opt/keycloak/configure-idps.sh" \
        --name "configure-idps"
}

setup_keycloak_net_pols() {
    # Allow keycloak tasks to reach the running keycloak app via internal route
    cf add-network-policy keycloak keycloak --protocol tcp --port 8080

    CURRENT_SPACE=$(cf target | grep -Eo "tanf-[a-z]+")

    if [ "$CURRENT_SPACE" == "tanf-dev" ]; then
        for app in ${DEV_BACKEND_APPS[@]} ${DEV_CELERY_APPS[@]}; do
            cf add-network-policy $app keycloak --protocol tcp --port 8080
        done
    elif [ "$CURRENT_SPACE" == "tanf-staging" ]; then
        for app in ${STAGING_BACKEND_APPS[@]} ${STAGING_CELERY_APPS[@]}; do
            cf add-network-policy $app keycloak --protocol tcp --port 8080
        done
    elif [ "$CURRENT_SPACE" == "tanf-prod" ]; then
        cf add-network-policy $PROD_BACKEND keycloak --protocol tcp --port 8080
        cf add-network-policy $PROD_CELERY keycloak --protocol tcp --port 8080
    fi
}

pushd "$(dirname "$0")"

while getopts ":hd:p:i:u:" option; do
   case $option in
      h) # display Help
         help
         exit;;
      d) # RDS service name
         DB_SERVICE_NAME=$OPTARG;;
      p) # Public hostname
         PUBLIC_HOSTNAME=$OPTARG;;
      i) # Docker image
         DOCKER_IMAGE=$OPTARG;;
      u) # Docker username
         DOCKER_USERNAME=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         echo
         help
         popd
         exit 1;;
   esac
done

if [ "$#" -eq 0 ]; then
    help
    exit
fi

if [ "$DB_SERVICE_NAME" == "" ]; then
    echo "Error: you must include a database service name with -d."
    echo
    help
    popd
    exit 1
fi

if [ "$PUBLIC_HOSTNAME" == "" ]; then
    echo "Error: you must include a public hostname with -p."
    echo
    help
    popd
    exit 1
fi

if [ "$DOCKER_IMAGE" == "" ]; then
    echo "Error: you must include a Docker image with -i."
    echo
    help
    popd
    exit 1
fi

if [ "$DOCKER_USERNAME" == "" ]; then
    echo "Error: you must include a Docker username with -u."
    echo
    help
    popd
    exit 1
fi

check_required_env_vars

echo "Deploying Keycloak..."
echo "  Docker image:   $DOCKER_IMAGE"
echo "  RDS service:    $DB_SERVICE_NAME"
echo "  Internal route: keycloak.apps.internal"
echo "  Public route:   ${PUBLIC_HOSTNAME}.${PUBLIC_DOMAIN}"
echo ""

deploy_keycloak "$DB_SERVICE_NAME" "$PUBLIC_HOSTNAME" "$DOCKER_IMAGE" "$DOCKER_USERNAME"
setup_keycloak_net_pols
configure_keycloak_idps

popd
