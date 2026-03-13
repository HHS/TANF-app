---
name: Release Tracker
about: Track the release handoff to OFA, staging validation, and production deployment.
title: Release Tracker vX.X.X
labels: ''
assignees: ''

---

# Release Tracker Issue Template

**TITLE:** Release vX.X.X

**CONTENT:**

### 🔗 Included Pull Requests (Dev Team)
*List the PRs included in this release. **Testing instructions for each feature must be located within these linked PRs.***
* #XXX - [Feature/Bugfix Title]
* #XXX - [Feature/Bugfix Title]

### ➡️ URL of GitHub Release Tag:
https://github.com/raft-tech/TANF-app/releases/tag/vX.X.X

---

### 📦 1. Preparation & Handoff (Dev / UX / PM)
*Ensuring the release branch is ready and documented before ACF takes over.*

- [ ] **Release Tagged:** `develop` branch tagged with the new release version.
- [ ] **Release Branch Created:** Branch cut from `develop`.
- [ ] **PR Opened to Staging:** PR opened from the release branch to `HHS:main`.
- [ ] **Testing Instructions Verified:** All linked PRs contain clear testing instructions for ACF validation.
- [ ] **UX/Documentation Check:** UX team has reviewed the PRs, confirmed user-facing changes, and started drafting Release Notes and Knowledge Center guidance.
- [ ] **Migration Flag:** Does this release include a database migration? **[Yes / No]** *(If Yes, rollback from production will be highly complex).*
- [ ] **Handoff Complete:** Issue assigned to @[Alex_username] for Staging validation.

---

### 🧪 2. Staging Validation & QASP (ACF / Alex)
*Tracking the status once ACF takes over deployment and testing.*

- [ ] **Staging Cleared:** Team notified that Staging is about to be updated/restarted.
- [ ] **Deployed to Staging:** PR merged and deployed to the Staging environment.
- [ ] **Feature Validation:** Testing instructions from the linked PRs have been executed and passed.
- [ ] **Regression Validation:** Core workflows (login, submissions, data integrity, etc.) remain functional.

**🐛 Bug Tracking Protocol (If issues are found in Staging):**
1. **Non-Dev Team:** Add a comment on this issue describing the bug/unexpected behavior.
2. **Dev Team:** Review the comment, investigate root cause, and open a formal GitHub Issue.
3. **Triage Decision:**
    * *Revert:* If isolated to a new feature, revert the PR out of the release candidate.
    * *Hotfix:* Warranted **only if** the bug blocks the release entirely AND the production release is needed ASAP. (Dev cuts hotfix PR against the release branch -> merged to `HHS:main` for re-testing).

- [ ] **Documentation Finalized:** UX team confirms all Release Notes and Knowledge Center updates are finalized and ready for launch.

---

### 🚦 3. Production-Ready Sign-Off
- [ ] ACF/Alex confirms all PRs are validated, no blocking bugs exist, documentation is finalized, and the release is approved for production deployment.

---

### 🛟 4. Rollback & Contingency Reference
*Review before production deployment.*

* **Pipeline/CircleCI Failure:** Retry the pipeline. If it fails again, requires a hotfix to unblock.
* **Missing Config/Secrets (App crashes on boot):** Do not rollback. ACF updates environment variables in the production console and restarts the app.
* **Third-Party API Blocked in Prod:** Dev provides an emergency hotfix to hide the broken UI component.
* **Performance/Database Lockup Under Load:** Dev writes an emergency hotfix for the offending query.
* **Critical Regression Post-Deploy:**
    * *No migrations in release:* Rollback the deployment to the previous stable version.
    * *Migrations in release:* Rollback is generally not possible; requires an emergency hotfix.

---

### 🚀 5. Production Deployment (ACF / Alex)
*The final deployment executed by ACF.*

- [ ] **Maintenance Mode:** Alex has enabled the maintenance page to ensure users are out of the system.
- [ ] **Deployed to Prod:** PR opened and merged to `HHS:master`, triggering deployment.
- [ ] **Post-Launch Verification:** Quick check that the production environment is stable post-deploy, and the maintenance page is deactivated.

---

### 📢 6. Post-Release Communication (PM / UX / ACF)
*Closing the loop with users and stakeholders.*

- [ ] **Release Notes Published:** (UX team) Plain-language, user-facing release notes and Knowledge Center guidance have been published.
- [ ] **Stakeholders Notified:** (ACF) Any required external communication regarding the new version has been sent.
- [ ] **Close this Issue:** (ACF / PM) The release is fully deployed and stable.
