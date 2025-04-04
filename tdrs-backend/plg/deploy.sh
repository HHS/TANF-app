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
    DATASOURCES="datasources.yml"
    cp datasources.template.yml $DATASOURCES
    MANIFEST=manifest.tmp.yml
    cp manifest.yml $MANIFEST

    yq eval -i ".datasources[0].url = \"http://prometheus.apps.internal:8080\""  $DATASOURCES
    yq eval -i ".datasources[1].url = \"http://loki.apps.internal:8080\""  $DATASOURCES
    yq eval -i ".applications[0].services[0] = \"$1\""  $MANIFEST

    cf push --no-route -f $MANIFEST -t 180  --strategy rolling
    cf map-route grafana apps.internal --hostname grafana

    rm $DATASOURCES
    rm $MANIFEST
    popd
}

deploy_prometheus() {
    pushd prometheus
    cf push --no-route -f manifest.yml -t 180  --strategy rolling
    cf map-route prometheus apps.internal --hostname prometheus
    popd
}

deploy_loki() {
    pushd loki
    cf push --no-route -f manifest.yml -t 180  --strategy rolling
    cf map-route loki apps.internal --hostname loki
    popd
}

deploy_alertmanager() {
    pushd alertmanager
    CONFIG=alertmanager.prod.yml
    cp alertmanager.yml $CONFIG
    SENDGRID_API_KEY=$(cf env tdp-backend-prod | grep SENDGRID | cut -d " " -f2-)
    yq eval -i ".global.smtp_auth_password = \"$SENDGRID_API_KEY\"" $CONFIG
    yq eval -i ".receivers[0].email_configs[0].to = \"${ADMIN_EMAILS}\"" $CONFIG
    yq eval -i ".receivers[1].email_configs[0].to = \"${DEV_EMAILS}\"" $CONFIG
    cf push --no-route -f manifest.yml -t 180  --strategy rolling
    cf map-route alertmanager apps.internal --hostname alertmanager
    rm $CONFIG
    popd
}

setup_prod_net_pols() {
    # Target prod environment just in case
    cf target -o hhs-acf-ofa -s tanf-prod

    # Let grafana talk to prometheus and loki
    cf add-network-policy grafana prometheus --protocol tcp --port 8080
    cf add-network-policy grafana loki --protocol tcp --port 8080

    # Let prometheus talk to alertmanager/grafana/loki/prod backend
    cf add-network-policy prometheus alertmanager --protocol tcp --port 8080
    cf add-network-policy prometheus $PROD_BACKEND --protocol tcp --port 8080
    cf add-network-policy prometheus grafana --protocol tcp --port 8080
    cf add-network-policy prometheus loki --protocol tcp --port 8080

    # Let alertmanager/grafana talk to the prod frontend and vice versa
    cf add-network-policy alertmanager $PROD_FRONTEND --protocol tcp --port 80
    cf add-network-policy grafana $PROD_FRONTEND --protocol tcp --port 80
    cf add-network-policy $PROD_FRONTEND alertmanager -s tanf-prod --protocol tcp --port 8080
    cf add-network-policy $PROD_FRONTEND grafana -s tanf-prod --protocol tcp --port 8080

    # Let prod backend send logs to loki
    cf add-network-policy $PROD_BACKEND  loki -s tanf-prod --protocol tcp --port 8080

    # Add network policies to allow alertmanager/grafana to talk to all frontend apps
    for app in ${DEV_FRONTEND_APPS[@]}; do
        cf add-network-policy alertmanager $app -s "tanf-dev" --protocol tcp --port 80
        cf add-network-policy grafana $app -s tanf-dev --protocol tcp --port 80
    done
    for app in ${STAGING_FRONTEND_APPS[@]}; do
        cf add-network-policy alertmanager $app -s "tanf-staging" --protocol tcp --port 80
        cf add-network-policy grafana $app -s tanf-staging --protocol tcp --port 80
    done

    # Add network policies to allow prometheus to talk to all backend apps in all environments
    for app in ${DEV_BACKEND_APPS[@]}; do
        cf add-network-policy prometheus $app -s tanf-dev --protocol tcp --port 8080
        cf add-network-policy prometheus $app -s tanf-dev --protocol tcp --port 9100 # node-exporter
    done
    for app in ${STAGING_BACKEND_APPS[@]}; do
        cf add-network-policy prometheus $app -s tanf-staging --protocol tcp --port 8080
        cf add-network-policy prometheus $app -s tanf-staging --protocol tcp --port 9100 # node-exporter
    done
}

setup_dev_staging_net_pols() {
    # Add network policies to handle routing traffic from lower envs to the prod env
    cf target -o hhs-acf-ofa -s tanf-dev
    for i in ${!DEV_BACKEND_APPS[@]}; do
        cf add-network-policy ${DEV_FRONTEND_APPS[$i]} grafana -s tanf-prod --protocol tcp --port 8080
        cf add-network-policy ${DEV_BACKEND_APPS[$i]} loki -s tanf-prod --protocol tcp --port 8080
        cf add-network-policy ${DEV_FRONTEND_APPS[$i]} alertmanager -s tanf-prod --protocol tcp --port 8080
    done

    cf target -o hhs-acf-ofa -s tanf-staging
    for i in ${!STAGING_BACKEND_APPS[@]}; do
        cf add-network-policy ${STAGING_FRONTEND_APPS[$i]} grafana -s tanf-prod --protocol tcp --port 8080
        cf add-network-policy ${STAGING_BACKEND_APPS[$i]} loki -s tanf-prod --protocol tcp --port 8080
        cf add-network-policy ${STAGING_FRONTEND_APPS[$i]} alertmanager -s tanf-prod --protocol tcp --port 8080
    done
    cf target -o hhs-acf-ofa -s tanf-prod
}

check_email_vars() {
    if [ "${ADMIN_EMAILS}" != "" ] && [ "${DEV_EMAILS}" != "" ]; then
        echo "${ADMIN_EMAILS}"
        echo "${DEV_EMAILS}"
    else
        echo "Missing definitions for ADMIN_EMAILS or DEV_EMAILS or both."
        exit 1
    fi
}

err_help_exit() {
    echo $1
    echo
    help
    popd
    exit
}

pushd "$(dirname "$0")"

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
         err_help_exit "Error: Invalid option";;
   esac
done

if [ "$#" -eq 0 ]; then
    help
    exit
fi

check_email_vars

if [ "$DB_SERVICE_NAME" == "" ]; then
    err_help_exit "Error: you must include a database service name."
fi
if [ "$DEPLOY" == "plg" ]; then
    deploy_prometheus
    deploy_loki
    deploy_grafana $DB_SERVICE_NAME
    deploy_alertmanager
    setup_prod_net_pols
    setup_dev_staging_net_pols
fi
if [ "$DEPLOY" == "pg-exporter" ]; then
    if [ "$DB_URI" == "" ]; then
        err_help_exit "Error: you must provide a database uri when deploying a postgres exporter."
    fi
    deploy_pg_exporter $ENV $DB_URI $DB_SERVICE_NAME
fi
popd
