# 9. Git Workflow

Date: 2021-02-23 (_updated 2021-12-28_)

## Status

Accepted

## Context

In order to maintain the principal of Least Privilege, it was decided at the onset of this project that the vendor (Raft) would work from a fork of the government repo and issue pull requests to the government repo from the fork. The vendor would not have write access to the government repository or the government's CircleCI account.

Throughout the project all vendor development work has been done in the vendor's forked repository, while pull requests from the government and even some documentation pull requests from the vendor were made directly to the government repository.

This has created a situation where the vendor has needed to continuously rebase with the government repository to make sure the vendor's repository was up to date. As a result, problems with the Git history have arisen that make it confusing for both the government and the vendor to track the history of the work.

The proposed workflow below provides a remedy to these issues, as well as many others, as detailed in the [Consequences]() section.

## Decision

**A contributor to the TDP project would always use the following steps to propose changes to the repository. No merges directly into `HHS:main`.**

**<details><summary> Git Workflow Steps </summary>**

1. If working locally from [CLI](https://en.wikipedia.org/wiki/Command-line_interface), check out `raft-tdp-main` branch (or another branch if this work is dependent on a branch that hasn't been merged yet) in `raft-tech/TANF-app`: `git checkout <raft-tdp-main OR unmerged branch>`.
    * run `git pull`
    * check out new feature branch: `git checkout -b <BRANCH NAME>`
    * update the repo with code, documentation, etc.
    * add changes: `git add <file(s)>` and confirm updates: `git status`
    * commit changes with a message: `git commit -am '<BRIEF DESCRIPTION OF CHANGES>'` 
    * run `git push origin <BRANCH NAME>`
    * create [a draft pull request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/about-pull-requests#draft-pull-requests) from new branch to `raft-tdp-main` or `<unnmerged branch>` (if dependent on another branch that has yet to be merged). The PR title should include DRAFT e.g. `[DRAFT] Issue #: Adding a feature` 
    * _If working from GitHub instead of locally, follow [these steps](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request#creating-the-pull-request) to create a draft pull request_.

2. Implement, Test, Review work independently
    * If content is devops oriented, developer can freely merge to `HHS:hhs-dev-devops` to test their changes. No merges from `HHS:hhs-dev-devops` to `HHS:main` will be accepted.

3. Finalize pull request template.
    * Confirm all tasks in issue are completed/checked off.
    * Add ACs and testing steps to the [template](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/.github/pull_request_template.md).
    * Add in-line comments to the file changes to provide context for the proposed changes.
    * Ensure there are no merge conflicts. 
    * Ensure CI/CD pipelines are green.
    * Update the title to remove `DRAFT` and change the PR to [Ready for Review](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/changing-the-stage-of-a-pull-request), assign label `raft review`.

4. Assign Raft reviewer(s): 
    * For research and design work, assign **at least two** of the following: `reitermb`, `sreedevip` or `valeriecollignon`. 
    * For development work, including security controls, assign **at least two** Raft developers with one of them being `abottoms-coder`. If issue tasks includes `a11y review`, also assign `reitermb`.
    * For project management work, assign `abottoms_coder` and `reitermb`.

5. Assigned Raft reviewer(s) perform the review and/or requests changes.
    * For development work, author is expected to schedule a [tabletop meeting]() at least 48 hours after `raft review` label added. 
    * When changes are asked for, the changes are made by the author.
    * When satisfied, the reviewer(s) confirm that ACs are met,  `approve` the PR, remove `raft review` and add `QASP review` labels.
        * See exceptions [below]()
    * For project management, research, and design work, tag `lfrohlich` for government review.
    * For development work, including security controls, tag `adpennington` for government review.

6. Assigned Government reviewer(s) perform the review and/or requests changes.
    * Government reviewer is expected to tick-off the QASP checklist in the PR description relating to the deliverables described.
    * When changes are asked for, the changes are made by the author. These changes should be prioritized over other work in-progress. 
    * For project management, research, and design work, `lfrohlich` will tag `adpennington` for review, as needed. 
    * For development work that requires `gov a11y` review, `adpennington` will complete code review and tag `ttran-hub` + `iamjolly` via comment, and add `gov a11y` label to PR. Gov a11y review team will conduct this portion of the review as described [here.](https://github.com/HHS/TANF-app/blob/main/docs/Technical-Documentation/how-government-will-test-a11y.md) 
    * When satisfied, the Government reviewer `approves` the PR and tags with the  `ready-to-merge` and removes the `QASP review` label.

7. `abottoms-coder` (or his back-up) merges changes into `raft-tdp-main`. This includes:
    * opening a PR from `raft-tdp-main` to `HHS:main`
    * updating the PR template to change `addresses` to `closes` so that issue [can be automatically closed when the Government merges](https://docs.github.com/en/github/managing-your-work-on-github/linking-a-pull-request-to-an-issue#linking-a-pull-request-to-an-issue-using-a-keyword)
    * ensuring the CI/CD pipelines are green
    * assigning `lfrohlich` or `adpennington`as Government as reviewers. They will approve and  merge to `HHS:main` which will trigger the CI/CD process to deploy code to the prod environment. 
</details>

![](images/TANF-Git-Workflow.png)

## Consequences

**Benefits**
- Dependency chains would be much easier to manage.
  - We can daisy chain PRs with dependencies allowing GitHub to manage changes for downline PRs much more simply and cleanly, ie. `my_branch_1` depends on `my_branch_0` and there is an open PR from `my_branch_0` to `raft-tdp-main`. Can open a PR in raft-tech from `my_branch_1` to `my_branch_0` and only the changes from the latest branch will be shown to reviewers, but the dependent code will still be present and kept up to date by GitHub exposing a button to update with upstream branch.
  - Because of this, we can more easily submit smaller PRs since this removes much of the maintenance work currently involved to achieve that goal
- Less complexity for contributers and reviewers
- No need to rebase from `HHS:main` back to `raft-tdp-main`
- Much smaller chance of needing to revert commits to `HHS:main`
- Git history will be much cleaner
- Much less time managing git history
- All reviews will be in one place, so the entire history of a branch/PR will be viewable in one place
- Will allow us to keep the current CircleCi setup
  - Once staging is in place, we can deploy to the development server when code is merged in to `raft-tdp-main` and test deployment ahead of opening a PR to `HHS:main`
- We can implement GitHub Hooks to automatically issue PRs to `HHS:main` when one is merged to `raft-tdp-main`
- Maintain "Least Privelege" by restricting vendor from having write access to Gov repo and CircleCI
- Tests automated deployment before merging to `HHS:main`

**Risks**
- Only one pull request at a time will be able to go to `HHS:main`, but this won't be a problem since they will only be issued once approved and therefore can be merged immediately
- All PR comments will be on the vendor repo rather than the government repo, so it will be important to link to the native PR to keep track of the conversation from `HHS:main`

## Notes
- Overarching TDP [workflow]() should be followed prior to and after opening PRs. 
- All PRs into `HHS:main` should come from raft-tech/raft-tdp-main unless absolutely needed, in which case `lfrohlich` or `adpennington` must review and approve. 
- PRs created by Dependabot for [dev-only dependencies](), which will not be installed on deployed environments, may be merged in to `raft-tdp-main` as they are created. 
- See [Dependabot ADR]() for more detail on the `raft review` process for PRs created by Dependabot for frontend dependencies.

