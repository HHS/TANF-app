#!/usr/bin/env bash

set -euo pipefail

EXPECTED_CF_ORG="hhs-acf-ofa"
EXPECTED_CF_SPACE="tanf-prod"
BACKEND_APP_NAME="tdp-backend-prod"
KEYCLOAK_APP_NAME="keycloak"

ADMIN_FRONTEND_ORIGIN="https://admin.tanfdata.acf.hhs.gov"
DJANGO_PUBLIC_ORIGIN="https://tanfdata.acf.hhs.gov"
DJANGO_INTERNAL_ORIGIN="http://${BACKEND_APP_NAME}.apps.internal:8080"
ADMIN_SESSION_COOKIE_NAME="admin_sessionid"
KEYCLOAK_TDP_ADMIN_CLIENT_ID="tdp-admin"

ADMIN_APP_NAME=""
APPLY=false
ALLOW_SECRET_ROTATION=false

usage() {
  cat <<'EOF'
Configure the standalone TDP admin console in the production Cloud Foundry
space. This script configures tdp-admin, tdp-backend-prod, and keycloak.

SAFETY
  * The script only operates in org hhs-acf-ofa / space tanf-prod.
  * It is a dry run unless --apply is supplied.
  * It never prints secret values.
  * It does not restage or restart any application.
  * It refuses to replace an existing secret unless --rotate-secrets is used.

PREREQUISITES
  * Cloud Foundry CLI authenticated with permission to update production apps.
  * jq and openssl installed locally.
  * The production admin app already exists.
  * https://admin.tanfdata.acf.hhs.gov is mapped to the production admin app.
  * A network policy allows the admin app to reach tdp-backend-prod on port 8080.
  * An approved secret manager is ready to store both generated values.

INITIAL PRODUCTION SETUP
  1. Target production and verify the target before doing anything else:

       cf target -o hhs-acf-ofa -s tanf-prod
       cf target
       cf apps
       cf routes

     If the admin-to-backend network policy has not been created, add it:

       cf add-network-policy <production-admin-app> tdp-backend-prod \
         --protocol tcp --port 8080

  2. Generate two independent secrets. Store both values in the approved
     secret manager immediately; they cannot be recovered from this script:

       export ADMIN_API_PROXY_TOKEN="$(openssl rand -hex 32)"
       export KC_TDP_ADMIN_CLIENT_SECRET="$(openssl rand -hex 32)"

     ADMIN_API_PROXY_TOKEN is shared by the admin and Django apps.
     KC_TDP_ADMIN_CLIENT_SECRET is written to Keycloak and to Django as
     KEYCLOAK_TDP_ADMIN_CLIENT_SECRET.

  3. Review the dry run. Replace <production-admin-app> with the app name shown
     by `cf apps`:

       ./scripts/configure-admin-production-env.sh \
         --admin-app <production-admin-app>

  4. Apply the environment variables:

       ./scripts/configure-admin-production-env.sh \
         --admin-app <production-admin-app> \
         --apply

  5. Activate the values during an approved deployment window. Run these in
     order and wait for each command to complete:

       cf restage keycloak
       cf logs keycloak --recent
       # Confirm the logs contain: Keycloak config import complete.

       cf restage tdp-backend-prod
       cf restage <production-admin-app>

  6. Verify both Login.gov and AMS admin login, logout, session isolation, and
     one read plus one CSRF-protected write through /api/admin/*.

SECRET ROTATION
  Generate and store new secrets as in step 2, then repeat the dry run and apply
  commands with --rotate-secrets. This flag acknowledges that existing values
  will be replaced and that admin authentication may be unavailable between
  the Keycloak and application restages.

OPTIONS
  --admin-app NAME    Production Cloud Foundry app serving the admin console.
                      Required; there is intentionally no assumed default.
  --apply             Write the environment variables after all checks pass.
  --rotate-secrets    Permit --apply to replace existing, different secrets.
  -h, --help          Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --admin-app)
      ADMIN_APP_NAME=${2:?--admin-app requires a value}
      shift 2
      ;;
    --apply)
      APPLY=true
      shift
      ;;
    --rotate-secrets)
      ALLOW_SECRET_ROTATION=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument: $1" >&2
      echo >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$ADMIN_APP_NAME" ]]; then
  echo "Error: --admin-app is required. Use --help for the production procedure." >&2
  exit 1
fi

ADMIN_API_PROXY_TOKEN=${ADMIN_API_PROXY_TOKEN:-}
KC_TDP_ADMIN_CLIENT_SECRET=${KC_TDP_ADMIN_CLIENT_SECRET:-}

require_apply_prerequisites() {
  local missing_secrets=()

  [[ -n "$ADMIN_API_PROXY_TOKEN" ]] || missing_secrets+=("ADMIN_API_PROXY_TOKEN")
  [[ -n "$KC_TDP_ADMIN_CLIENT_SECRET" ]] || missing_secrets+=("KC_TDP_ADMIN_CLIENT_SECRET")

  if [[ ${#missing_secrets[@]} -gt 0 ]]; then
    echo "Error: required secret inputs are missing:" >&2
    printf '  %s\n' "${missing_secrets[@]}" >&2
    echo "Generate and store them as described by --help before using --apply." >&2
    exit 1
  fi

  if [[ ${#ADMIN_API_PROXY_TOKEN} -lt 32 ]]; then
    echo "Error: ADMIN_API_PROXY_TOKEN must be at least 32 characters." >&2
    exit 1
  fi

  if [[ ${#KC_TDP_ADMIN_CLIENT_SECRET} -lt 32 ]]; then
    echo "Error: KC_TDP_ADMIN_CLIENT_SECRET must be at least 32 characters." >&2
    exit 1
  fi

  for command_name in cf jq; do
    if ! command -v "$command_name" >/dev/null 2>&1; then
      echo "Error: required command '$command_name' is not installed." >&2
      exit 1
    fi
  done
}

verify_production_target() {
  local target_output current_org current_space

  target_output=$(cf target)
  current_org=$(awk -F':[[:space:]]*' '$1 == "org" { print $2 }' <<< "$target_output")
  current_space=$(awk -F':[[:space:]]*' '$1 == "space" { print $2 }' <<< "$target_output")

  if [[ "$current_org" != "$EXPECTED_CF_ORG" || "$current_space" != "$EXPECTED_CF_SPACE" ]]; then
    echo "Error: refusing to apply outside the production Cloud Foundry target." >&2
    echo "  Current:  org='${current_org:-none}' space='${current_space:-none}'" >&2
    echo "  Required: org='$EXPECTED_CF_ORG' space='$EXPECTED_CF_SPACE'" >&2
    echo "Run: cf target -o $EXPECTED_CF_ORG -s $EXPECTED_CF_SPACE" >&2
    exit 1
  fi
}

verify_apps_exist() {
  local app_name

  for app_name in "$ADMIN_APP_NAME" "$BACKEND_APP_NAME" "$KEYCLOAK_APP_NAME"; do
    if ! cf app "$app_name" --guid >/dev/null 2>&1; then
      echo "Error: production app '$app_name' does not exist or is not accessible." >&2
      exit 1
    fi
  done
}

get_app_environment() {
  local app_name=$1
  local app_guid

  app_guid=$(cf app "$app_name" --guid)
  cf curl "/v3/apps/${app_guid}/env"
}

refuse_unapproved_secret_change() {
  local app_name=$1
  local environment_json=$2
  local variable_name=$3
  local proposed_value=$4
  local is_present current_value

  is_present=$(jq -r --arg key "$variable_name" \
    '.environment_variables | has($key)' <<< "$environment_json")
  if [[ "$is_present" != "true" ]]; then
    return
  fi

  current_value=$(jq -r --arg key "$variable_name" \
    '.environment_variables[$key]' <<< "$environment_json")
  if [[ "$current_value" != "$proposed_value" && "$ALLOW_SECRET_ROTATION" != "true" ]]; then
    echo "Error: $variable_name already has a different value on $app_name." >&2
    echo "Refusing an unapproved production secret rotation. Review --help and rerun" >&2
    echo "with --rotate-secrets during an approved deployment window." >&2
    exit 1
  fi
}

verify_bound_keycloak_credentials() {
  local backend_environment=$1
  local service_name="tdp-keycloak-prod"
  local bound_client_id bound_client_secret

  bound_client_id=$(jq -r --arg service "$service_name" '
    [.system_env_json.VCAP_SERVICES["user-provided"][]?
     | select(.instance_name == $service)
     | .credentials.tdp_admin_client_id // empty]
    | first // empty
  ' <<< "$backend_environment")
  bound_client_secret=$(jq -r --arg service "$service_name" '
    [.system_env_json.VCAP_SERVICES["user-provided"][]?
     | select(.instance_name == $service)
     | .credentials.tdp_admin_client_secret // empty]
    | first // empty
  ' <<< "$backend_environment")

  if [[ -n "$bound_client_id" && "$bound_client_id" != "$KEYCLOAK_TDP_ADMIN_CLIENT_ID" ]]; then
    echo "Error: bound service '$service_name' overrides the admin client ID." >&2
    echo "Update its tdp_admin_client_id credential to '$KEYCLOAK_TDP_ADMIN_CLIENT_ID'" >&2
    echo "before running this script. Django gives the bound service precedence." >&2
    exit 1
  fi

  if [[ -n "$bound_client_secret" && "$bound_client_secret" != "$KC_TDP_ADMIN_CLIENT_SECRET" ]]; then
    echo "Error: bound service '$service_name' overrides the admin client secret." >&2
    echo "Update its tdp_admin_client_secret credential with the approved secret" >&2
    echo "before running this script. Django gives the bound service precedence." >&2
    exit 1
  fi
}

preflight_secret_changes() {
  local admin_environment backend_environment keycloak_environment

  admin_environment=$(get_app_environment "$ADMIN_APP_NAME")
  backend_environment=$(get_app_environment "$BACKEND_APP_NAME")
  keycloak_environment=$(get_app_environment "$KEYCLOAK_APP_NAME")

  verify_bound_keycloak_credentials "$backend_environment"

  refuse_unapproved_secret_change \
    "$ADMIN_APP_NAME" "$admin_environment" ADMIN_API_PROXY_TOKEN "$ADMIN_API_PROXY_TOKEN"
  refuse_unapproved_secret_change \
    "$BACKEND_APP_NAME" "$backend_environment" ADMIN_API_PROXY_TOKEN "$ADMIN_API_PROXY_TOKEN"
  refuse_unapproved_secret_change \
    "$BACKEND_APP_NAME" "$backend_environment" KEYCLOAK_TDP_ADMIN_CLIENT_SECRET "$KC_TDP_ADMIN_CLIENT_SECRET"
  refuse_unapproved_secret_change \
    "$KEYCLOAK_APP_NAME" "$keycloak_environment" KC_TDP_ADMIN_CLIENT_SECRET "$KC_TDP_ADMIN_CLIENT_SECRET"
}

set_app_env() {
  local app_name=$1
  local variable_name=$2
  local variable_value=$3
  local sensitive=${4:-false}

  if [[ "$APPLY" == "true" ]]; then
    cf set-env "$app_name" "$variable_name" "$variable_value"
  elif [[ "$sensitive" == "true" ]]; then
    echo "Would set $variable_name=<redacted> on $app_name"
  else
    echo "Would set $variable_name=$variable_value on $app_name"
  fi
}

if [[ "$APPLY" == "true" ]]; then
  require_apply_prerequisites
  verify_production_target
  verify_apps_exist
  preflight_secret_changes
fi

echo "Production admin environment configuration"
echo "  Cloud Foundry: $EXPECTED_CF_ORG / $EXPECTED_CF_SPACE"
echo "  Admin app:     $ADMIN_APP_NAME"
echo "  Backend app:   $BACKEND_APP_NAME"
echo "  Keycloak app:  $KEYCLOAK_APP_NAME"
if [[ "$APPLY" == "true" ]]; then
  echo "  Mode:          APPLY"
else
  echo "  Mode:          DRY RUN"
fi
if [[ "$ALLOW_SECRET_ROTATION" == "true" ]]; then
  echo "  Rotation:      AUTHORIZED"
fi
echo

set_app_env "$ADMIN_APP_NAME" NEXT_PUBLIC_AUTH_URL "$DJANGO_INTERNAL_ORIGIN"
set_app_env "$ADMIN_APP_NAME" NEXT_PUBLIC_AUTH_BROWSER_URL "$DJANGO_PUBLIC_ORIGIN"
set_app_env "$ADMIN_APP_NAME" NEXT_PUBLIC_BACKEND_URL "$DJANGO_INTERNAL_ORIGIN/v1"
set_app_env "$ADMIN_APP_NAME" ADMIN_BACKEND_URL "$DJANGO_INTERNAL_ORIGIN/admin-api/v1"
set_app_env "$ADMIN_APP_NAME" ADMIN_FRONTEND_ORIGIN "$ADMIN_FRONTEND_ORIGIN"
set_app_env "$ADMIN_APP_NAME" ADMIN_SESSION_COOKIE_NAME "$ADMIN_SESSION_COOKIE_NAME"
set_app_env "$ADMIN_APP_NAME" ADMIN_API_PROXY_TOKEN "$ADMIN_API_PROXY_TOKEN" true

set_app_env "$BACKEND_APP_NAME" ADMIN_FRONTEND_BASE_URL "$ADMIN_FRONTEND_ORIGIN"
set_app_env "$BACKEND_APP_NAME" ADMIN_SESSION_COOKIE_NAME "$ADMIN_SESSION_COOKIE_NAME"
set_app_env "$BACKEND_APP_NAME" ADMIN_API_PROXY_TOKEN "$ADMIN_API_PROXY_TOKEN" true
set_app_env "$BACKEND_APP_NAME" KEYCLOAK_TDP_ADMIN_CLIENT_ID "$KEYCLOAK_TDP_ADMIN_CLIENT_ID"
set_app_env "$BACKEND_APP_NAME" KEYCLOAK_TDP_ADMIN_CLIENT_SECRET "$KC_TDP_ADMIN_CLIENT_SECRET" true

set_app_env "$KEYCLOAK_APP_NAME" KC_TDP_ADMIN_CLIENT_SECRET "$KC_TDP_ADMIN_CLIENT_SECRET" true

echo
if [[ "$APPLY" == "true" ]]; then
  echo "Environment variables were set. Running applications were not changed."
  echo "Complete steps 5 and 6 from --help to activate and verify the configuration."
else
  echo "Dry run complete. No Cloud Foundry changes were made."
  echo "Review --help, provide both stored secrets, and add --apply when approved."
fi
