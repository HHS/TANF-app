# 8. Deployment Flow
Date: 2021-01-27 (Updated 2021-12-20)

## Status

Accepted

## Context

As of January 2021, the project has only a single deployment environment on Cloud.gov, which we are calling `development`.

This poses challenges to the vendor development team. The team works on multiple features or fixes at any one time, but only has a single environment to test deployed code. This is leading to "crowding", where multiple in-progress features by different devs all want to be deployed to the same environment for testing. 

Our Cloud.gov organization currently has three Spaces -- dev, staging, and prod. Staging and prod are currently empty as of January 2021. The vendor team currently has access to the dev Space only.

## Decision

_Note that this represents a planned future state, not the current state._

Deploy Environment | Cloud.gov Space | Cloud.gov Dev Access | Role                                             | Deploys when ...                      |
-------------------|-----------------|----------------------|--------------------------------------------------|---------------------------------------|
A11y Review        | Tanf-Dev        | Vendor & Gov         | Deploy code for vendor internal testing & review | A11y-review github label assigned     |
Sandbox             | Tanf-Dev        | Vendor & Gov       | Deploy code for vendor internal testing & review | Sandbox github label assigned         |
Raft                | Tanf-Dev        | Vendor & Gov      | Deploy code for vendor internal testing & review | Raft github label assigned               |
QASP                | Tanf-Dev        | Vendor & Gov      | Deploy code submitted for gov review             | QASP-review github label assigned     |
Gov Staging            | Tanf-Staging    | Gov               | Deploy code once gov-approved                    | Code merged to `HHS/TANF-app:staging` 
Production         | Tanf-Prod       | Gov                  | Deploy code tested in staging & ready for prod   | Code merged to `HHS/TANF-app:main`    

## Consequences

**Pros:**
* Vendor dev team "crowding" should be reduced through this solution.
* Only need to maintain/monitor vendor dev access to a single Cloud.gov Space using this solution -- least privilege, simplified account management.
* Good: Code deploys automatically upon gov approval, but does not deploy immediately to prod, leaving room for further gov testing. Any mistakes that make it past gov review will not deploy immediately to prod.
* Tradeoff: A four-environment setup has more complexity than a three-environment setup.

## Notes

Each deploy environment consists of a pair of applications, one frontend and one backend.

### How would this affect #521? "As a developer, I want a staging site..."

Under the proposed deployment flow, the staging site built in #521 will be the `vendor staging` site. 

Future stories will be built out for `production`.
