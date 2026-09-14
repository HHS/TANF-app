# Feedback access testing checklist

Feedback is available after authentication and account approval. The API also
requires an active account and an assigned role, using the existing approval
permission. The anonymous option controls the feedback object's user association;
it does not bypass these access checks.

## Automated checks

Local verification on September 14, 2026:

- [x] Frontend Jest suite: 83 suites, 1,010 tests passed. Global coverage:
  95.41% statements, 90.36% branches, 94.11% functions, 95.66% lines.
  Run with `npm run test:ci -- --watchAll=false --runInBand`.
- [x] Frontend ESLint: passed with existing warnings.
- [x] Backend Flake8: passed for the full backend.
- [x] Git diff whitespace check: passed.
- [x] Full backend pytest suite: 1,783 passed and 1 existing large-file test
  skipped for its documented long runtime. Final run used
  `pytest --no-cov --basetemp=/tmp/tdp-pytest-final-6048` in the backend container.
- [x] Backend feedback API and user view tests: 86 passed. Reloading factory users
  normalizes UUID values for comparisons with persisted feedback; older view
  tests now authenticate before testing anonymous submissions and validation.
- [x] Go parser package tests and `go vet ./...`: passed, including the optional
  PostgreSQL state-transition tests with `TEST_DATABASE_URL` configured.
- [x] Django-to-Go parser integration suite: 97 passed.
- [x] ETL integration suite: 1 passed.
- [x] Cypress suite: all 6 specs and 123 tests passed, including all feedback
  scenarios and the embedded accessibility tests.
- [x] Pa11y: all 4 pages passed with zero errors, using installed Chrome via
  `PUPPETEER_EXECUTABLE_PATH`.

Browser tests used the current branch's frontend and a fresh local backend
database because the existing local database contained schema changes from
another branch. Integration suites also used isolated databases. Temporary
services and databases were removed after verification.

The frontend tests cover login-dependent visibility, hiding open forms and upload
widgets on logout, anonymous payloads, pending POST/PATCH requests, duplicate
clicks and keyboard shortcuts, failures, and retries. The backend tests cover
unauthenticated requests, every unapproved status, inactive accounts, missing
roles, approved users, and creating/updating anonymous feedback.

## Manual checks remaining

- [ ] Visit `/` while signed out. Confirm there is no Give Feedback button,
  feedback modal, or upload feedback widget.
- [ ] Sign in with an approved Login.gov account, then repeat with an approved
  AMS account. Confirm Give Feedback opens the form.
- [ ] Use an account awaiting approval. Confirm feedback controls are hidden.
- [ ] Select a rating and submit a comment. Confirm the thank-you message appears
  and the stored feedback belongs to the signed-in user.
- [ ] Repeat with Send anonymously selected before choosing a rating, and again
  by selecting it after the rating save. Confirm the resulting feedback has
  `anonymous=true` and `user=null`.
- [ ] Throttle requests. Confirm Send Feedback is disabled during both rating
  saves and final submission, and repeated clicks or Cmd/Ctrl+Enter do not send
  overlapping requests. Repeat in an upload feedback widget.
- [ ] Fail a feedback request in the general modal. Confirm the button becomes
  enabled, the entered feedback remains, and retry succeeds.
- [ ] Log out with feedback open. Confirm the form disappears.

The full testing checklist remains incomplete until the unchecked items pass.
