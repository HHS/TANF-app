# 14. Migrating to Github Native Dependabot for TDP Dependency Management
Date: 2021-05-14 (_Updated: 2021-12-28_)

## Status

Accepted

## Context

Currently our Snyk configuration is configured on the carltonsmith Snyk organization which will no longer work after @carltonsmith leaves the project.
Additionally, these Snyk PRs require us to manage an unnecessary requirements.txt file in addition to our Pipfile and python dependency update PRs are not complete when they get opened since they don't update anything in our actual dependencies.

Furthermore, we currently use the Dependabot Preview app which is being deprecated in favor of a GitHub Native Dependabot which has more features and is configured via a YAML file committed to the repo.

## Decision
Rather than setting up Snyk on a new organization and in order to get ahead on the impending Dependabot migration, we propose an update which provides the necessary YAML config to enable the new GitHub Native version of Dependabot.

## Consequences
To maintain our gitflow:

* We need to explicitly disable automated PR updates on the HHS repo if it is not already, otherwise once this file gets merged in we will get Dependabot security-related PRs to both repos. This can be disabled in the security analysis settings as shown below:
![disable-dependabot-security-updates](https://user-images.githubusercontent.com/22626085/118340020-8b744f80-b4e8-11eb-8bb1-eb851f074627.png)
* We also need to specify a target_branch in the dependabot configuration file to prevent automated version-related PR updates from opening in the HHS repo.
* An unforeseen consequence of this switchover was that Synk was missing out on version updates that Dependabot is now flagging. We have accummulated a significant but unknown size backlog as dependabot is limited to 10 PRs at a time. As a response, we are proposing a mass-merge in #1023 instead of individual PRs per version update due to the laborious nature of this stream of updates. We will manually create a unique branch and modify the configuration file to have dependabot scan for updates on this new target branch without the numeric limit for PRs opened. Once all are merged, we will follow our gitflow process and open a PR to 'tdp-raft-main' branch and have raft-review and so on. For merging those PRs, the github-native dependabot does not have auto-merge capabilities so these would have to be done manually or we'd have to add a [third-party bot](https://github.com/ahmadnassri/action-dependabot-auto-merge) for this limited use-case. The above outlined process is an as-needed process to clear the backlog -- once the backlog is cleared, we will resume the previous process of one PR per update.

**Benefits**
* Mitigate the need to manage unnecessary file for dependency management
* Mitigate the need to manage multiple dependency management tools
* Dependency management no longer contingent upon project user accounts.

**Risks**
* (minor) The GitHub README status badges currently don't work for the GitHub Native Dependabot: [as noted in this open dependabot issue](https://github.com/dependabot/dependabot-core/issues/1912)
* We are seeing a plethora of recurring updates so to stem the tide here, we are going to decrease dependabot's sensitivity to patch-level updates and for the worst offenders we will only be updating on minor version updates. This is denoted in our [dependabot config](https://github.com/raft-tech/TANF-app/.github/dependabot.yml). Note that this change will not prevent security-related patch updates (to the extent that dependency managers identify these updates as such). 

## Notes
### Development Dependencies
This project defines a number of "Development Dependencies" which are not installed in production-esque environments (ie. deployed in Cloud.gov) but are instead only used for supporting operations during local development and automated unit testing in CI/CD.

These dependencies will still be kept up to date by Dependabot but needn't follow the same review flow as updates to packages we actively use within the codebase outside of development/testing. In those cases, as long as the tests all pass on the branch opened to update the dev dependency it may be merged directly into `develop`.

Dev dependencies are listed in two locations in this project:
* [package.json](https://github.com/raft-tech/TANF-app/blob/develop/tdrs-frontend/package.json#L66) as `devDependencies` for the React UI
* [Pipfile](https://github.com/raft-tech/TANF-app/blob/develop/tdrs-backend/Pipfile#L6) as`dev-packages` for the Django application

### Frontend Dependencies
`A11y review` aas not been part of our [git workflow]() for reviewing dependency-related PRs opened by Dependabot. Instead, we focus on reviewing the changelog to better understand how the upgrade will impact TDP (if at all), confirm that the dependency is actually still needed, and we test for breaking changes.

However, a11y should still be considered when reviewing these upgrades to help ensure there are no impacts on TDP end users. During 11/17 dev sync, the team agreed to the following workflow process re: dependency PRs and a11y review:

- Update dependabot config to add a11y review label to frontend dependency PRs (tracked in #1449)
- When dev picks up these tickets for review and testing, the release notes/changelog section should be reviewed to inspect for changes that could have a11y implications (user-facing changes)
- After testing, dev will follow existing git workflow steps, which include tagging `reitermb` for `a11y review` (Git workflow Step 4).
