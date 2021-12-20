# 8. Deployment Flow
Date: 2021-01-27 (Updated 2021-12-20)

## Status

Accepted

## Context

As of January 2021, the project has only a single deployment environment on Cloud.gov, which we are calling `development`.

This poses challenges to the vendor development team. The team works on multiple features or fixes at any one time, but only has a single environment to test deployed code. This is leading to "crowding", where multiple in-progress features by different devs all want to be deployed to the same environment for testing. 

Our Cloud.gov organization currently has three Spaces -- dev, staging, and prod. Staging and prod are currently empty as of January 2021. The vendor team currently has access to the dev Space only.

Additionally, since the recent changes to our [Git workflow](https://github.com/HHS/TANF-app/blob/main/docs/Architecture%20Decision%20Record/009-git-workflow.md) we believe our current deploy strategy should be updated to more closely match the workflow. Previously, since we had approvals on two different repositories we decided that it made sense to maintain [two separate staging sites](https://github.com/HHS/TANF-app/blob/main/docs/Architecture%20Decision%20Record/008-deployment-flow.md). We would deploy to one with approval in the raft-tech repository, and another with approval to HHS. Since we now have all approvals made in raft-tech, the deploy after approval serves the same purpose as deploying to the Government staging site would have.

## Decision

_Note that this represents a planned future state, not the current state._

Deploy Environment | Cloud.gov Space | Cloud.gov Dev Access | Role                                             | Deploys when ...                                  |
-------------------|-----------------|----------------------|--------------------------------------------------|---------------------------------------------------|
Dev                | Tanf-Dev        | Vendor & Gov      | Deploy code submitted for gov review             | Relevant github label assigned as shown below     |
Staging            | Tanf-Staging    | Gov               | Deploy code once gov-approved                    | Code merged to `raft-tech/TANF-app:raft-tdp-main` |
Production         | Tanf-Prod       | Gov                  | Deploy code tested in staging & ready for prod   | Code merged to `HHS/TANF-app:main`                |  


Within the dev space:

| Dev Site | Frontend URL | Backend URL | Purpose                                          |
| -------- | -------- | -------- |--------------------------------------------------|
| Sandbox     | https://tdp-frontend-sandbox.app.cloud.gov | https://tdp-backend-sandbox.app.cloud.gov     | Space for devs to test in a deployed environment |
| A11y | https://tdp-frontend-a11y.app.cloud.gov | https://tdp-backend-a11y.app.cloud.gov | Space for accessibility testing                  |
| QASP | https://tdp-frontend-qasp.app.cloud.gov | https://tdp-backend-qasp.app.cloud.gov | Space for QASP review                            |
| raft | https://tdp-frontend-raft.app.cloud.gov | https://tdp-backend-raft.app.cloud.gov | Space for vendor review                          |

## Consequences

**Pros:**
* Vendor dev team "crowding" should be reduced through this solution.
* Only need to maintain/monitor vendor dev access to a single Cloud.gov Space using this solution -- least privilege, simplified account management.
* Code deploys automatically upon gov approval, but does not deploy immediately to prod, leaving room for further gov testing. Any mistakes that make it past gov review will not deploy immediately to prod.
* Aligns better with our current workflow
* Frees up memory and disk space in the dev environment

Tradeoff: A four-environment setup has more complexity than a three-environment setup.

## Notes

Each deploy environment consists of a pair of applications, one frontend and one backend. As of December 2021, HHS/main deploys to "Staging" as we are pending activation of the production space. 

### How would this affect #521? "As a developer, I want a staging site..."

Under the proposed deployment flow, the staging site built in #521 will be the `vendor staging` site. 

Future stories will be built out for `production`.
