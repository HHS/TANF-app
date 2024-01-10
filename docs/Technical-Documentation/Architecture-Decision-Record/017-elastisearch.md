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
   * Additional overhead to run a proxy application to control access to ES + Kibana+
 * Security & Authentication
   * Cloud.gov ES service is a wrapper around AWS OpenSearch/ES. AWS ES does not support Xpack (Elastic/Kibana native security features) because it was forked off of Elastic 7.10.2 which did not support Xpack at that time. This implies that our current Xpack configuration we are using with our local Elastic 7.17.6/Kibana 7.17.10 deployments ([implemented here](https://github.com/raft-tech/TANF-app/pull/2775)) will not be applicable to our deployed environments. To get around this issue, AWS suggests introducing a [proxy EC2 node](https://aws.amazon.com/blogs/security/how-to-control-access-to-your-amazon-elasticsearch-service-domain/) to implement the same type of features that Xpack natively provides by way of IAM policies and Signature Version 4 request signing. However, Cloud.gov does not allow access to the underlying AWS resources it is wrapping, thus making this workaround impossible.
   * Another option to workaround AWS ES and Cloud.gov would be to deploy and manage our own ES cluster to Cloud.gov in each space. This also introduces large blocks in and of itself. To deploy/manage our own cluster would take at least one dedicated Elastic SME to ensure uptime, availability, updates, security, etc... This would also imply that we would need to purchase Elastic Stack self-managed licenses from Elastic. To acquire the minimum feature set we need to have robust security and authentication integration with TDP, we would need to procure platinum tier licenses. Elastic requires a minimum of three licenses to be purchased. We at a minimum, would need three nodes per environment (9 licenses total) to have a functioning Elastic cluster. However, the cost of these licenses and the cost of at least one person to manage the cluster(s)/licenses makes this an infeasible option.
   * With these things considered, the best security/authentication we can provide at this time (12/22/2023) is by blocking all external incoming traffic to our Elastic and Kibana servers, and by leveraging the view based auth [implemented here](https://github.com/raft-tech/TANF-app/pull/2775), which prevents non admin and non HHS AMS authenticated users from navigating to Kibana via the frontend. We will not be able to use any Xpack features (RBAC, Realms, P2P encryption, etc...) used in that PR in our deployed environments.

## Notes

These changes are slated for later in our releases: currently release 3 but might not be fully implemented until v4.

Please also see these notes: https://gist.github.com/jtwillis92/a6840a412676fc2d3f58c0dccbf10da1

