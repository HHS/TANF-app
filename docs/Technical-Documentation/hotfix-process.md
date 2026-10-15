# Hotfix process

ADRs [009-git-workflow](./Architecture-Decision-Record/009-git-workflow.md) and [018-versioning-and-releases](./Architecture-Decision-Record/018-versioning-and-releases.md) outline the git workflow and release process. The purpose of this document is to explain the hotfix workflow in more detail to save time and prevent missteps in the future.

Hotfixes are reserved for release-blocking or high-severity production defects. Non-blocking bugs/defects should follow the normal process for prioritizing tickets.

The hotfix steps below supersede the older hotfix routes described in ADRs 009 and 018. Hotfixes must first be reviewed and merged into `raft-tech/TANF-app:develop`, then cherry-picked onto a new release branch created from the target release tag.

The commands below assume `origin` points to `raft-tech/TANF-app`. Replace the example versions, issue number, and commit SHAs as appropriate.

1. Identify the target release tag, e.g., `v4.23.0`, and the new patch version, e.g., `v4.23.1`.
2. Create a hotfix branch from the latest `develop` in `raft-tech/TANF-app`:

   ```bash
   git fetch origin --tags
   git switch develop
   git pull --ff-only origin develop
   git switch -c hotfix/v4.23.0-<ISSUE>
   ```

3. Implement the fix, add tests, run the required checks, commit the changes, and push the branch:

   ```bash
   git push -u origin hotfix/v4.23.0-<ISSUE>
   ```

4. Open the hotfix PR in `raft-tech/TANF-app`:
   - Base branch: `develop`
   - Head branch: `hotfix/v4.23.0-<ISSUE>`
5. Obtain the required reviews and approvals described in [009-git-workflow](./Architecture-Decision-Record/009-git-workflow.md), including government review when required, and ensure required checks pass. Then merge the hotfix PR into `develop`.
6. Create a new release branch from the **target release tag**, then cherry-pick the hotfix commit(s) that landed on `develop`, in their original order:

   ```bash
   git fetch origin --tags
   git switch -c release/v4.23.1 v4.23.0
   git cherry-pick -x <HOTFIX-COMMIT-SHA> [<ADDITIONAL-HOTFIX-COMMIT-SHA>...]
   ```

   Use the commit SHAs on `develop` after the PR was merged. For a squash merge, cherry-pick the resulting squash commit. For a merge commit, cherry-pick the individual hotfix commits or use `git cherry-pick -x -m 1 <MERGE-COMMIT-SHA>` to apply the hotfix PR's changes relative to its first parent. Resolve any conflicts and rerun the relevant tests against the release branch.

7. Update the changelog for the new patch version as described in [018-versioning-and-releases](./Architecture-Decision-Record/018-versioning-and-releases.md), commit any release updates, and push the release branch:

   ```bash
   git push -u origin release/v4.23.1
   ```

8. Open a release PR against the HHS repository and link the reviewed hotfix PR:
   - Base repository: `HHS/TANF-app`
   - Base branch: `main`
   - Head repository: `raft-tech/TANF-app`
   - Head branch: `release/v4.23.1`
9. Create the new release tag from the final hotfix release commit on `release/v4.23.1`, and push it to `raft-tech/TANF-app`:

   ```bash
   git switch release/v4.23.1
   git tag -a v4.23.1 -m "Release v4.23.1"
   git push origin v4.23.1
   ```

   The tag must point to the release branch commit containing the cherry-picked fix(es) and release updates, not the original commit on `develop`. Create the GitHub release in `raft-tech/TANF-app` using this tag, and complete the government review and release process described in [009-git-workflow](./Architecture-Decision-Record/009-git-workflow.md) and [018-versioning-and-releases](./Architecture-Decision-Record/018-versioning-and-releases.md).
