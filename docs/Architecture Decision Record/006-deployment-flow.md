# 6. Deployment Flow
Date: 2021-01-25

## Status

Proposed.

## Context

As of January 2021, the project has only a single deployment environment on Cloud.gov, which we are calling `development`.

This poses challenges to the vendor development team. The team works on multiple features or fixes at any one time, but only has a single environment to test deployed code. This is leading to "crowding", where multiple in-progress features by different devs all want to be deployed to the same environment for testing. 

Our Cloud.gov organization currently has three Spaces -- dev, staging, and prod. Staging and prod are currently empty as of January 2021. The vendor team currently has access to the dev Space only. 

The proposed deploy solution below adds a second Cloud.gov deploy environment to the dev Space. (Each deploy environment is really a pair of applications, one frontend and one backend.) One of the environments will be called `experiment` and used for internal vendor team review. The other will be called `development` and will be used for government review. This aims to solve the "crowding" problem by allowing the vendor team two separate places to deploy code, without giving the vendor team deploy access to two separate Spaces in Cloud.gov.

## Proposed Decision

_Note that this represents a planned future state, not the current state._

Deploy Environment | Cloud.gov Space | Cloud.gov Dev Access | Role                                              | Deploys when ...  |
-------------------|-----------------|----------------------|---------------------------------------------------|-------------------|
Experiment         | Dev             | Vendor & Gov         | Deploy code for vendor internal testing & review  | Anytime           |
Development        | Dev             | Vendor & Gov         | Deploy code submitted for gov review             | Anytime work is ready for QASP review |
Staging            | Staging         | Gov                  | Deploy code once gov-approved               | Code merged to `HHS/TANF-app:staging`
Production         | Prod            | Gov                  | Deploy code tested in staging & ready for prod    | Code merged to `HHS/TANF-app:main`


## Consequences

* Good: Vendor dev team "crowding" should be reduced through this solution.
* Good: Only need to maintain/monitor vendor dev access to a single Cloud.gov Space using this solution.
* Good: Code deploys automatically upon gov approval, but does not deploy immediately to prod, leaving room for further gov testing.
* Bad: A four-environment setup has more complexity than a three-environment setup.
* Alternative: An alternative would be to have a single gov-only Space in Cloud.gov, prod. Gov-approved code would deploy directly to prod on merge. However, this leaves no room for testing code after it has been gov-approved. In this alternative flow, mistakes would deploy immediately to prod.