#!/usr/bin/env bash

echo "Starting celery"

# Celery worker config can be found here: https://docs.celeryq.dev/en/stable/userguide/workers.html#:~:text=The-,hostname,-argument%20can%20expand
celery -A tdpservice.settings worker --loglevel=INFO --concurrency=1 --max-tasks-per-child=1 -n worker1@%h & # tune -c ?
sleep 5

# TODO: Uncomment the following line to add flower service when memory limitation is resolved
celery -A tdpservice.settings --broker=$REDIS_URI flower --port=8080 &
celery -A tdpservice.settings beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler # &