# TDP Environments

## Development

| Dev Site | Frontend URL | Backend URL | Purpose |
| -------- | -------- | -------- | -------- |
| Sandbox     | https://tdp-frontend-sandbox.app.cloud.gov | https://tdp-backend-sandbox.app.cloud.gov/admin/     | Space for devs to test in a deployed environment |
| A11y | https://tdp-frontend-a11y.app.cloud.gov | https://tdp-backend-a11y.app.cloud.gov/admin/ | Space for accessibility testing |
| QASP | https://tdp-frontend-qasp.app.cloud.gov | https://tdp-backend-qasp.app.cloud.gov/admin/ | Space for QASP review |
| raft | https://tdp-frontend-raft.app.cloud.gov | https://tdp-backend-raft.app.cloud.gov/admin/ | Space for raft review |

### Dependencies

- `clamav-rest` - Virus scanner REST service used to scan file uploads.

**Cloud.gov AWS RDS `(tanf-dev)`**

- `tdp-db-dev` - Stores application-level models (e.g. Users, Reports).

**Cloud.gov AWS S3 `(tanf-dev)`**

- `tdp-staticfiles-dev` - Stores static HTML/CSS for Django Admin.
- `tdp-datafiles-dev` - Stores the files uploaded by STTs (no real STT data to be stored in dev).
- `tdp-tf-states` - Stores the Terraform state files used to create and re-recreate services infrastructure.

## Staging

The Staging environment contains two frontend and backend deployments.

| Frontend URL | Backend URL | Purpose |
| -------- | -------- | -------- |
| https://tdp-frontend-staging.app.cloud.gov | https://tdp-backend-staging.app.cloud.gov/admin/     | Space for government users to test in a deployed, production-like environment    |
| https://tdp-frontend-develop.app.cloud.gov | https://tdp-backend-develop.app.cloud.gov/admin/     | Space for government users to test in a deployed, production-like environment    |

### Dependencies

- `clamav-rest` - Virus scanner REST service used to scan file uploads.

**Cloud.gov AWS RDS `(tanf-staging)`**

- `tdp-db-staging` - Stores application-level models (e.g. Users, Reports).
- `tdp-db-develop` - Stores application-level models (e.g. Users, Reports).

**Cloud.gov AWS S3 `(tanf-staging)`**

- `tdp-staticfiles-staging` - Stores static HTML/CSS for Django Admin.
- `tdp-staticfiles-develop` - Stores static HTML/CSS for Django Admin.
- `tdp-datafiles-staging` - Stores the files uploaded by STTs (no real STT data to be stored in staging).
- `tdp-datafiles-develop` - Stores the files uploaded by STTs (no real STT data to be stored in staging).

**Cloud.gov AWS S3 `(tanf-staging)`**

- `tdp-tf-states` - Stores the Terraform state files used to create and re-recreate services infrastructure. Note this
  S3 bucket lives in the staging space.

## Production

Like Staging, there is only one Production deployment. Note that developers do *not* ever have access to production.

| Frontend URL | Backend URL | Purpose |
|--------------|-------------| -------- |
| https://tanfdata.acf.hhs.gov | https://api-tanfdata.acf.hhs.gov | Production space for active users of the application.    |

### Dependencies

- `clamav-rest` - Virus scanner REST service used to scan file uploads.

**Cloud.gov AWS RDS `(tanf-prod)`**

- `tdp-db-prod` - Stores application-level models (e.g. Users, Reports).

**Cloud.gov AWS S3 `(tanf-prod)`**

- `tdp-staticfiles-prod` - Stores static HTML/CSS for Django Admin.
- `tdp-datafiles-prod` - Stores the files uploaded by STTs.
- `tdp-tf-states` - Stores the Terraform state files used to create and re-recreate services infrastructure.

## External Dependencies

These are shared across all environments.

- [CircleCI](https://circleci.com/)
- [Login.gov](https://login.gov/)
- [Cloud.gov](https://cloud.gov/)
- [ClamAV Rest](https://registry.hub.docker.com/r/rafttech/clamav-rest)
