# 20. Pipeline Build Flow

Date: 2023-06-07 (_Updated 2023-06-13_)

## Status

Pending

## Context

We use [CircleCI](https://app.circleci.com/pipelines/github/raft-tech/TANF-app)] as our primary pipeline build tool.  On the HHS side, the standard pipeline, build all and deploy ran by CircleCI is sufficiently granular to meet all our build needs. However, on the dev Raft-TANF side, where work can often be held up by waiting for build and test pipelines, it's useful to reduce build times by filtering which workflows run based upon which code is changing. In order to do this, GitHub Actions is leveraged to kick off different CircleCI build workflows since Actions has more granular control over what paths are changed. 

These pipelines are closely tied to the [Git workflow](./009-git-workflow.md) and should run build and test as expected based on what code changed, and still deploy to the correct CF spaces based upon the Decision tree in the [Deployment Flow](./008-deployment-flow.md)   

## Build Logic

For all release branches, the main, and the master branch, CircleCI should run the full build, infrastructure deploy, and app deployment.

for feature/development branches, only the build and test pertainint to the code changed should be built.
Front end tests should be run if /tdrs-frontent changes
Back end tests should be run if /tdrs-backend changes
the entire build and test all should run if anything pertaining to the pipeline changes
infrastructure deploy should run if /terraform or infrastructure deploy pipeline changes

Once a pull request is flagged as ready for review and/or has reviewers assigned, a full build and test all should be run (and tests must pass before merge to develop)

Develop merges trigger a deploy to the develop CF space, and then a special integration end-2-end test that tests against the real development environment instead of a simulated environment on the CircleCI build servers. 

## Consequences

**Pros**
* reduce time of build and tests by only running the appropriate workflows.
* only run infrastructure deploys when changes are made to infrastructure code.
* only run end-2-end tests when code is ready to be reviewed.
* only run full integration end-2-end testing when the develop environment assets are updated.

**Risks**
* Increased pipeline logic complexity

## Notes

- For the nuanced build triggers, CircleCI documentation recommends using Actions to trigger CircleCI builds and send different flags to tell which workflows should run. See this [blog](https://circleci.com/blog/trigger-circleci-pipeline-github-action/) for details, though we use [promiseofcake/circleci-trigger-action@v](https://github.com/promiseofcake/circleci-trigger-action) plugin vs circleci/trigger_circleci_pipeline@v1.0

- This could be an argument for future complete pipeline switchover to GitHub Actions in order to reduce pipeline complexity, while maintaining the desired build granularity.