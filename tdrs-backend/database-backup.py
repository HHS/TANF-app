"""Back up the database to S3 bucket"""
import subprocess
import os
import boto3

ORGANIZATION = "hhs-acf-prototyping"
SPACE = "tanf-dev"
APP_NAME = "tdp-backend-raft"
SERVICE_INSTANCE_NAME = "tdp-db-dev"


f = subprocess.Popen(["find", "/", "-iname", "pg_dump"], stdout=subprocess.PIPE)
f.wait()
output, error = f.communicate()
output = output.split('\n')
if output[0] == '':
    raise Exception("Postgres client is not found")

postgres_client_add = None
for _ in output:
    if 'pg_dump' in _ and 'postgresql' in _:
        postgres_client_add = _

"""
From local: first have to login to be able to ssh, then run this script. But this script will be running from the
server. The pg_dump has to be available as part of build packs
"""

f = subprocess.Popen(["printenv"], stdout=subprocess.PIPE)
f.wait()
output, error = f.communicate()
output = output.split('\n')
if "FAILED" in output:
    raise Exception('Failed to receive response')
else:
    pass

for _ in output:
    if 'uri' in _ and 's3' in _:
        S3_URI = _[_.find('s3:'):_.rfind('"')]
    if 'uri' in _ and 'postgres:' in _:
        DATABASE_URI = _[_.find('postgres'):_.rfind('"')]
    # get database connection uri
    # output_json = json.loads(output[output.find('{'):output.rfind('VCAP_APPLICATION')])
    # database_uri = output_json['aws-rds'][0]['credentials']['uri']

    # get S3 connection
    # s3_connection = output_json['s3']


'''
pg_dump -F c \
    --no-acl \
    --no-owner \
    -f backup.pg \
    postgresql://${USERNAME}:${PASSWORD}@${HOST}:${PORT}/${NAME}
'''

os.system(postgres_client_add + "-F c --no-acl -f backup.pg" + DATABASE_URI)

# s3 upload
s3_ = boto3.s3
