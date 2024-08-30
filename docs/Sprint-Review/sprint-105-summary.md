# sprint-105-summary

7/31/2024 - 8/14/2024

### Priority Setting

* Reparsing&#x20;
  * Tickets:&#x20;
    * \#3064 — Re-parse Meta Model
    * \#3113 —  As tech lead, I need the validation on the header update indicator revised to unblock parsing
    * \#3073 — \[bug] TDP is raising cat 4 error on TANF/SSP closed case files that is not present
* System Monitoring &#x20;
* DIGIT Work  &#x20;

### Sprint Goal

**Dev:**

_**Plain Language Error Messaging and Application Health Monitoring work, improved dev tooling, and fixing bugs**_

* \#2792  — \[Error Audit] Category 3 error messages clean-up&#x20;
* \#2965 — As tech lead, I want a database seed implemented for testing
* \#3064 — Re-parse Meta Model
* \#3113 —  As tech lead, I need the validation on the header update indicator revised to unblock parsing
* \#3073 — \[bug] TDP is raising cat 4 error on TANF/SSP closed case files that is not present
* \#3062  — bug: ES docker image for non-dev spaces stored in personal dockerhub
* \#1646 — \[A11y Fix] Correct TDP home : aria label mismatch

**DevOps:**

_**Successful deployments across environments and pipeline stability investments**_

* \#2458  — Integrate Nexus into CircleCI

**Design:**

_**Support reviews, Complete Research Synthesis, Continue Error Audit (Cat 4)**_

* \#3078 — DIGIT Admin Experience Synthesis
* \#3114  — \[Design Spike] In-app banner for submission history pages
* \#2968  — \[Design Deliverable] Update Error Audit for Cat 4 / QA

## Tickets

### Completed/Merged

* [#1621 As a TDP user, I'd like to see a descriptive error message page if authentication source is unavailable.](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1621)
* [#1646 \[A11y Fix\] Correct TDP home : aria label mismatch](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1646)
* [#3033 As tech lead, I need the sections 3 and 4 calendar quarter logic updated](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3033)
* [#3055 Service timeout blocks parsing completion](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3055)
* [#3057 \[Design Deliverable\] Spec for light-lift fiscal quarter / calendar quarter explainer in TDP](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3057)
* [#3113 As tech lead, I need the validation on the header update indicator revised to unblock parsing ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3113)

### Submitted (QASP Review, OCIO Review)

* [#2954 Extend SESSION\_COOKIE\_AGE](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2954)
* [#3061 \[a11y fix\] Django multi-select filter ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3061)
* [#3079 DB Backup Script Fix](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3079)
* [#2883 Pre-Made Reporting Dashboards on Kibana](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2883)
* [#2985 \[Design Deliverable\] Email spec for Admin Notification for stuck files](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2985)
* [#2996 Add dynamic field name to cat4 error messages](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2996)
* [#2993 Kibana Dashboard MVP](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2993)

### Ready to Merge

* [#3058 \[Design Deliverable\] Release notes email template](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3058)
* [#3062 bug: ES docker image for non-dev spaces stored in personal dockerhub](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3062)
* [#3073 \[bug\] TDP is raising cat 4 error on TANF/SSP closed case files that is not present](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3073)
* [#3107 \[Re-parse command\] Retain original submission date when command runs](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3107)

### Closed (Not Merged)

* [#1355 Research questions around DIGIT teams query usage for parsed data](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1355)

### Moved to Next Sprint&#x20;

**In Progress**&#x20;

* [#2965 As tech lead, I want a database seed implemented for testing](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2965)

#### Blocked

* [#2458 Integrate Nexus into CircleCI](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2458)

**Raft Review**

* [#3043 Sentry: Local environment for Debugging](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3043)
* [#3064 Re-parse Meta Model](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3064)
* [#3065 Spike - Guarantee Sequential Execution of Re-parse Command](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3065)
* [#3078 \[Research Synthesis\] DIGIT Admin Experience Improvements](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3078)
* [#3087 Admin By Newest Filter Enhancements for Data Files Page](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3087)
* [#2792 \[Error Audit\] Category 3 error messages clean-up](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2792)
