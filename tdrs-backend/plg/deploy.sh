#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Error, this script expects 3 parameters."
    echo "I.e: ./deploy.sh env_name db_uri aws_rds_service_name"
    exit 1
fi

deploy_pg_exporter() {
    MANIFEST=manifest.$1.yml
    cp manifest.yml $MANIFEST

    APP_NAME="pg-exporter-$1"

    yq eval -i ".applications[0].name = $APP_NAME"  $MANIFEST
    yq eval -i ".applications[0].env.PG_EXPORTER_METRIC_PREFIX = \"pg_$1\""  $MANIFEST
    yq eval -i ".applications[0].env.DATA_SOURCE_NAME = \"$2\""  $MANIFEST
    yq eval -i ".applications[0].services[0] = \"$3\""  $MANIFEST

    cf push --no-route -f $MANIFEST -t 180 --strategy rolling || exit 1
}

# Commands below for when prometheus is deployed
# cf map-route "$APP_NAME" apps.internal --hostname "$APP_NAME"
# cf add-network-policy "$PROMETHEUS" "$APP_NAME" --protocol tcp --port 9187
