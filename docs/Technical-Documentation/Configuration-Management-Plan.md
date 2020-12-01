# Configuration Management Plan

This document describes how the team approaches configuration management of the core platform. Before configuration changes go into production, they need to pass through **[our Workflow](../How-We-Work/team-charter/our-workflow.md#workflow)**.

## What goes into configuration management?
In short, everything needed to run and operate the platform that is not a _secret_.

Here are some examples that should be in configuration management:

- Application code
- CircleCI configuration (currently managed in `.circleci`)
- Cloud.gov configuration (currently managed via deploy scripts)

For changing settings that we currently cannot manage as configuration files in version control, such as GitHub repository settings, you must first get agreement from another team member that the change should be made, using a tool such as Microsoft Teams.

## Where should all this configuration go?
All configuration must be stored in GitHub using the following "Change Workflow" unless it is a _secret_.

## How do we test these changes?
If possible, first test the changes locally.

After that, upload them to a development environment where either manual or automated testing needs to be run as per the Workflow.

## Change workflow

1. All configuration changes must flow through a git repository, centrally managed through GitHub, unless they contain sensitive information.
1. A change is initiated and discussed, following the steps in our [Workflow](../How-We-Work/team-charter/our-workflow.md#workflow).
1. In the appropriate GitHub repository for the component, a pull request (PR) against the `main` branch is created that addresses the change.
1. The PR is reviewed by someone other than the committer. Pairing via screen-sharing is encouraged and qualifies as a review. Review should include assessment of architectural design, DRY principles, security and code quality. The reviewer approves the PR via GitHub.
1. The reviewer merges the approved PR. The committer may merge an approved PR if the changes made are time-sensitive.
1. A continuous integration (CI) server handles automated tests and continuous deployment (CD) of the merged changes.
    - All changes are deployed to a testing environment, such as development.
    - Any and all automated tests are run.
    - If all tests pass, changes can be promoted for deployment to production in the pipeline.

## Roles and responsibilities

* **All team members**
  * Follow the configuration management plan.
  * Make suggestions (such as in PRs) if you have ideas for improving the plan.
* **Product Owner**
  * Ensure the team follows the Feature Lifecycle, Story Lifecycle, and other operational aspects of the plan.
  * Ensure that team members uphold their responsibilities.
  * Approve any major changes to the plan.

### Squashing commits

[Squashing commits](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History#Squashing-Commits) is allowed but discouraged, except in rare instances.

### Rebase or merge

Does the team prefer [rebasing or merging](https://www.atlassian.com/git/tutorials/merging-vs-rebasing/)?

### When should a PR be created?

The use of work-in-progress or [Draft PRs](https://github.blog/2019-02-14-introducing-draft-pull-requests/) PRs is encouraged. If you create a work-in-progress PR, you might also make it plain in the PR name with a `[WIP]` prefix.

### Should PRs be assigned?

PRs are typically not assigned in GitHub, unless someone specifically needs to sign off on the change.

You can request a review using GitHub's built-in tools, mention someone in the PR with the `@` notation, or contact them outside the GitHub context to request a review.

#### Acknowledgement

Portions of this plan were adapted from the [Cloud.gov Configuration Management Plan](https://cloud.gov/docs/ops/configuration-management/); thank you to the authors and the Cloud.gov team for this terrific modern security and compliance work!