# Database backup

The backup process in cloudfoundry is done using the pg_dump utility from Postgres client 
version 12. According to [Cloud.Gov documentation](https://cloud.gov/docs/services/relational-database/#backups) 
the RDS service that is used by Cloud.Gov uses 14 days retention for automatic backups. These backups can be restored by 
Cloud.Gov support.

There are other approaches to access database data by performing backups using pg_dump such as using: 
```bash
cg-manage-rds export -o "-F c" -f ./backup.pg ${SERVICE_NAME}
```

This command uses "pg_dump -O" to create backup, which doesn't set the ownership on the backup 
file.
Another way to create backup is to use cf-service-connect and to run pg_dump command
(see [Cloud.Gov documentation](https://cloud.gov/docs/services/relational-database/#using-cf-service-connect-plugin)). 

However, the caveat is that we have to first connect to the database service and keep that 
connection live, while performing backup using cloudfoundry connection. This causes issues 
while we need to create shell scripts.

The db_backup.py is written as a python script to perform backup and restore commands.

+ Backup database 
+ Restore the backup 
+ Save local file to S3 instance 
+ Download remote s3 file 
+ List S3 files (To be added)

### Preparation
SSH to the instance:
```bash
cf ssh <instance name>
```
instance name: e.g.: tdp-backend-raft

We need to have postgres12 and Python available before being able to use the script: 
```bash
export LD_LIBRARY_PATH=~/deps/#/python/lib
```
Note: '#' can change depending on programs/packages installed on the instance. Normally # == 0 or 1

Then:
```bash
cd /home/vcap/deps/#/python/bin
```
This runs the python3 version installed on the system	


## Backup
```bash
./python /app/scripts/db_backup.py -b -f <filename> -d <database URI>
```
where:
+ -b: run backup script
+ -f <filename> [Optional]: defines the filename for backup file. If not defines, it defaults to backup.pg. The filename
also accepts absolute path: e.g: /tmp/backup.pg
+ -d <database URI> [Optional]: URI format: ```postgresql://$<USERNAME>:$<PASSWORD>@$<HOST>:$<PORT>/$<NAME>```

## Restore
```bash
./python /app/scripts/db_backup.py -r -f <filename> -d <database URI>
```
where:
+ -r: run restore script
+ -f <filename> [Optional]: defines the filename for backup file. If not defines, it defaults to backup.pg. The filename
also accepts absolute path: e.g: /tmp/backup.pg
The utility uses the URI which includes all addresses needed to connect to remote AWS RDS.
