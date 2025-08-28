---
description: July 2, 2025 - July 15, 2025
---

# Sprint 129 Summary

## Summary

### Highlights

During this sprint, the team focused on equipping our teams with valuable continuous user research tools, conducting user research for in-app error reporting and replacement of fTANF, improving user access management for FRA data submissions, and preparing Grafana for DIGIT use. These highlights included:

**Continuous User Research & Feedback Loops:**

* Introduced a persistent, general-purpose feedback button and modal to collect anonymous or attributed user input.

**Enabling Secure Data Access for DIGIT via Grafana:**

* Updated Postgres users and roles across Grafana.
* Laid the groundwork for centralizing and automating secret storage via Vault.

**FRA Post-MVP Enhancements:**

* Improved user access management by replacing a backend FRA feature flag with a user-declared permission via the Request Access form.

**FTANF Replacement:**

* Clarified functional requirements and surfaced system constraints for FTANF replacement through detailed process mapping.

**Operations & Maintenance:**

* Improved performance and scalability by storing pre-generated XLS error reports in S3 during parsing.
* Ensured that audit logs in the Django Admin Console accurately link to the associated data file uploads.
* Strengthened pre-QASP testing by generating supporting tickets and documentation to improve end-to-end testing.
* Implemented auto formatting in code to enforce consistent code style.
* Improved system resilience and usability by allowing users to submit data in various formats (e.g., UTF-16).

**User Experience Enhancements:**

* Ensured users can quickly identify and resolve program-type mismatches without mistaking them for formatting errors.
* Improved clarity and reduces user confusion by explicitly stating that the validation applies to the _total_ benefit amount.

## Product Roadmap Progress&#x20;

{% hint style="info" %}
For more detailed information on task progress, please visit the [overall roadmap](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/timeline) for these epics.
{% endhint %}

* Application Health Monitoring | <mark style="color:red;">**ON HOLD**</mark> | Progress: 89% <mark style="color:green;">**(+2%)**</mark> | Estimated Completion Date: TBD
  * <mark style="color:purple;">**Note:**</mark> All work has been completed, while we wait for Sentry to be funded.
* Continuous User Research & Feedback Loops | <mark style="color:green;">**ON TRACK**</mark> | Progress: 82% <mark style="color:green;">**(+2%)**</mark> | Estimated Completion Date: September 23, 2025
* Enabling Secure Data Access for DIGIT in Grafana | <mark style="color:green;">**ON TRACK**</mark> | Progress: 90% <mark style="color:green;">**(+9%)**</mark> | Estimated Completion Date: August 12, 2025
  * <mark style="color:purple;">**Note:**</mark>  This epic encapsulates has not yet been finalized, as there are additional items that may impact scope (e.g., data retention strategy). Thus, timelines and progress percentage are subject to change.
* FRA Post-MVP Enhancements | <mark style="color:green;">**ON TRACK**</mark> | Progress: 60% <mark style="color:green;">**(+19%)**</mark> | Estimated Completion Date: September 23, 2025
* fTANF Replacement - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 38% <mark style="color:green;">**(+4%)**</mark> | Estimated Completion Date: December 16, 2025
* In-App Error Reporting - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 25% <mark style="color:green;">**(+5%)**</mark> | Estimated Completion Date: February 10, 2026
* Regional Staff TDP Access & Onboarding | <mark style="color:red;">**ON HOLD**</mark> | Progress: 38% <mark style="color:red;">**(-9%)**</mark> | Estimated Completion Date: TBD
  * <mark style="color:purple;">**Note:**</mark>  Due to some of the unforeseen changes in HHS staffing, this epic is on pause until further notice.

## Tasks

### Continuous User Feedback & Research Loops

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/5071">#5071</a> - Implement general feedback modal in TDP frontend</td><td>Introduces a persistent, general-purpose feedback button and modal to collect anonymous or attributed user input across the TDP frontend, enabling proactive insight gathering and continuous product improvement.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5072">#5072</a> - Implement contextual feedback modal on data file submission</td><td>Adds contextual, post-submission feedback prompts to Data Files pages, enabling real-time, targeted insights that improve usability, inform prioritization, and advance the platform’s Continuous Feedback Loops initiative.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### Enabling Secure Data Access for DIGIT in Grafana

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3580">#3580</a> - Create PostgreSQL users, roles, and permissions based on privilege mapping</td><td>Strengthens data security by enforcing least-privilege access and preventing unauthorized exposure of sensitive information.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4795">#4795</a> -  Explore Vault integration for credential rotation</td><td>Lays the groundwork for centralized, automated secrets management that enhances security, reduces operational overhead, and aligns with long-term DevSecOps goals across the platform.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4796">#4796</a> - Configure Vault for managing DB credentials</td><td>Strengthens security, enables automated secret rotation, and aligns infrastructure with DevSecOps best practices.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5056">#5056</a> - Design user training materials for DIGIT Grafana Access</td><td>Scopes and delivers user-friendly Grafana training materials tailored for DIGIT users, enabling secure, effective dashboard use while promoting adoption, self-sufficiency, and standardized data practices across the TDP platform.</td><td><mark style="color:orange;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5175">#5175</a> - Limit DIGIT Grafana access to required dashboards</td><td>Ensures DIGIT users have access only to necessary dashboards and tabs, reinforcing least privilege access, protecting environment-specific data, and streamlining their experience by reducing clutter and exposure to non-essential or sensitive operational tools.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### FRA Post-MVP Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4972">#4972</a> - Migrate FRA access from feature flag to user permission on Request Access page</td><td>Improves user access management by replacing a backend FRA feature flag with a user-declared permission via the Request Access form, enabling clearer onboarding, better scalability, and role-specific access logic for STTs, Tribes, and Regional staff.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4974">#4974</a> - Implement admin review workflow for user change requests</td><td>Introduces an auditable workflow for user-initiated profile and access change requests, improving self-service, administrative oversight, and compliance as the platform scales.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4882">#4882 </a>- Handle multi-sheet XLSX files and populate total errors on FRA validation</td><td>Ensures users receive accurate validation results and meaningful error counts, reducing frustration, preventing silent failures, and enabling smoother resubmissions—all of which improve system trust and overall file validation reliability.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### fTANF Replacement

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://github.com/raft-tech/TANF-app/issues/5002">#5002</a> - Develop fTANF replacement MVP process map(s)</td><td>Clarifies functional requirements, surfaces system constraints, and enables more informed design ideation and feasibility discussions for an MVP solution.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr></tbody></table>

### In-App Error Reporting

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4567">#4567</a> - Ideate on designs for in-app error reporting interface</td><td>Ideates on designs to empower users to independently understand and resolve data submission issues faster by providing clear, centralized, and actionable error visibility, reducing reliance on support channels and improving user confidence and task completion within TDP.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Operations & Maintenance

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3237">#3237</a> - Store error reports in S3</td><td>Improves performance and scalability by storing pre-generated XLS error reports in S3 during parsing, eliminating redundant processing and enabling faster, more consistent downloads for users.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://github.com/raft-tech/TANF-app/issues/5115">#5115</a> - Generate Integration Testing Plans, Designs, and Tickets</td><td>Strengthens pre-QASP testing by generating supporting tickets and documentation to catch defects earlier, reducing churn during QA, supporting compliance, and improving release readiness across teams.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4338">#4338</a> - Bug: LogEntry Object Column Links Broken for File Uploads</td><td>Ensures that audit logs in the Django Admin Console accurately link to the associated data file uploads, improving admin usability, reducing confusion during investigations or audits, and maintaining the integrity of system traceability.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3494">#3494</a> - Implement auto formatting with Black and isort for code consistency</td><td>Reduces manual effort, enforce consistent code style, and minimize formatting-related merge conflicts—ultimately improving code quality, review efficiency, and long-term maintainability for the backend team.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3612">#3612</a> - Add encoding support to extract year/quarter from non-UTF-8 files</td><td>Improves system resilience and usability by allowing users to submit data in various formats (e.g., UTF-16), reducing failed submissions and manual troubleshooting while ensuring accurate year/quarter extraction for all valid files.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4904">#4904</a> - Bug: Reparse action fails on latest territory files</td><td>Ensures that all valid submissions—regardless of source—can be reliably reprocessed, supporting data integrity, enabling accurate auditing, and preventing operational bottlenecks in file validation workflows.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2736">#2736</a> - Investigate solutions for handling identity conflicts with re-created login.gov accounts</td><td>Tickets following investigations will reduce user lockouts, eliminate risky manual account deletions, and preserve data integrity—ultimately improving system reliability, user experience, and long-term maintainability of identity management in TDP.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### User Experience Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4916">#4916</a> - Update TANF/SSP file upload validation to detect incorrect program type</td><td>Ensures users can quickly identify and resolve program-type mismatches without mistaking them for formatting errors, reducing support burden and enhancing data submission accuracy.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4929">#4929</a> - Update error message for missing benefits total</td><td>Improves clarity and reduces user confusion by explicitly stating that the validation applies to the <em>total</em> benefit amount, enabling faster issue resolution, minimizing support needs, and supporting accurate, compliant TANF submissions.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5143">#5143</a> - Allow files with no records to be accepted</td><td>Ensures accurate handling of legitimate "no data to report" scenarios, reduces false rejections, and improves trust in the system's ability to reflect real-world program activity.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>
