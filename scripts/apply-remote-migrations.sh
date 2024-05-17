#!/bin/bash

app=${1}

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
guid=$(cf app --guid $app)
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