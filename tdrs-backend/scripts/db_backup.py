#!/usr/bin/python

"""Back up the database to S3 bucket."""
# Need to run "export LD_LIBRARY_PATH=~/deps/1/python/lib/" before running python from ~/deps/1/python
# which has boto3 available

import subprocess
import os
import boto3
import logging
import json
import sys
import getopt

OS_ENV = os.environ
SPACE = json.loads(OS_ENV['VCAP_APPLICATION'])['space_name']

# Postgres client pg_dump directory
f = subprocess.Popen(["find", "/", "-iname", "pg_dump"], stdout=subprocess.PIPE)
f.wait()
output, error = f.communicate()
output = output.decode("utf-8").split('\n')
if output[0] == '':
    raise Exception("Postgres client is not found")

POSTGRES_CLIENT = None
for _ in output:
    if 'pg_dump' in str(_) and 'postgresql' in str(_):
        POSTGRES_CLIENT = _[:_.find('pg_dump')]


S3_ENV_VARS = json.loads(OS_ENV['VCAP_SERVICES'])['s3']
S3_CREDENTIALS = S3_ENV_VARS[0]['credentials']
S3_ACCESS_KEY_ID = S3_CREDENTIALS['access_key_id']
S3_SECRET_ACCESS_KEY = S3_CREDENTIALS['secret_access_key']
S3_BUCKET = S3_CREDENTIALS['bucket']
S3_REGION = S3_CREDENTIALS['region']
DATABASE_URI = OS_ENV['DATABASE_URL']

# Set AWS credentials in env, Boto3 uses the env variables for connection
os.environ["AWS_ACCESS_KEY_ID"] = S3_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = S3_SECRET_ACCESS_KEY


def backup_database(file_name,
                    postgres_client,
                    database_uri
                    ):
    """Back up postgres database into file."""
    """
    :param file_name: back up file name
    :param postgres_client: directory address for postgres application
    :param database_uri: postgres URI
    pg_dump -F c --no-acl --no-owner -f backup.pg postgresql://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${NAME}
    """
    try:
        os.system(postgres_client + "pg_dump -F c --no-acl -f " + file_name + " " + database_uri)
        return True
    except Exception as e:
        logging.log(e)
        return False


def restore_database(file_name, postgres_client, database_uri):
    """Restore the database from filename."""
    """
    :param file_name: database backup filename
    :param postgres_client: directory address for postgres application
    :param database_uri: database URI
    """
    try:
        os.system(postgres_client + "pg_restore --clean --no-owner --no-password --no-privileges "
                                    "--no-acl -F c -d" + database_uri + " " + file_name)
        return True
    except Exception as e:
        logging.log(e)
        return False


def upload_file(file_name, bucket, object_name=None, region='us-gov-west-1'):
    """Upload a file to an S3 bucket."""
    """
    :param file_name: file name being uploaded to s3 bucket
    :param bucket: bucket name
    :param object_name: S3 object name. If not specified then file_name is used
    :param region: s3 AWS region to be used. defaults to government west
    :return: True is file is uploaded, False if not successful
    """
    if object_name is None:
        object_name = os.path.basename(file_name)
    # upload the file
    s3_client = boto3.client('s3', region_name=region)
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        return True
    except Exception as e:
        logging.error(e)
        return False


def download_file(bucket,
                  file_name,
                  region,
                  object_name=None,
                  ):
    """Download file from s3 bucket."""
    """
    :param bucket
    :param file_name
    :param region
    :param object_name
    """
    if object_name is None:
        object_name = os.path.basename(file_name)
    s3 = boto3.client('s3', region_name=region)
    s3.download_file(bucket, object_name, file_name)


def list_s3_files(bucket,
                  region):
    """List the files in s3 bucket.

    :param bucket:
    :param region:
    """
    session = boto3.Session(aws_access_key_id=S3_ACCESS_KEY_ID,
                            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
                            region_name=region)
    s3 = session.resource('s3')
    my_bucket = s3.Bucket(bucket)
    return my_bucket.objects.all()


def handle_args(argv):
    """Handle commandline args."""
    arg_file = "../../scripts/backup.pg"
    arg_database = DATABASE_URI
    arg_to_restore = False
    arg_to_backup = False
    arg_help = "-f <filename> \t\t: the file name used for backup file \n" \
               "-h \t\t\t: help \n" \
               "-b \t\t\t: backup \n" \
               "-r \t\t\t: restore \n" \
               "-d <database URI> \t: " \
               "Database URI as postgresql://$<USERNAME>:$<PASSWORD>@$<HOST>:$<PORT>/$<NAME>"

    try:
        opts, args = getopt.getopt(argv, "hbrf:d", ["help", "file", "backup", "restore", "database"])
        for opt, arg in opts:
            if "backup" in opt or "-b" in opt:
                arg_to_backup = True
            elif "restore" in opt or "-r" in opt:
                arg_to_restore = True
            elif "file" in opt or "-f" in opt:
                arg_file = arg
            elif "database" in opt or "-d" in opt:
                arg_database = arg
    except Exception as e:
        print(e)
        print(arg_help)
        sys.exit(2)

    if arg_to_backup:
        # back up database
        backup_database(file_name=arg_file,
                        postgres_client=POSTGRES_CLIENT,
                        database_uri=arg_database)

        # upload backup file
        upload_file(file_name=arg_file,
                    bucket=S3_BUCKET,
                    region=S3_REGION)

    elif arg_to_restore:
        # download file from s3
        download_file(bucket=S3_BUCKET,
                      file_name=arg_file,
                      region=S3_REGION,
                      object_name="/backup/"+arg_file)

        # restore database
        restore_database(file_name=arg_file,
                         postgres_client=POSTGRES_CLIENT,
                         database_uri=arg_database)
        sys.exit(0)  # successful


def main(argv):
    """Perform main task."""
    handle_args(argv=argv)


if __name__ == '__main__':
    main(sys.argv[1:])
