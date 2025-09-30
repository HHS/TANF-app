---
description: July 30, 2025 - August 12, 2025
---

# Sprint 131 Summary

## Summary

### Highlights

During this sprint, the team focused on equipping our teams with valuable continuous user research tools, conducting user research for in-app error reporting and centralization of feedback reports, and preparing Grafana for DIGIT use. These highlights included:

**Centralized Feedback Reports in TDP - Foundational Discovery:**

* Captured critical insights from Yun to inform how feedback report workflows are centralized in TDP.

**Enabling Secure Data Access for DIGIT via Grafana:**

* Delivered user-friendly Grafana training materials tailored for DIGIT users.
* Ensured Grafana dashboards only surfaces accurate, non-null records.

**In-App Error Reporting:**

* Defines the scope, testing approach, and measurable success criteria for concept testing the in-app error reporting interface.

**Operations & Maintenance:**

* Streamlined alerting by suppressing redundant `UpTime` notifications during `AppDown` events and reducing their frequency.
* Ensured the file input resets to show only the most recently selected file after an upload error.
* Delivered automated Cypress end-to-end test coverage for TANF, SSP, and Tribal data file submissions.

## Product Roadmap Progress&#x20;

{% hint style="info" %}
For more detailed information on task progress, please visit the [overall roadmap](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/timeline) for these epics.
{% endhint %}

* Application Health Monitoring | <mark style="color:green;">**ON TRACK**</mark> | Progress: 92% <mark style="color:green;">**(+1%)**</mark> | Estimated Completion Date: September 23, 2025
* Centralizing Feedback Reports in TDP - Foundational Discovery | <mark style="color:green;">**ON TRACK**</mark> | Progress: 68% <mark style="color:green;">**(+9%)**</mark> | Estimated Completion Date: September 23, 2025
* Continuous User Research & Feedback Loops | <mark style="color:green;">**ON TRACK**</mark> | Progress: 91% <mark style="color:orange;">**(+0%)**</mark> | Estimated Completion Date: September 23, 2025
* Enabling Secure Data Access for DIGIT in Grafana | <mark style="color:orange;">**AT RISK**</mark> | Progress: 94% <mark style="color:green;">**(+2%)**</mark> | Estimated Completion Date: August 26, 2025
  * <mark style="color:purple;">**Note:**</mark>  The timeline has been slightly extended while we work to bump resources in Grafana.
* FRA Post-MVP Enhancements | <mark style="color:green;">**ON TRACK**</mark> | Progress: 79% <mark style="color:green;">**(+7%)**</mark> | Estimated Completion Date: September 23, 2025
* fTANF Replacement - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 38% <mark style="color:yellow;">**(+0%)**</mark> | Estimated Completion Date: January 27, 2026
* In-App Error Reporting - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 42% <mark style="color:green;">**(+10%)**</mark> | Estimated Completion Date: February 10, 2026
* Regional Staff TDP Access & Onboarding | <mark style="color:red;">**ON HOLD**</mark> | Progress: 38% <mark style="color:red;">**(-9%)**</mark> | Estimated Completion Date: TBD
  * <mark style="color:purple;">**Note:**</mark>  Due to some of the unforeseen changes in HHS staffing, this epic is on pause until further notice.

## Tasks

### Centralizing Feedback Reports in TDP - Foundational Discovery

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5224">#5224</a> - Conduct research session with Yun on centralizing feedback reports in TDP</td><td>Ensures we capture critical insights from Yun to inform how feedback report workflows are centralized in TDP, enabling a more streamlined and well-scoped MVP versus post-MVP roadmap.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5222">#5222</a> - Design MVP interface for centralized feedback reports</td><td>Delivers dev-ready designs for in-app and email delivery of feedback reports, enabling a shift from manual email distribution to a streamlined, accessible, and integrated experience within TDP.</td><td><mark style="color:yellow;"><strong>IN PROGRES &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Continuous User Feedback & Research Loops

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5197">#5197</a> - Add metadata to feedback submissions to support contextual analysis + a11y fixes</td><td>Adds rich, structured metadata to every feedback submission (page, type, widget, file refs), enabling precise triage, better filtering and analysis, and faster, data-driven UX improvements.</td><td><mark style="color:yellow;"><strong>IN PROGRES &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Enabling Secure Data Access for DIGIT in Grafana

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5056">#5056</a> - Design user training materials for DIGIT Grafana Access</td><td>Scopes and delivers user-friendly Grafana training materials tailored for DIGIT users, enabling secure, effective dashboard use while promoting adoption, self-sufficiency, and standardized data practices across the TDP platform.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5267">#5267 </a>- Handle Null Values in Custom Where Clauses</td><td>Ensures Grafana dashboards only surface accurate, non-null records, improving data reliability, reducing noise, and enabling stakeholders to make clearer, more actionable decisions.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5269">#5269</a> - Bump Grafana memory in prod by 4GB to support 1.5M record visualizations</td><td>Enables reliable visualization of datasets up to 1.5M records, eliminating OOM failures and accelerating troubleshooting for large TANF/SSP submissions.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr></tbody></table>

### FRA Post-MVP Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4974">#4974</a> - Implement admin review workflow for user change requests</td><td>Introduces an auditable workflow for user-initiated profile and access change requests, improving self-service, administrative oversight, and compliance as the platform scales.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4973">#4973</a> - Implement Edit Profile page with shared Request Access logic</td><td>Delivers a redesigned, self-service “Edit Profile” experience that aligns with the latest design system, reuses proven Request Access components, and enables users to easily request accurate profile updates while reducing support workload and improving data quality.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3485">#3485</a> - Design FRA successful processing email template</td><td>Delivers an accessible, USWDS-compliant FRA success notification email that gives users clear, trustworthy confirmation of processed submissions, reduces uncertainty, and aligns communications with our established design system.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### In-App Error Reporting

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4991">#4991</a> - Pre-planning for next phases of in-app error reporting</td><td>Defines the scope, testing approach, and measurable success criteria for concept testing the in-app error reporting interface, ensuring we can evaluate its impact on user comprehension, resolution speed, and support demand ahead of the pilot launch.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4753">#4753</a> - Develop concepts for testing</td><td>Delivers structured, testable design concepts for in-app error reporting, enabling usability testing that validates workflows, improves user understanding, and guides more effective error resolution experiences.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### Operations & Maintenance

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3432">#3432</a> - Update Alertmanager Inhibition Rules</td><td>Streamlines alerting by suppressing redundant <code>UpTime</code> notifications during <code>AppDown</code> events and reducing their frequency, minimizing alert fatigue and ensuring focus stays on actionable issues.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4908">#4908</a> - Bug: File input displays multiple files after error state</td><td>Ensures the file input resets to show only the most recently selected file after an upload error, preventing confusion and giving users clear confirmation of what will be submitted.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5167">#5167 </a>- Develop E2E tests for data analyst submissions (TANF/SSP Data Files)</td><td>Delivers automated Cypress end-to-end test coverage for TANF, SSP, and Tribal data file submissions, ensuring analysts can successfully upload, validate, and track files while catching errors early and safeguarding compliance with federal reporting requirements.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5168">#5168</a> - Develop E2E tests for FRA data file submissions</td><td>Provides automated, role-aware Cypress tests for FRA data file submissions that verify permissions and workflows end-to-end, reduce regressions, and strengthen compliance and confidence in the platform.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5226">#5226</a> - Develop E2E tests for non-data analyst submissions (TANF/SSP Data Files)</td><td>Delivers automated, role-based Cypress tests that verify TANF/SSP access controls end-to-end, reducing regressions, safeguarding compliance and data security, and increasing confidence in the platform’s permissions model.</td><td><mark style="color:yellow;"><strong>IN PROGRES &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5166">#5166</a> - Develop E2E tests for login and account management</td><td>Delivers automated end-to-end coverage of login and account approval flows, ensuring secure, role-correct onboarding, preventing access misconfigurations, and increasing confidence that users only see features appropriate to their permissions.</td><td><mark style="color:yellow;"><strong>IN PROGRES &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### User Experience Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3251">#3251</a> - Update email templates for STT data submissions re: status and error guidance</td><td>Ensures STTs receive clear, action-oriented submission emails that highlight errors early, reduce confusion, and drive timely corrections, ultimately improving data quality and compliance.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>
