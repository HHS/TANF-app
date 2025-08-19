---
description: July 16, 2025 - July 29, 2025
---

# Sprint 130 Summary

## Summary

### Highlights

During this sprint, the team focused on equipping our teams with valuable continuous user research tools, conducting user research for in-app error reporting and centralization of feedback reports, and preparing Grafana for DIGIT use. These highlights included:

**Centralized Feedback Reports in TDP - Foundational Discovery:**

* Defined a user-centered, technically feasible design for centralizing TANF data feedback report distribution and related documentation in TDP.

**Continuous User Research & Feedback Loops:**

* Added contextual, post-submission feedback prompts to Data Files pages.

**Enabling Secure Data Access for DIGIT via Grafana:**

* Ensured DIGIT users have access only to necessary dashboards and tabs.

**FRA Post-MVP Enhancements:**

* Ensured users receive accurate validation results and meaningful error counts.

**In-App Error Reporting:**

* Ideated on designs to empower users to independently understand and resolve data submission issues faster.

**Operations & Maintenance:**

* Ensured that all valid submissions—regardless of source—can be reliably reprocessed.
* Conducted investigation to reduce user lockouts, eliminate risky manual account deletions, and preserve data integrity.

**User Experience Enhancements:**

* Ensured accurate handling of legitimate "no data to report" scenarios, reduces false rejections, and improves trust in the system's ability to reflect real-world program activity.

## Product Roadmap Progress&#x20;

{% hint style="info" %}
For more detailed information on task progress, please visit the [overall roadmap](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/timeline) for these epics.
{% endhint %}

* Application Health Monitoring | <mark style="color:green;">**ON TRACK**</mark> | Progress: 91% <mark style="color:green;">**(+2%)**</mark> | Estimated Completion Date: September 23, 2025
* Centralizing Feedback Reports in TDP - Foundational Discovery | <mark style="color:green;">**ON TRACK**</mark> | Progress: 59% <mark style="color:green;">**(+59%)**</mark> | Estimated Completion Date: September 23, 2025
* Continuous User Research & Feedback Loops | <mark style="color:green;">**ON TRACK**</mark> | Progress: 91% <mark style="color:green;">**(+6%)**</mark> | Estimated Completion Date: September 23, 2025
* Enabling Secure Data Access for DIGIT in Grafana | <mark style="color:green;">**ON TRACK**</mark> | Progress: 92% <mark style="color:green;">**(+2%)**</mark> | Estimated Completion Date: August 12, 2025
  * <mark style="color:purple;">**Note:**</mark>  This epic encapsulates has not yet been finalized, as there are additional items that may impact scope (e.g., data retention strategy). Thus, timelines and progress percentage are subject to change.
* FRA Post-MVP Enhancements | <mark style="color:green;">**ON TRACK**</mark> | Progress: 72% <mark style="color:green;">**(+12%)**</mark> | Estimated Completion Date: September 23, 2025
* fTANF Replacement - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 38% <mark style="color:yellow;">**(+0%)**</mark> | Estimated Completion Date: January 27, 2026
* In-App Error Reporting - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 32% <mark style="color:green;">**(+7%)**</mark> | Estimated Completion Date: February 10, 2026
* Regional Staff TDP Access & Onboarding | <mark style="color:red;">**ON HOLD**</mark> | Progress: 38% <mark style="color:red;">**(-9%)**</mark> | Estimated Completion Date: TBD
  * <mark style="color:purple;">**Note:**</mark>  Due to some of the unforeseen changes in HHS staffing, this epic is on pause until further notice.

## Tasks

### Centralizing Feedback Reports in TDP - Foundational Discovery

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5041">#5041</a> - Conduct foundational discovery for centralized TANF feedback reports &#x26; KC integration</td><td>Defines a user-centered, technically feasible design for centralizing TANF data feedback report distribution and related documentation in TDP, reducing manual effort, improving secure access, and laying the groundwork for scalable, maintainable workflows across all user groups.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr></tbody></table>

### Continuous User Feedback & Research Loops

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5072">#5072</a> - Implement contextual feedback modal on data file submission</td><td>Adds contextual, post-submission feedback prompts to Data Files pages, enabling real-time, targeted insights that improve usability, inform prioritization, and advance the platform’s Continuous Feedback Loops initiative.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr></tbody></table>

### Enabling Secure Data Access for DIGIT in Grafana

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5175">#5175</a> - Limit DIGIT Grafana access to required dashboards</td><td>Ensures DIGIT users have access only to necessary dashboards and tabs, reinforcing least privilege access, protecting environment-specific data, and streamlining their experience by reducing clutter and exposure to non-essential or sensitive operational tools.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5056">#5056</a> - Design user training materials for DIGIT Grafana Access</td><td>Scopes and delivers user-friendly Grafana training materials tailored for DIGIT users, enabling secure, effective dashboard use while promoting adoption, self-sufficiency, and standardized data practices across the TDP platform.</td><td><mark style="color:orange;"><strong>QASP REVIEW</strong></mark></td></tr></tbody></table>

### FRA Post-MVP Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4882">#4882 </a>- Handle multi-sheet XLSX files and populate total errors on FRA validation</td><td>Ensures users receive accurate validation results and meaningful error counts, reducing frustration, preventing silent failures, and enabling smoother resubmissions—all of which improve system trust and overall file validation reliability.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4974">#4974</a> - Implement admin review workflow for user change requests</td><td>Introduces an auditable workflow for user-initiated profile and access change requests, improving self-service, administrative oversight, and compliance as the platform scales.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4973">#4973</a> - Implement Edit Profile page with shared Request Access logic</td><td>Delivers a redesigned, self-service “Edit Profile” experience that aligns with the latest design system, reuses proven Request Access components, and enables users to easily request accurate profile updates while reducing support workload and improving data quality.</td><td><mark style="color:yellow;"><strong>IN PROGRES &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### In-App Error Reporting

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4567">#4567</a> - Ideate on designs for in-app error reporting interface</td><td>Ideates on designs to empower users to independently understand and resolve data submission issues faster by providing clear, centralized, and actionable error visibility, reducing reliance on support channels and improving user confidence and task completion within TDP.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4991">#4991</a> - Pre-planning for next phases of in-app error reporting</td><td>Defines the scope, testing approach, and measurable success criteria for concept testing the in-app error reporting interface, ensuring we can evaluate its impact on user comprehension, resolution speed, and support demand ahead of the pilot launch.</td><td><mark style="color:yellow;"><strong>IN PROGRES &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Operations & Maintenance

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4904">#4904</a> - Bug: Reparse action fails on latest territory files</td><td>Ensures that all valid submissions—regardless of source—can be reliably reprocessed, supporting data integrity, enabling accurate auditing, and preventing operational bottlenecks in file validation workflows.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2736">#2736</a> - Investigate solutions for handling identity conflicts with re-created login.gov accounts</td><td>Conducted investigation to reduce user lockouts, eliminate risky manual account deletions, and preserve data integrity—ultimately improving system reliability, user experience, and long-term maintainability of identity management in TDP.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3432">#3432</a> - Update Alertmanager Inhibition Rules</td><td>Streamlines alerting by suppressing redundant <code>UpTime</code> notifications during <code>AppDown</code> events and reducing their frequency, minimizing alert fatigue and ensuring focus stays on actionable issues.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4908">#4908</a> - Bug: File input displays multiple files after error state</td><td>Ensures the file input resets to show only the most recently selected file after an upload error, preventing confusion and giving users clear confirmation of what will be submitted.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### User Experience Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5143">#5143</a> - Allow files with no records to be accepted</td><td>Ensures accurate handling of legitimate "no data to report" scenarios, reduces false rejections, and improves trust in the system's ability to reflect real-world program activity.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr></tbody></table>
