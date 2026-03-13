#!/usr/bin/env bash

echo "Starting celery"

if [[ $1 == "cloud" ]]; then
    # Build the broker URL with TLS scheme and correct DB number (matching cloudgov.py logic)
    REDIS_BASE=$(echo $VCAP_SERVICES | jq -r '."aws-elasticache-redis"[0].credentials | "rediss://:\(.password)@\(.host):\(.port)"')
    ENV_NAME=$(echo $VCAP_APPLICATION | jq -r '.application_name | split("-") | last')
    # Running python method, to not duplicate logic for determining the DB number
    BROKER_DB=$(python -c "from tdpservice.common.util import get_cloudgov_broker_db_numbers; print(get_cloudgov_broker_db_numbers('${ENV_NAME}')['celery'])")
    REDIS_URI="${REDIS_BASE}/${BROKER_DB}"

    echo "Starting Alloy"
    mkdir /home/vcap/app/alloy-data
    wget https://github.com/grafana/alloy/releases/download/v1.9.1/alloy-boringcrypto-linux-amd64.zip
    unzip -a alloy-boringcrypto-linux-amd64.zip && rm -rf alloy-boringcrypto-linux-amd64.zip
    chmod +x alloy-boringcrypto-linux-amd64
    ./alloy-boringcrypto-linux-amd64 run --server.http.listen-addr=0.0.0.0:12345 --storage.path=/home/vcap/app/alloy-data /home/vcap/app/plg/alloy/alloy.config &

    echo "Starting the Celery Exporter"
    curl -L https://github.com/danihodovic/celery-exporter/releases/download/latest/celery-exporter -o ./celery-exporter
    chmod +x ./celery-exporter
    ./celery-exporter --broker-url="$REDIS_URI" --port 9808 &
fi

# Celery worker config can be found here: https://docs.celeryq.dev/en/stable/userguide/workers.html#:~:text=The-,hostname,-argument%20can%20expand
celery -A tdpservice.settings worker --loglevel=INFO --concurrency=1 --max-tasks-per-child=100 -n worker1@%h & # tune -c ?
sleep 5

# TODO: Uncomment the following line to add flower service when memory limitation is resolved
celery -A tdpservice.settings --broker="$REDIS_URI" flower --port=8080 &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
