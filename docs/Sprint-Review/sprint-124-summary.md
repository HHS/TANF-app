---
description: 04/23/2025 - 05/07/2025
---

# Sprint 124 Summary

## Summary

### Deliverables

In the past sprint, we completed the following deliverables:

* **Delivered  Application Health Monitoring Deliverable 3: Alerts, Incident Response, and Health Monitoring**, integrating Alertmanager with Prometheus and SendGrid for email-based alerting, deploying Alertmanager to production with cross-environment UI access, and setting up a local self-hosted Sentry instance for backend debugging. These improvements boost our incident response and developer visibility across environments.

### Other Highlights

During this sprint, the team focused on enhancing the functionality of the FRA report interface, conducting research for the fTANF replacement, and ensuring data security. Other highlights included:

**FRA Post-MVP Enhancements:**

* Created designs to streamline onboarding for states and territories involved in FRA reporting.

**FRA Reporting Requirements MVP:**

* Ensured users can successfully re-upload updated files without needing to rename them.
* Prevents files from remaining indefinitely in 'Pending' status.

**fTANF Replacement - Foundational Research & Concept Validation:**

* Equipped OFA with a shared understanding of user challenges and unmet needs in fTANF.

**Operations & Maintenance:**

* Strengthened data integrity through updates to allowable values in the Citizenship field.

## Product Roadmap Progress&#x20;

{% hint style="info" %}
For more detailed information on task progress, please visit the [overall roadmap](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/timeline) for these epics.
{% endhint %}

* Application Health Monitoring | <mark style="color:green;">**ON TRACK**</mark> | Progress: 78% <mark style="color:green;">**(+4%)**</mark> | Estimated Completion Date: July 29, 2025
  * <mark style="color:purple;">**Note:**</mark>  [#3261](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3261) was closed due to limitations with Cloud.gov, meaning that Deliverable 3 (Alerts, Incident Response, and Health Monitoring) is now complete.
  * <mark style="color:yellow;">**Potential Risk:**</mark>  Timeline for completion may be affected due to delays in allowing Sentry.
* Continuous User Research & Feedback Loops | <mark style="color:green;">**ON TRACK**</mark> | Progress: 19% <mark style="color:green;">**(+19%)**</mark> | Estimated Completion Date: September 23, 2025
* Enabling Secure Data Access for DIGIT in Grafana | <mark style="color:green;">**ON TRACK**</mark> | Progress: 29% <mark style="color:green;">**(+13%)**</mark> | Estimated Completion Date: August 12, 2025
  * <mark style="color:purple;">**Note:**</mark>  This epic encapsulates has not yet been finalized, as there are additional items that may impact scope (e.g., data retention strategy). Thus, timelines and progress percentage are subject to change.
* FRA Post-MVP Enhancements | <mark style="color:green;">**ON TRACK**</mark> | Progress: 9% <mark style="color:green;">**(+9%)**</mark> | Estimated Completion Date: September 23, 2025
  * <mark style="color:purple;">**Note:**</mark>  Developer tickets for some design work is yet to be created, which may impact timelines.
* FRA Reporting Requirements MVP | <mark style="color:green;">**ON TRACK**</mark> | Progress: 98% <mark style="color:green;">**(+6%)**</mark> | Estimated Completion Date: May 15, 2025
  * <mark style="color:purple;">**Note:**</mark>  All originally committed work has been completed. We are currently in the process of addressing bugs from early access testing.
* fTANF Replacement - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 14% <mark style="color:green;">**(+7%)**</mark> | Estimated Completion Date: November 18, 2025
* Regional Staff TDP Access & Onboarding | <mark style="color:red;">**OFF TRACK**</mark> | Progress: 38% <mark style="color:red;">**(-9%)**</mark> | Estimated Completion Date: November 4, 2025
  * <mark style="color:purple;">**Note:**</mark>  Due to some of the unforeseen changes in HHS staffing, this epic is on pause until further notice.

## Tasks

### Application Health Monitoring

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3295">#3295</a> - Associate parsing log files with datafile submissions in DAC</td><td>Improves transparency and traceability, giving OFA users direct access to debugging details and enhancing trust in data processing outcomes.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3258">#3258</a> - Implement Cloud.gov log drain for centralized logging with Promtail and Loki</td><td>Streamlines logging infrastructure, reduces deployment complexity, and ensures scalable, unified access to app logs in Loki.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Continuous User Feedback & Research Loops

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4510">#4510</a> - Establish feedback review and synthesis process</td><td>Establishes a consistent, transparent process for turning user feedback into actionable insights—ensuring valuable input informs product and design decisions while reinforcing a culture of continuous improvement.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4483">#4483</a> - Ideate on designs for persistent feedback button &#x26; modal</td><td>Empowers users to share real-time insights in context, fostering continuous improvement through spontaneous, high-quality input while strengthening user trust and platform usability.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4502">#4502</a> - Design contextual in-app feedback prompts</td><td>Enables the design of lightweight, compliant in-app prompts that gather contextual user feedback at key moments in the TANF data workflow—empowering evidence-based product improvements while minimizing user disruption.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Enabling Secure Data Access for DIGIT in Grafana

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3579">#3579</a> - Set up Postgres views for all record types</td><td>Enhances data security, supports compliance, and enables safe, efficient access for Grafana and automation workflows without exposing sensitive information.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3472">#3472</a> - Investigate Grafana resource requirements for large exports</td><td>Helps determine whether Grafana can efficiently handle large TANF data exports, identifying potential memory constraints, performance limitations, and cost-effective solutions to meet DIGIT's interim data access needs.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4477">#4477</a> - Explore &#x26; align on structure for continuous feedback sessions on Grafana with DIGIT</td><td>Ensures dashboards evolve to meet real user needs, surface usability issues early, and support a culture of continuous improvement without placing a heavy burden on internal stakeholders.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3422">#3422</a> - Create and configure read-only RDS user for Grafana integration</td><td>Enables secure data exploration and dashboarding for OFA while safeguarding production data from accidental changes.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### FRA Reporting Requirements MVP

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4892">#4892</a> - Bug: File selector doesn't get reset when a file of the same name is provided</td><td>Ensures users can successfully re-upload updated files without needing to rename them, preserving expected workflows, reducing friction during submission, and preventing avoidable validation errors.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3555">#3555</a> - Bug: File stuck in pending if Decoder.UNKNOWN not handled</td><td>Prevents files from remaining indefinitely in 'Pending' status, improves user feedback, and supports faster issue resolution.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4897">#4897</a> - Bug: Rapid clicking of the submit button submits multiple copies of the file</td><td>Ensures accurate submission records, prevents user confusion, and maintains the integrity of the submission history view.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3489">#3489</a> - Fix file input collapsing after cancelling file selection on FRA page</td><td>Ensures a consistent and accessible user experience during file uploads, preventing UI confusion and maintaining usability across browsers.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4900">#4900</a> - Bug: Spinner &#x26; auto refresh don't consistently appear/occur</td><td>Enhances user confidence, prevents confusion during file processing, and improves the overall transparency of the submission workflow.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### FRA Post-MVP Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/3488">#3488</a> - Create design for integrating FRA into access request flow</td><td>Streamlines onboarding for states and territories involved in FRA reporting, reduce manual follow-up, and ensure proper access is granted from the start—all while improving clarity and supporting compliance.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4467">#4467</a> - Extend parser log file support to FRA submissions</td><td>Ensures consistent traceability, simplifies debugging, and aligns FRA reporting with the platform’s standardized logging infrastructure.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### fTANF Replacement - Foundational Research & Concept Validation

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4547">#4547</a> - Prepare synthesis on FTANF ahead of research recommendations</td><td>Equips OFA with a shared understanding of user challenges and unmet needs in fTANF, laying the foundation for focused, informed research that supports a thoughtful transition to a modernized solution.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4665">#4665</a> - Build STT fTANF use case tracker</td><td>Enables the team to design a modern replacement grounded in real Tribal workflows, minimizing the risk of building tools that miss critical user needs.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### Operations & Maintenance

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3454">#3454</a> - Remove 0 as a value for Citizenship</td><td>Strengthens data integrity, ensures compliance with updated policy, and prevents inaccurate eligibility data from entering the system.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3498">#3498</a> - Migrate Raft/OFA to GHCR</td><td>Ensures long-term access, organizational control, and alignment with HHS-wide infrastructure standards, reducing dependency on third-party registries.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4951">#4951</a> - Create requirements document for centralizing TANF feedback reports in TDP</td><td>Provides a shared, well-defined foundation for designing and developing centralized TANF data feedback reports in TDP, ensuring alignment across teams, reducing ambiguity, and supporting user-centered, compliant implementation.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4660">#4660</a> - Ensure SSN errors for invalid/missing SSNs in WEIs appear in critical tab</td><td>Ensures data integrity and timely error resolution by making high-impact validation issues more visible to STTs, ultimately reducing delays and improving compliance with employment tracking requirements.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### Regional Staff TDP Access & Onboarding

_Note: Due to unforeseen changes in staffing, we will be postponing work with regional staff features at this time. This may be picked up at a later date._

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3461">#3461 </a>- Create and facilitate Project Updates meeting for regional staff</td><td>Ensures regional staff are well-informed about their new TDP access, providing them with a clear understanding of key functionalities, a live demonstration, and an opportunity for Q&#x26;A, ultimately supporting a smooth onboarding process.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3523">#3523 </a>- Refine research plan for regional staff MVP onboarding experience</td><td>Ensures user feedback is captured early, guiding design decisions with real-world insights and supporting the creation of a user-centered, effective interface.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3462">#3462</a> - Create and facilitate optional training session for regional staff</td><td>Empowers them to confidently navigate and utilize TDP’s features, fostering engagement, reducing support needs, and ensuring effective use of the platform.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr></tbody></table>

### User Experience Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3557">#3557</a> - Explore error message clarity in identified issue areas</td><td>Lays the groundwork for improving error clarity by investigating confusing messages, identifying actionable fixes, and proposing changes that will help users resolve issues more confidently and independently during data submission.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4632">#4632</a> - Revisit UX strategic roadmap and define team objectives</td><td>Ensures alignment with product goals, strengthens cross-functional collaboration, and empowers the UX team to deliver more consistent, user-centered improvements across TDP.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>
