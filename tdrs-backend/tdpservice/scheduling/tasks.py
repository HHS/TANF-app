from __future__ import absolute_import

import os

from celery import shared_task
from django.conf import settings
import datetime
import paramiko

from tdpservice.data_files.models import DataFile

SERVER_ADDRESS = settings.SERVER_ADDRESS
LOCAL_KEY = settings.LOCAL_KEY
USERNAME = settings.USERNAME

import logging
logger = logging.getLogger(__name__)

@shared_task
def upload(
           source,                      # the file name
           destination,                 # the file name
           quarter,                     # Quarter as number in (1,2,3,4)
           data_file_pk,
           ):
    print('-------------------------in upload 1')
    today_date = datetime.datetime.today()
    upper_directory_name = today_date.strftime('%Y%m%d')
    lower_directory_name = today_date.strftime('%Y-' + str(quarter))
    server_address = SERVER_ADDRESS
    local_key = LOCAL_KEY
    username = USERNAME
    logger.debug('in upload 2')
    transport = paramiko.SSHClient()
    logger.debug('in upload 3')
    transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    logger.debug('in upload 4')
    transport.connect(server_address, key_filename=local_key, username=username)

    sftp = transport.open_sftp()

    data_file = DataFile.objects.get(id=data_file_pk)
    print('________________________________________________')
    f = data_file.file.read()
    with open('temp_file', 'wb') as f1:
        f1.write(f)
        f1.close()
    print('______________________GG________________________')
    # Check if UPPER directory exists, then change to that directory
    try:
        sftp.chdir(upper_directory_name)
    except IOError as e:
        sftp.mkdir(upper_directory_name)
        sftp.chdir(upper_directory_name)

    # Check if LOWER directory exists
    try:
        sftp.chdir(lower_directory_name)
    except IOError as e:
        sftp.mkdir(lower_directory_name)
        sftp.chdir(lower_directory_name)

    logger.debug('++++++++++++++++ in run upload')

    # Upload file
    try:
        # sftp = transport.open_sftp()
        sftp.put('temp_file', destination)
        os.remove('temp_file')
        return True
    except Exception as e:
        print(e)
        return False


import logging
logger = logging.getLogger(__name__)


@shared_task
def run_backup(b):
    """    No params, setup for actual backup call. """
    logger.debug("my arg was" + b)
    print('00000000000000000000000000000000000000000')
    return 0
