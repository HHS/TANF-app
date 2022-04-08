# 18. Versioning and Release strategy

Date: 2022-04-05 (yyyy-mm-dd)

## Status

Accepted

## Context
As discussed briefly in [deployment-flow](./008-deployment-flow.md), we will need a strategy for our versioning and releases.

## Decision

### Gitflow
We will use the industry standards "gitflow" to handle release branching above our [git-workflow](./009-git-workflow.md). You can read more about gitflow [here](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow) and [here](https://datasift.github.io/gitflow/IntroducingGitFlow.html). As shown below, the raft team will merge any relevant feature branches of the form `feat/###-branch-description` into the `develop` branch. From this branch, we will split off a release-specific branch of the form `release/v#.#.#`. This release branch can be merged to `HHS/TANF-app:main`  which will deploy to staging site for review and testing. Once this release is fully ready, `HHS/TANF-app:main` will be merged into `HHS/TANF-app:master` which should contain only finalized merge commits of the release versions and will deploy to production.

![image](https://user-images.githubusercontent.com/84722778/161764906-d9c9e66a-ea44-4042-850d-5f0e927c8c81.png)

Source: https://nvie.com/posts/a-successful-git-branching-model

### Semver
For versioning, we will be adopting [semver](https://semver.org/) for our versioning strategy. Semver is not just a rubric for incrementing our numbers but has a technical meaning for backwards compatibility of our API(s) and codebase generally. As we gear up for production, we will be releasing v1.0.0 which serves MAJOR version 1 with no extra features. As detailed in the semver link, minor and patches updates will be backwards compatible. Feature sets that add functionality will increment the minor version and bug fixes will increment the patch version. Each version of our codebase will require an entry into the changelog file for a high-level overview of what was added, changed, or obsolesced. This changelog will be stored [here](../tanf-app-changelog.md).

Changelog entries must of the form with newer releases above older:
```
## \[#.#.#\]\(https://github.com/raft-tech/TANF-app/releases/tag/v#.#.#\) - YYYY/MM/DD
### Added

### Changed

### Removed

### Fixed

```

The link to the release page will generated from the creation of releases [here](https://github.com/raft-tech/TANF-app/releases/new).


### Hotfixes
Hotfixes should always be the exception but may become necessary in a production environment for a severe bug or breakage and should essentially be a user-stopping emergency. As you'll note below, the hotfix will be split directly from the master branch and merged directly back in with a new version with the patch updated. We will also need to update the changelog and have this new hotfix merged and tested within the develop branch. If the issue is not a show-stopper, it should be treated as a regular feature would be and created as a bug ticket and branch (e.g., `bug/####-branch-description`).

![image](https://user-images.githubusercontent.com/84722778/161772154-f2c64025-95f4-4aa2-9635-f6cb5b507356.png)

Source: https://nvie.com/posts/a-successful-git-branching-model

## Consequences

### Benefits

 * We have an established well-known set of processes and notation for release branching and versioning.
 * We will understand based on a label what changesets will be breaking in nature.

### Risks
 * New notation and process to learn for the team

## Notes


