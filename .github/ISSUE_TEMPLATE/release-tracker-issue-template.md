---
name: Release Tracker
about: Track the release handoff to OFA, staging validation, and production deployment.
title: Release Tracker vX.X.X
labels: ''
assignees: 'reitermb,victoriaatraft,elipe17,kennymcnett'
---

## 🔗 1. Included Pull Requests (Dev Team)
Link to GitHub release tag:
https://github.com/raft-tech/TANF-app/releases/tag/vX.X.X

###  Users will see a change:
- [ ] #XXX - Title

### No visible change for end users:
- [ ] #XXX - Title

---

## 📦 2. Preparation (Dev)
- [ ] **Release Tagged:** `develop` branch tagged with the new release version.
- [ ] **Release Branch Created:** Branch cut from `develop`.
- [ ] **PR Opened to Staging:** PR opened from the release branch to `HHS:main`.
- [ ] **Testing Instructions Verified:** All linked PRs contain clear testing instructions for ACF validation.

---

## 📄 3. Documentation (UX)

### Release notes
- [ ] Yes, there will be release notes. See sub-issues of this tracker for details.
- [ ] No release notes.

### Knowledge Center updates
- [ ] Yes, there will be Knowledge Center updates. see sub-issues of this tracker for details.
- [ ] No Knowledge Center updates.

---

## ✈️ 4. Pre-flight (Dev)
### Database Migration
 - [ ] No database migration.
 - [ ] Yes, this release includes a database migration. Rollback from production will be highly complex.

### Base image updates
- [ ] Does NOT require base image updates.
- [ ] Requires base image updates.
  - [ ] Re-tag `ghcr.io/raft-tech/tdp-frontend-base:vX.X.X` for the HHS GHCR instance.
  - [ ] Re-tag `ghcr.io/raft-tech/tdp-backend-base:vX.X.X` for the HHS GHCR instance.

### HHS CircleCI updates
- [ ] Does NOT Require HHS CircleCI config updates.
- [ ] Requires HHS CircleCI config updates.
  - [ ] (add checklist of updates here)

### PLG Deployment
- [ ] Does NOT require PLG deployment.
- [ ] Requires PLG deployment.

---

## 🧪 5. Staging & QASP (ACF)

- [ ] **Pre-flight:** Reviewed and executed pre-flight actions.
- [ ] **Staging Cleared:** Team notified that Staging is about to be updated/restarted.
- [ ] **Deployed to Staging:** PR merged and deployed to the Staging environment.
- [ ] **Feature Validation:** Testing instructions from the linked PRs have been executed and passed.
- [ ] **Regression Validation:** Core workflows (login, submissions, data integrity, etc.) remain functional.

🪲 _Bug Tracking Protocol (If issues are found in Staging):_
- Non-Dev Team: Add a comment on this issue describing the bug/unexpected behavior.
- Dev Team: Review the comment, investigate root cause, and open a formal GitHub Issue.
- Triage Decision:
    - *Revert:* If isolated to a new feature, revert the PR out of the release candidate.
    - *Hotfix:* Warranted **only if** the bug blocks the release entirely AND the production release is needed ASAP. (Dev cuts hotfix PR against the release branch -> merged to `HHS:main` for re-testing).

---

## 🚦 6. Production-Ready Sign-Off (ACF / UX)

- [ ] All documentation is finalized and ready for launch.
- [ ] All PRs are validated.
- [ ] No blocking bugs exist.
- [ ] **Release is approved for production deployment.**

---

## 🚀 7. Deploy to Production (ACF)

- [ ] **Maintenance Mode ON:** Enabled to ensure users are out of the system.
- [ ] **Deployed to Prod:** PR opened and merged to `HHS:master`, triggering deployment.
- [ ] **Post-Launch Verification:** Quick check that the production environment is stable.
- [ ] **Maintenance Mode OFF:** Maintenance page is deactivated.

🛟 _Rollback & Contingency Reference_
- Pipeline/CircleCI Failure: Retry the pipeline. If it fails again, requires a hotfix to unblock.
- Missing Config/Secrets (App crashes on boot): Do not rollback. ACF updates environment variables in the production console and restarts the app.
- Third-Party API Blocked in Prod: Dev provides an emergency hotfix to hide the broken UI component.
- Performance/Database Lockup Under Load: Dev writes an emergency hotfix for the offending query.
- Critical Regression Post-Deploy:
    - No migrations in release: Rollback the deployment to the previous stable version.
    - Migrations in release: Rollback is generally not possible; requires an emergency hotfix.

---

## 📢 8. Post-Release Communication (UX / ACF / PM)

- [ ] **Public Documentation Published: (UX)** Release notes and Knowledge Center guidance have been published. Related sub-issues are closed.
- [ ] **Stakeholders Notified: (ACF)** Required external communication regarding the new version has been sent.
- [ ] **Ready to Close: (ACF / PM)** The release is fully deployed and stable.
