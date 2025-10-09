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

cd ./tdrs-backend

echo "Install dependencies..."
sudo apt-get install -y gcc && sudo apt-get install -y graphviz && sudo apt-get install -y graphviz-dev
sudo apt install -y libpq-dev python3-dev

python -m venv ./env
source ./env/bin/activate
pip install --upgrade pip pipenv
pipenv install --dev --system --deploy
echo "Done."

echo "Getting credentials..."
app_vars=$(cf curl /v2/apps/$guid/env)

db_creds=$(echo $app_vars | jq -r '.system_env_json.VCAP_SERVICES."aws-rds"[0].credentials')
connection_str=$(echo $db_creds | jq -r '[.host, .port]' | jq -r 'join(":")')
echo "Done."

echo "Starting tunnel..."
cf ssh -N -L 5432:$connection_str $app &
sleep 5
echo "Done."

echo "Setting up environment..."
cp ./.env.example ./.env.ci

vcap_services=$(echo $app_vars | jq -r '.system_env_json.VCAP_SERVICES')
vcap_application=$(echo $app_vars | jq -rc '.application_env_json.VCAP_APPLICATION')

# replace host env var
fixed_vcap_services=$(echo $vcap_services | jq -rc '."aws-rds"[0].credentials.host="localhost"')

echo "VCAP_SERVICES='$fixed_vcap_services'" >> .env.ci
echo "VCAP_APPLICATION='$vcap_application'" >> .env.ci

set -a
source .env.ci
export DJANGO_CONFIGURATION=Development
export DJANGO_SETTINGS_MODULE=tdpservice.settings.cloudgov
set +a
echo "Done."

echo "Applying migrations..."
python manage.py migrate
status=$?
echo "Done."

echo "Generating Admin and User Views"
python ./plg/grafana_views/generate_views.py --all
echo "Done."

echo "Applying SQL views"
python manage.py runscript apply_grafana_views
echo "Done."

echo "Creating Postgres Roles and Users"
python manage.py runscript create_grafana_postgres_role --script-args read_only stt_section_to_type_mapping data_files_datafile django_admin_log parsers_datafilesummary parser_error stts_stt stts_region users_user users_user_groups ssp_m1 ssp_m2 ssp_m3 ssp_m4 ssp_m5 ssp_m6 ssp_m7 tanf_t1 tanf_t2 tanf_t3 tanf_t4 tanf_t5 tanf_t6 tanf_t7 tribal_tanf_t1 tribal_tanf_t2 tribal_tanf_t3 tribal_tanf_t4 tribal_tanf_t5 tribal_tanf_t6 tribal_tanf_t7
python manage.py runscript create_grafana_postgres_role --script-args admin_read_only all
python manage.py runscript create_grafana_readonly_postgres_users --script-args ofa_read_only $OFA_READ_ONLY_PASSWORD read_only ofa_admin_read_only $OFA_ADMIN_READ_ONLY_PASSWORD admin_read_only
echo "Done."


if [[ $app == "tdp-backend-develop" || $space == "tanf-dev" ]]; then
    echo "Applying e2e test data"
    python manage.py loaddata cypress/users cypress/data_files
    echo "Done."
fi

echo "Cleaning up..."
deactivate
kill $!
rm ./.env.ci
cd ..
echo "Done."

if [ $status -eq 0 ]
then
    echo "Migrations applied successfully."
    exit 0
else
    echo "Migrations failed."
    exit $status
fi
