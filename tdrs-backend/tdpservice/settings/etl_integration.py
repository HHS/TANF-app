"""Settings for the live ETL integration suite."""

from copy import deepcopy

from .local import Local


class ETLIntegration(Local):
    """Use a live database with eager Celery Canvas execution."""

    DATABASES = deepcopy(Local.DATABASES)
    DATABASES["default"]["TEST"] = {"MIRROR": "default"}

    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

    EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
