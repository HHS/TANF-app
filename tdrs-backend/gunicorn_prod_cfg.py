"""Gunicorn production config file."""

# WSGI application path MODULE_NAME:VARIABLE_NAME
wsgi_app = "tdpservice.wsgi:application"

# The granularity of Error log outputs
loglevel = "info"

# The number of worker processes for handling requests
workers = 3
# The socket to bind
bind = "0.0.0.0:8080"
# Restart workers when code changes (development only!)
reload = False
# Write access and error info to /var/log
# accesslog = errorlog = "/var/log/gunicorn/dev.log"
# Redirect stdout/stderr to log file
capture_output = True
# PID file so you can easily fetch process ID
# pidfile = "/var/run/gunicorn/dev.pid"
# Daemonize the Gunicorn process (detach & enter background)
# daemon = True

timeout = 100
