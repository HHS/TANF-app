# 8. Deployment Flow
Date: 2021-01-27

## Status

Proposed.

## Context

As of January 2021, the project has only a single deployment environment on Cloud.gov, which we are calling `development`.

This poses challenges to the vendor development team. The team works on multiple features or fixes at any one time, but only has a single environment to test deployed code. This is leading to "crowding", where multiple in-progress features by different devs all want to be deployed to the same environment for testing. 

Our Cloud.gov organization currently has three Spaces -- dev, staging, and prod. Staging and prod are currently empty as of January 2021. The vendor team currently has access to the dev Space only. 

The proposed deploy solution below adds a second Cloud.gov deploy environment to the dev Space, called `vendor staging`. (Each deploy environment consists of a pair of applications, one frontend and one backend.)

The `development` environment will be used for internal vendor team review. The `vendor staging` environment will be used for government review. This aims to solve the "crowding" problem by allowing the vendor team two separate places to deploy code, within one Space.

## Proposed Decision

_Note that this represents a planned future state, not the current state._

Deploy Environment | Cloud.gov Space | Cloud.gov Dev Access | Role                                              | Deploys when ...  |
-------------------|-----------------|----------------------|---------------------------------------------------|-------------------|
Development         | Dev             | Vendor & Gov         | Deploy code for vendor internal testing & review  | Anytime           |
Vendor Staging        | Dev             | Vendor & Gov         | Deploy code submitted for gov review             | Anytime work is ready for QASP review |
Gov Staging            | Staging         | Gov                  | Deploy code once gov-approved               | Code merged to `HHS/TANF-app:staging`
Production         | Prod            | Gov                  | Deploy code tested in staging & ready for prod    | Code merged to `HHS/TANF-app:main`

### How would this affect #521? "As a developer, I want a staging site..."

Under the proposed deployment flow, the staging site built in #521 will be the `vendor staging` site. 

Future stories will be built out for `gov staging` and `production`.

## Consequences

* Good: Vendor dev team "crowding" should be reduced through this solution.
* Good: Only need to maintain/monitor vendor dev access to a single Cloud.gov Space using this solution -- least privilege, simplified account management.
* Good: Code deploys automatically upon gov approval, but does not deploy immediately to prod, leaving room for further gov testing. Any mistakes that make it past gov review will not deploy immediately to prod.
* Tradeoff: A four-environment setup has more complexity than a three-environment setup.
* Alternative: An alternative would be to have a single gov-only Space in Cloud.gov, prod. Gov-approved code would deploy directly to prod on merge. However, this leaves no room for testing code after it has been gov-approved. In this alternative flow, mistakes would deploy immediately to prod.