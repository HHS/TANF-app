# 15. Development Environments

Date: 2021-04-06 (yyyy-mm-dd)

## Status

Pending

## Context

Recently we have run into issues where we needed multiple branches deployed for testing purposes and our current strategy will only allow for one branch to be deployed at a time in our development environment. 

## Proposed Decision


We propose setting up four separate apps in the dev environment

_This does not reflect the current state, but a proposed future state_

| Dev Site | App Name(s) | Purpose |
| -------- | -------- | -------- |
| Sandbox     | tdp-frontend-sandbox & tdp-backend-sandbox     | Space for devs to test in a deployed environment    |
| A11y | tdp-frontend-a11y & tdp-backend-a11y | Space for accessibility testing |
| QASP | tdp-frontend-qasp & tdp-backend-qasp | Space for QASP review |
| raft | tdp-frontend-raft & tdp-backend-raft | Space for raft review |

We could very easily add three new labels for deploying to the different environments, and this would cut down significantly on needing to wait for a space to deploy a branch we are working on. Additionally, the backend deployments are currently set for 2GB of memory with only approximately 600MB used. We can safely reduce it to 1GB. The frontend is currently allocated 256MB of memory, while only using 27MB. This can be safely reduced to 128MB. This will reduce our currently allocated memory by half, ensuring that all four proposed dev space applications will run smoothly.

## Consequences

### Pros

- Allows for multiple deployed dev instances
- Allows testing for multiple branches simultaneously
- Unblocks testing and dev deploy work
- Streamlines process of managing dev deployments

### Cons

- More resources being used because there would be more apps running (minimal)
    - Note: We recently decreased the memory allocated to each deployment as we were previously using more resources than we needed to per instance. 

## Impact
_In order to get here, the following tasks will have to be completed_

- Update CircleCI deploy workflow
  - For all branches other than raft-tdp-main and HHS:main deploy to a distinct app 
- Move vendor staging to new staging space/domain
- Update merge to `raft-tdp-main` to deploy to staging and not any development environment

Time estimate for development: 4-6 hours
Story Points: 2
