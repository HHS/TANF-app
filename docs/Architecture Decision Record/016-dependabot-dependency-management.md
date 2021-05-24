# 16. Migrating to Github Native Dependabot for TDP Dependency Management
Date: 2021-05-14 (yyyy-mm-dd)

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

### Pros
* Mitigate the need to manage unnecessary file for dependency management
* Mitigate the need to manage multiple dependency management tools
* Dependency management no longer contingent upon project user accounts.

### Cons

* (minor) The GitHub README status badges currently don't work for the GitHub Native Dependabot: [as noted in this open dependabot issue](https://github.com/dependabot/dependabot-core/issues/1912)

### Notes

Time estimate for development: n/a.

[#917](https://github.com/raft-tech/TANF-app/pull/917) and [#932](https://github.com/raft-tech/TANF-app/pull/932) were created to support this migration and PR [#944](https://github.com/raft-tech/TANF-app/pull/944) completes this migration.
