#!/usr/bin/env bash
set -e

echo "REDIS_SERVER"
echo "redis local: $REDIS_SERVER_LOCAL"
if [[ "$REDIS_SERVER_LOCAL" = "TRUE" || "$CIRCLE_JOB" = "backend-owasp-scan" ]]; then
    echo "Run redis server on docker"
else
    echo "Run redis server locally"
    export LD_LIBRARY_PATH=/home/vcap/deps/0/lib/:/home/vcap/deps/1/lib:$LD_LIBRARY_PATH
    ( cd  /home/vcap/deps/0/bin/; ./redis-server /home/vcap/app/redis.conf &)
fi

# Collect static files. This is needed for swagger to work in local environment
if [[ $DISABLE_COLLECTSTATIC ]]; then
    echo "DISABLE_COLLECTSTATIC is set to true, skipping collectstatic"
else
    echo "Collecting static files"
    python manage.py collectstatic --noinput
fi


celery -A tdpservice.settings worker --loglevel=WARNING --concurrency=2 -n worker1@%h &
celery -A tdpservice.settings worker --loglevel=WARNING --concurrency=2 -n worker2@%h &
sleep 5

# TODO: Uncomment the following line to add flower service when memory limitation is resolved
celery -A tdpservice.settings --broker=$REDIS_URI flower &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="-c gunicorn_dev_cfg.py"
else
    gunicorn_params="-c gunicorn_prod_cfg.py"
fi

gunicorn_cmd="gunicorn $gunicorn_params"

exec $gunicorn_cmd
