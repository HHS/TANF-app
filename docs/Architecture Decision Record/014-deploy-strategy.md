# 14. Deployment Strategy Change

Date: 2021-04-06 (yyyy-mm-dd)

## Status

Approved

## Context

Since the recent changes to our [Git workflow](https://github.com/HHS/TANF-app/blob/main/docs/Architecture%20Decision%20Record/009-git-workflow.md) we believe our current deploy strategy should be updated to more closely match the workflow. Previously, since we had approvals on two different repositories we decided that it made sense to maintain [two separate staging sites](https://github.com/HHS/TANF-app/blob/main/docs/Architecture%20Decision%20Record/008-deployment-flow.md). We would deploy to one with approval in the raft-tech repository, and another with approval to HHS. Since we now have all approvals made in raft-tech, the deploy after approval serves the same purpose as deploying to the Government staging site would have.

## Proposed Decision

We would like to replace the Government and Vendor staging sites with one staging site that will live in the `tanf-staging` Cloud.gov space.

_Note that this represents a planned future state, not the current state._

Deploy Environment | Cloud.gov Space | Cloud.gov Dev Access | Role                                              | Deploys when ...  |
-------------------|-----------------|----------------------|---------------------------------------------------|-------------------|
Development        | Dev             | Vendor & Gov         | Deploy code for testing & review  | Anytime           |
Staging        | Staging             | Vendor & Gov         | Deploy code after gov review            | Code merged to `raft-tech/TANF-app:raft-tdp-main` | `HHS/TANF-app:staging`
Production         | Prod            | Gov                  | Deploy code tested in staging & ready for prod    | Code merged to `HHS/TANF-app:main`

## Consequences

### Pros
- Aligns better with our current workflow
- Frees up memory and disk space in the dev environment
- Simplifies the deploy process

### Cons
- None that we can see at this time

## Impact
_In order to get here, the following tasks will have to be completed_

- Move vendor staging to new staging space/domain
- Update documentation to reflect new strategy

Time estimate for development: 2-4 hours
Story points: 2
