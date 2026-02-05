#!/usr/bin/env bash

echo "Starting celery"

if [[ $1 == "cloud" ]]; then
    # Get the computed URI from django settings
    REDIS_URI=$(python manage.py shell -c "from django.conf import settings; print(settings.CELERY_BROKER_URL)" 2>/dev/null)

    echo "Starting Alloy"
    mkdir /home/vcap/app/alloy-data
    wget https://github.com/grafana/alloy/releases/download/v1.9.1/alloy-boringcrypto-linux-amd64.zip
    unzip -a alloy-boringcrypto-linux-amd64.zip && rm -rf alloy-boringcrypto-linux-amd64.zip
    chmod +x alloy-boringcrypto-linux-amd64
    ./alloy-boringcrypto-linux-amd64 run --server.http.listen-addr=0.0.0.0:12345 --storage.path=/home/vcap/app/alloy-data /home/vcap/app/plg/alloy/alloy.config &

    echo "Starting the Celery Exporter"
    curl -L https://github.com/danihodovic/celery-exporter/releases/download/latest/celery-exporter -o ./celery-exporter
    chmod +x ./celery-exporter
    ./celery-exporter --broker-url=$REDIS_URI --port 9808 &
fi

# Celery worker config can be found here: https://docs.celeryq.dev/en/stable/userguide/workers.html#:~:text=The-,hostname,-argument%20can%20expand
celery -A tdpservice.settings worker --loglevel=INFO --concurrency=1 --max-tasks-per-child=1 -n worker1@%h & # tune -c ?
sleep 5

# TODO: Uncomment the following line to add flower service when memory limitation is resolved
celery -A tdpservice.settings --broker=$REDIS_URI flower --port=8080 &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler