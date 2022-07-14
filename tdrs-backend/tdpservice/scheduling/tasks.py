from __future__ import absolute_import
from celery import shared_task
from django.conf import settings

import paramiko


SERVER_ADDRESS = settings.SERVER_ADDRESS
LOCAL_KEY = settings.LOCAL_KEY
USERNAME = settings.USERNAME


@shared_task
def upload(server_address: SERVER_ADDRESS,
           local_key: LOCAL_KEY,
           username: USERNAME,
           source,                      # includes the file name
           destination                  # includes the file name
           ):
    transport = paramiko.SSHClient()
    transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    transport.connect(server_address, key_filename=local_key, username=username)

    # Upload file
    try:
        # sftp = transport.open_sftp()
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(source, destination)
        return True
    except Exception as e:
        print(e)
        return False


