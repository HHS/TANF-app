"""
WSGI config for tdpservice project.

It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/
"""
import logging
import os

from django.conf import settings

from tdpservice.tracing import initialize_tracer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tdpservice.settings.local")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

from configurations.wsgi import get_wsgi_application  # noqa

# Initialize OpenTelemetry tracing if enabled
try:
    if getattr(settings, "OTEL_ENABLED", False):
        initialize_tracer()
except Exception as e:
    logging.exception(f"Failed to initialize OpenTelemetry tracing: {e}")

application = get_wsgi_application()
