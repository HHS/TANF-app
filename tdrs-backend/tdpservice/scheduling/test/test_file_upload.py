"""Integration test(s) for clamav-rest operations."""
from os import remove
from requests.sessions import Session
import pytest

from django.contrib.admin import site as admin_site
from django.core.files.base import File
from rest_framework.status import HTTP_400_BAD_REQUEST
from tdpservice.scheduling.tasks import upload

"""
WRITE TEST:

1. CREATE FILE -> clean_file fixture -> DONE
2. UPLOAD TO ACF_TITAN -> 
3. SSH TO ACF TITAN AND MAKE SURE THE FILE EXISTS
"""


from tdpservice.data_files.test.factories import DataFileFactory


@pytest.fixture()
def upload_file():
    return DataFileFactory()


@pytest.mark.django_db
def test_upload_server(upload_file):
    assert upload_file.original_filename == 'data_file.txt'
