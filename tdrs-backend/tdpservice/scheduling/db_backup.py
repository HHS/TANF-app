#!/usr/bin/python

"""Back up the database to S3 bucket."""
# Need to run "export LD_LIBRARY_PATH=~/deps/1/python/lib/" before running python from ~/deps/1/python
# which has boto3 available

import getopt
import json
import os
import subprocess
import sys
from django.conf import settings
import boto3
import logging
from tdpservice.users.models import User
from django.contrib.admin.models import ADDITION, ContentType, LogEntry


logger = logging.getLogger(__name__)


OS_ENV = os.environ
content_type = ContentType.objects.get_for_model(LogEntry)

def get_system_values():
    """Return dict of keys and settings to use whether local or deployed."""
    sys_values = {}

    sys_values['SPACE'] = json.loads(OS_ENV['VCAP_APPLICATION'])['space_name']

    # Postgres client pg_dump directory
    sys_values['POSTGRES_CLIENT_DIR'] = "/home/vcap/deps/0/apt/usr/lib/postgresql/15/bin/"

    # If the client directory and binaries don't exist, we need to find them.
    if not (os.path.exists(sys_values['POSTGRES_CLIENT_DIR']) and
            os.path.isfile(f"{sys_values['POSTGRES_CLIENT_DIR']}pg_dump")):
        logger.warning("Couldn't find postgres client binaries at the hardcoded path: "
                       f"{sys_values['POSTGRES_CLIENT_DIR']}. Searching OS for client directory.")
        pgdump_search = subprocess.Popen(["find", "/", "-iname", "pg_dump"],
                                         stderr=subprocess.DEVNULL, stdout=subprocess.PIPE)
        pgdump_search.wait()
        pg_dump_paths, pgdump_search_error = pgdump_search.communicate()
        pg_dump_paths = pg_dump_paths.decode("utf-8").split('\n')
        if pg_dump_paths[0] == '':
            raise Exception("Postgres client is not found")

        for _ in pg_dump_paths:
            if 'pg_dump' in str(_) and 'postgresql' in str(_):
                sys_values['POSTGRES_CLIENT'] = _[:_.find('pg_dump')]

    logger.info(f"Using postgres client at: {sys_values['POSTGRES_CLIENT_DIR']}")

    sys_values['S3_ENV_VARS'] = json.loads(OS_ENV['VCAP_SERVICES'])['s3']
    sys_values['S3_CREDENTIALS'] = sys_values['S3_ENV_VARS'][0]['credentials']
    sys_values['S3_URI'] = sys_values['S3_CREDENTIALS']['uri']
    sys_values['S3_ACCESS_KEY_ID'] = sys_values['S3_CREDENTIALS']['access_key_id']
    sys_values['S3_SECRET_ACCESS_KEY'] = sys_values['S3_CREDENTIALS']['secret_access_key']
    sys_values['S3_BUCKET'] = sys_values['S3_CREDENTIALS']['bucket']
    sys_values['S3_REGION'] = sys_values['S3_CREDENTIALS']['region']
    sys_values['DATABASE_URI'] = OS_ENV['DATABASE_URL']
    # Set AWS credentials in env, Boto3 uses the env variables for connection
    os.environ["AWS_ACCESS_KEY_ID"] = sys_values['S3_ACCESS_KEY_ID']
    os.environ["AWS_SECRET_ACCESS_KEY"] = sys_values['S3_SECRET_ACCESS_KEY']

    # Set Database connection info
    AWS_RDS_SERVICE_JSON = json.loads(OS_ENV['VCAP_SERVICES'])['aws-rds'][0]['credentials']
    sys_values['DATABASE_PORT'] = AWS_RDS_SERVICE_JSON['port']
    sys_values['DATABASE_PASSWORD'] = AWS_RDS_SERVICE_JSON['password']
    sys_values['DATABASE_DB_NAME'] = AWS_RDS_SERVICE_JSON['db_name']
    sys_values['DATABASE_HOST'] = AWS_RDS_SERVICE_JSON['host']
    sys_values['DATABASE_USERNAME'] = AWS_RDS_SERVICE_JSON['username']

    # write .pgpass
    with open('/home/vcap/.pgpass', 'w') as f:
        f.write(sys_values['DATABASE_HOST'] + ":"
                + sys_values['DATABASE_PORT'] + ":"
                + settings.DATABASES['default']['NAME'] + ":"
                + sys_values['DATABASE_USERNAME'] + ":"
                + sys_values['DATABASE_PASSWORD'])
    os.environ['PGPASSFILE'] = '/home/vcap/.pgpass'
    os.system('chmod 0600 /home/vcap/.pgpass')
    return sys_values


def backup_database(file_name,
                    postgres_client,
                    database_uri,
                    system_user):
    """Back up postgres database into file.

    :param file_name: back up file name
    :param postgres_client: directory address for postgres application
    :param database_uri: postgres URI
    pg_dump -F c --no-acl --no-owner -f backup.pg postgresql://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${NAME}
    """
    try:
        # TODO: This is a bandaid until the correct logic is determined for the system values
        # cmd = postgres_client + "pg_dump -Fc --no-acl -f " + file_name + " -d " + database_uri
        db_host = settings.DATABASES['default']['HOST']
        db_port = settings.DATABASES['default']['PORT']
        db_name = settings.DATABASES['default']['NAME']
        db_user = settings.DATABASES['default']['USER']

        export_password = f"export PGPASSWORD={settings.DATABASES['default']['PASSWORD']}"
        cmd = (f"{export_password} && {postgres_client}pg_dump -h {db_host} -p {db_port} -d {db_name} -U {db_user} "
               f"-F c --no-password --no-acl --no-owner -f {file_name}")
        logger.info(f"Executing backup command: {cmd}")
        os.system(cmd)
        msg = "Successfully executed backup. Wrote pg dumpfile to {}".format(file_name)
        logger.info(msg)
        LogEntry.objects.log_action(
            user_id=system_user.pk,
            content_type_id=content_type.pk,
            object_id=None,
            object_repr="Executed Database Backup",
            action_flag=ADDITION,
            change_message=msg
        )
        file_size = os.path.getsize(file_name)
        logger.info(f"Pg dumpfile size in bytes: {file_size}.")
        return True
    except Exception as e:
        logger.error(f"Caught Exception while backing up database. Exception: {e}")
        raise e


def restore_database(file_name, postgres_client, database_uri, system_user):
    """Restore the database from filename.

    :param file_name: database backup filename
    :param postgres_client: directory address for postgres application
    """
    [DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT,
     DATABASE_DB_NAME] = get_database_credentials(database_uri)
    os.environ['PGPASSWORD'] = DATABASE_PASSWORD
    try:
        logger.info("Begining database creation.")
        cmd = (postgres_client + "createdb " + "-U " + DATABASE_USERNAME + " -h " + DATABASE_HOST + " -T template0 "
               + DATABASE_DB_NAME)
        logger.info(f"Executing create command: {cmd}")
        os.system(cmd)
        msg = "Completed database creation."
        LogEntry.objects.log_action(
            user_id=system_user.pk,
            content_type_id=content_type.pk,
            object_id=None,
            object_repr="Executed Database create",
            action_flag=ADDITION,
            change_message=msg
        )
        logger.info(msg)

        # write .pgpass
        with open('/home/vcap/.pgpass', 'w') as f:
            f.write(DATABASE_HOST+":"+DATABASE_PORT+":"+DATABASE_DB_NAME+":"+DATABASE_USERNAME+":"+DATABASE_PASSWORD)
        os.environ['PGPASSFILE'] = '/home/vcap/.pgpass'
        os.system('chmod 0600 /home/vcap/.pgpass')

        logger.info("Begining database restoration.")
        cmd = (postgres_client + "pg_restore" + " -p " + DATABASE_PORT + " -h " +
               DATABASE_HOST + " -U " + DATABASE_USERNAME + " -d " + DATABASE_DB_NAME + " " + file_name)
        logger.info(f"Executing restore command: {cmd}")
        os.system(cmd)
        msg = "Completed database restoration."
        LogEntry.objects.log_action(
            user_id=system_user.pk,
            content_type_id=content_type.pk,
            object_id=None,
            object_repr="Executed Database restore",
            action_flag=ADDITION,
            change_message=msg
        )
        logger.info(msg)
        return True
    except Exception as e:
        logger.error(f"Caught exception while restoring the database. Exception: {e}.")
        raise e


def upload_file(file_name, bucket, sys_values, system_user, object_name=None, region='us-gov-west-1'):
    """Upload a file to an S3 bucket.

    :param file_name: file name being uploaded to s3 bucket
    :param bucket: bucket name
    :param object_name: S3 object name. If not specified then file_name is used
    :param region: s3 AWS region to be used. defaults to government west
    :return: True is file is uploaded, False if not successful
    """
    if object_name is None:
        object_name = os.path.basename(file_name)

    logger.info(f"Uploading {file_name} to S3.")
    s3_client = boto3.client('s3', region_name=sys_values['S3_REGION'])

    s3_client.upload_file(file_name, bucket, object_name)
    msg = "Successfully uploaded {} to s3://{}/{}.".format(file_name, bucket, object_name)
    LogEntry.objects.log_action(
        user_id=system_user.pk,
        content_type_id=content_type.pk,
        object_id=None,
        object_repr="Executed database backup S3 upload",
        action_flag=ADDITION,
        change_message=msg
    )
    logger.info(msg)
    return True


def download_file(bucket,
                  file_name,
                  region,
                  system_user,
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
    logger.info("Begining download for backup file.")
    s3 = boto3.client('s3', region_name=region)
    s3.download_file(bucket, object_name, file_name)
    msg = "Successfully downloaded s3 file {}/{} to {}.".format(bucket, object_name, file_name)
    LogEntry.objects.log_action(
        user_id=system_user.pk,
        content_type_id=content_type.pk,
        object_id=None,
        object_repr="Executed database backup S3 download",
        action_flag=ADDITION,
        change_message=msg
    )
    logger.info(msg)


def list_s3_files(sys_values):
    """List the files in s3 bucket."""
    """
    :param bucket:
    :param region:
    """
    session = boto3.Session(aws_access_key_id=sys_values['S3_ACCESS_KEY_ID'],
                            aws_secret_access_key=sys_values['S3_SECRET_ACCESS_KEY'],
                            region_name=sys_values['S3_REGION'])
    s3 = session.resource('s3')
    my_bucket = s3.Bucket(sys_values['S3_BUCKET'])
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


def main(argv, sys_values, system_user):
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
        LogEntry.objects.log_action(
            user_id=system_user.pk,
            content_type_id=content_type.pk,
            object_id=None,
            object_repr="Begining Database Backup",
            action_flag=ADDITION,
            change_message="Begining database backup."
        )
        # back up database
        backup_database(file_name=arg_file,
                        postgres_client=sys_values['POSTGRES_CLIENT_DIR'],
                        database_uri=arg_database,
                        system_user=system_user)

        # upload backup file
        upload_file(file_name=arg_file,
                    bucket=sys_values['S3_BUCKET'],
                    sys_values=sys_values,
                    system_user=system_user,
                    region=sys_values['S3_REGION'],
                    object_name="backup"+arg_file,
                    )

        LogEntry.objects.log_action(
            user_id=system_user.pk,
            content_type_id=content_type.pk,
            object_id=None,
            object_repr="Finished Database Backup",
            action_flag=ADDITION,
            change_message="Finished database backup."
        )

        logger.info(f"Deleting {arg_file} from local storage.")
        os.system('rm ' + arg_file)

    elif arg_to_restore:
        LogEntry.objects.log_action(
            user_id=system_user.pk,
            content_type_id=content_type.pk,
            object_id=None,
            object_repr="Begining Database Restore",
            action_flag=ADDITION,
            change_message="Begining database restore."
        )

        # download file from s3
        download_file(bucket=sys_values['S3_BUCKET'],
                      file_name=arg_file,
                      region=sys_values['S3_REGION'],
                      system_user=system_user,
                      object_name="backup"+arg_file,
                      )

        # restore database
        restore_database(file_name=arg_file,
                         postgres_client=sys_values['POSTGRES_CLIENT_DIR'],
                         database_uri=arg_database,
                         system_user=system_user)

        LogEntry.objects.log_action(
            user_id=system_user.pk,
            content_type_id=content_type.pk,
            object_id=None,
            object_repr="Finished Database Restore",
            action_flag=ADDITION,
            change_message="Finished database restore."
        )

        logger.info(f"Deleting {arg_file} from local storage.")
        os.system('rm ' + arg_file)


def run_backup(arg):
    """No params, setup for actual backup call."""
    if settings.USE_LOCALSTACK is True:
        logger.info("Won't backup locally")
    else:
        try:
            system_user, created = User.objects.get_or_create(username='system')
            if created:
                logger.debug('Created reserved system user.')
            main([arg], sys_values=get_system_values(), system_user=system_user)
        except Exception as e:
            logger.error(f"Caught Exception in run_backup. Exception: {e}.")
            LogEntry.objects.log_action(
                user_id=system_user.pk,
                content_type_id=content_type.pk,
                object_id=None,
                object_repr="Exception in run_backup",
                action_flag=ADDITION,
                change_message=str(e)
            )
            return False
    return True


if __name__ == '__main__':
    system_user, created = User.objects.get_or_create(username='system')
    if created:
        logger.debug('Created reserved system user.')
    main(sys.argv[1:], get_system_values(), system_user)
