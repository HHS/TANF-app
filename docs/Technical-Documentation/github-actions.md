# How We Use GitHub Actions
For now, the only use case we have for GitHub Actions is to help up trigger CircleCI builds the way we want to. This is actually the preferred method CircleCI advises for branch, path, pull-request, and labelled filtering and job triggering. See this [blog](https://circleci.com/blog/trigger-circleci-pipeline-github-action/) for details, though we use [promiseofcake/circleci-trigger-action@v](https://github.com/promiseofcake/circleci-trigger-action) plugin vs circleci/trigger_circleci_pipeline@v1.0

## Path Filtering
We use Actions to filter which workflows are getting run by CircleCI by sending different flags to CircleCI through the promiseofcake CircleCI API trigger. See the individual files in [.github](../../.github/) for detailed instructions for how to use each.


## Release Tracker
`.github/workflows/release-tracker.yml` creates the `Release Tracker vX.Y.Z` issue for every published release, including patch and hotfix releases. It uses `.github/ISSUE_TEMPLATE/release-tracker-issue-template.md` for the title, assignees, labels, and body, and runs `.github/scripts/release_tracker.py`.

- **Trigger:** a release is published, or a manual run (Actions > Release Tracker > Run workflow) with a `tag` and a `dry_run` flag. Run it manually with `dry_run` on to preview the issue body for any existing tag.
- **Items:** the pull requests listed in the release notes are copied into section 1 as `- [ ] <title> by @<author> in <PR url>`. If the notes list none, the script uses GitHub's generated notes, then the commits between the previous tag and this tag. They land under an `Uncategorized (to be sorted)` heading above the three empty headings (External, Internal, No visible change). Sort them by hand or let a later step do it.
- **Safe to re-run:** if an issue with the exact title exists (open or closed), no new issue is created. The issue number is still printed and set as the `tracker_issue` step output.
- **Optional webhook:** after creating a tracker, the script POSTs `{"event":"release_tracker_created","tag":"<tag>","tracker_issue":<number>,"repo":"raft-tech/TANF-app"}` so another system can react. It is skipped when the secret is unset. Failures are retried three times and never fail the job.

  | Setting | Type | Purpose |
  | --- | --- | --- |
  | `RELEASE_TRACKER_AGENT_WEBHOOK_URL` | secret | HTTPS URL to POST to. Leave unset to turn the webhook off. |
  | `RELEASE_TRACKER_AGENT_WEBHOOK_KEY` | secret | Sender key. |
  | `RELEASE_TRACKER_AGENT_WEBHOOK_KEY_HEADER` | variable | Header that carries the key. Default `Authorization`, sent as `Bearer <key>`. Any other header name sends the raw key. |

- **Re-sending the webhook:** run the workflow manually with `dry_run` off and `notify_existing` on. No new issue is created if the tracker already exists.
- **Permissions:** `contents: read` and `issues: write` with the built-in `GITHUB_TOKEN`. The Projects board is not touched.
- **Limits:** a release created by another workflow using `GITHUB_TOKEN` does not trigger this workflow (GitHub does this to prevent loops). Releases are currently created by hand on the Releases page, so this does not apply today. If releases are ever automated, use a GitHub App token or PAT there, or run this workflow manually. A `release` event runs the workflow file from the tagged commit, so a hotfix tag cut from a release that predates this workflow will not trigger it. Use the manual run for those.
