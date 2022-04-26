"""Back up the database to S3 bucket."""
# Need to run "export LD_LIBRARY_PATH=~/deps/1/python/lib/" before running python from ~/deps/1/python
# which has boto3 available

import subprocess
import os
import boto3
import logging
import json

ORGANIZATION = "hhs-acf-prototyping"
SPACE = os.environ['VCAP_APPLICATION']['space_name']
APP_NAME = os.environ['VCAP_APPLICATION']['application_name']
SERVICE_INSTANCE_NAME = "tdp-db-dev"

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

OS_ENV = os.environ
S3_ENV_VARS = json.loads(OS_ENV['VCAP_SERVICES'])['s3']
S3_CREDENTIALS = json.loads(OS_ENV['VCAP_SERVICES'])['s3'][0]['credentials']
S3_ACCESS_KEY_ID = S3_CREDENTIALS['access_key_id']
S3_SECRET_ACCESS_KEY = S3_CREDENTIALS['secret_access_key']
S3_BUCKET = S3_CREDENTIALS['bucket']
S3_REGION = S3_CREDENTIALS['region']
DATABASE_URI = OS_ENV['DATABASE_URL']

# Set AWS credentials in env, Boto3 uses the env variables for connection
os.environ["AWS_ACCESS_KEY_ID"] = S3_ACCESS_KEY_ID
os.environ["AWS_SECRET_ACCESS_KEY"] = S3_SECRET_ACCESS_KEY


def backup_database(postgres_client,
                    database_uri
                    ):
    """Back up postgres database into file.
    :param postgres_client:
    :param database_uri:
    pg_dump -F c --no-acl --no-owner -f backup.pg postgresql://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${NAME}
    """
    try:
        os.system(postgres_client + "pg_dump -F c --no-acl -f backup.pg " + database_uri)
        return True
    except Exception as e:
        logging.log(e)
        return False


is_database_backed_up = backup_database(POSTGRES_CLIENT, DATABASE_URI)


def restore_database(postgres_client, database_uri):
    """Restores the database from filename
    :param postgres_client
    :param database_uri
    pg_restore -F c -d postgresql://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${NAME} -f backup.pg
    """
    try:
        os.system(postgres_client + "pg_restore -F c -d" + database_uri + " -f backup.pg ")
        return True
    except Exception as e:
        logging.log(e)
        return False


def upload_file(file_name,
                bucket,
                object_name=None,
                region='us-gov-west-1'):
    """Upload a file to an S3 bucket.
    :param file_name:
    :param bucket:
    :param object_name:
    :param region:
    :return:
    """

    if object_name is None:
        object_name = os.path.basename(file_name)

    # upload the file
    s3_client = boto3.client('s3', region_name=region)

    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except Exception as e:
        logging.error(e)
        return False
    return True


# upload backup file
upload_file('backup.pg', S3_BUCKET, region=S3_REGION)


def download_file(bucket,
                  file_name,
                  region,
                  object_name=None,
                  ):
    """Downloads file from s3 bucket
    :param bucket
    :param file_name
    :param region
    :param object_name
    """
    if object_name is None:
        object_name = os.path.basename(file_name)
    s3 = boto3.client('s3', region_name=region)
    s3.download_file(bucket, object_name, file_name)


download_file(bucket=S3_BUCKET, file_name='backup.pg', region=S3_REGION)
"""
session = boto3.Session(aws_access_key_id=S3_ACCESS_KEY_ID, aws_secret_access_key=S3_SECRET_ACCESS_KEY,region_name='us-gov-west-1')
s3 =session.resource('s3')
my_bucket = s3.Bucket(S3_BUCKET)
for obj in my_bucket.objects.all():
    print(obj)
"""

