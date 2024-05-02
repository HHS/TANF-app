# Sprint 96 Summary

03-27-2024 - 04-09-2024


## Sprint Goal
* Dev:
*Support closing out (14) tickets in review & continue progress on Cat4, and walk on more parsing enhancement tickets*
    * Category 4 Validators #2842
    * Further validation enhancements #2757, #2807, #2818, ... 

* DevOps:
*Successful deployments across environments and pipeline stability investments*
    * ES re-indexing automation #2870
    * OWASP scan fix #2768 

* Design: 
*QASP review Tribal friendly names and continue on to TANF & SSP, Continue KC work*
    * Error Categories GitHub Documentation
    * Friendly name fixes (#2801) 
    * Knowledge Center Content (#2847, #2846)
        * Submission History
        * Error reports / data file structure
   


## Tickets
### Completed/Merged
* [#1441 As OFA tech lead, I need a new permissions group for OFA data analysts](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1441)
* [#2845 [Design Deliverable] GitHub Error Categories Guide](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2845)
* [#2871 As tech lead I need file transfer bug resolved](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2871)
* [#2877 Move ES AWS routing docker image to RAFT hub](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2877)
* [#2886 [bug] SSP feedback reports and files not downloadable from submission history tab](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2886)
* [#2887 as tech lead, I need SSP Section 2 item # 18A (REC_OASDI_INSURANCE) schema def updated as not a required field](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2887) 
* [#2673 Cat 1 Errors Audit Fixes](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2673)


### Ready to Merge







### Submitted (QASP Review, OCIO Review)
* [#2536 [spike] Cat 4 validation](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2536)
* [#2908 As a `DIGIT Team` user, I need the ability to export parsed data from DAC to csv#2908](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2908)
* [#2846 [Design Deliverable] Submission History Knowledge Center Explainer#2846](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2846)
* [#2801 Friendly name cleanup](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2801)
* [#2757 Generate preparser errors when multi-record rows are the wrong length or are missing space-filled second records](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/27570)





### Closed (not merged)
* [#2840 DIGIT Kibana Access](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2840)


---

## Moved to Next Sprint (In Progress, Blocked, Raft Review)
### In Progress
*	[#2509 As a data analyst I need to know when my data has been processed with or w/o errors](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2509)
*	[#2847 Report Knowledge Center Explainer](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2847)
* [2870 Spike: As tech lead, I need elastic re-indexing to be automated](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2870)
* [#2592 Deploy celery as a separate cloud.gov app](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2592)
*	[#2796 Add `STT_CODE` (or location information) to tanf/tribal t1-t7 and m1-m7 records in the django admin](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2796)
*	[#2797 [Knowledge Center a11y] The purpose of a link must be descriptive](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2798)
*	[#2814 Aggregate Cloud.gov ES instances](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2814)
*	[#2818 [As tech lead, I need TDP to reject files that do not have an update indicator == DD]](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2818)
*	[#2688 TANF Section 2 validation clean-up](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2688)
* [#2749 As tech lead, I need validation checks to be consistent with FTANF validation checks](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2749)
* [#2884 Generate preparser errors when multi-record rows are the wrong length or are missing space-filled second records - M3 and Tribal T3](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2884)

### Blocked
* [#2883 Pre-Made Reporting Dashboards on Kibana](https://github.com/raft-tech/TANF-app/issues/2883)
* [#2870 Spike: As tech lead, I need elastic re-indexing to be automated](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2870)

### Raft Review
* [#1349 Terraform: Automate Deployment of Elasticsearch#1349](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1349)
* [#2839 Spike - Cloud.gov Kibana Reschedule Route](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2839)
* [#2826 As tech lead, I need some record types that currently require trailing spaces to be parsed](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2826)
* [#2846 [Design Deliverable] Submission History Knowledge Center Explainer](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2846)
