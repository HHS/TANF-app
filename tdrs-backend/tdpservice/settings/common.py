"""Define settings for all environments."""

import json
import logging
import logging.handlers
import os
from distutils.util import strtobool
from os.path import join
from typing import Any, Optional

from django.core.exceptions import ImproperlyConfigured
from celery.schedules import crontab

from configurations import Configuration
from celery.schedules import crontab
from corsheaders.defaults import default_headers

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_required_env_var_setting(
    env_var_name: str,
    setting_name: Optional[str] = None
) -> Any:
    """Retrieve setting from environment variable, otherwise raise an error."""
    env_var = os.getenv(env_var_name)
    if not env_var:
        raise ImproperlyConfigured(
            f'Missing required setting: {setting_name or env_var_name} - must '
            f'set {env_var_name} environment variable'
        )

    return env_var


class Common(Configuration):
    """Define configuration class."""

    INSTALLED_APPS = (
        "colorfield",
        "admin_interface",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        # Third party apps
        "rest_framework",  # Utilities for rest apis
        "rest_framework.authtoken",  # Token authentication
        "django_filters",
        "django_admin_logs",  # logs for admin site
        "corsheaders",
        "django_extensions",
        "drf_yasg",
        "django_celery_beat",
        "storages",
        "django_prometheus",
        # Local apps
        "tdpservice.core.apps.CoreConfig",
        "tdpservice.users",
        "tdpservice.stts",
        "tdpservice.data_files",
        "tdpservice.security",
        "tdpservice.scheduling",
        "tdpservice.email",
        "tdpservice.search_indexes",
        "tdpservice.parsers",
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        "django_prometheus.middleware.PrometheusBeforeMiddleware",
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "tdpservice.users.api.middleware.AuthUpdateMiddleware",
        "csp.middleware.CSPMiddleware",
        "tdpservice.middleware.NoCacheMiddleware",
        "django_prometheus.middleware.PrometheusAfterMiddleware",
    )
    
    # OpenTelemetry Tracing Configuration
    OTEL_ENABLED = bool(strtobool(os.getenv("OTEL_ENABLED", "yes")))
    OTEL_SERVICE_NAME = "tdp-backend"
    OTEL_EXPORTER_OTLP_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4317")
    OTEL_PROPAGATORS = "tracecontext"

    PROMETHEUS_LATENCY_BUCKETS = (.1, .2, .5, .6, .8, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.5, 9.0, 12.0, 15.0, 20.0, 30.0, float("inf"))
    PROMETHEUS_METRIC_NAMESPACE = ""

    APP_NAME = "dev"
    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = "tdpservice.urls"
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
    WSGI_APPLICATION = "tdpservice.wsgi.application"

    # Application URLs
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:8080/v1')
    FRONTEND_BASE_URL = os.getenv('FRONTEND_BASE_URL', 'http://localhost:3000')

    # Email Server
    EMAIL_BACKEND = "tdpservice.email.backend.SendgridEmailBackend"
    EMAIL_HOST_USER = "no-reply@tanfdata.acf.hhs.gov"
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', None)
    SENDGRID_SANDBOX_MODE_IN_DEBUG = False

    # Whether to use localstack in place of a live AWS S3 environment
    USE_LOCALSTACK = bool(strtobool(os.getenv("USE_LOCALSTACK", "no")))

    # Those who will receive error notifications from django via email
    ADMINS = (("Admin1", "ADMIN_EMAIL_FIRST"), ("Admin2", "ADMIN_EMAIL_SECOND"))

    DATABASES = {
        "default": {
            "ENGINE": "django_prometheus.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT"),
        }
    }

    # General
    APPEND_SLASH = True
    TIME_ZONE = "UTC"
    LANGUAGE_CODE = "en-us"
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_URL = FRONTEND_BASE_URL
    LOGIN_REDIRECT_URL = "/"

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = os.path.join(BASE_DIR, "static")
    STATICFILES_DIRS = []
    STATIC_URL = "/static/"
    STATICFILES_FINDERS = (
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    )

    # By default collectstatic will store files locally so these settings are
    # not used but they must be defined, lest the server will fail to startup.
    AWS_S3_STATICFILES_ACCESS_KEY = None
    AWS_S3_STATICFILES_SECRET_KEY = None
    AWS_S3_STATICFILES_BUCKET_NAME = None
    AWS_S3_STATICFILES_ENDPOINT = None
    AWS_S3_STATICFILES_REGION_NAME = None

    # Store uploaded files in S3
    # http://django-storages.readthedocs.org/en/latest/index.html
    DEFAULT_FILE_STORAGE = 'tdpservice.backends.DataFilesS3Storage'
    AWS_S3_DATAFILES_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_S3_DATAFILES_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_S3_DATAFILES_BUCKET_NAME = os.getenv('AWS_BUCKET')
    AWS_S3_DATAFILES_REGION_NAME = os.getenv('AWS_REGION_NAME', 'us-gov-west-1')
    AWS_S3_DATAFILES_ENDPOINT = \
        f'https://s3-{AWS_S3_DATAFILES_REGION_NAME}.amazonaws.com'

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), "media")
    MEDIA_URL = "/media/"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [os.path.join(BASE_DIR, "templates")],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(os.getenv("DJANGO_DEBUG", "no"))

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": (
                "django.contrib.auth.password_validation."
                "UserAttributeSimilarityValidator"
            ),
        },
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]

    # Logging
    # set level as 'INFO' if env var is not set
    LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "django.server": {
                "()": "django.utils.log.ServerFormatter",
                "format": "[%(server_time)s] %(message)s",
            },
            "verbose": {
                "format": (
                    "%(asctime)s %(levelname)s %(filename)s::%(funcName)s:L%(lineno)d :  %(message)s"
                )
            },
            "simple": {"format": "%(levelname)s %(message)s"},
            "color": {"()": "tdpservice.core.logger.ColorFormatter",
                      "format": "%(asctime)s %(levelname)s %(filename)s::%(funcName)s:L%(lineno)d :  %(message)s"}
        },
        "filters": {"require_debug_true": {"()": "django.utils.log.RequireDebugTrue"}},
        "handlers": {
            "django.server": {
                "level": LOGGING_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "django.server",
            },
            "console": {
                "level": LOGGING_LEVEL,
                "class": "logging.StreamHandler",
                "formatter": "simple",
            },
            "application": {
                "class": "logging.StreamHandler",
                "formatter": "color",
            },
            "s3":{
                "class": "tdpservice.log_handler.S3FileHandler",
                'filename': "/tmp/s3.log",
                "formatter": "verbose",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "verbose",
                "filename": "/tmp/django.log",
                "maxBytes": 1024*1024*10, # 10 MiB
                "backupCount": 5,
            }
        },
        "loggers": {
            "tdpservice": {
               "handlers": ["application", "file"],
               "propagate": True,
               "level": LOGGING_LEVEL
            },
            "tdpservice.parsers": {
               "handlers": ["application", "file", "s3"],
               "propagate": False,
               "level": LOGGING_LEVEL
            },
            "django": {"handlers": ["console", "file"], "propagate": True},
            "django.server": {
                "handlers": ["django.server", "file"],
                "propagate": False,
                "level": LOGGING_LEVEL
            },
            "django.request": {
                "handlers": ["console", "file"],
                "propagate": False,
                "level": LOGGING_LEVEL
            },
            "django.db.backends": {"handlers": ["console", "file"], "level": "INFO"},
        },
    }

    PARSER_LOGGER = logging.getLogger('tdpservice.parsers')

    # Custom user app
    AUTH_USER_MODEL = "users.User"

    # Username or email for initial Django Super User
    # NOTE: In a deployed context this will default to the Product Owner
    DJANGO_SUPERUSER_NAME = get_required_env_var_setting(
        'DJANGO_SU_NAME',
        'DJANGO_SUPERUSER_NAME'
    )

    # Sessions
    SESSION_ENGINE = "tdpservice.core.custom_session_engine"
    SIGNED_COOKIE_EXPIRES = 60 * 60 * 12  # 12 hours
    SESSION_COOKIE_HTTPONLY = True
    SESSION_SAVE_EVERY_REQUEST = True
    SESSION_COOKIE_AGE = 60 * 30  # 30 minutes
    # The CSRF token Cookie holds no security benefits when confined to HttpOnly.
    # Setting this to false to allow the frontend to include it in the header
    # of API POST calls to prevent false negative authorization errors.
    # https://docs.djangoproject.com/en/2.2/ref/settings/#csrf-cookie-httponly
    CSRF_COOKIE_HTTPONLY = False
    CSRF_TRUSTED_ORIGINS = ['.app.cloud.gov', '.acf.hhs.gov']


    # Django Rest Framework
    DEFAULT_RENDERER_CLASSES = ['rest_framework.renderers.JSONRenderer']
    TEST_REQUEST_RENDERER_CLASSES = ['rest_framework.renderers.JSONRenderer',
                                     'rest_framework.renderers.MultiPartRenderer']
    if DEBUG:
        DEFAULT_RENDERER_CLASSES.append('rest_framework.renderers.BrowsableAPIRenderer')

    REST_FRAMEWORK = {
        "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
        "PAGE_SIZE": int(os.getenv("DJANGO_PAGINATION_LIMIT", 32)),
        "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
        "DEFAULT_RENDERER_CLASSES": DEFAULT_RENDERER_CLASSES,
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
        "DEFAULT_AUTHENTICATION_CLASSES": (
            "tdpservice.users.authentication.CustomAuthentication",
            "rest_framework.authentication.SessionAuthentication",
            "tdpservice.security.utils.ExpTokenAuthentication",
        ),
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend",
        ],
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
        "TEST_REQUEST_RENDERER_CLASSES": TEST_REQUEST_RENDERER_CLASSES,
    }

    AUTHENTICATION_BACKENDS = (
        "tdpservice.users.authentication.CustomAuthentication",
        "django.contrib.auth.backends.ModelBackend",
    )

    TOKEN_EXPIRATION_HOURS = int(os.getenv("TOKEN_EXPIRATION_HOURS", 24))

    # CORS
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = True
    CORS_PREFLIGHT_MAX_AGE = 1800
    CORS_ALLOW_HEADERS = list(default_headers) + [
        'x-service-name',
    ]


    # Capture all logging statements across the service in the root handler
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler())

    ###
    # AV Scanning Settings
    #
    ###

    # Flag for local testing to enable AV Scans
    RAW_CLAMAV = os.getenv('CLAMAV_NEEDED', "True").strip("\"")
    logger.debug("RAW_CLAMAV: " + str(RAW_CLAMAV))
    CLAMAV_NEEDED = bool(strtobool(RAW_CLAMAV))

    # The URL endpoint to send AV scan requests to (clamav-rest/clamav-nginx-proxy)
    AV_SCAN_URL = os.getenv('AV_SCAN_URL')

    # The factor used to determine how long to wait before retrying failed scans
    # NOTE: This value exponentially increases up to the maximum retries allowed
    # algo: {backoff factor} * (2 ** ({number of total retries} - 1))
    AV_SCAN_BACKOFF_FACTOR = int(os.getenv('AV_SCAN_BACKOFF_FACTOR', 1))

    # The maximum number of times to retry failed virus scans
    AV_SCAN_MAX_RETRIES = int(os.getenv('AV_SCAN_MAX_RETRIES', 5))

    # The number of seconds to wait for socket response from clamav-rest
    AV_SCAN_TIMEOUT = int(os.getenv('AV_SCAN_TIMEOUT', 30))

    s3_src = "s3-us-gov-west-1.amazonaws.com"

    CSP_DEFAULT_SRC = ("'none'")
    CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", s3_src)
    CSP_IMG_SRC = ("'self'", "data:", s3_src)
    CSP_FONT_SRC = ("'self'", s3_src)
    CSP_CONNECT_SRC = ("'self'", "*.cloud.gov")
    CSP_MANIFEST_SRC = ("'self'")
    CSP_OBJECT_SRC = ("'none'")
    CSP_FRAME_ANCESTORS = ("'none'")
    CSP_FORM_ACTION = ("'self'")
    CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", s3_src)


    ####################################
    # Authentication Provider Settings #
    ####################################

    # Login.gov #
    LOGIN_GOV_ACR_VALUES = os.getenv(
        'ACR_VALUES',
        'http://idmanagement.gov/ns/assurance/ial/1'
    )
    LOGIN_GOV_AUTHORIZATION_ENDPOINT = os.getenv(
        'OIDC_OP_AUTHORIZATION_ENDPOINT',
        'https://idp.int.identitysandbox.gov/openid_connect/authorize'
    )
    LOGIN_GOV_CLIENT_ASSERTION_TYPE = os.getenv(
        'CLIENT_ASSERTION_TYPE',
        'urn:ietf:params:oauth:client-assertion-type:jwt-bearer'
    )
    LOGIN_GOV_CLIENT_ID = os.getenv(
        'OIDC_RP_CLIENT_ID',
        'urn:gov:gsa:openidconnect.profiles:sp:sso:hhs:tanf-proto-dev'
    )
    LOGIN_GOV_ISSUER = os.getenv(
        'OIDC_OP_ISSUER',
        'https://idp.int.identitysandbox.gov/'
    )
    LOGIN_GOV_JWKS_ENDPOINT = os.getenv(
        'OIDC_OP_JWKS_ENDPOINT',
        'https://idp.int.identitysandbox.gov/api/openid_connect/certs'
    )
    # JWT_KEY must be set, there is no functional default.
    LOGIN_GOV_JWT_KEY = get_required_env_var_setting(
        'JWT_KEY',
        'LOGIN_GOV_JWT_KEY'
    )
    LOGIN_GOV_LOGOUT_ENDPOINT = os.getenv(
        'OIDC_OP_LOGOUT_ENDPOINT',
        'https://idp.int.identitysandbox.gov/openid_connect/logout'
    )
    LOGIN_GOV_TOKEN_ENDPOINT = os.getenv(
        'OIDC_OP_TOKEN_ENDPOINT',
        'https://idp.int.identitysandbox.gov/api/openid_connect/token'
    )

    ENABLE_DEVELOPER_GROUP = True

    # AMS OpenID #
    AMS_CONFIGURATION_ENDPOINT = os.getenv(
        'AMS_CONFIGURATION_ENDPOINT',
        'https://sso-stage.acf.hhs.gov/auth/realms/ACF-SSO/.well-known/openid-configuration'
    )

    # The CLIENT_ID and SECRET must be set for the AMS authentication flow to work.
    # In dev and testing environments, these can be dummy values.
    AMS_CLIENT_ID = os.getenv(
        'AMS_CLIENT_ID',
        ''
    )

    AMS_CLIENT_SECRET = os.getenv(
        'AMS_CLIENT_SECRET',
        ''
    )

    # -------- CELERY CONFIG
    REDIS_URI = os.getenv(
        'REDIS_URI',
        'redis://redis-server:6379'
    )
    logger.debug("REDIS_URI: " + REDIS_URI)

    CELERY_BROKER_URL = REDIS_URI
    CELERY_RESULT_BACKEND = REDIS_URI
    CELERY_ACCEPT_CONTENT = ['application/json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_TIMEZONE = 'UTC'
    CELERYD_SEND_EVENTS=True

    CELERY_BEAT_SCHEDULE = {
        'Database Backup': {
            'task': 'tdpservice.scheduling.tasks.postgres_backup',
            'schedule': crontab(minute='0', hour='4'), # Runs at midnight EST
            'args': "-b",
        },
        'Account Deactivation Warning': {
            'task': 'tdpservice.email.tasks.check_for_accounts_needing_deactivation_warning',
            'schedule': crontab(day_of_week='*', hour='13', minute='0'), # Every day at 1pm UTC (9am EST)

            'options': {
                'expires': 15.0,
            },
        },
        'Deactivate Users': {
            'task': 'tdpservice.email.tasks.deactivate_users',
            'schedule': crontab(day_of_week='*', hour='13', minute='0'), # Every day at 1pm UTC (9am EST)
            'options': {
                'expires': 15.0,
            },
        },
        'Email Admin Number of Access Requests' : {
            'task': 'tdpservice.email.tasks.email_admin_num_access_requests',
            'schedule': crontab(minute='0', hour='1', day_of_week='*', day_of_month='*', month_of_year='*'), # Every day at 1am UTC (9pm EST)
        },
        'Email Admin Number of Stuck Files' : {
            'task': 'tdpservice.data_files.tasks.notify_stuck_files',
            'schedule': crontab(minute='0', hour='1', day_of_week='*', day_of_month='*', month_of_year='*'), # Every day at 1am UTC (9pm EST)
        },
        'Email Data Analyst Q1 Upcoming Submission Deadline Reminder': {
            'task': 'tdpservice.email.tasks.send_data_submission_reminder',
            # Feb 9 at 1pm UTC (9am EST)
            'schedule': crontab(month_of_year='2', day_of_month='9', hour='13', minute='0'),
            'kwargs': {
                'due_date': 'February 14th',
                'reporting_period': 'Oct - Dec',
                'fiscal_quarter': 'Q1',
            }
        },
        'Email Data Analyst Q2 Upcoming Submission Deadline Reminder': {
            'task': 'tdpservice.email.tasks.send_data_submission_reminder',
            # May 10 at 1pm UTC (9am EST)
            'schedule': crontab(month_of_year='5', day_of_month='10', hour='13', minute='0'),
            'kwargs': {
                'due_date': 'May 15th',
                'reporting_period': 'Jan - Mar',
                'fiscal_quarter': 'Q2',
            }
        },
        'Email Data Analyst Q3 Upcoming Submission Deadline Reminder': {
            'task': 'tdpservice.email.tasks.send_data_submission_reminder',
            # Aug 9 at 1pm UTC (9am EST)
            'schedule': crontab(month_of_year='8', day_of_month='9', hour='13', minute='0'),
            'kwargs': {
                'due_date': 'August 14th',
                'reporting_period': 'Apr - Jun',
                'fiscal_quarter': 'Q3',
            }
        },
        'Email Data Analyst Q4 Upcoming Submission Deadline Reminder': {
            'task': 'tdpservice.email.tasks.send_data_submission_reminder',
            # Nov 9 at 1pm UTC (9am EST)
            'schedule': crontab(month_of_year='11', day_of_month='9', hour='13', minute='0'),
            'kwargs': {
                'due_date': 'November 14th',
                'reporting_period': 'Jul - Sep',
                'fiscal_quarter': 'Q4',
            }
        },
    }

    CYPRESS_TOKEN = os.getenv('CYPRESS_TOKEN', None)
    FIXTURE_DIRS = [os.path.join(BASE_DIR, "fixtures")]

    GENERATE_TRAILER_ERRORS = os.getenv("GENERATE_TRAILER_ERRORS", False)
    IGNORE_DUPLICATE_ERROR_PRECEDENCE = os.getenv("IGNORE_DUPLICATE_ERROR_PRECEDENCE", False)
    BULK_CREATE_BATCH_SIZE = os.getenv("BULK_CREATE_BATCH_SIZE", 10000)
    MEDIAN_LINE_PARSE_TIME = os.getenv("MEDIAN_LINE_PARSE_TIME", 0.0005574226379394531)
    BYPASS_OFA_AUTH = os.getenv("BYPASS_OFA_AUTH", False)

    CELERY_WORKER_SEND_TASK_EVENTS = True
    CELERY_TASK_SEND_SENT_EVENT = True

    FRA_PILOT_STATES = json.loads(os.getenv("FRA_PILOT_STATES", "[]"))
