#!/bin/bash

app=${1}
space=${2}

guid=$(cf app "$app" --guid || true)

if [[ $guid == 'FAILED' ]]; then
    echo "Backend not available, skipping migrations."
    exit 0
else
    echo Applying migrations to "$app"
fi

cd ./tdrs-backend || exit 1

run_required() {
    "$@"
    local result=$?
    if [[ $result -ne 0 ]]; then
        echo "Database configuration failed." >&2
        exit "$result"
    fi
}

tunnel_pid=""
env_file="$PWD/.env.ci"
env_created=false

cleanup() {
    local result=$?
    trap - EXIT
    if [[ -n $tunnel_pid ]]; then
        kill "$tunnel_pid" 2>/dev/null || true
        wait "$tunnel_pid" 2>/dev/null || true
    fi
    if [[ $env_created == true ]]; then
        rm -f -- "$env_file"
    fi
    exit "$result"
}
trap cleanup EXIT

if [[ -e $env_file || -L $env_file ]]; then
    echo "Refusing to overwrite an existing .env.ci file." >&2
    exit 1
fi

echo "Install dependencies..."
run_required sudo apt-get install -y gcc
run_required sudo apt-get install -y graphviz
run_required sudo apt-get install -y graphviz-dev
run_required sudo apt install -y libpq-dev python3-dev

run_required python -m venv ./env
run_required source ./env/bin/activate
run_required pip install --upgrade pip pipenv==2026.0.3
run_required pipenv install --dev --system --deploy
echo "Done."

echo "Getting credentials..."
app_vars=$(cf curl /v3/apps/$guid/env)

db_creds=$(echo $app_vars | jq -r '.system_env_json.VCAP_SERVICES."aws-rds"[0].credentials')
connection_str=$(echo $db_creds | jq -r '[.host, .port]' | jq -r 'join(":")')
echo "Done."

echo "Starting tunnel..."
cf ssh -N -L 5432:$connection_str $app &
tunnel_pid=$!
sleep 5
echo "Done."

echo "Setting up environment..."
env_created=true
run_required cp ./.env.example "$env_file"

vcap_services=$(echo $app_vars | jq -r '.system_env_json.VCAP_SERVICES')
vcap_application=$(echo $app_vars | jq -rc '.application_env_json.VCAP_APPLICATION')

# replace host env var
fixed_vcap_services=$(echo $vcap_services | jq -rc '."aws-rds"[0].credentials.host="localhost"')

echo "VCAP_SERVICES='$fixed_vcap_services'" >> .env.ci
echo "VCAP_APPLICATION='$vcap_application'" >> .env.ci
echo "CGAPPNAME_BACKEND='$app'" >> .env.ci
echo "KEYCLOAK_SYNC_ENABLED='no'" >> .env.ci

set -a
run_required source "$env_file"
export DJANGO_CONFIGURATION=Development
export DJANGO_SETTINGS_MODULE=tdpservice.settings.cloudgov
set +a
echo "Done."

echo "Applying migrations..."
run_required python manage.py migrate
echo "Done."

echo "Generating Admin and User Views"
run_required python ./plg/grafana_views/generate_views.py --all
echo "Done."

echo "Applying SQL views"
run_required python manage.py runscript apply_grafana_views
echo "Done."

echo "Creating Postgres Roles and Users"
if [[ $app == "tdp-backend-prod" ]]; then
    echo "Creating prod roles and users"
    run_required python manage.py runscript create_grafana_postgres_role --script-args read_only mr_record_counts_by_tableview stt_section_to_type_mapping
fi
run_required python manage.py runscript create_grafana_postgres_role --script-args read_only data_files_datafile data_files_datafile_view django_admin_log parsers_datafilesummary parser_error stts_stt stts_region users_user users_user_groups user_views
run_required python manage.py runscript create_grafana_postgres_role --script-args admin_read_only all
run_required python manage.py runscript create_grafana_postgres_role --script-args digit_sensitive data_files_datafile data_files_datafile_view django_admin_log etl_etlartifact etl_etlnoderun etl_etlpipelinerun etl_etlqaresult etl_statisticalweight etl_statisticalweightscasecount parsers_datafilesummary parser_error stts_stt stts_region users_user users_user_groups mr_record_counts_by_tableview stt_section_to_type_mapping user_views admin_views
run_required python manage.py runscript create_grafana_readonly_postgres_users --script-args ofa_read_only "$OFA_READ_ONLY_PASSWORD" read_only ofa_admin_read_only "$OFA_ADMIN_READ_ONLY_PASSWORD" admin_read_only ofa_digit_sensitive "$OFA_DIGIT_SENSITIVE_PASSWORD" digit_sensitive
echo "Done."

echo "Populating history tables"
python manage.py populate_history --auto
echo "Done."


if [[ $app == "tdp-backend-develop" || $space == "tanf-dev" ]]; then
    echo "Applying e2e test data"
    python manage.py populate_stts
    python manage.py reset_cypress_profile_editing_users --allow-non-debug
    python manage.py loaddata cypress/users cypress/data_files cypress/regions cypress/profile_editing_regions cypress/profile_editing_users cypress/feature_flags
    echo "Done."
fi

echo "Database configuration applied successfully."
