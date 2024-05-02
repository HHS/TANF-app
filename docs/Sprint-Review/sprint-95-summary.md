# Sprint 95 Summary

03/13/2024 - 03/26/2024

Velocity (Dev): 19

## Sprint Goal
* Dev:
    * Category 4 Validators #2842
    * Further validation enhancements #2757, #2807, #2818, ... 

* DevOps:
    * ES re-indexing #2870
    * ES aggregation #2814

* Design: 
    * Error Categories GitHub Documentation
    * Friendly name fixes (#2801)
    * Knowledge Center Content (#2847, #2846)
        * Submission History
        * Error reports / data file structure
   


## Tickets
### Completed/Merged
* [#2746 As an STT, I need to know if there are issues with the DOBs reported in my data files](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2746)
* [#2729 As a developer, I want to move migration commands in the pipeline to CircleCI](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2729)
* [#2820 [bug] Uncaught exception re: parsing error preventing feedback report generation](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2820)
* [#2799 Generate error mismatching field rpt_month_year w/ header](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2799)
* [#2793 update dateYearIsLargerThan() validator logic for rpt_month_year](https://github.com/raft-tech/TANF-app/issues/2793)
* [#2754 As tech lead I need sections 3,4 rejected if T6, T7, M7 records can't be parsed](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2754)
* [V3.3.2 yq hotfix](https://github.com/raft-tech/TANF-app/pull/2895)
* [#2861 DIGIT Team Group + Kibana + Queries](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2861)

### Ready to Merge
* [Move ES AWS routing image](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2877)






### Submitted (QASP Review, OCIO Review)
* [#2536 [spike] Cat 4 validation](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2536)
* [#2807 Update validation logic for CALENDAR_Quarter field](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2807)
* [#2681 TANF Section 1 Validation cleanup](https://github.com/raft-tech/TANF-app/issues/2681)
* [#1441 As tech lead I need new permissions group for OFA data analysts](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1441)
* [#2871 As tech lead I need file transfer bug resolved](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2871)
* [#2818 I need TDP to reject files that do not have an update indicator](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2818)
* [#2886 Bug SSP feedback reports not downloadable](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2886)





### Closed (not merged)



---

## Moved to Next Sprint (In Progress, Blocked, Raft Review)
### In Progress
* [#2673 Cat 1 errors audit fixes](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2673)
* [#2509 As a data analyst I need to know when my data has been processed with or w/o errors](https://github.com/raft-tech/TANF-app/issues/2509)
* [#2801 Friendly Name Cleanup](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2801)
* [#2846 Submission History Knowledge Center Explainer](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2846)
* [#2847 Error Report Knowledge Center Explainer](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2847)
* [#2845 GitHub Error Categories guide](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2845)
* [#2870 As tech lead I need elastic re-indexing to be automated](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2870)



### Blocked
* [#2768 Fix production OWASP scan reporting](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2768)
* [#2592 Deploy celery as a separate cloud.gov app](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2592)


### Raft Review
* [#2757 Generate preparser errors when multirecord rows are the wrong length](https://github.com/raft-tech/TANF-app/issues/2757)
* [#2842 Complete cat4 validation implementation](https://github.com/raft-tech/TANF-app/issues/2842)
* [#2814 Aggregate cloud.gov ES instances](https://github.com/raft-tech/TANF-app/issues/2814)
* [#2887 SSP Section 2 item # 18A (REC_OASDI_INSURANCE) schema def](https://github.com/raft-tech/TANF-app/issues/2887)







