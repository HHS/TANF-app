# Sprint 97 Summary

04-10-2024 - 04-23-2024

## Sprint Goal
* Dev:*Support closing out (6) tickets in review & continue progress on parsing enhancement tickets*
  * Category 4 Validators #2842
  * Further validation enhancements #2757, #2807, #2818, ...

* DevOps:Successful deployments across environments and pipeline stability investments
    * ES re-indexing automation #2870
    * Terraform: Automate Deployment of Elasticsearch #1349
    * Aggregate Cloud.gov ES instances #2814

* Design: Continue Knowledge Center Work, Build out new email notification templates*
    * Email notification template supporting #2473 (due date reminders)
    * Knowledge Center Content
      * Open PR / Content Draft for Error report explainer (#2846)
      * Complete review and merge Submission History PR

## Tickets
### Completed/Merged
  * [#1349 Terraform: Automate Deployment of Elasticsearch](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1349)
  * [#2536 STRETCH: Spike/attempt to implement cat4 validation as well](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2536)
  * [#2768 Spike - fix production owasp scan reporting](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2768)
  * [#2796 Add STT_CODE (or location information) to tanf/tribal t1-t7 and m1-m7 records in the django admin#](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2796)
  * [#2797 [Knowledge Center a11y] The purpose of a link must be descriptive](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2797)
  * [#2807 Update validation logic for the CALENDAR_QUARTER field](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2807)
  * [#2814 Aggregate Cloud.gov ES instances](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2814)
  * [#2818 As tech lead, I need TDP to reject files that do not have an update indicator == D](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2818)
  * [#2839 Spike - Cloud.gov Kibana Reschedule Route Issue](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2839)
  * [#2846 [Design Deliverable] Submission History Knowledge Center Explainer](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2846)
  * [#2908 As a DIGIT Team user, I need the ability to export parsed data from DAC to csv](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2908)

### Ready to Merge

### Submitted (QASP Review, OCIO Review)
  * [#2757 Generate preparser errors when multi-record rows are the wrong length or are missing space-filled second records](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2802)
  * [#2826 As tech lead, I need some record types that currently require trailing spaces to be parsed](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2826)
  * [#2847 [Design Deliverable] Error Report Knowledge Center Explainer](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2847)

### Closed (not merged)

---

## Moved to Next Sprint (In Progress, Blocked, Raft Review)
### In Progress
  * [#1345 [Design Deliverable] Email Template for Data Due Date Reminder](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1345)
  * [#2509 As a data analyst I need to know when my data has been processed with or w/o errors](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2509)
  * [#2897 As a data analyst I want finalized language and guidance resources in Submission History & Error Reports](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2897)
  * [#2688 TANF Section 2 validation clean-up](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2688)
  * [#2795 As tech lead, I need TDP to detect duplicate records within a file and not store them in the db.](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2795)
  * [#2801 Friendly name cleanup](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2801)

### Blocked
  * [#2870 Spike: As tech lead, I need elastic re-indexing to be automated](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2870)

### Raft Review
* [#2842 Complete cat4 validation implementation](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2842)
* [#2884 Generate preparser errors when multi-record rows are the wrong length or are missing space-filled second records - M3 and Tribal T3](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2884)
* [#2749 As tech lead, I need validation checks to be consistent with FTANF validation checks.](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2749)
* [#2822 Resolve WebInspect scan findings for Jan-Feb 2024](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2822)
