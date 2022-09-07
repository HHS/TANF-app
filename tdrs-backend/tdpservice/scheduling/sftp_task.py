"""schedule tasks."""
from __future__ import absolute_import
# The tasks

import hashlib
import os

from celery import shared_task
from django.conf import settings
import datetime
import paramiko
import logging
from tdpservice.data_files.models import DataFile, LegacyFileTransfer

logger = logging.getLogger(__name__)


@shared_task
def upload(data_file_pk,
           server_address=settings.ACFTITAN_SERVER_ADDRESS,
           local_key=settings.ACFTITAN_LOCAL_KEY,
           username=settings.ACFTITAN_USERNAME,
           port=22
           ):
    """
    Upload to SFTP server.

    This task uploads the file in DataFile object with pk = data_file_pk
    to sftp server as defined in Settings file
    """
    # Upload file
    data_file = DataFile.objects.get(id=data_file_pk)
    file_transfer_record = LegacyFileTransfer(
        data_file=data_file,
        uploaded_by=data_file.user,
        file_name=data_file.filename,
    )

    def write_key_to_file(private_key):
        """Paramiko require the key in file object format."""
        with open('temp_key_file', 'w') as f:
            f.write(private_key)
            f.close()
        return 'temp_key_file'

    def create_dir(directory_name, sftp_server):
        """Code snippet to create directory in SFTP server."""
        try:
            sftp_server.chdir(directory_name)  # Test if remote_path exists
        except IOError:
            sftp_server.mkdir(directory_name)  # Create remote_path
            sftp_server.chdir(directory_name)

    try:
        # Create directory names for ACF titan
        destination = str(data_file.filename)
        today_date = datetime.datetime.today()
        upper_directory_name = today_date.strftime('%Y%m%d')
        lower_directory_name = today_date.strftime(str(data_file.year) + '-' + str(data_file.quarter))

        # Paramiko need local file
        paramiko_local_file = data_file.file.read()
        with open(destination, 'wb') as f1:
            f1.write(paramiko_local_file)
            file_transfer_record.file_size = f1.tell()
            file_transfer_record.file_shasum = hashlib.sha256(paramiko_local_file).hexdigest()
            f1.close()

        # Paramiko SSH connection requires private key as file
        temp_key_file = write_key_to_file(local_key)
        os.chmod(temp_key_file, 0o600)

        # Create SFTP/SSH connection
        transport = paramiko.SSHClient()
        transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        pkey = paramiko.RSAKey.from_private_key_file(temp_key_file)
        transport.connect(server_address,
                          pkey=pkey,
                          username=username,
                          port=port,
                          look_for_keys=False,
                          disabled_algorithms={'pubkeys': ['rsa-sha2-512', 'rsa-sha2-256']})
        # remove temp key file
        os.remove(temp_key_file)
        sftp = transport.open_sftp()

        # Create remote directory
        create_dir(settings.ACFTITAN_DIRECTORY, sftp_server=sftp)
        create_dir(upper_directory_name, sftp_server=sftp)
        create_dir(lower_directory_name, sftp_server=sftp)

        # Put the file in SFTP server
        sftp.put(destination, destination)

        # Delete temp file
        os.remove(destination)
        logger.info('File {} has been successfully uploaded to {}'.format(destination, server_address))

        # Add the log LegacyFileTransfer
        file_transfer_record.result = LegacyFileTransfer.Result.COMPLETED
        file_transfer_record.save()
        transport.close()
        return True

    except Exception as e:
        logger.error('Failed to upload {} with error:{}'.format(destination, e))
        file_transfer_record.file_size = 0
        file_transfer_record.result = LegacyFileTransfer.Result.ERROR
        file_transfer_record.save()
        transport.close()
        return False
