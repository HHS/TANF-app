web: python3 manage.py collectstatic --noinput ; gunicorn -b :8080 tanf.wsgi
worker: python3 manage.py process_tasks --log-std
