#!/usr/bin/env bash
# Apply database migrations
set -e
echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate
python manage.py populate_stts
python manage.py collectstatic --noinput

#
celery -A tdpservice.settings worker -l info &
sleep 5
celery -A tdpservice.settings --broker=redis://redis-server:6379 flower &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="--bind 0.0.0.0:8080 --timeout 10 --workers 3 --reload --log-level $LOGGING_LEVEL"
else
    gunicorn_params="--bind 0.0.0.0:8080 --timeout 10 --workers 3 --log-level $LOGGING_LEVEL"
fi

gunicorn_cmd="gunicorn tdpservice.wsgi:application $gunicorn_params"

exec $gunicorn_cmd
