---
description: 04/09/2025 - 04/23/2025
---

# Sprint 123 Summary

## Summary

### Deliverables

In the past sprint, we completed the following deliverables:

* **Delivered FRA Reporting Requirements MVP Deliverable 3: Research, Testing, & UX**, advancing the user-centered foundation for FRA submission workflows and error reporting. This milestone focused on usability research, prototype testing, and stakeholder-aligned user testing plans—ensuring the next phase of development is informed by real user feedback and accessible, validated experiences.

### Other Highlights

During this sprint, the team focused on enhancing the functionality of the FRA report interface, improving user interaction, and ensuring data security. Other highlights included:

**Application Health Monitoring:**

* Removed unused Elastic and Kibana resources from Cloud.gov.

**FRA Reporting Requirements MVP:**

* Enabled UX to test and validate Regional user flows in a controlled environment.
* Standardized FRA submission and error report filenames.

**Operations & Maintenance:**

* Ensured the Mississippi Band of Choctaw Indians (and another tribe) can fully participate in Tribal TANF reporting.

**User Experience Enhancements:**

* Ensured faster, more accurate issue diagnosis for data submitters and internal teams through improved error handling for record length issues during submission.

## Product Roadmap Progress&#x20;

{% hint style="info" %}
For more detailed information on task progress, please visit the [overall roadmap](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/timeline) for these epics.
{% endhint %}

* Application Health Monitoring | <mark style="color:green;">**ON TRACK**</mark> | Progress: 74% <mark style="color:green;">**(+7%)**</mark> | Estimated Completion Date: July 29, 2025
  * <mark style="color:purple;">**Note:**</mark>  Integration of the Node exporter was not completed due to constraints with Cloud.gov.
* Enabling Secure Data Access for DIGIT in Grafana | <mark style="color:green;">**ON TRACK**</mark> | Progress: 16% <mark style="color:green;">**(+6%)**</mark> | Estimated Completion Date: August 12, 2025
  * <mark style="color:purple;">**Note:**</mark>  This epic encapsulates new work and has not yet been finalized, as there are additional items that may impact scope. Thus, timelines and progress percentage are subject to change.
* FRA Reporting Requirements MVP | <mark style="color:green;">**ON TRACK**</mark> | Progress: 92% <mark style="color:green;">**(+2%)**</mark> | Estimated Completion Date: May 6, 2025
* fTANF Replacement - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 7% <mark style="color:green;">**(+2%)**</mark> | Estimated Completion Date: November 18, 2025
* Regional Staff TDP Access & Onboarding | <mark style="color:red;">**OFF TRACK**</mark> | Progress: 38% <mark style="color:red;">**(-9%)**</mark> | Estimated Completion Date: November 4, 2025
  * <mark style="color:purple;">**Note:**</mark>  Due to some of the unforeseen changes in HHS staffing, this epic is on pause until further notice.

## Tasks

### Application Health Monitoring

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3255">#3255</a> - Integrate Node exporter for system metrics and alerting</td><td>Provides critical system-level visibility, enabling proactive alerts and faster diagnosis of infrastructure issues that could affect TDP performance and reliability.</td><td><mark style="color:red;"><strong>WILL NOT COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3529">#3529</a> - Remove Elastic and Kibana from cloud.gov and Nginx</td><td>Removes unused Elastic and Kibana resources from Cloud.gov, reducing costs, improving security, and ensuring a more maintainable and efficient infrastructure.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3295">#3295</a> - Associate parsing log files with datafile submissions in DAC</td><td>Improves transparency and traceability, giving OFA users direct access to debugging details and enhancing trust in data processing outcomes.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3258">#3258</a> - Implement Cloud.gov log drain for centralized logging with Promtail and Loki</td><td>Streamlines logging infrastructure, reduces deployment complexity, and ensures scalable, unified access to app logs in Loki.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Enabling Secure Data Access for DIGIT in Grafana

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3579">#3579</a> - Set up Postgres views for all record types</td><td>Enhances data security, supports compliance, and enables safe, efficient access for Grafana and automation workflows without exposing sensitive information.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3422">#3422</a> - Create and configure read-only RDS user for Grafana integration</td><td>Enables secure data exploration and dashboarding for OFA while safeguarding production data from accidental changes.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3472">#3472</a> - Investigate Grafana resource requirements for large exports</td><td>Helps determine whether Grafana can efficiently handle large TANF data exports, identifying potential memory constraints, performance limitations, and cost-effective solutions to meet DIGIT's interim data access needs.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4477">#4477</a> - Explore &#x26; align on structure for continuous feedback sessions on Grafana with DIGIT</td><td>Ensures dashboards evolve to meet real user needs, surface usability issues early, and support a culture of continuous improvement without placing a heavy burden on internal stakeholders.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### FRA Reporting Requirements MVP

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3533">#3533</a> - Set up demo environment for regional staff and FRA MVP testing</td><td>Enables UX to test and validate Regional user flows in a controlled environment, ensuring accurate data access and a smooth user experience ahead of the FRA MVP release.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3556">#3556</a> - Rename FRA uploaded files and error reports to standardized format</td><td>Standardizes FRA submission and error report filenames to align with processing requirements, improve clarity for users, and ensure consistent file handling across the system.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4892">#4892</a> - Bug: File selector doesn't get reset when a file of the same name is provided</td><td>Ensures users can successfully re-upload updated files without needing to rename them, preserving expected workflows, reducing friction during submission, and preventing avoidable validation errors.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4897">#4897</a> - Bug: Rapid clicking of the submit button submits multiple copies of the file</td><td>Ensures accurate submission records, prevents user confusion, and maintains the integrity of the submission history view.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3555">#3555</a> - Bug: File stuck in pending if Decoder.UNKNOWN not handled</td><td>Prevents files from remaining indefinitely in 'Pending' status, improves user feedback, and supports faster issue resolution.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### FRA Post-MVP Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/3488">#3488</a> - Create design for integrating FRA into access request flow</td><td>Streamlines onboarding for states and territories involved in FRA reporting, reduce manual follow-up, and ensure proper access is granted from the start—all while improving clarity and supporting compliance.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### fTANF Replacement - Foundational Research & Concept Validation

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.gitbook.com/s/dohVQ7a9KV4HbM0vkj9d/friendly-names-reparsing-and-parity-review-may-17-2024">#4547</a> - Prepare synthesis on FTANF ahead of research recommendations</td><td>Equips OFA with a shared understanding of user challenges and unmet needs in fTANF, laying the foundation for focused, informed research that supports a thoughtful transition to a modernized solution.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr></tbody></table>

### Operations & Maintenance

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3291">#3291</a> - Add Mississippi Band of Choctaw Indians to tribal TANF system for quarterly reporting</td><td>Ensures the Mississippi Band of Choctaw Indians (and another tribe) can fully participate in Tribal TANF reporting, supporting data submission, access requests, and compliance with federal reporting requirements.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3454">#3454</a> - Remove 0 as a value for Citizenship</td><td>Strengthens data integrity, ensures compliance with updated policy, and prevents inaccurate eligibility data from entering the system.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3498">#3498</a> - Migrate Raft/OFA to GHCR</td><td>Ensures long-term access, organizational control, and alignment with HHS-wide infrastructure standards, reducing dependency on third-party registries.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### Regional Staff TDP Access & Onboarding

_Note: Due to unforeseen changes in staffing, we will be postponing work with regional staff features at this time. This may be picked up at a later date._

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3461">#3461 </a>- Create and facilitate Project Updates meeting for regional staff</td><td>Ensures regional staff are well-informed about their new TDP access, providing them with a clear understanding of key functionalities, a live demonstration, and an opportunity for Q&#x26;A, ultimately supporting a smooth onboarding process.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3523">#3523 </a>- Refine research plan for regional staff MVP onboarding experience</td><td>Ensures user feedback is captured early, guiding design decisions with real-world insights and supporting the creation of a user-centered, effective interface.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3462">#3462</a> - Create and facilitate optional training session for regional staff</td><td>Empowers them to confidently navigate and utilize TDP’s features, fostering engagement, reducing support needs, and ensuring effective use of the platform.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr></tbody></table>

### User Experience Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3561">#3561 </a>- Improve error handling for record length issues in file parsing</td><td>Ensures faster, more accurate issue diagnosis for data submitters and internal teams, reducing confusion, investigation time, and compliance risks.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3557">#3557</a> - Explore error message clarity in identified issue areas</td><td>Lays the groundwork for improving error clarity by investigating confusing messages, identifying actionable fixes, and proposing changes that will help users resolve issues more confidently and independently during data submission.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4632">#4632</a> - Revisit UX strategic roadmap and define team objectives</td><td>Ensures alignment with product goals, strengthens cross-functional collaboration, and empowers the UX team to deliver more consistent, user-centered improvements across TDP.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>
