# Connect-to-Service dependencies

From [this github](https://github.com/cloud-gov/cf-service-connect) which has some of these instructions.



## For OSX
1. Install psql

> `brew install postgresql`

2. Install cf cli

> `brew install cloudfoundry/tap/cf-cli@8` -- you can install `@7` if you prefer, 8 is newest.

3. Install service-connect plugin

> `cf install-plugin https://github.com/cloud-gov/cf-service-connect/releases/download/1.1.0/cf-service-connect-darwin-amd64`

[Releases](https://github.com/cloud-gov/cf-service-connect/releases), if needed.

3. Use connection

> `cf connect-to-service tdp-backend-<name> tdp-db-dev`


# How to DROP existing DB and Recreate a fresh DB

### Connecting to DB service
First step is to connect to the instance DB (see above).

#### Optional: DB backup
Before deleting the DB and recreating a fresh DB, you might want to create a backup from the existing data in case you decide to revert the DB changes back.

For creating a DB backup, please see: `/tdpservice/scheduling/BACKUP_README.md`

#### Drop and Recreate

e.g: 
>`cf connect-to-service tdp-backend-qasp tdp-db-dev`

After connection to the DB is made (the step above will make a psql connection), then the following Postgres commands have to run:

1. List the DBs: `\l`
2. Potgres does not _DROP_ a database when you are connected to the same DB. As such, you will have to connect to a different DB using command:  
>`\c {a_database}`
   
   A good candiadate is:
>`\c postgres`
3. find the associated DB name with instance. E.g: `tdp_db_dev_qasp`
4. use the following command to delete the DB:
>`DROP DATABASE {DB_NAME}`
5. use the following command to create the DB:
>`CREATE DATABASE {DB_NAME}`

After the DB is created, since the database is cinoketely empty, we will need to redeploy the app again to create tables (or alternatively we can restore a good backup), and then we should run populate stt command to add STT data to the empty DB

>`./manage.py populatestts`
