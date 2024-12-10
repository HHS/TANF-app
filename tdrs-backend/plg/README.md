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

### Grafana Auth and RBAC Config
Grafana is accessible by any frontend app on a private route to users who have the correct role. The Grafana UI is not be accessible to any user or application unless they are routed to it via a frontend app. Grafana is configured to require user and password authentication. Having the extra layer of authentication is required because the roles defined in Grafana are not in alignment with the roles TDP defines. Assigning users to appropriate role and teams in Grafana allows for least privilege access to any information that Grafana might be able to display.

Grafana has three roles: `Admin`, `Editor`, and `Viewer`. We have also defined two teams (groups) in Grafana: `OFA` and `Raft` and several users. The teams are how we manage least privilege to Grafana's resources. Upon creation, all users are given one of the base roles. All Raft dev user accounts are given read only access (`Viewer`) to Grafana and OFA has a user account(s) associated with each of the roles. All users who are outside of OFA should always be assigned the `Viewer` role to maintain least privilege. All dashboards in Grafana are viewable by team as opposed to individual users/roles. Dashboard permissions are configured per dashboard and each team is given read only access to the appropriate dashboards. The `ofa-admin` user is the only direct user given access to resources. This account is given exclusive admin rights to all of Grafana.

All Grafana administration is handled under the `Administration` drop down in the hamburger menu which is only accessible to `Admin` users. Users can be created, assigned a role, and then associated with a team. As new dashboards are added to Grafana their permissions need to be configured for least privilege by going to Dashboards-><New Dashboard>->Settings->Permissions. The admin can use other dashboard permission configurations to help finish the configuration.
