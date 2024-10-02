# Cloud Foundry, Cloud.gov AWS RDS Database Upgrade
The process below provides a guide to roll our backend applications over to a new RDS version and instance. The entire process can take several hours and does involve downtime for the environment which you are upgrading. Be sure to take those factors into account when commencing the process.

## Process

### 1. Open an SSH tunnel to the service
To execute commands on the RDS instance we can open an SSH tunnel to the service and run all our commands locally. Keep this tunnel open in a separate terminal window until this process is complete!

```
cf connect-to-service --no-client <APP_NAME_THAT_IS_BOUND_TO_RDS> <RDS_SERVICE_NAME>
```

You should see out put similar to:

```
Finding the service instance details...
Setting up SSH tunnel...
SSH tunnel created.
Skipping call to client CLI. Connection information:

Host: localhost
Port: 63634
Username: <REDACTED>
Password: <REDACTED>
Name: <REDACTED>

Leave this terminal open while you want to use the SSH tunnel. Press Control-C to stop.
```

### 2. Create a backup of the database(s) in the RDS instance
In a separate terminal from your SSH tunnel terminal, generate the `pg_dump` files.
Note: the <HOST>, <PORT>, <DB_USER>, and <PASSWORD> are the values you received from the output of the SSH tunnel. The <DB_NAME> parameter is the name of the DB you want to export, e.g `tdp_db_raft`. You will need to run this command for each DB in the instance.

```
pg_dump -h <HOST> -p <PORT> -d <DB_NAME> -U <DB_USER> -F c --no-acl --no-owner -f <FILE_NAME>.pg
```

After the command finishes, you should see <FILE_NAME>.pg in your current working directory. Do some sanity checks on this backup file to assert it makes sense. Now that we have our backup(s), we need to begin making the Terraform changes required to support the upgrade.
<br/>

### 3. Update Terraform to create a new RDS instance
Follow the instructions in the `terraform/README.md` to get Terraform configured. Modify the `main.tf` file in the `terraform/<ENV>` to include a new RDS instance. E.g if you were updating `prod` to version 15.x you would add the following code to the `main.tf` file. We are NOT removing the existing `resource "cloudfoundry_service_instance" "database"` from the `main.tf` file. Note that the resource and the `name` of the new RDS instance are not the same as the original resource name and RDS name. This is on purpose and we will remedy this in later steps.

```yaml
resource "cloudfoundry_service_instance" "new-database" {
  name             = "tdp-db-prod-new"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.rds.service_plans["medium-gp-psql"]
  json_params      = "{\"version\": \"15\", \"storage_type\": \"gp3\", \"storage\": 500}"
  recursive_delete = true
  timeouts {
    create = "60m"
    update = "60m"
    delete = "2h"
  }
}
```
After adding the new RDS resource to `main.tf`, you can follow the rest of the instructions in the `terraform/README.md` to plan and then apply this change with Terraform.

### 4. Bind an app to the new RDS instance
In the `tdrs-backend/db-upgrade` directory, open the `manifest.yml` file and update the `services` block to reference the new RDS service you just created: in the example this would be: `- tdp-db-prod-new`. Then deploy this manifest: `cf push --no-route -f manifest.yml -t 180`. Wait for the connector app to deploy. We need to deploy a temporary app to avoid too much downtime for the backend app(s) and so that we can start new SSH tunnel to the new RDS instance. You should now close the original SSH tunnel we opened in step 1.

### 5. Open an SSH tunnel to the new RDS instance
Again, in a separate terminal execute the following command and leave that terminal/connection alive until further notice.
```
cf connect-to-service --no-client db-connector <NEW_RDS_SERVICE_NAME>
```

### 6. Create the appropriate database(s) in the new RDS server
Using the credentials from the new SSH tunnel, create the same DB(s) you dumped in the new RDS instance.
```
createdb -U <DB_USER> -h <HOST> -p <PORT> <DB_NAME>
```

### 7. Restore the backup(s) to the appropriate database(s)
Using the credentials from the new SSH tunnel, restore the backups to the appropriate DBs.
```
pg_restore -p <PORT> -h <HOST> -U <DB_USER> -d <DB_NAME> <FILE_NAME>.pg
```

During this step, you may see errors similar to the message below. Note `<DB_USER>` is imputed in the message to avoid leaking environment specific usernames/roles.

```
pg_restore: from TOC entry 215; 1259 17313 SEQUENCE users_user_user_permissions_id_seq <DB_USER>
pg_restore: error: could not execute query: ERROR:  role "<DB_USER>" does not exist
Command was: ALTER TABLE public.users_user_user_permissions_id_seq OWNER TO <DB_USER>;
```

and the result and total amount of these errors should be something like:

```
pg_restore: warning: errors ignored on restore: 68
```

If this is what you see, everything is OK. This happens because the `pg_dump` doesn't remove owner associations on sequences for some reason. But you will see in the blocks above that `pg_restore` correctly alters the sequence owner to the new database user.

### 8. Use `psql` to get into the database(s) to check state
Using the credentials from the new SSH tunnel, use the psql cli to inspect the restored DBs.
```
psql -p <PORT> -h <HOST> -U <DB_USER> -d <DB_NAME>
```
<br/>

### 9. Rename and Move RDS instances
Now that we have verified that the data in our new RDS instance looks good. We need to lift and shift the backend app(s) to point to our new RDS instance as if it is the existing (now old) RDS instance.

First we need to unbind the existing RDS instance from the backend app(s) so that way we can make name changes.
```
cf unbind service <BACKEND_APP_NAME> <OLD_RDS_SERVICE_NAME>
```

After unbinding the service we want to update the "old RDS" service `name` to something different, plan, and then apply those changes with Terraform.
```yaml
resource "cloudfoundry_service_instance" "database" {
  name             = "something-that-isnt-tdp-db-prod"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.rds.service_plans["medium-gp-psql"]
  json_params      = "{\"version\": \"15\", \"storage_type\": \"gp3\", \"storage\": 500}"
  recursive_delete = true
  timeouts {
    create = "60m"
    update = "60m"
    delete = "2h"
  }
}
```

Now we can name our "new RDS" service to the expected `name`. Then we can also plan and apply those changes with Terraform

```yaml
resource "cloudfoundry_service_instance" "new-database" {
  name             = "tdp-db-prod"
  space            = data.cloudfoundry_space.space.id
  service_plan     = data.cloudfoundry_service.rds.service_plans["medium-gp-psql"]
  json_params      = "{\"version\": \"15\", \"storage_type\": \"gp3\", \"storage\": 500}"
  recursive_delete = true
  timeouts {
    create = "60m"
    update = "60m"
    delete = "2h"
  }
}
```

Now we will bind the new RDS service back to the backend app(s) and restage it. Be sure to monitor the app's logs to ensure it connects to the instance.

```
cf bind service <BACKEND_APP_NAME> <RDS_SERVICE_NAME>
```

Then

```
cf restage <BACKEND_APP_NAME>
```

If the backend app is running with no issues, we can now safely remove the "old RDS" service from Terraform. Remove the entire resource block named `database` from `main.tf` re-plan and then apply the changes to remove that instance with Terraform.

Finally, to get our Terraform state looking like it originally did, we want to rename our `new-database` resource back to `database`. That way we are consistent. To do so we rename the resource, and to avoid Terraform from deleting it (since `database` won't exist in the state) we want to inform Terraform that we have "moved" the resource. We do so by adding the following code to the `main.tf`. Note, when running `terraform plan ...` it will not show any infrastructure changes, only a name change. Ensure you still apply even if it looks like there are no changes!

```yaml
moved {
  from = cloudfoundry_service_instance.new-database
  to   = cloudfoundry_service_instance.database
}
```

After adding the above code, re-plan and apply the changes with Terrform. Once Terraform has successfully applied the change, remove the `moved` block from `main.tf`. Re-plan with Terraform and assert it agrees that there are no changes to be made. If Terraform reports changes, you have made a mistake and need to figure out where you made the mistake.

### 10. Access the re-staged app(s) and run a smoke test
- Log in
- Submit a few datafiles
- Make sure new and existing submission histories populate correctly
- Checkout the DACs data

If everything looks good, there is nothing to do. If apps aren't working/connecting to the new RDS instance, you will need to debug manually and determine if/where you made a mistake.

### 11. Update the `postgresql-client` version to the new version in `tdrs-backend/apt.yml`
```yaml
- postgresql-client-<NEW VERSION>
```
Note: if the underlying OS for CloudFoundry is no longer `cflinuxfs4` (code name `jammy`) you may also need to update the repo we point to for the postgres client binaries.

### 12. Update the postgres container version in `tdrs-backend/docker-compose.yml`
```yaml
postgres:
image: postgres:<NEW VERSION>
```

### 13. Commit and push correct changes, revert unnecessary changes.
Commit and push the changes for:
- `main.tf`
- `tdrs-backend/apt.yml`
- `tdrs-backend/docker-compose.yml`

Revert the changes for:
- `manifest.yml`
