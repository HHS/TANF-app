import subprocess
import json
ORGANIZATION = "hhs-acf-prototyping"
SPACE = "tanf-dev"
APP_NAME = "tdp-backend-raft"
SERVICE_INSTANCE_NAME = "tdp-db-dev"


"""
From local: first have to login to be able to ssh, then run this script. But this script will be running from the
server. The pg_dump has to be available as part of build packs
"""

f = subprocess.Popen(["cf", "env", "tdp-backend-raft"], stdout=subprocess.PIPE)
f.wait()
output, error = f.communicate()
output = output.decode('utf-8')
if "FAILED" in output:
    raise Exception('Failed to receive response')
else:
    # get database connection uri
    output_json = json.loads(output[output.find('{'):output.rfind('VCAP_APPLICATION')])
    database_uri = output_json['aws-rds'][0]['credentials']['uri']

    # get S3 connection
    s3_connection = output_json['s3']
