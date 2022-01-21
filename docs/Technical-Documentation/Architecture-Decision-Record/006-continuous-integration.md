# 6. Continuous integration
Date: 2021-08-04 (_Updated 2021-12-27_)

## Status

Accepted

## Context

For improvement of our software engineering processes, we should implement continuous integration.

## Decision

We will use CircleCI as our continuous integration platform.

## Consequences

Using CircleCI for continuous integration and deployment (CI/CD) will make the ATO process simpler, since it has a [FedRAMP ATO on file](https://marketplace.fedramp.gov/#/product/circleci-cloud?sort=productName). 

## Notes

- CircleCI is used to automate builds, testing, and deploys from GitHub.
- MFA is enforced via approval and merging of code changes by TDP's privileged users (i.e. sys admins). 