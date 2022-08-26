#!/usr/bin/env bash
# Apply database migrations
set -e

echo "REDIS_SERVER"
echo $REDIS_SERVER_LOCAL
if [[ "$REDIS_SERVER_LOCAL" = "TRUE" || "$CIRCLE_JOB" = "backend-owasp-scan" ]]; then
    echo "Run redis server on docker"
else
    echo "Run redis server locally"
    export LD_LIBRARY_PATH=/home/vcap/deps/0/lib/:/home/vcap/deps/1/lib:$LD_LIBRARY_PATH
    ( cd  /home/vcap/deps/0/bin/; ./redis-server /home/vcap/app/redis.conf &)
fi

#
echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate
python manage.py populate_stts
python manage.py collectstatic --noinput

celery -A tdpservice.settings worker -c 1 --max-memory-per-child 5000 &
sleep 5
# TODO: Uncomment the following line to add flower service when memory limitation is resolved
# celery -A tdpservice.settings --broker=$REDIS_URI flower &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="--bind 0.0.0.0:8080 --timeout 10 --workers 3 --reload --log-level $LOGGING_LEVEL"
else
    gunicorn_params="--bind 0.0.0.0:8080 --timeout 10 --workers 3 --log-level $LOGGING_LEVEL"
fi

gunicorn_cmd="gunicorn tdpservice.wsgi:application $gunicorn_params"

exec $gunicorn_cmd
