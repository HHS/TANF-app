# 18. Versioning and Release strategy

Date: 2022-04-05 (yyyy-mm-dd)

## Status

Accepted

## Context
As discussed briefly in [deployment-flow](./008-deployment-flow.md), we will need a strategy for our versioning and releases.

## Decision

We will use the industry standard "gitflow" to handle releases, versioning, and process. You can read more about it [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) and [here](https://datasift.github.io/gitflow/IntroducingGitFlow.html). For versinoning we will be adopting [semver]
() as you can redhttps://semver.org/

## Consequences

Branch nomenclature will become more standardized and will adopt the semver standard for versioning

### Benefits

 * Significant performance increase at large scales.
   * Elasticsearch retains near real-time search capabilities even with datasets measured in hundreds of Terabytes.
   * PostgreSQL encounters table/index bloatings with very large data sets (>=1 MM rows) which negatively affect performance without advanced DBA operations.
 * Built in Reporting and Analytics capabilities - with UI capabilities to create Saved Searches, Visualizations and Dashboards.
 * Built in CSV export of Visualization data.
 * Access over REST API or Kibana UI, no database client needed.
   * This has the added security benefit of ensuring there is not direct database access and users must be passed through our standard authentication which for OFA users will include PIV/CAC card.
 * Auto-generated index mappings, which can be tweaked to gain further performance advantages. These are also much more flexible than traditional schemas used by relational databases.
 * Capabilities to perform ML and AI analytics on data sets.
 * Cloud.gov includes the ES service with FISMA moderate pricing.
 * Automated Index Lifecycle Management policies can be configured to move data into cold storage, etc to satisfy retention requirements.

### Risks
 * New query language and interface to learn for OFA staff members who will have access
   - This is mostly mitigated through a SQL Workbench provided in Kibana where you can use regular SQL syntax to query records.
 * More infrastructure to manage.
   * This is mostly mitigated due to using a Cloud.gov managed service for ES and Terraform, this greatly simplifies scaling the cluster and abstracts away a lot of the difficult cluster management tasks we would have to do if we didn't use a managed service.
   * Additional overhead to run a proxy application to control access to ES + Kibana

## Notes


