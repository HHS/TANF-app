# TDP PLG Stack
Before attempting to deploy the PLG stack or an postgres exporter you MUST have access to the production space in cloud.gov.

## Deploying PLG
Before deploying the PLG stack you must have the `ADMIN_EMAILS` and `DEV_EMAILS` variables defined in your shell environment. The variables should be a comma separated string of emails, eg: `ADMIN_EMAILS="email1@email.com, email2@email.com, email3@email.com"` and `DEV_EMAILS="email4@email.com, email5@email.com, email6@email.com"`.

Once both of the above items have been confirmed, you can target the production environment with the CF CLI and run the command below.

```
./deploy.sh -a -d tdp-db-prod
```

The command will deploy the entire PLG stack to the production environment and setup all appropriate network policies and routes.

## Deploying a Postgres Exporter
Before deploying a postgres exporter, you need to acquire the AWS RDS database URI for the RDS instance in the environment you are deploying the exporter to.

```
cf env <BACKEND_APP>
```

From the output of this command find the `VCAP_SERVICES` variable. Within this variable is a JSON list of services the app you provided is bound to. Find the `aws-rds` key and copy the `uri` value to your clipboard from the `credentials` key. Then you can deploy your exporter with the command below.

```
./deploy.sh -p <ENVIRONMENT_NAME> -d <RDS_SERVICE_NAME> -u <DATABASE_URI>
```
where `<ENVIRONMENT_NAME>` MUST be one of `[dev, staging, production]`, and `<DATABASE_URI>` is the uri you just copied from the app's `VCAP_SERVICES` environment variable. This command also handles all of the necessary networking configuration.
