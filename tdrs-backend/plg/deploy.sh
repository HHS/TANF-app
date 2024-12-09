#!/bin/bash
set -e

DEV_BACKEND_APPS=("tdp-backend-raft" "tdp-backend-qasp" "tdp-backend-a11y")
STAGING_BACKEND_APPS=("tdp-backend-develop" "tdp-backend-staging")
PROD_BACKEND="tdp-backend-prod"

DEV_FRONTEND_APPS=("tdp-frontend-raft" "tdp-frontend-qasp" "tdp-frontend-a11y")
STAGING_FRONTEND_APPS=("tdp-frontend-develop" "tdp-frontend-staging")
PROD_FRONTEND="tdp-frontend-prod"

help() {
    echo "Deploy the PLG stack or a Postgres exporter to the Cloud Foundry space you're currently authenticated in."
    echo "Syntax: deploy.sh [-h|a|p|u|d]"
    echo "Options:"
    echo "h     Print this help message."
    echo "a     Deploy the entire PLG stack."
    echo "p     Deploy a postgres exporter, expects the environment name (dev, staging, production) to be passed with switch. Requires -u and -d"
    echo "u     Requires -p. The database URI the exporter should connect with."
    echo "d     The Cloud Foundry service name of the RDS instance. Should be included with all deployments."
    echo
}

deploy_pg_exporter() {
    pushd postgres-exporter
    MANIFEST=manifest.$1.yml
    cp manifest.yml $MANIFEST

    APP_NAME="pg-exporter-$1"
    EXPORTER_SPACE=$(cf target | grep -Eo "tanf(.*)")

    yq eval -i ".applications[0].name = \"$APP_NAME\""  $MANIFEST
    yq eval -i ".applications[0].env.DATA_SOURCE_NAME = \"$2\""  $MANIFEST
    yq eval -i ".applications[0].services[0] = \"$3\""  $MANIFEST

    cf push --no-route -f $MANIFEST -t 180 --strategy rolling
    cf map-route $APP_NAME apps.internal --hostname $APP_NAME

    # Add policy to allow prometheus to talk to pg-exporter regardless of environment
    cf target -o hhs-acf-ofa -s tanf-prod
    cf add-network-policy prometheus $APP_NAME -s "$EXPORTER_SPACE" --protocol tcp --port 9187
    cf target -o hhs-acf-ofa -s "$EXPORTER_SPACE"
    rm $MANIFEST
    popd
}

deploy_grafana() {
    pushd grafana
    APP_NAME="grafana"
    DATASOURCES="datasources.yml"
    cp datasources.template.yml $DATASOURCES
    MANIFEST=manifest.tmp.yml
    cp manifest.yml $MANIFEST

    yq eval -i ".datasources[0].url = \"http://prometheus.apps.internal:8080\""  $DATASOURCES
    yq eval -i ".datasources[1].url = \"http://loki.apps.internal:8080\""  $DATASOURCES
    yq eval -i ".applications[0].services[0] = \"$1\""  $MANIFEST

    cf push --no-route -f $MANIFEST -t 180  --strategy rolling
    cf map-route $APP_NAME apps.internal --hostname $APP_NAME

    # Add policy to allow grafana to talk to prometheus and loki
    cf add-network-policy $APP_NAME prometheus --protocol tcp --port 8080
    cf add-network-policy $APP_NAME loki --protocol tcp --port 8080

    # Add network policies to allow grafana to talk to all frontend apps in all environments
    for app in ${DEV_FRONTEND_APPS[@]}; do
        cf add-network-policy "grafana" $app -s "tanf-dev" --protocol tcp --port 80
    done
    for app in ${STAGING_FRONTEND_APPS[@]}; do
        cf add-network-policy "grafana" $app -s "tanf-staging" --protocol tcp --port 80
    done
    cf add-network-policy "grafana" $PROD_FRONTEND --protocol tcp --port 80

    rm $DATASOURCES
    rm $MANIFEST
    popd
}

deploy_prometheus() {
    pushd prometheus
    cf push --no-route -f manifest.yml -t 180  --strategy rolling
    cf map-route prometheus apps.internal --hostname prometheus

    # Add network policies to allow prometheus to talk to all backend apps in all environments
    for app in ${DEV_BACKEND_APPS[@]}; do
        cf add-network-policy prometheus $app -s "tanf-dev" --protocol tcp --port 8080
    done
    for app in ${STAGING_BACKEND_APPS[@]}; do
        cf add-network-policy prometheus $app -s "tanf-staging" --protocol tcp --port 8080
    done
    cf add-network-policy prometheus $PROD_BACKEND --protocol tcp --port 8080

    popd
}

deploy_loki() {
    pushd loki
    cf push --no-route -f manifest.yml -t 180  --strategy rolling
    cf map-route loki apps.internal --hostname loki
    popd
}

setup_extra_net_pols() {
    # Add network policies to allow frontend/backend to talk to grafana/loki
    cf target -o hhs-acf-ofa -s tanf-dev
    for i in ${!DEV_BACKEND_APPS[@]}; do
        cf add-network-policy ${DEV_FRONTEND_APPS[$i]} grafana -s tanf-prod --protocol tcp --port 8080
        cf add-network-policy ${DEV_BACKEND_APPS[$i]} loki -s tanf-prod --protocol tcp --port 8080
    done

    cf target -o hhs-acf-ofa -s tanf-staging
    for i in ${!STAGING_BACKEND_APPS[@]}; do
        cf add-network-policy ${STAGING_FRONTEND_APPS[$i]} grafana -s tanf-prod --protocol tcp --port 8080
        cf add-network-policy ${STAGING_BACKEND_APPS[$i]} loki -s tanf-prod --protocol tcp --port 8080
    done

    cf target -o hhs-acf-ofa -s tanf-prod
    cf add-network-policy $PROD_FRONTEND grafana -s tanf-prod --protocol tcp --port 8080
    cf add-network-policy $PROD_BACKEND  loki -s tanf-prod --protocol tcp --port 8080
}

err_help_exit() {
    echo $1
    echo
    help
    popd
    exit
}

while getopts ":hap:u:d:" option; do
   case $option in
      h) # display Help
         help
         exit;;
      a) # Deploy PLG stack
         DEPLOY="plg";;
      p) # Deploy a Postgres exporter to $ENV
         ENV=$OPTARG
         DEPLOY="pg-exporter";;
      u) # Bind a Postgres exporter to $DB_URI
         DB_URI=$OPTARG;;
      d) # Bind a Postgres exporter or Grafana to $DB_SERVICE_NAME
         DB_SERVICE_NAME=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         help
         exit;;
   esac
done

if [ "$#" -eq 0 ]; then
    help
    exit
fi

pushd "$(dirname "$0")"
if [ "$DB_SERVICE_NAME" == "" ]; then
    err_help_exit "Error: you must include a database service name."
fi
if [ "$DEPLOY" == "plg" ]; then
    deploy_prometheus
    deploy_loki
    deploy_grafana $DB_SERVICE_NAME
    setup_extra_net_pols
fi
if [ "$DEPLOY" == "pg-exporter" ]; then
    if [ "$DB_URI" == "" ]; then
        err_help_exit "Error: you must provide a database uri when deploying a postgres exporter."
    fi
    deploy_pg_exporter $ENV $DB_URI $DB_SERVICE_NAME
fi
popd
