# TDP Environments

## Development

| Dev Site | Frontend URL | Backend URL | Purpose |
| -------- | -------- | -------- | -------- |
| Sandbox     | https://tdp-frontend-sandbox.app.cloud.gov | https://tdp-backend-sandbox.app.cloud.gov     | Space for devs to test in a deployed environment 
| A11y | https://tdp-frontend-a11y.app.cloud.gov | https://tdp-backend-a11y.app.cloud.gov | Space for accessibility testing |
| QASP | https://tdp-frontend-qasp.app.cloud.gov | https://tdp-backend-qasp.app.cloud.gov | Space for QASP review |
| raft | https://tdp-frontend-raft.app.cloud.gov | https://tdp-backend-raft.app.cloud.gov | Space for raft review |

### Dependencies 

- `clamav-rest`

**Cloud.gov AWS RDS `(tanf-dev)`**
- `tdp-db-dev`
  
**Cloud.gov AWS S3 `(tanf-dev)`**
- `tdp-staticfiles-dev`
- `tdp-datafiles-dev`
- `tdp-tf-states` - Stores the Terraform state files used to create and re-recreate services infrastructure.

## Staging

Unlike Development, the Staging environment contains a single frontend and backend deployment.

| Frontend URL | Backend URL | Purpose |
| -------- | -------- | -------- |
| https://tdp-frontend-staging.app.cloud.gov | https://tdp-backend-staging.app.cloud.gov     | Space for government users to test in a deployed, production-like environment    |

### Dependencies 

- `clamav-rest`

**Cloud.gov AWS RDS `(tanf-staging)`**
- `tdp-db-staging`
  
**Cloud.gov AWS S3 `(tanf-staging)`**
- `tdp-staticfiles-staging`
- `tdp-datafiles-staging`
  
**Cloud.gov AWS S3 `(tanf-dev)`**
- `tdp-tf-states` - Stores the Terraform state files used to create and re-recreate services infrastructure. Note this S3 bucket lives in the development space.

## Production

Like Staging, there is only one Production deployment. Note that developers do *not* ever have access to production.

| Frontend URL | Backend URL | Purpose |
| -------- | -------- | -------- |
| https://tdp-frontend-production.app.cloud.gov | https://tdp-backend-production.app.cloud.gov     | Production space for active users of the application.    |

### Dependencies 

- `clamav-rest`

**Cloud.gov AWS RDS `(tanf-production)`**
- `tdp-db-production`
  
**Cloud.gov AWS S3 `(tanf-production)`**
- `tdp-staticfiles-production`
- `tdp-datafiles-production`
- `tdp-tf-states` - Stores the Terraform state files used to create and re-recreate services infrastructure.

## External Dependencies

These are shared across all environments.

- [CircleCI](https://circleci.com/)
- [Login.gov](https://login.gov/)
- [Cloud.gov](https://cloud.gov/)
- [ClamAV Rest](https://registry.hub.docker.com/r/rafttech/clamav-rest)
