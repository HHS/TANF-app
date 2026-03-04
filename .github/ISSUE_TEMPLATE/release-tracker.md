---
name: Release Tracker
about: Track the release handoff to OFA, staging validation, and production deployment.
title: Release Tracker vX.X.X
labels: ''
assignees: ''

---

#Release Tracker issue template
**TITLE**: Release vX.X.X
**CONTENT**:

## ➡️ URL of github release tag
https://github.com/raft-tech/TANF-app/releases/tag/vX.X.X

## 🔗 Included Pull Requests (Dev Team)
*List the PRs included in this release. **Testing instructions for each feature must be located within these linked PRs.***
* #XXX - [Feature/Bugfix Title]
* #XXX - [Feature/Bugfix Title]

---

## 📦 1. Preparation & Handoff (Dev Team)
*Ensuring the release branch is ready for ACF.*

- [ ] **Release Tagged:** `develop` branch tagged with the new release version.
- [ ] **Release Branch Created:** Branch cut from `develop`.
- [ ] **PR Opened to Staging:** PR opened from the release branch to `HHS:main`.
- [ ] **Testing Instructions Verified:** All linked PRs above contain clear testing instructions for OFA validation.
- [ ] **Handoff Complete:** Alex/ACF notified that the PR to `HHS:main` is ready for review and merge.

---

## 🧪 2. Staging Validation & QASP (ACF / Alex)
*Tracking the status once OFA takes over deployment and testing.*

- [ ] **Merged to Staging:** PR to `HHS:main` merged (Auto-deployed to Staging).
- [ ] **Feature Validation:** All testing instructions from the linked PRs above have been executed and passed.
- [ ] **Regression Validation:** Core workflows (login, submissions, data integrity, etc.) remain functional and unbroken.

**🐛 Bug Tracking Protocol (If issues are found in Staging):**
1. Log a new GitHub Issue detailing the bug.
2. Link that bug as a comment in this Release tracker issue.
3. Dev Team will cut a hotfix PR against the `release` branch.
4. Hotfix PR is merged to `HHS:main` for re-testing.

- [ ] **🚦 Production-Ready Sign-Off:** ACF/Alex confirms all PRs are validated, no blocking bugs exist, and the release is approved for production deployment.

---

## 🚀 3. Production Deployment (ACF / Alex)
*The final deployment executed by ACF.*

- [ ] **PR Opened to Prod:** Alex has opened a PR to `HHS:master`.
- [ ] **Merged to Prod:** Alex has merged to `HHS:master` (Auto-deployed to Production).
- [ ] **Post-Launch Verification:** Quick check that the production environment is stable post-deploy.

---

## 📢 4. Post-Release Communication (PM / UX / ACF)
*Closing the loop with users and stakeholders.*

- [ ] **Release Notes Published:** (UX team) Plain-language, user-facing release notes posted to Knowledge Center.
- [ ] **Stakeholders Notified:** (ACF) Any required external communication regarding the new version has been sent.
- [ ] **Close this Issue:** (ACF / PM) The release is fully deployed and stable.
