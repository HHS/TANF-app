
import os
from .common import Common
from os.path import join, dirname
from dotenv import load_dotenv
# load env vars from .env file and override any system environment variables
from pathlib import Path  # Python 3.6+ only
dotenv_path = join(dirname(__file__), './env_vars/.env.local')
load_dotenv(dotenv_path)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class Local(Common):
    DEBUG = True
    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS
    INSTALLED_APPS += ('django_nose',)
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = [
        BASE_DIR,
        '-s',
        '--nologcapture',
        '--with-coverage',
        '--with-progressive',
        '--cover-package=tdpservice'
    ]

    # Mail
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    
