#!/usr/bin/env bash
# Apply database migrations
echo "Apply database migrations"
python manage.py makemigrations
python manage.py migrate

echo "Starting Gunicorn"
exec gunicorn tdpservice.wsgi:application --bind 0.0.0.0:8000 --timeout 10 --workers 3 --log-file=- --log-level debug 