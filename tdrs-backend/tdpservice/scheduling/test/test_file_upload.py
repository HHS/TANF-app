"""Scheduling tests."""

from datetime import datetime

import pytest
from paramiko import Transport
from paramiko.sftp_client import SFTPClient
from tdpservice.scheduling.sftp_task import upload
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.stts.models import STT
from django.conf import settings

"""
To mock sftp server, pytest_sftpserver (https://github.com/ulope/pytest-sftpserver) is used.
The package provides two main fixtures for testing: sftpserver and sftpclient.
"""

@pytest.fixture
def stt_instance(region):
    """Return an STT."""
    stt, _ = STT.objects.get_or_create(
        name="first",
        region=region,
        code="AR",
        stt_code=1234,
        filenames={
            'Aggregate Data': 'ADS.E2J.NDM3.TS22',
            'Active Case Data': 'test',
            'Closed Case Data': 'ADS.E2J.NDM2.TS22'}
    )
    return stt

@pytest.fixture
def data_file_instance(stt_instance):
    """Prepare data file fixture instance for testing datafile."""
    return DataFileFactory.create(
        created_at=datetime.now(),
        stt=stt_instance
    )


@pytest.fixture
def sftp_connection_values(sftpserver):
    """SFTP connection values for local sftp server."""
    server_address = sftpserver.host
    local_key = settings.ACFTITAN_SFTP_PYTEST
    username = "user"
    port = sftpserver.port
    return {
        'server_address': server_address,
        'username': username,
        'local_key': local_key,
        'port': port
    }


@pytest.fixture(scope="session")
def sftpclient(sftpserver):
    """SFTP client for local sftp server."""
    transport = Transport((sftpserver.host, sftpserver.port))
    transport.connect(username="a", password="b")
    sftpclient = SFTPClient.from_transport(transport)
    yield sftpclient
    sftpclient.close()
    transport.close()


@pytest.mark.django_db
def test_new_data_file(sftpserver, data_file_instance, sftp_connection_values, sftpclient):
    """Datafile object for testing the file."""
    data_file_instance.save()

    """
    Need .serve_content to keep the communication alive
    Here we put a dummy file somefile.txt in a_dir to keep the port open
    """
    with sftpserver.serve_content({'a_dir': {'somefile.txt': "File content"}}):
        upload(data_file_instance.pk,
               server_address=sftp_connection_values['server_address'],
               local_key=sftp_connection_values['local_key'],
               username=sftp_connection_values['username'],
               port=sftp_connection_values['port'])

        # Create directory structure as needed for ACF_TITAN to assert correct directory name
        today_date = datetime.today()
        upper_directory_name = today_date.strftime('%Y%m%d')
        lower_directory_name = today_date.strftime(str(data_file_instance.year) +
                                                   '-' +
                                                   str(data_file_instance.quarter))
        assert sftpclient.listdir(upper_directory_name+'/'+lower_directory_name)[0] == \
               data_file_instance.filename
