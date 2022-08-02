"""Celery task configurations."""
from __future__ import absolute_import

import hashlib
import os

from celery import shared_task
from django.conf import settings
import datetime
import paramiko
import logging
from tdpservice.data_files.models import DataFile, LegacyFileTransfer

logger = logging.getLogger(__name__)

server_address = settings.SERVER_ADDRESS
local_key = settings.LOCAL_KEY
username = settings.USERNAME


def write_key_to_file(private_key):
    """Paramiko require the key in file object format."""
    with open('temp_key_file', 'w') as f:
        f.write(private_key)
        f.close()
    return 'temp_key_file'


@shared_task
def upload(data_file_pk):
    """
    Upload to SFTP server.

    This task uploads the file in DataFile object with pk = data_file_pk
    to sftp server as defined in Settings file
    """
    # Upload file
    try:
        data_file = DataFile.objects.get(id=data_file_pk)
        file_transfer_record = LegacyFileTransfer(
            data_file=data_file,
            uploaded_by=data_file.user,
            file_name=data_file.create_filename(),
        )
        logger.info(file_transfer_record)
        destination = str(data_file.create_filename())
        logger.info(destination)
        today_date = datetime.datetime.today()
        upper_directory_name = today_date.strftime('%Y%m%d')
        lower_directory_name = today_date.strftime(str(data_file.year) + '-' + str(data_file.quarter))

        transport = paramiko.SSHClient()
        transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        transport.connect(server_address, key_filename=write_key_to_file(local_key), username=username)
        sftp = transport.open_sftp()

        transport.exec_command('mkdir -p ' + upper_directory_name +
                               '/' + lower_directory_name)

        f = data_file.file.read()
        with open(destination, 'wb') as f1:
            f1.write(f)
            file_transfer_record.file_size = f1.tell()
            file_transfer_record.file_shasum = hashlib.sha256(f).hexdigest()
            f1.close()
        logger.info(os.listdir())

        # temp file can be the file object
        sftp.put(destination, upper_directory_name + '/' + lower_directory_name + '/' + destination)
        os.remove(destination)
        logger.info('File {} has been successfully uploaded to {}'.format(destination, server_address))
        file_transfer_record.result = LegacyFileTransfer.Result.COMPLETED
        file_transfer_record.save()
        return True
    except Exception as e:
        logger.error('Failed to upload {} with error:{}'.format(destination, e))
        file_transfer_record.result = LegacyFileTransfer.Result.ERROR
        file_transfer_record.save()
        return False
