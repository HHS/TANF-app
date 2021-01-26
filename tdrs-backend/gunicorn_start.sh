#!/usr/bin/env bash
# Apply database migrations
echo "Applying database migrations"
python manage.py makemigrations
python manage.py migrate
python manage.py populate_stts
python manage.py collectstatic --noinput
echo "Starting Gunicorn"
exec gunicorn tdpservice.wsgi:application --bind 0.0.0.0:8080 --timeout 10 --workers 3 --log-file=- --log-level debug 
