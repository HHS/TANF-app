#!/bin/bash
set -e

DEV_BACKEND_APPS=("tdp-backend-raft" "tdp-backend-qasp" "tdp-backend-a11y")
DEV_CELERY_APPS=("tdp-celery-raft" "tdp-celery-qasp" "tdp-celery-a11y")
STAGING_BACKEND_APPS=("tdp-backend-develop" "tdp-backend-staging")
STAGING_CELERY_APPS=("tdp-celery-develop" "tdp-celery-staging")
PROD_BACKEND="tdp-backend-prod"
PROD_CELERY="tdp-celery-prod"

help() {
    echo "Deploy Keycloak to the Cloud Foundry space you're currently authenticated in."
    echo "Syntax: deploy.sh [-h] -d <rds_service_name>"
    echo "Options:"
    echo "h     Print this help message."
    echo "d     The Cloud Foundry service name of the RDS instance (e.g. tdp-keycloak-db-dev)."
    echo
}

deploy_keycloak() {
    MANIFEST=manifest.tmp.yml
    cp manifest.yml $MANIFEST

    yq eval -i ".applications[0].services[0] = \"$1\"" $MANIFEST

    cf push --no-route -f $MANIFEST -t 180 --strategy rolling
    cf map-route keycloak apps.internal --hostname keycloak

    rm $MANIFEST
}

setup_keycloak_net_pols() {
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

while getopts ":hd:" option; do
   case $option in
      h) # display Help
         help
         exit;;
      d) # RDS service name
         DB_SERVICE_NAME=$OPTARG;;
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

deploy_keycloak $DB_SERVICE_NAME
setup_keycloak_net_pols

popd
