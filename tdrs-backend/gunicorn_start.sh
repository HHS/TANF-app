#!/usr/bin/env bash
set -e

# Collect static files. This is needed for swagger to work in local environment
if [[ $DISABLE_COLLECTSTATIC ]]; then
    echo "DISABLE_COLLECTSTATIC is set to true, skipping collectstatic"
else
    echo "Collecting static files"
    python manage.py collectstatic --noinput
fi

if [[ $1 == "cloud" ]]; then
    echo "Starting Alloy"
    mkdir /home/vcap/app/alloy-data
    wget https://github.com/grafana/alloy/releases/download/v1.9.1/alloy-boringcrypto-linux-amd64.zip
    unzip -a alloy-boringcrypto-linux-amd64.zip && rm -rf alloy-boringcrypto-linux-amd64.zip
    chmod +x alloy-boringcrypto-linux-amd64
    ./alloy-boringcrypto-linux-amd64 run --server.http.listen-addr=0.0.0.0:12345 --storage.path=/home/vcap/app/alloy-data /home/vcap/app/plg/alloy/alloy.config &
fi

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="-c gunicorn_dev_cfg.py"
else
    gunicorn_params="-c gunicorn_prod_cfg.py"
fi

gunicorn_cmd="gunicorn $gunicorn_params"

python manage.py runscript create_readonly_grafana_user --script-args "$GRAFANA_PASSWORD" "$GRAFANA_USER"

exec $gunicorn_cmd
