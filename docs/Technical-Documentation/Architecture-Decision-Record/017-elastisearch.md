# 17. Elasticsearch Architecture

Date: 2021-01-12 (yyyy-mm-dd)

## Status

Accepted

## Context

To modernize the eventual reporting stack for TDP, we have a need for a usable data backend. To establish parity with the legacy TDRS system, we originally planned to store parsed TANF and SSP data in our PostGreSQL database; however, the data required cleaning that is burdensome to perform prior to storage so a faster, scalable solution is desired. 

## Decision

We will use an Elastisearch and Kibana stack for their modern feature set and scalability with large data sets. The Elastisearch/Kibana cluster will be an application hosted in Cloud.gov with the rest of our TDP application so we can leverage all the work surrounding authentication, security, and data compliance.

## Consequences

### Benefits
 * Great performance boost, specifically at large scale.
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

These changes are slated for later in our releases: currently release 3 but might not be fully implemented until v4.

Please also see these notes: https://gist.github.com/jtwillis92/a6840a412676fc2d3f58c0dccbf10da1

