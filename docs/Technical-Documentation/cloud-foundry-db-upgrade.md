# Cloud Foundry, Cloud.gov AWS RDS Database Upgrade

## Process

If you are performing this process for the staging or production, you need to ensure you are performing the changes through the [HHS](https://github.com/HHS/TANF-app) repo and not the [Raft](https://github.com/raft-tech/TANF-app) repo.
<br/>

### 1. SSH into a backend app in your desired environment
```bash
cf ssh tdp-backend-<APP>
```
<br/>

### 2. Create a backup of all the databases in the ENV's RDS instance
Note: you can get the required field values from `VCAP_SERVICES`.
```bash
/home/vcap/deps/0/apt/usr/lib/postgresql/<CURRENT VERSION>/bin/pg_dump -h <HOST> -p <PORT> -d <DB_NAME> -U <DB_USER> -F c --no-acl --no-owner -f <FILE_NAME>.pg
```
<br/>

### 3. Copy the backup(s) to your local machine
Note: This assumes you ran the backup command above in the home directory of the app. As an added bonus for later steps, you should execute this command from somewhere within `tdrs-backend` directory! Make sure not to commit the files/directories that are copied to your local directory.
```bash
cf ssh tdp-backend--<APP> -c 'tar cfz - ~/app/*.pg' | tar xfz - -C .
```
<br/>

### 4. Verify backup file size(s) match the backup size(s) in the app
```bash
ls -lh <PWD>/home/vcap/app
```
As an added verification step, you should consider restoring the backups into a local server and verifying the contents with `psql` or `pgAdmin`.
<br/><br/>

### 5. Update the `version` key in the `json_params` item in the `database` resource in the `main.tf` file in the environment(s) you're upgrading with the new database server version
```yaml
json_params      = "{\"version\": \"<NEW VERSION>\"}"
```
<br/>

### 6. Update the `postgresql-client` version to the new version in `tdrs-backend/apt.yml`
```yaml
- postgresql-client-<NEW VERSION>
```
Note: if the underlying OS for CloudFoundry is no longer `cflinuxfs4` you may also need to update the repo we point to for the postgres client binaries.
<br/><br/>

### 7. Update the postgres container version in `tdrs-backend/docker-compose.yml`
```yaml
postgres:
image: postgres:<NEW VERSION>
```
<br/>

### 8. Update Terraform state to delete then re-create RDS instance
Follow the instuctions in the `terraform/README.md` and proceed from there. Modify the `main.tf` file in the `terraform/<ENV>` directory to inform TF of the changes. To delete the existing RDS instance you can simply comment out the whole database `resource` in the file (even though you made changes in the steps above). TF will see that the resource is no longer there, delete it, and appropriately update it's state. Then you simply re-comment the database `resource` back in with the changes you made in previous steps. TF will create the new RDS instance with your new updates, and also update the state in S3.
<br/><br/>

### 9. Bind backend to the new RDS instance to get credentials
```bash
cf bind-service tdp-backend-<APP> tdp-db-<ENV>
```
Be sure to re-stage the app when prompted
<br/><br/>

### 10. Apply the backend manifest to begin the restore process
If you copied the backups as mentioned in the note from step 3, the backups will be copied for you to the app instance in the command below. If not, you will need to use `scp` to copy the backups to the app instance after running the command below.
```bash
cf push tdp-backend-<APP> --no-route -f manifest.buildpack.yml -t 180 --strategy rolling
```
<br/>

### 11. SSH into the app you just pushed
```bash
cf ssh tdp-backend-<APP>
```
<br/>

### 12. Create the appropriate database(s) in the new RDS server
Note: you can get the required field values from `VCAP_SERVICES`.
```bash
/home/vcap/deps/0/apt/usr/lib/postgresql/<NEW VERSION>/bin/createdb -U <DB_USER> -h <HOST> <DB_NAME>
```
<br/>

### 13. Restore the backup(s) to the appropriate database(s)
Note: you can get the required field values from `VCAP_SERVICES`.
```bash
/home/vcap/deps/0/apt/usr/lib/postgresql/<NEW VERSION>/bin/pg_restore -p <PORT> -h <HOST> -U <DB_USER> -d <DB_NAME> <FILE_NAME>.pg
```
During this step, you may see errors similar to the message below. Note `<DB_USER>` is imputed in the message to avoid leaking environment specific usernames/roles.
```bash
pg_restore: from TOC entry 215; 1259 17313 SEQUENCE users_user_user_permissions_id_seq <DB_USER>
pg_restore: error: could not execute query: ERROR:  role "<DB_USER>" does not exist
Command was: ALTER TABLE public.users_user_user_permissions_id_seq OWNER TO <DB_USER>;
```
and the result and total amount of these errors should be:
```bash
pg_restore: warning: errors ignored on restore: 68
```
If this is what you see, everything is OK. This happens because the `pg_dump` doesn't remove owner associations on sequences for some reason. But you will see in the blocks above that `pg_restore` correctly alters the sequence owner to the new database user.
<br/><br/>

### 14. Use `psql` to get into the database to check state
Note: you can get the required field values from `VCAP_SERVICES`.
```bash
/home/vcap/deps/0/apt/usr/lib/postgresql/<NEW VERSION>/bin/psql <RDS URI>
```
<br/>

### 15. Re-deploy or Re-stage the backend and frontend apps
Pending your environment you can do this GitHub labels or you can re-stage the apps from Cloud.gov.
<br/><br/>

### 16. Access the re-deployed/re-staged apps and run a smoke test
- Log in
- Submit a few datafiles
- Make sure new and existing submission histories populate correctly
- Checkout the DACs data
<br/>
