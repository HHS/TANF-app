from __future__ import absolute_import
from celery import shared_task
from django.conf import settings

import paramiko

SERVER_ADDRESS = settings.SERVER_ADDRESS
LOCAL_KEY = settings.LOCAL_KEY
USERNAME = settings.USERNAME

'''

from django.utils import timezone
last_24 = timezone.now()-timezone.timedelta(hours=24)
DataFile.objects.filter(created_at__gt=last_24)

# what should the filename be?
with open('write.txt','wb') as f1:
     ...:     with df.file.file.open() as f2:
     ...:         f1.write(f2.read())


# ssh connect and command
_stdin, _stdout,_stderr = transport.exec_command("ls")
print(_stdout.read().decode())

1) try to create directory
if successful, then good,
if not, then either directory exists, or something else happened.
    in case of error, we can list the directories, and confirm if it exists, or we can do this first

2) Query DISTINCT values based on year, STT

'''


@shared_task
def upload(
           source,                      # includes the file name
           destination                  # includes the file name
           ):
    server_address = SERVER_ADDRESS
    local_key = LOCAL_KEY
    username = USERNAME
    transport = paramiko.SSHClient()
    transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    transport.connect(server_address, key_filename=local_key, username=username)

    # Upload file
    try:
        # sftp = transport.open_sftp()
        sftp = transport.open_sftp()
        sftp.put(source, destination)
        return True
    except Exception as e:
        print(e)
        return False

@shared_task
def run_backup(b):
    """    No params, setup for actual backup call. """
    logger.debug("my arg was" + b)
