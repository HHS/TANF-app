#!/bin/bash
set -e

deploy_pg_exporter() {
    pushd postgres-exporter
    MANIFEST=manifest.$1.yml
    cp manifest.yml $MANIFEST

    APP_NAME="pg-exporter-$1"

    yq eval -i ".applications[0].name = \"$APP_NAME\""  $MANIFEST
    yq eval -i ".applications[0].env.DATA_SOURCE_NAME = \"$2\""  $MANIFEST
    yq eval -i ".applications[0].services[0] = \"$3\""  $MANIFEST

    cf push --no-route -f $MANIFEST -t 180
    cf map-route $APP_NAME apps.internal --hostname $APP_NAME

    # Add policy to allow prometheus to talk to pg-exporter
    cf add-network-policy prometheus $APP_NAME --protocol tcp --port 9187
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

    cf push --no-route -f manifest.yml -t 180
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
    cf push --no-route -f manifest.yml -t 180
    cf map-route prometheus apps.internal --hostname prometheus
    popd
}

deploy_loki() {
    pushd loki
    cf push --no-route -f manifest.yml -t 180
    cf map-route loki apps.internal --hostname loki
    popd
}

pushd "$(dirname "$0")"
# Fancy logic for deploys goes here
deploy_prometheus
deploy_loki
deploy_grafana
deploy_pg_exporter REDACTED
popd
