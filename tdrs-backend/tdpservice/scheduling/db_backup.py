#!/usr/bin/python

"""Back up the database to S3 bucket."""
# Need to run "export LD_LIBRARY_PATH=~/deps/1/python/lib/" before running python from ~/deps/1/python
# which has boto3 available

import getopt
import json
import os
import subprocess
import sys
from celery import shared_task
from django.conf import settings
import boto3
import logging


logger = logging.getLogger(__name__)


OS_ENV = os.environ

def get_system_values():
    sys_values = {}

    if settings.REDIS_SERVER_LOCAL is True:

            #TODO: ensure pg_client is available in docker images

            sys_values['POSTGRES_CLIENT'] = "/usr/bin/"

            sys_values['S3_ACCESS_KEY_ID'] = settings.AWS_S3_DATAFILES_ACCESS_KEY 
            sys_values['S3_SECRET_ACCESS_KEY'] = settings.AWS_S3_DATAFILES_SECRET_KEY 
            sys_values['S3_BUCKET'] = settings.AWS_S3_DATAFILES_BUCKET_NAME 
            sys_values['S3_REGION'] = settings.AWS_S3_DATAFILES_REGION_NAME 


            # Set Database connection info
            host = settings.DATABASES['default']["HOST"]
            port = settings.DATABASES['default']["PORT"]
            user = settings.DATABASES['default']["USER"]
            pw = settings.DATABASES['default']["PASSWORD"]
            db_name = settings.DATABASES['default']["NAME"]

            sys_values['DATABASE_PORT'] = port
            sys_values['DATABASE_PASSWORD'] = pw
            sys_values['DATABASE_DB_NAME'] = db_name
            sys_values['DATABASE_HOST'] =  host
            sys_values['DATABASE_USERNAME'] = user
            sys_values['DATABASE_URI'] = "postgresql://"+user+":"+pw+"@"+host+":"+str(port)+"/"+db_name
        
            # write .pgpass
            with open('/root/.pgpass', 'w') as f:
                f.write(sys_values['DATABASE_HOST'] + ":"\
                        + sys_values['DATABASE_PORT'] + ":"\
                        + sys_values['DATABASE_DB_NAME'] + ":"\
                        + sys_values['DATABASE_USERNAME'] + ":"\
                        + sys_values['DATABASE_PASSWORD'])
            os.environ['PGPASSFILE'] = '/root/.pgpass'
            os.system('chmod 0600 /root/.pgpass')
            return sys_values
    else:
        try:
            sys_values['SPACE'] = json.loads(OS_ENV['VCAP_APPLICATION'])['space_name']

            # Postgres client pg_dump directory
            pgdump_search = subprocess.Popen(["find", "/", "-iname", "pg_dump"],
                                             stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
            pgdump_search.wait()
            pg_dump_paths, pgdump_search_error = pgdump_search.communicate()
            pg_dump_paths = pg_dump_paths.decode("utf-8").split('\n')
            if pg_dump_paths[0] == '':
                raise Exception("Postgres client is not found")

            POSTGRES_CLIENT = None
            for _ in pg_dump_paths:
                if 'pg_dump' in str(_) and 'postgresql' in str(_):
                    sys_values['POSTGRES_CLIENT'] = _[:_.find('pg_dump')]
                    print("Found PG client here: {}".format(_))

            sys_values['S3_ENV_VARS'] = json.loads(OS_ENV['VCAP_SERVICES'])['s3']
            sys_values['S3_CREDENTIALS'] = S3_ENV_VARS[0]['credentials']
            sys_values['S3_ACCESS_KEY_ID'] = S3_CREDENTIALS['access_key_id']
            sys_values['S3_SECRET_ACCESS_KEY'] = S3_CREDENTIALS['secret_access_key']
            sys_values['S3_BUCKET'] = S3_CREDENTIALS['bucket']
            sys_values['S3_REGION'] = S3_CREDENTIALS['region']
            sys_values['DATABASE_URI'] = OS_ENV['DATABASE_URL']

            # Set AWS credentials in env, Boto3 uses the env variables for connection
            os.environ["AWS_ACCESS_KEY_ID"] = S3_ACCESS_KEY_ID
            os.environ["AWS_SECRET_ACCESS_KEY"] = S3_SECRET_ACCESS_KEY

            # Set Database connection info
            AWS_RDS_SERVICE_JSON = json.loads(OS_ENV['VCAP_SERVICES'])['aws-rds'][0]['credentials']
            sys_values['DATABASE_PORT'] = AWS_RDS_SERVICE_JSON['port']
            sys_values['DATABASE_PASSWORD'] = AWS_RDS_SERVICE_JSON['password']
            sys_values['DATABASE_DB_NAME'] = AWS_RDS_SERVICE_JSON['db_name']
            sys_values['DATABASE_HOST'] = AWS_RDS_SERVICE_JSON['host']
            sys_values['DATABASE_USERNAME'] = AWS_RDS_SERVICE_JSON['username']

            # write .pgpass
            with open('/home/vcap/.pgpass', 'w') as f:
                f.write(sys_values['DATABASE_HOST'] + ":"\
                        + sys_values['DATABASE_PORT'] + ":"\
                        + sys_values['DATABASE_DB_NAME'] + ":"\
                        + sys_values['DATABASE_USERNAME'] + ":"\
                        + sys_values['DATABASE_PASSWORD'])
            os.environ['PGPASSFILE'] = '/home/vcap/.pgpass'
            os.system('chmod 0600 ~/.pgpass')
            return sys_values

        except Exception as e:
            print(e)
            sys.exit(1)


def backup_database(file_name,
                    postgres_client,
                    database_uri):
    """Back up postgres database into file."""
    """
    :param file_name: back up file name
    :param postgres_client: directory address for postgres application
    :param database_uri: postgres URI
    pg_dump -F c --no-acl --no-owner -f backup.pg postgresql://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${NAME}
    """
    try:
        os.system(postgres_client + "pg_dump -Fc --no-acl -f " + file_name + " -d " + database_uri)
        print("Wrote pg dumpfile to {}".format(file_name))
        return True
    except Exception as e:
        print(e)
        return False


def restore_database(file_name, postgres_client, database_uri):
    """Restore the database from filename."""
    """
    :param file_name: database backup filename
    :param postgres_client: directory address for postgres application
    """

    [DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT,
     DATABASE_DB_NAME] = get_database_credentials(database_uri)
    os.environ['PGPASSWORD'] = DATABASE_PASSWORD
    try:
        os.system(postgres_client + "createdb " + "-U " + DATABASE_USERNAME + " -h " + DATABASE_HOST + " -T template0 "
                  + DATABASE_DB_NAME)
    except Exception as e:
        print(e)
        return False

    # write .pgpass
    with open('/home/vcap/.pgpass', 'w') as f:
        f.write(DATABASE_HOST+":"+DATABASE_PORT+":"+DATABASE_DB_NAME+":"+DATABASE_USERNAME+":"+DATABASE_PASSWORD)
    os.environ['PGPASSFILE'] = '/home/vcap/.pgpass'
    os.system('chmod 0600 ~/.pgpass')

    os.system(postgres_client + "pg_restore" + " -p " + DATABASE_PORT + " -h " +
              DATABASE_HOST + " -U " + DATABASE_USERNAME + " -d " + DATABASE_DB_NAME + " " + file_name)
    return True


def upload_file(file_name, bucket, sys_values, object_name=None, region='us-gov-west-1'):
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
    s3_client = boto3.client('s3', region_name=region, aws_secret_access_key=sys_values['S3_SECRET_ACCESS_KEY'], aws_access_key_id=sys_values['S3_ACCESS_KEY_ID'])
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print("Uploaded {} to S3:{}{}".format(file_name, bucket, object_name))
        return True
    except Exception as e:
        print(e)
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
    print("Downloaded s3 file {}{} to {}.".format(bucket, object_name, file_name))


def list_s3_files(bucket,
                  region):
    """List the files in s3 bucket."""
    """
    :param bucket:
    :param region:
    """
    session = boto3.Session(aws_access_key_id=S3_ACCESS_KEY_ID,
                            aws_secret_access_key=S3_SECRET_ACCESS_KEY,
                            region_name=region)
    s3 = session.resource('s3')
    my_bucket = s3.Bucket(bucket)
    return list(_ for _ in my_bucket.objects.all())


def get_database_credentials(database_uri):
    """Export database credentials from database URI."""
    """
    :param database_uri: Database URI as postgresql://$<USERNAME>:$<PASSWORD>@$<HOST>:$<PORT>/$<NAME>
    """
    database_uri = database_uri[database_uri.find('//')+2:]
    username = database_uri[:database_uri.find(':')]
    database_uri = database_uri[database_uri.find(':')+1:]
    password = database_uri[:database_uri.find('@')]
    database_uri = database_uri[database_uri.find('@') + 1:]
    host = database_uri[:database_uri.find(':')]
    database_uri = database_uri[database_uri.find(':') + 1:]
    port = database_uri[:database_uri.find('/')]
    database_uri = database_uri[database_uri.find('/') + 1:]
    database_name = database_uri
    return [username, password, host, port, database_name]


def main(argv, sys_values):
    """Handle commandline args."""
    arg_file = "/tmp/backup.pg"
    arg_database = sys_values['DATABASE_URI']
    arg_to_restore = False
    arg_to_backup = False

    try:
        opts, args = getopt.getopt(argv, "hbrf:d:", ["help", "backup", "restore", "file=", "database=", ])
        for opt, arg in opts:
            if "backup" in opt or "-b" in opt:
                arg_to_backup = True
            elif "restore" in opt or "-r" in opt:
                arg_to_restore = True
            if "file" in opt or "-f" in opt and arg:
                arg_file = arg if arg[0] == "/" else "/tmp/" + arg
            if "database" in opt or "-d" in opt:
                arg_database = arg

    except Exception as e:
        raise e

    if arg_to_backup:
        # back up database
        backup_database(file_name=arg_file,
                        postgres_client=sys_values['POSTGRES_CLIENT'],
                        database_uri=arg_database)

        # upload backup file
        upload_file(file_name=arg_file,
                    bucket=sys_values['S3_BUCKET'],
                    sys_values=sys_values,
                    region=sys_values['S3_REGION'],
                    object_name="/backup"+arg_file)
        os.system('rm ' + arg_file)
        sys.exit(0)

    elif arg_to_restore:
        # download file from s3
        download_file(bucket=sys_values['S3_BUCKET'],
                      file_name=arg_file,
                      region=sys_values['S3_REGION'],
                      object_name="backup"+arg_file)

        # restore database
        restore_database(file_name=arg_file,
                         postgres_client=sys_values['POSTGRES_CLIENT'],
                         database_uri=arg_database)

        os.system('rm ' + arg_file)
        sys.exit(0)  # successful


#@shared_task
def run_backup(arg): #name=celery
    """    No params, setup for actual backup call. """
    main([arg], sys_values=get_system_values()) 

if __name__ == '__main__':
    main(sys.argv[1:])
