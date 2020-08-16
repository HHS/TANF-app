import os
import json
from os.path import join
from distutils.util import strtobool
from configurations import Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Common(Configuration):

    INSTALLED_APPS = (
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',

        # Third party apps
        'rest_framework',            # Utilities for rest apis
        'rest_framework.authtoken',  # Token authentication
        'django_filters',

        # Local apps
        'tdpservice.users',
    )

    # https://docs.djangoproject.com/en/2.0/topics/http/middleware/
    MIDDLEWARE = (
        'django.middleware.security.SecurityMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',

    )

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = 'tdpservice.urls'
    SECRET_KEY = os.environ['DJANGO_SECRET_KEY']
    WSGI_APPLICATION = 'tdpservice.wsgi.application'

    # Email Server
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    # Those who will receive error notifications from django via email
    ADMINS = (
        ('Admin1', 'ADMIN_EMAIL_FIRST'),
        ('Admin2', 'ADMIN_EMAIL_SECOND')
    )

    # Postgres
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }

    # General
    APPEND_SLASH = False
    TIME_ZONE = 'UTC'
    LANGUAGE_CODE = 'en-us'
    # If you set this to False, Django will make some optimizations so as not
    # to load the internationalization machinery.
    USE_I18N = False
    USE_L10N = True
    USE_TZ = True
    LOGIN_REDIRECT_URL = '/'

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), 'static'))
    STATICFILES_DIRS = []
    STATIC_URL = '/static/'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    )

    # Media files
    MEDIA_ROOT = join(os.path.dirname(BASE_DIR), 'media')
    MEDIA_URL = '/media/'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': STATICFILES_DIRS,
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(os.getenv('DJANGO_DEBUG', 'no'))

    # Password Validation
    # https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]

    # Logging
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'django.server': {
                '()': 'django.utils.log.ServerFormatter',
                'format': '[%(server_time)s] %(message)s',
            },
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
        },
        'filters': {
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'django.server': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'django.server',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple'
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler'
            }
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'propagate': True,
            },
            'django.server': {
                'handlers': ['django.server'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['mail_admins', 'console'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['console'],
                'level': 'INFO'
            },
        }
    }

    # Custom user app
    AUTH_USER_MODEL = 'users.User'

    # Sessions
    SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SESSION_COOKIE_PATH = '/;HttpOnly'

    # Django Rest Framework
    REST_FRAMEWORK = {
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': int(os.getenv('DJANGO_PAGINATION_LIMIT', 10)),
        'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
        'DEFAULT_RENDERER_CLASSES': (
            'rest_framework.renderers.JSONRenderer',
            'rest_framework.renderers.BrowsableAPIRenderer',
        ),
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_AUTHENTICATION_CLASSES': (
            'tdpservice.auth_backend.CustomAuthentication',
            'rest_framework.authentication.SessionAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        )
    }

    AUTHENTICATION_BACKENDS = (
        'tdpservice.auth_backend.CustomAuthentication',
        'django.contrib.auth.backends.ModelBackend',
    )

    LOGIN_REDIRECT_URL = "http://127.0.0.1:8000/api"
    LOGOUT_REDIRECT_URL = "http://127.0.0.1:8000"

    # conditionally set which URI to go to
    if 'VCAP_APPLICATION' in os.environ:
        appjson = os.environ['VCAP_APPLICATION']
        appinfo = json.loads(appjson)
        if len(appinfo['application_uris']) > 0:
            appuri = 'https://' + \
                appinfo['application_uris'][0] + '/openid/callback/login/'
        else:
            # We are not a web task, so we have no appuri
            appuri = ''
    else:
        # we are running locally
        appuri = 'http://localhost:8000/openid/callback/login/'


# configure things set up by cloudfoundry
if 'VCAP_SERVICES' in os.environ:
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    servicejson = os.environ['VCAP_SERVICES']
    services = json.loads(servicejson)
    AWS_STORAGE_BUCKET_NAME = services['s3'][0]['credentials']['bucket']
    AWS_S3_REGION_NAME = services['s3'][0]['credentials']['region']
    AWS_ACCESS_KEY_ID = services['s3'][0]['credentials']['access_key_id']
    AWS_SECRET_ACCESS_KEY = services['s3'][0]['credentials']['secret_access_key']
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': services['aws-rds'][0]['credentials']['db_name'],
            'USER': services['aws-rds'][0]['credentials']['username'],
            'PASSWORD': services['aws-rds'][0]['credentials']['password'],
            'HOST': services['aws-rds'][0]['credentials']['host'],
            'PORT': services['aws-rds'][0]['credentials']['port'],
        }
    }
    STATIC_ROOT = os.path.join(BASE_DIR, "static/")
    print('configured for cloud.gov')
else:
    # we are in local development mode
    MEDIA_ROOT = '/tmp/tanf'
    if 'BUCKETNAME' in os.environ:
        DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        AWS_STORAGE_BUCKET_NAME = os.environ['BUCKETNAME']
        AWS_S3_ENDPOINT_URL = os.environ['AWS_S3_ENDPOINT_URL']
        AWS_S3_REGION_NAME = os.environ['AWS_S3_REGION_NAME']
        AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
        AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
    if 'POSTGRES_USER' in os.environ:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ['POSTGRES_DB'],
                'USER': os.environ['POSTGRES_USER'],
                'PASSWORD': os.environ['POSTGRES_PASSWORD'],
                'HOST': os.environ['POSTGRES_HOST'],
                'PORT': os.environ['POSTGRES_PORT'],
            }
        }
    print('configured for local development')
