#!/usr/bin/env bash

set -euo pipefail

verify_app()
{
  APP_NAME=$1
  APP_GUID=$(cf app "$APP_NAME" --guid)
  PROCESS_GUID=$(cf curl "/v3/apps/$APP_GUID/processes" | jq -r '.resources[0].guid // empty')

  if [[ -z "$PROCESS_GUID" ]]; then
    echo "$APP_NAME has no runnable process."
    return 1
  fi

  cf curl "/v3/processes/$PROCESS_GUID/stats" | jq -e \
    --arg app "$APP_NAME" \
    'if (.resources | length) == 0 then error($app + " has no running instances") else all(.resources[]; .state == "RUNNING") end'
}

for app_name in "$@"; do
  verify_app "$app_name"
done
