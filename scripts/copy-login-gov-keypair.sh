#!/usr/bin/env bash
###
# Copies Login.gov JWT_KEY + JWT_CERT from one Cloud.gov application to another.
#
SOURCE_APP=${1}
DEST_APP=${2}

set -e

SOURCE_APP_GUID=$(cf app "$SOURCE_APP" --guid)
SOURCE_APP_ENV=$(cf curl "/v2/apps/$SOURCE_APP_GUID/env")
ENVIRONMENT_JSON=$(printf '%s\n' "$SOURCE_APP_ENV" | jq -r '.environment_json')

JWT_KEY=$(printf '%s\n' "$ENVIRONMENT_JSON" | jq -r '.JWT_KEY')
JWT_CERT=$(printf '%s\n' "$ENVIRONMENT_JSON" | jq -r '.JWT_CERT')

echo "JWT_KEY: $JWT_KEY"
echo "JWT_CERT: $JWT_CERT"

if [ -n "$DEST_APP" ];then
    echo "Copying JWT key and cert from $SOURCE_APP to $DEST_APP..."
    cf set-env "$DEST_APP" JWT_KEY "$JWT_KEY"
    cf set-env "$DEST_APP" JWT_CERT "$JWT_CERT"

    echo "Restaging $DEST_APP..."
    cf restage "$DEST_APP"
fi
