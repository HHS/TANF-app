# 8. Deployment Flow

Date: 2021-01-27 (_Updated 2021-12-27_)

## Status

Accepted

## Context

Our Cloud.gov organization currently has three Spaces -- dev, staging, and prod. The vendor team currently has access to the dev Space only.

Since the recent changes to our [Git workflow](https://github.com/HHS/TANF-app/blob/main/docs/Architecture%20Decision%20Record/009-git-workflow.md) we believe our current deploy strategy should be updated to more closely match the workflow. Previously, since we had approvals on two different repositories we decided that it made sense to maintain [two separate staging sites](https://github.com/HHS/TANF-app/blob/main/docs/Architecture%20Decision%20Record/008-deployment-flow.md). We would deploy to one with approval in the raft-tech repository, and another with approval to HHS. Since we now have all approvals made in raft-tech, the deploy after approval serves the same purpose as deploying to the Government staging site would have.

Additionally, as of January 2021, the project has only a single deployment environment on Cloud.gov, which we are calling `development`. This poses challenges to the vendor development team. The team works on multiple features or fixes at any one time, but only has a single environment to test deployed code. This is leading to "crowding", where multiple in-progress features by different devs all want to be deployed to the same environment for testing. 

## Decision

Deploy Environment | Cloud.gov Space | Cloud.gov Dev Access | Role                                             | Deploys when ...                                  |
-------------------|-----------------|----------------------|--------------------------------------------------|---------------------------------------------------|
Dev                | Tanf-Dev        | Vendor & Gov      | Deploy code submitted for gov review             | Relevant github label assigned as shown below     |
Staging            | Tanf-Staging    | Gov               | Deploy code once gov-approved                    | Code merged to `raft-tech/TANF-app:raft-tdp-main` |
Production         | Tanf-Prod       | Gov                  | Deploy code tested in staging & ready for prod   | Code merged to `HHS/TANF-app:master`                |  

### Gitflow and Deployments
We will be following the Gitflow process which is an industry standard. You can read more about it [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) and [here](https://datasift.github.io/gitflow/IntroducingGitFlow.html). I will just highlight the parts relevant for our deployment and versioning strategy. As shown below, the raft team will merge any relevant feature branches of the form `feat/###-branch-description` into the develop branch which should deploy to `staging`. From this branch, we will split off a release-specific branch of the form `release/v#.#.#`. Once this release is ready, it will be merged to HHS:master which should contain only finalized merge commits of the release versions and should deploy to production.

![image](https://user-images.githubusercontent.com/84722778/161764906-d9c9e66a-ea44-4042-850d-5f0e927c8c81.png)

Source: https://nvie.com/posts/a-successful-git-branching-model


### Dev deployments
Within the dev space, there is no correlation for branch to environment as these feature or bugfix branches will constantly vary:

| Dev Site | Frontend URL | Backend URL | Purpose                                          |
| -------- | -------- | -------- |--------------------------------------------------|
| Sandbox     | https://tdp-frontend-sandbox.app.cloud.gov | https://tdp-backend-sandbox.app.cloud.gov/admin/     | Space for development in a deployed environment |
| A11y | https://tdp-frontend-a11y.app.cloud.gov | https://tdp-backend-a11y.app.cloud.gov/admin/ | Space for accessibility testing                  |
| QASP | https://tdp-frontend-qasp.app.cloud.gov | https://tdp-backend-qasp.app.cloud.gov/admin/ | Space for QASP review                            |
| raft | https://tdp-frontend-raft.app.cloud.gov | https://tdp-backend-raft.app.cloud.gov/admin/ | Space for Raft review                          |

## Consequences

**Pros**
* 3-space strategy instead of 4 aligns better with our current gitflow. 
* Code deploys automatically upon gov approval, but does not deploy immediately to prod, leaving room for further gov testing. Any mistakes that make it past gov review will not deploy immediately to prod.
* Vendor dev team "crowding" should be reduced through this solution.
* Only need to maintain/monitor vendor dev access to a single Cloud.gov Space using this solution -- least privilege, simplified account management.
* Frees up memory and disk space in the dev environment

**Risks**
* None that we can see at this time

## Notes

- As of December 2021, merges into `HHS/TANF-app:main` do not deploy to any environment, since we are pending activation of the production space (#721). 
