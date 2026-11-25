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

## DataFile reporting in Grafana

Use `data_files_datafile_view` for submission metadata with readable classifications. It exposes the DataFile columns, including `section_id`, plus `section` (the canonical Section name) and `program_type` (its Program code). All submission versions are included.

The view is generated and applied through the existing Grafana SQL pipeline. The database configuration step grants access to the `read_only`, `digit_sensitive`, and `admin_read_only` roles.

```sql
SELECT id, year, quarter, section, program_type, version
FROM data_files_datafile_view;
```

### Custom DIGIT dashboard views

The maintained definitions live in `plg/grafana_views/custom_views/`, separate from the ignored `user_views/` and `admin_views/` generated output:

| View | Purpose |
| --- | --- |
| `latest_tanf_exiters_view_prod` | FRA Work Outcomes records from the highest-version file per STT, canonical section, fiscal year, and quarter, starting in 2025. Includes raw SSNs and invalid/duplicate flags. |
| `mr_record_counts_by_tableview` | Record and distinct-case counts by source view, reporting period, and STT across TANF, SSP, Tribal TANF, and FRA. Case counts are NULL for aggregate/stratum records and FRA. |
| `stt_section_to_type_mapping` | Catalog of program, section label, STT type, region, record type, and source view. This is reporting metadata, not participation eligibility. |

The exiter definition joins `data_files_datafile.section_id` to `data_files_section`, then joins `section.program_id` to `data_files_program`. `DataFile.program` is a Python property, not a stored SQL column. The readable `section` output uses the canonical name's `varchar(100)` type. Existing dashboard aliases such as `program_type` remain unchanged.

Compatibility details:

- The mapping view's `section_id` is a **text label**, not a canonical foreign-key ID. Its join produces a row per matching STT; STTs sharing a type and region can produce duplicate projected rows. Do not remove these duplicates as incidental cleanup.
- FRA `EXIT_DATE` is an integer. The existing adjacent-duplicate flag uses a numeric difference of 1, not calendar-day arithmetic; the count view uses EXIT_DATE as its reporting period.
- A latest file with no parsed records does not fall back to an older version. Existing SSN validation and duplicate rules are retained, including the original handling of NULL SSNs.

#### Application order and access

The existing `scripts/apply-database-config.sh` deployment step runs migrations, generates user/admin views, applies the SQL, and then provisions reporting roles/users. The shared `apply_grafana_views` loader applies generated user/admin views with `CREATE OR REPLACE`, then drops the three managed custom views in reverse dependency order (counts → mapping → exiter) using `DROP VIEW IF EXISTS ... CASCADE`. It recreates the custom definitions in forward order:

1. Generated user views and helper functions.
2. Generated admin views and helper functions.
3. Custom exiter view.
4. Custom mapping view.
5. Custom counts view, which depends on the generated views and custom exiter view.

All three custom definitions are created in every environment, despite the exiter view's `_prod` suffix. Existing grants remain environment-specific:

| Role | Counts and mapping | Raw exiter view |
| --- | --- | --- |
| `read_only` | Production only | Not granted |
| `digit_sensitive` | All environments | Production only |
| `admin_read_only` | All environments | All environments, through its existing public-schema-wide SELECT grant |

Creating a view does not grant it to PUBLIC. Do not add raw exiters to the ordinary user-view grant list. Local Compose startup applies the SQL but does not provision deployment reporting roles or an application PostgreSQL Grafana datasource.

**Operational policy:** deployment restores only version-controlled view definitions and grants. A successful cascading recreation removes unversioned views or other database objects that depend on these three views, and they are **not automatically restored**. Independent views are not targeted. DIGIT/dashboard owners must be informed of this behavior and submit dependent definitions and required grants for version control if they need to survive deployment. Recreating ordinary views does not delete the underlying submission tables or records.

#### Local application and verification

From the repository root, with backend prerequisites configured:

```bash
task backend-up
python3 tdrs-backend/plg/grafana_views/generate_views.py --all
task backend-exec CMD="runscript apply_grafana_views"
```

The generator uses only the Python standard library. The backend task uses the running container's configured local database. Repeating generation/application is supported, but each successful run drops dependent unversioned objects and resets grants on the three recreated views. Standalone loader runs and local Compose startup do not restore reporting grants; reapply the approved role-provisioning commands separately if using reporting roles locally. Do not run the cloud database-configuration script locally.

Use `task psql` to inspect the installed definitions without exporting sensitive records:

```sql
SELECT to_regclass('public.latest_tanf_exiters_view_prod'),
       to_regclass('public.stt_section_to_type_mapping'),
       to_regclass('public.mr_record_counts_by_tableview');

SELECT program_type, section, record_type, source_table,
       total_record_count, unique_case_count
FROM mr_record_counts_by_tableview
LIMIT 10;
```

Check results against known synthetic submissions and repeat application to confirm unchanged results. Verify actual role access separately where deployment roles are provisioned. Never include real SSNs or credentials in screenshots, logs, or query exports.

#### Failures and recovery

Missing required SQL or SQL errors stop the loader; success is logged only after every definition applies. Custom drops and recreations run in one transaction: a failure restores the prior custom definitions, dependent objects, and their grants. Earlier generated views and migrations are **not** rolled back with that batch. After successful recreation, the deployment's existing role-provisioning step reapplies the managed grants. Nonzero statuses from required setup, migration, generation, application, and role/user commands fail database configuration. Its exit trap stops the owned SSH tunnel and removes only the temporary `.env.ci` it created, preserving the operation's exit status; a pre-existing `.env.ci` is not overwritten. The existing unavailable-backend skip remains unchanged.

Recreation handles missing custom views and incompatible existing output names/types, including the deployed `section_id` → `section` mismatch. It cannot repair an invalid SQL definition after arbitrary future schema changes, or bypass ownership restrictions. For those failures, have an authorized database owner inspect the definition, owners, and dependent objects, correct the SQL or arrange an approved ownership transition, then rerun the normal pipeline. Do not broaden grants to bypass ownership failures.

### Grafana Auth and RBAC Config
Grafana is accessible by any frontend app on a private route to users who have the correct role. The Grafana UI is not be accessible to any user or application unless they are routed to it via a frontend app. Grafana is configured to require user and password authentication. Having the extra layer of authentication is required because the roles defined in Grafana are not in alignment with the roles TDP defines. Assigning users to appropriate role and teams in Grafana allows for least privilege access to any information that Grafana might be able to display.

Grafana has three roles: `Admin`, `Editor`, and `Viewer`. We have also defined two teams (groups) in Grafana: `OFA` and `Raft` and several users. The teams are how we manage least privilege to Grafana's resources. Upon creation, all users are given one of the base roles. All Raft dev user accounts are given read only access (`Viewer`) to Grafana and OFA has a user account(s) associated with each of the roles. All users who are outside of OFA should always be assigned the `Viewer` role to maintain least privilege. All dashboards in Grafana are viewable by team as opposed to individual users/roles. Dashboard permissions are configured per dashboard and each team is given read only access to the appropriate dashboards. The `ofa-admin` user is the only direct user given access to resources. This account is given exclusive admin rights to all of Grafana.

All Grafana administration is handled under the `Administration` drop down in the hamburger menu which is only accessible to `Admin` users. Users can be created, assigned a role, and then associated with a team. As new dashboards are added to Grafana their permissions need to be configured for least privilege by going to Dashboards-><New Dashboard>->Settings->Permissions. The admin can use other dashboard permission configurations to help finish the configuration.
