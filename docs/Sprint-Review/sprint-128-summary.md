---
description: June 18, 2025 - July 1, 2025
---

# Sprint 128 Summary

## Summary

### Highlights

During this sprint, the team focused on improving our application health monitoring stack, conducting equipping our teams with valuable continuous user research tools, and preparing Grafana for DIGIT use. These highlights included:

**Application Health Monitoring:**

* Improved scalability, reliability, and maintainability of TDP’s background task infrastructure.

**Continuous User Research & Feedback Loops:**

* Equipped internal teams with actionable insights into user behavior.
* Enabled secure, structured collection of user feedback within TDP

**Enabling Secure Data Access for DIGIT via Grafana:**

* Improves data integrity across T3 and T7 file views by filtering out malformed records and handling null age calculations gracefully.

## Product Roadmap Progress&#x20;

{% hint style="info" %}
For more detailed information on task progress, please visit the [overall roadmap](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/timeline) for these epics.
{% endhint %}

* Application Health Monitoring | <mark style="color:red;">**OFF TRACK**</mark> | Progress: 89% <mark style="color:green;">**(+2%)**</mark> | Estimated Completion Date: TBD
  * <mark style="color:purple;">**Note:**</mark> Completion of this epic is on hold until Sentry can be funded.
* Continuous User Research & Feedback Loops | <mark style="color:green;">**ON TRACK**</mark> | Progress: 80% <mark style="color:green;">**(+13%)**</mark> | Estimated Completion Date: September 23, 2025
* Enabling Secure Data Access for DIGIT in Grafana | <mark style="color:green;">**ON TRACK**</mark> | Progress: 81% <mark style="color:green;">**(+14%)**</mark> | Estimated Completion Date: August 12, 2025
  * <mark style="color:purple;">**Note:**</mark>  This epic encapsulates has not yet been finalized, as there are additional items that may impact scope (e.g., data retention strategy). Thus, timelines and progress percentage are subject to change.
* FRA Post-MVP Enhancements | <mark style="color:green;">**ON TRACK**</mark> | Progress: 41% <mark style="color:green;">**(+14%)**</mark> | Estimated Completion Date: September 23, 2025
* fTANF Replacement - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 34% <mark style="color:green;">**(+9%)**</mark> | Estimated Completion Date: December 16, 2025
* In-App Error Reporting - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 20% <mark style="color:green;">**(+5%)**</mark> | Estimated Completion Date: February 10, 2026
* Regional Staff TDP Access & Onboarding | <mark style="color:red;">**OFF TRACK**</mark> | Progress: 38% <mark style="color:red;">**(-9%)**</mark> | Estimated Completion Date: November 4, 2025
  * <mark style="color:purple;">**Note:**</mark>  Due to some of the unforeseen changes in HHS staffing, this epic is on pause until further notice.

## Tasks

### Application Health Monitoring

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3336">#3336</a> - Decouple Celery and Redis from backend into separate Cloud.gov services</td><td>Improves scalability, reliability, and maintainability of TDP’s background task infrastructure while aligning with cloud-native best practices.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr></tbody></table>

### Continuous User Feedback & Research Loops

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4789">#4789</a> - Finalize frontend observability dashboard</td><td>Equips internal teams with actionable insights into user behavior, enabling continuous UX and product improvements driven by real-world usage data.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5073">#5073</a> - Create backend endpoint and model for feedback submissions</td><td>Enables secure, structured collection of user feedback within TDP, laying the groundwork for real-time insight generation and data-informed product improvements</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/5071">#5071</a> - Implement general feedback modal in TDP frontend</td><td>Introduces a persistent, general-purpose feedback button and modal to collect anonymous or attributed user input across the TDP frontend, enabling proactive insight gathering and continuous product improvement.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5072">#5072</a> - Implement contextual feedback modal on data file submission</td><td>Adds contextual, post-submission feedback prompts to Data Files pages, enabling real-time, targeted insights that improve usability, inform prioritization, and advance the platform’s Continuous Feedback Loops initiative.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Enabling Secure Data Access for DIGIT in Grafana

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/5114">#5114</a> - Grafana SQL View Updates/Fixes</td><td>Improves data integrity across T3 and T7 file views by filtering out malformed records and handling null age calculations gracefully, ensuring downstream systems produce accurate reports, reduce error propagation, and maintain trust in administrative and compliance workflows.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3580">#3580</a> - Create PostgreSQL users, roles, and permissions based on privilege mapping</td><td>Strengthens data security by enforcing least-privilege access and preventing unauthorized exposure of sensitive information.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4795">#4795</a> -  Explore Vault integration for credential rotation</td><td>Lays the groundwork for centralized, automated secrets management that enhances security, reduces operational overhead, and aligns with long-term DevSecOps goals across the platform.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4796">#4796</a> - Configure Vault for managing DB credentials</td><td>Strengthens security, enables automated secret rotation, and aligns infrastructure with DevSecOps best practices.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5056">#5056</a> - Design user training materials for DIGIT Grafana Access</td><td>Scopes and delivers user-friendly Grafana training materials tailored for DIGIT users, enabling secure, effective dashboard use while promoting adoption, self-sufficiency, and standardized data practices across the TDP platform.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### FRA Post-MVP Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4972">#4972</a> - Migrate FRA access from feature flag to user permission on Request Access page</td><td>Improves user access management by replacing a backend FRA feature flag with a user-declared permission via the Request Access form, enabling clearer onboarding, better scalability, and role-specific access logic for STTs, Tribes, and Regional staff.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4974">#4974</a> - Implement admin review workflow for user change requests</td><td>Introduces an auditable workflow for user-initiated profile and access change requests, improving self-service, administrative oversight, and compliance as the platform scales.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### fTANF Replacement

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://github.com/raft-tech/TANF-app/issues/5002">#5002</a> - Develop fTANF replacement MVP process map(s)</td><td>Clarifies functional requirements, surfaces system constraints, and enables more informed design ideation and feasibility discussions for an MVP solution.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### In-App Error Reporting

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4567">#4567</a> - Ideate on designs for in-app error reporting interface</td><td>Ideates on designs to empower users to independently understand and resolve data submission issues faster by providing clear, centralized, and actionable error visibility, reducing reliance on support channels and improving user confidence and task completion within TDP.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Operations & Maintenance

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3237">#3237</a> - Store error reports in S3</td><td>Improves performance and scalability by storing pre-generated XLS error reports in S3 during parsing, eliminating redundant processing and enabling faster, more consistent downloads for users.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://github.com/raft-tech/TANF-app/issues/5115">#5115</a> - Generate Integration Testing Plans, Designs, and Tickets</td><td>Strengthens pre-QASP testing by generating supporting tickets and documentation to catch defects earlier, reducing churn during QA, supporting compliance, and improving release readiness across teams.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Regional Staff TDP Access & Onboarding

_Note: Due to unforeseen changes in staffing, we will be postponing work with regional staff features at this time. This may be picked up at a later date._

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3461">#3461 </a>- Create and facilitate Project Updates meeting for regional staff</td><td>Ensures regional staff are well-informed about their new TDP access, providing them with a clear understanding of key functionalities, a live demonstration, and an opportunity for Q&#x26;A, ultimately supporting a smooth onboarding process.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3523">#3523 </a>- Refine research plan for regional staff MVP onboarding experience</td><td>Ensures user feedback is captured early, guiding design decisions with real-world insights and supporting the creation of a user-centered, effective interface.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3462">#3462</a> - Create and facilitate optional training session for regional staff</td><td>Empowers them to confidently navigate and utilize TDP’s features, fostering engagement, reducing support needs, and ensuring effective use of the platform.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr></tbody></table>

### User Experience Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4916">#4916</a> - Update TANF/SSP file upload validation to detect incorrect program type</td><td>Ensures users can quickly identify and resolve program-type mismatches without mistaking them for formatting errors, reducing support burden and enhancing data submission accuracy.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>
