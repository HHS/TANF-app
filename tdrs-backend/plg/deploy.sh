#!/bin/bash
set -e

help() {
    echo "Deploy the PLG stack or a Postgres exporter to the Cloud Foundry space you're currently authenticated in."
    echo "Syntax: deploy.sh [-h|a|p|u|d]"
    echo "Options:"
    echo "h     Print this help message."
    echo "a     Deploy the entire PLG stack."
    echo "p     Deploy a postgres exporter. Requires -u and -d"
    echo "u     Requires -p. The database URI the exporter should connect with."
    echo "d     Requires -p. The Cloud Foundry service name of the RDS instance."
    echo
}

deploy_pg_exporter() {
    pushd postgres-exporter
    MANIFEST=manifest.$1.yml
    cp manifest.yml $MANIFEST

    APP_NAME="pg-exporter-$1"

    yq eval -i ".applications[0].name = \"$APP_NAME\""  $MANIFEST
    yq eval -i ".applications[0].env.DATA_SOURCE_NAME = \"$2\""  $MANIFEST
    yq eval -i ".applications[0].services[0] = \"$3\""  $MANIFEST

    cf push --no-route -f $MANIFEST -t 180 --strategy rolling
    cf map-route $APP_NAME apps.internal --hostname $APP_NAME

    # Add policy to allow prometheus to talk to pg-exporter
    # TODO: this logic needs to be updated to allow routing accross spaces based on where we want PLG to live.
    cf add-network-policy prometheus $APP_NAME -s "tanf-dev" --protocol tcp --port 9187
    rm $MANIFEST
    popd
}

deploy_grafana() {
    pushd grafana
    APP_NAME="grafana"
    DATASOURCES="datasources.yml"
    cp datasources.template.yml $DATASOURCES

    yq eval -i ".datasources[0].url = \"http://prometheus.apps.internal:8080\""  $DATASOURCES
    yq eval -i ".datasources[1].url = \"http://loki.apps.internal:8080\""  $DATASOURCES

    cf push --no-route -f manifest.yml -t 180  --strategy rolling
    # cf map-route $APP_NAME apps.internal --hostname $APP_NAME
    # Give Grafana a public route for now. Might be able to swap to internal route later.
    cf map-route "$APP_NAME" app.cloud.gov --hostname "${APP_NAME}"

    # Add policy to allow grafana to talk to prometheus and loki
    cf add-network-policy $APP_NAME prometheus --protocol tcp --port 8080
    cf add-network-policy $APP_NAME loki --protocol tcp --port 8080
    rm $DATASOURCES
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
      d) # Bind a Postgres exporter to $DB_SERVICE_NAME
         DB_SERVICE_NAME=$OPTARG;;
     \?) # Invalid option
         echo "Error: Invalid option"
         exit;;
   esac
done

if [ "$#" -eq 0 ]; then
    help
    exit
fi

pushd "$(dirname "$0")"
if [ "$DEPLOY" == "plg" ]; then
    deploy_prometheus
    deploy_loki
    deploy_grafana
fi
if [ "$DEPLOY" == "pg-exporter" ]; then
    if [ "$DB_URI" == "" ] || [ "$DB_SERVICE_NAME" == "" ]; then
        echo "Error: you must also pass -u and -d when deploying a postgres exporter."
        echo
        help
        popd
        exit
    fi
    deploy_pg_exporter $ENV $DB_URI $DB_SERVICE_NAME
fi
popd
