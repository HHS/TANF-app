---
description: 5/21/2025 - 6/3/2025
---

# Sprint 126 Summary

## Summary

### Highlights

During this sprint, the team focused on enhancing our continuous user feedback stack, conducting in-app error reporting discovery, and preparing Grafana for DIGIT use. Other highlights included:

**Continuous User Feedback & Research Loops:**

* Established a consistent, transparent process for turning user feedback into actionable insights.
* Began surfacing meaningful user behavior insights.

**Enabling Secure Data Access for DIGIT via Grafana:**

* Addresses timeouts in Grafana when querying large datasets.
* Created new permission hierarchy to grant DIGIT users access to Grafana.

**FRA Post-MVP Enhancements:**

* Ensured that each FRA file submission is preserved as a distinct version.

**In-App Error Reporting:**

* Conducted initial discovery to enable us to design a compliant, high-impact in-app error reporting experience.

**Operations & Maintenance:**

* Adjusted reparsing timeout calculation to ensure processing estimates are accurate and practical

**User Experience Enhancements:**

* Updated file naming convention to improve clarity and traceability for users reviewing submission history outside the platform

## Product Roadmap Progress&#x20;

{% hint style="info" %}
For more detailed information on task progress, please visit the [overall roadmap](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/timeline) for these epics.
{% endhint %}

* Application Health Monitoring | <mark style="color:green;">**ON TRACK**</mark> | Progress: 82% <mark style="color:green;">**(+0%)**</mark> | Estimated Completion Date: July 29, 2025
  * <mark style="color:yellow;">**Potential Risk:**</mark>  Timeline for completion may be affected due to delays in allowing Sentry.
* Continuous User Research & Feedback Loops | <mark style="color:green;">**ON TRACK**</mark> | Progress: 55% <mark style="color:red;">**(-14%)**</mark> | Estimated Completion Date: September 23, 2025
  * <mark style="color:purple;">**Note:**</mark>  Development tickets were added to this epic, which will affect progress towards completion but not the estimated completion date.
* Enabling Secure Data Access for DIGIT in Grafana | <mark style="color:green;">**ON TRACK**</mark> | Progress: 56% <mark style="color:green;">**(+21%)**</mark> | Estimated Completion Date: August 12, 2025
  * <mark style="color:purple;">**Note:**</mark>  This epic encapsulates has not yet been finalized, as there are additional items that may impact scope (e.g., data retention strategy). Thus, timelines and progress percentage are subject to change.
* FRA Post-MVP Enhancements | <mark style="color:green;">**ON TRACK**</mark> | Progress: 20% <mark style="color:green;">**(+3%)**</mark> | Estimated Completion Date: September 23, 2025
  * <mark style="color:purple;">**Note:**</mark>  Developer tickets for some design work is yet to be created, which may impact timelines.
* fTANF Replacement - Foundational Research & Concept Validation | <mark style="color:green;">**ON TRACK**</mark> | Progress: 25% <mark style="color:green;">**(+0%)**</mark> | Estimated Completion Date: December 16, 2025
* Regional Staff TDP Access & Onboarding | <mark style="color:red;">**OFF TRACK**</mark> | Progress: 38% <mark style="color:red;">**(-9%)**</mark> | Estimated Completion Date: November 4, 2025
  * <mark style="color:purple;">**Note:**</mark>  Due to some of the unforeseen changes in HHS staffing, this epic is on pause until further notice.

## Tasks

### Application Health Monitoring

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3336">#3336</a> - Decouple Celery and Redis from backend into separate Cloud.gov services</td><td>Improves scalability, reliability, and maintainability of TDP’s background task infrastructure while aligning with cloud-native best practices.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Continuous User Feedback & Research Loops

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4510">#4510</a> - Establish feedback review and synthesis process</td><td>Establishes a consistent, transparent process for turning user feedback into actionable insights—ensuring valuable input informs product and design decisions while reinforcing a culture of continuous improvement.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4780">#4780</a> -  Explore frontend observability dashboard options and MVP setup</td><td>Allows us to confirm a compliant, privacy-conscious solution and begin surfacing meaningful user behavior insights that will inform future improvements to the TDP experience.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4789">#4789</a> - Finalize frontend observability dashboard</td><td>Equips internal teams with actionable insights into user behavior, enabling continuous UX and product improvements driven by real-world usage data.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### Enabling Secure Data Access for DIGIT in Grafana

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3472">#3472</a> - Investigate Grafana resource requirements for large exports</td><td>Helps determine whether Grafana can efficiently handle large TANF data exports, identifying potential memory constraints, performance limitations, and cost-effective solutions to meet DIGIT's interim data access needs.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3423">#3423</a> - Grant DIGIT Team access to Grafana with viewer/editor permissions</td><td>Enables secure, controlled data visibility for monitoring and analysis while preserving dashboard integrity and preventing unintended changes.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4983">#4983</a> - Bug: Grafana export fails for large queries due to nginx timeout</td><td>Addresses timeouts in Grafana when querying large datasets, ensuring reliable data exports and preventing user confusion caused by NGINX error messages.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3580">#3580</a> - Create PostgreSQL users, roles, and permissions based on privilege mapping</td><td>Strengthens data security by enforcing least-privilege access and preventing unauthorized exposure of sensitive information.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4795">#4795</a> -  Explore Vault integration for credential rotation</td><td>Lays the groundwork for centralized, automated secrets management that enhances security, reduces operational overhead, and aligns with long-term DevSecOps goals across the platform.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3362">#3362</a> - Redirect users to login page on 401/403 from PLG auth</td><td>Eliminates confusing error screens and ensures users are redirected appropriately, improving usability and maintaining consistent access control across the platform.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4796">#4796</a> - Configure Vault for managing DB credentials</td><td>Strengthens security, enables automated secret rotation, and aligns infrastructure with DevSecOps best practices.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### FRA Post-MVP Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4942">#4942</a> - Bug: FRA submissions overwriting S3 file versions</td><td>Ensures that each FRA file submission is preserved as a distinct version, protecting against data loss and enabling accurate auditability and recovery of historical submissions.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4976">#4976</a> - Remove download buttons under file upload to resolve UI collapse conflict</td><td>Resolves a conflict with recent improvements to file upload behavior, ensuring a more stable and intuitive experience for users submitting multiple files.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### In-App Error Reporting

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/4943">#4943</a> - Complete foundational discovery for in-app error reporting</td><td>Enables us to design a compliant, high-impact in-app error reporting experience that aligns with real user needs and implementation realities.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/tdp-command-center-67d9d9079cf6b20017b3725a/issues/gh/raft-tech/tanf-app/5035">#5035</a> - Map current and future-state journeys for in-app error reporting</td><td>Launches a UX mapping initiative to document current pain points and define future-state workflows for submission error resolution, laying the foundation for a more intuitive, contextual, and self-service in-app error reporting experience.</td><td><mark style="color:yellow;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Operations & Maintenance

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3516">#3516</a> - Reevaluate and adjust reparse timeout calculation</td><td>Ensures processing estimates are accurate and practical, improving system monitoring, task management, and developer confidence without affecting the user experience.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3525">#3525</a> - Remediate 2/25 webinspect findings related to RA-5 controls</td><td>Ensures compliance with NIST RA-5 requirements, preserves our system’s ATO standing, and reinforces our commitment to a secure and well-governed infrastructure—even when findings are determined to be false positives.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3562">#3562 </a>- Simplify SSN validation for tribal TANF</td><td>Simplifies SSN and citizenship validation rules for Tribal TANF submissions to eliminate incorrect errors, align with federal guidance, and reduce friction in the data submission process.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3546">#3546</a> - Update education level validation for adults when family affiliation is 1, 2, or 3</td><td>Updates Education Level validation for Adult records to align with coding instructions by preventing the use of <code>99</code> when Family Affiliation is 1–3, ensuring data accuracy and reducing future corrections for state partners.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5070">#5070</a> - Disallow 666 as an SSN prefix for FRA</td><td>Enhances data integrity by adding a validation rule that rejects FRA submissions containing SSNs beginning with “666,” ensuring compliance with SSA standards and preventing invalid or fraudulent data entries.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### Regional Staff TDP Access & Onboarding

_Note: Due to unforeseen changes in staffing, we will be postponing work with regional staff features at this time. This may be picked up at a later date._

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3461">#3461 </a>- Create and facilitate Project Updates meeting for regional staff</td><td>Ensures regional staff are well-informed about their new TDP access, providing them with a clear understanding of key functionalities, a live demonstration, and an opportunity for Q&#x26;A, ultimately supporting a smooth onboarding process.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3523">#3523 </a>- Refine research plan for regional staff MVP onboarding experience</td><td>Ensures user feedback is captured early, guiding design decisions with real-world insights and supporting the creation of a user-centered, effective interface.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3462">#3462</a> - Create and facilitate optional training session for regional staff</td><td>Empowers them to confidently navigate and utilize TDP’s features, fostering engagement, reducing support needs, and ensuring effective use of the platform.</td><td><mark style="color:red;"><strong>BLOCKED</strong></mark></td></tr></tbody></table>

### User Experience Enhancements

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4925">#4925</a> - Update file naming convention in submission history downloads</td><td>Improves clarity and traceability for users reviewing submission history outside the platform, reducing confusion and streamlining file organization.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3557">#3557</a> - Explore error message clarity in identified issue areas</td><td>Lays the groundwork for improving error clarity by investigating confusing messages, identifying actionable fixes, and proposing changes that will help users resolve issues more confidently and independently during data submission.</td><td><mark style="color:blue;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4916">#4916</a> - Update TANF/SSP file upload validation to detect incorrect program type</td><td>Ensures users can quickly identify and resolve program-type mismatches without mistaking them for formatting errors, reducing support burden and enhancing data submission accuracy.</td><td><mark style="color:purple;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>
