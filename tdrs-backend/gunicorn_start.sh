#!/usr/bin/env bash

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python manage.py createsuperuser --no-input)
fi
(exec gunicorn tdpservice.wsgi:application --bind 0.0.0.0:8000 --timeout 10 --workers 3 --log-file=- --log-level debug) 