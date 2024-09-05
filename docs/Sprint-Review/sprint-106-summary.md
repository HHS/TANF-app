# sprint-106-summary

8/14/202 - 8/27/2024

### <mark style="color:orange;">Priority Setting</mark>

* Reparsing &#x20;
  * Reasoning: OFA has ability to reparse and the data process with latest system logic which will enable STTs to get error reports that are meaningful and relevant and OFA gets the needed data. System, as a whole, will be more flexible with data flow (able to hot fix and hit reparse).  Additionally, we want to avoid missing data and be able to repopulate the database after cleaning the data. &#x20;
* Data Access Strategy&#x20;
  * Reasoning: Creating daily blockers &#x20;
* Admin Console Improvements&#x20;
  * Reasoning: Trigger has been met to refine tickets (Research Synthesis)
* Improved Dev Tooling&#x20;
  * improve test\_parse.py 2641&#x20;
  * separate celery 2592&#x20;
  * Reasoning: Developing / refining tickets to support the above priorities – These tickets will enhance capabilities while the above are being flushed out &#x20;

### <mark style="color:orange;">Sprint Goal</mark>

**Dev:**

_**Reparsing, Admin Console Improvements, Application Health Monitoring work, and Improved Dev Tooling**_

* \#2965 — As tech lead, I want a database seed implemented for testing
* \#3102  — Admin Exp: Django Implement Multi-Select Fiscal Period Dropdown For Data Export&#x20;
* \#2561 — As a sys admin, I need TDP to automatically deactivate accounts that are inactive for 180 days
* \#3110 — Spike - Investigate Custom Filter Integration
* \#3137 — \[bug] OFA unable to export data to csv by record type and fiscal period
* \#3074 — TDP Data Files page permissions for DIGIT & Sys Admin user groups
* \#3076  — Admin Filter Enhancements for Data Files Page&#x20;

**DevOps:**

_**Successful deployments across environments and pipeline stability investments**_

*

**Design:**

_**Support reviews, In-app banner to support parsed data, Continue Error Audit (Cat 4)**_

* \#2968  — \[Design Deliverable] Update Error Audit for Cat 4 / QA
* \#3114 — \[Design Spike] In-app banner for submission history pages w/ data parsed before May 2024
* \#3143 — August release notes — Knowledge Center & Email Template



## Tickets

### Completed/Merged

* [#2985 \[Design Deliverable\] Email spec for Admin Notification for stuck files](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2985)
* [#2996 Add dynamic field name to cat4 error messages](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2996)
* [#3143 August release notes — Knowledge Center & Email Template](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3143)
* [#3061 \[a11y fix\] Django multi-select filter ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3061)
* [#2954 Extend SESSION\_COOKIE\_AGE](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2954)
* [#3079 DB Backup Script Fix](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3079)

### Submitted (QASP Review, OCIO Review)

* [#3064 Re-parse Meta Model](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3064)
* [#3065 Spike - Guarantee Sequential Execution of Re-parse Command](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3065)
* [#2792 \[Error Audit\] Category 3 error messages clean-up](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2792)
* [#2883 Pre-Made Reporting Dashboards on Kibana](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2883)
* [#2561 As a sys admin, I need TDP to automatically deactivate accounts that are inactive for 180 days](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2561)
* [#3078 \[Research Synthesis\] DIGIT Admin Experience Improvements](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3078)

### Ready to Merge

### Closed (Not Merged)

* [#3147 S3 buckets contain fewer datafiles than DAC](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3147)

### Moved to Next Sprint&#x20;

**In Progress**&#x20;

* [#2965 As tech lead, I want a database seed implemented for testing](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2965)
* [#2458 Integrate Nexus into CircleCI](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2458)
* [#3137 \[bug\] OFA unable to export data to csv by record type and fiscal period](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3137)
* [#2968 \[Design Deliverable\] Update Error Audit for Cat 4 / QA](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2968)
* [#3060 As a TDP user, I need to stay logged in when I'm actively using the system](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3060)
* [#3074 TDP Data Files page permissions for DIGIT & Sys Admin user groups](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3074)
* [#3114 \[Design Spike\] In-app banner for submission history pages w/ data parsed before May 2024](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3114)
* [#3142 \[Research Spike\] Get more detail about Yun & DIGIT's data workflow and use cases](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3142)

#### Blocked

*

**Raft Review**

* [#3043 Sentry: Local environment for Debugging](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3043)
* [#3110 Spike - Investigate Custom Filter Integration](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3110)
* [#3102 Admin Exp: Django Implement Multi-Select Fiscal Period Dropdown For Data Export ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3102)
* [#3087 Admin By Newest Filter Enhancements for Data Files Page](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3087)
* [#3076 Admin Filter Enhancements for Data Files Page ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3076)
