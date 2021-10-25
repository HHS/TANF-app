# Circle CI Health Check Template

It is important to periodically audit Circle CI to make sure that it can catch failures as expected. This file serves as a template which outlines the major components which should be audited on a scheduled basis. 

For testing create a new branch off raft-tdp-main and make commits there. This branch will not be merged and is only used for testing purposes. Ensure that you delete it following this audit.

## Confirm secrets-check functionality
- [ ] Commit a randomly generated secret key to the repo and push your changes.
- [ ] Ensure that the build is failed and the offending key is flagged in the Circle CI checks.

## Confirm test-backend functionality
- [ ] Commit any incorrectly formatted python code and ensure the linter step of the build is failed as expected. (ex. line over 80 characters in length)
- [ ] Commit a failing pytest unit test and confirm the associated step is failed in the build. (Add `assert False` in any test to prompt a failure)
- [ ] Update `tdrs-backend/reports/zap.conf` to set rule 10106 (HTTP ONLY) to FAIL and confirm the OWASP scan step of the build is failed.
- [ ] Confirm artifact existence: owasp_report.html

## Confirm test-frontend functionality
- [ ] Commit any incorrectly formatted javascript code and ensure the linter step fails.
- [ ] Commit a failing jest unit test and confirm the associated step is failed in the build. (Add `expect(false).toStrictEqual(true)` in any test to prompt a failure)
- [ ] Confirm Pa11y tests are taking accurate screenshots by reviewing the build artifacts and ensuring the screenshot taken matches the page expected.
- [ ] Update `tdrs-frontend/reports/zap.conf` to set rule 10106 (HTTP ONLY) to FAIL and confirm the OWASP scan step fails.
- [ ] Confirm artifacts exist for owasp_report.html and all relevant Pa11y screenshots.

## Confirm deployment functionality
- [ ] Attempt to deploy a PR with failing or unfinished status checks using one of the `Deploy with CircleCI` labels and confirm that the GitHub Action is skipped and no deployment occurs.
- [ ] Assign a GitHub deployment label to a PR that is passing status checks and confirm there is no unexpected error output in the Circle CI deployment steps.
