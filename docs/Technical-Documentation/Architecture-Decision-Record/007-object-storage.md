# 7. Object Storage

Date: 2020-08-04 (_Updated 2021-12-27_)

## Status

Accepted

## Context

For TDP, we need the ability to store raw, unparsed data files from TANF grantees in the states, territories, and tribes. Additionally, we need a storage system for static HTML/CSS and files used to (re)create services infrastructure. Amazon S3 provides secure, durable, highly-scalable object storage. We will be able to store application content in S3 using Cloud.gov's secure and compliant  managed [service](https://cloud.gov/docs/services/s3/) that provides direct access to S3.

## Decision

We will use cloud.gov managed S3 for object storage.

## Consequences

**Benefits**
- Provides durability through redundancy 
- Versioning and Multi-Factor Authentication deletion 
- AWS S3 buckets configured through cloud.gov are encrypted at rest, using industry standard AES-256 encryption algorithm. 

**Risks**
-  Information stored in AWS S3 buckets is retained indefinitely by default. This behavior is out of compliance with the current [SORN](https://github.com/raft-tech/TANF-app/issues/798#issuecomment-887063640) and will need to be resolved before release 3. 

## Notes
