#!/usr/bin/env bash
set -e

# Collect static files. This is needed for swagger to work in local environment
if [[ $DISABLE_COLLECTSTATIC ]]; then
    echo "DISABLE_COLLECTSTATIC is set to true, skipping collectstatic"
else
    echo "Collecting static files"
    python manage.py collectstatic --noinput
fi

echo "Starting Gunicorn"
if [[ "$DJANGO_CONFIGURATION" = "Development" || "$DJANGO_CONFIGURATION" = "Local" ]]; then
    gunicorn_params="-c gunicorn_dev_cfg.py"
else
    gunicorn_params="-c gunicorn_prod_cfg.py"
fi

gunicorn_cmd="gunicorn $gunicorn_params"

exec $gunicorn_cmd
