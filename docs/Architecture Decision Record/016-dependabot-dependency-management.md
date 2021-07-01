# 16. Migrating to Github Native Dependabot for TDP Dependency Management
Date: 2021-05-14 (updated: 2021-06-16)
## Status

Approved

## Context

Currently our Snyk configuration is configured on the carltonsmith Snyk organization which will no longer work after @carltonsmith leaves the project.
Additionally, these Snyk PRs require us to manage an unnecessary requirements.txt file in addition to our Pipfile and python dependency update PRs are not complete when they get opened since they don't update anything in our actual dependencies.

Furthermore, we currently use the Dependabot Preview app which is being deprecated in favor of a GitHub Native Dependabot which has more features and is configured via a YAML file committed to the repo.


## Proposed Decision
Rather than setting up Snyk on a new organization and in order to get ahead on the impending Dependabot migration, We propose an update which provides the necessary YAML config to enable the new GitHub Native version of Dependabot.

## Consequences

To maintain our gitflow:

* We need to explicitly disable automated PR updates on the HHS repo if it is not already, otherwise once this file gets merged in we will get Dependabot security-related PRs to both repos. This can be disabled in the security analysis settings as shown below:
![disable-dependabot-security-updates](https://user-images.githubusercontent.com/22626085/118340020-8b744f80-b4e8-11eb-8bb1-eb851f074627.png)
* We also need to specify a target_branch in the dependabot configuration file to prevent automated version-related PR updates from opening in the HHS repo.

*: An unforeseen consequence of this switchover was that Synk was missing out on version updates that Dependabot is now flagging. We have accummulated a significant but unknown size backlog as dependabot is limited to 10 PRs at a time. As a response, we are proposing a mass-merge in #1023 instead of individual PRs per version update due to the laborious nature of this stream of updates. We will manually create a unique branch and modify the configuration file to have dependabot scan for updates on this new target branch without the numeric limit for PRs opened. Once all are merged, we will follow our gitflow process and open a PR to 'tdp-raft-main' branch and have raft-review and so on. For merging those PRs, the github-native dependabot does not have auto-merge capabilities so these would have to be done manually or we'd have to add a ![third-party bot](https://github.com/ahmadnassri/action-dependabot-auto-merge) for this limited use-case. The above outlined process is an as-needed process to clear the backlog -- once the backlogged is cleared, we will resume the previous process of one PR per update.


### Pros
* Mitigate the need to manage unnecessary file for dependency management
* Mitigate the need to manage multiple dependency management tools
* Dependency management no longer contingent upon project user accounts.

### Cons

* (minor) The GitHub README status badges currently don't work for the GitHub Native Dependabot: [as noted in this open dependabot issue](https://github.com/dependabot/dependabot-core/issues/1912)

### Notes

Time estimate for development: n/a.

[#917](https://github.com/raft-tech/TANF-app/pull/917) and [#932](https://github.com/raft-tech/TANF-app/pull/932) were created to support this migration and PR [#944](https://github.com/raft-tech/TANF-app/pull/944) completes this migration.
