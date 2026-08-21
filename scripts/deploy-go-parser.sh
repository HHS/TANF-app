#!/usr/bin/env bash

set -euo pipefail

DEPLOY_STRATEGY=${1}
PARSER_APP_NAME=${2}
BACKEND_APP_NAME=${3}
CF_SPACE=${4}

if [[ ! "$DEPLOY_STRATEGY" =~ ^(initial|rolling|rebuild)$ ]]; then
  echo "DEPLOY_STRATEGY must be one of: initial, rolling, rebuild"
  exit 1
fi

SPACE_NAME=${CF_SPACE#tanf-}
APP_GUID=$(cf app "$PARSER_APP_NAME" --guid || true)

if [[ "$DEPLOY_STRATEGY" == "rolling" && "$APP_GUID" == "FAILED" ]]; then
  DEPLOY_STRATEGY=initial
fi

if [[ "$DEPLOY_STRATEGY" == "rebuild" && "$APP_GUID" != "FAILED" ]]; then
  cf delete "$PARSER_APP_NAME" -f
  DEPLOY_STRATEGY=initial
fi

pushd tdrs-services/parser >/dev/null
mkdir -p build
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
  -trimpath \
  -o build/go-parser \
  ./cmd/parser

push_args=(
  "$PARSER_APP_NAME"
  -f manifest.cloudgov.yml
  --var "app-name=$PARSER_APP_NAME"
  --var "backend-app-name=$BACKEND_APP_NAME"
  --var "database-service=tdp-db-$SPACE_NAME"
  --var "datafiles-service=tdp-datafiles-$SPACE_NAME"
  --var "redis-service=tdp-redis-$SPACE_NAME"
  -t 180
)

if [[ "$DEPLOY_STRATEGY" == "rolling" ]]; then
  push_args+=(--strategy rolling)
fi

cf push "${push_args[@]}"
popd >/dev/null
