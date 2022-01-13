# 17. Elasticsearch Architecture

Date: 2021-01-12 (yyyy-mm-dd)

## Status

Accepted

## Context

To modernize the eventual reporting stack for TDP, we have a need for a usable data backend.

## Decision

We will use an Elastisearch and Kibana stack for their modern feature set and scalability with large data sets. The Elastisearch/Kibana cluster will be an application hosted in Cloud.gov with the rest of our TDP application so we can leverage all the work surrounding authentication, security, and data compliance.

## Consequences

### Benefits
 - Elastisearch is fast becoming the industry standard if not already the standard for large data sets and getting their feature sets for customizable queries, scalability, and advanced storage methods.
 - Kibana frontend will be very user friendly compared to home rolling our own reporting interface.


### Cons
By divorcing the database(s) of TANF data from our application's PostGre SQL database, we have introduced complexity in the architecture both for accessing this data in Kibana but also in the user hand-off from our frontend to the Kibana UI.

## Notes

These changes are slated for later in our releases: currently release 3 but might not be fully implemented until v4.
