# Sprint 93 Summary

02/14/2024 - 02/27/2024

Velocity (Dev): 18

## Sprint Goal
* Dev:
    * Continue parsing engine development and begin work on enhancement tickets
        * #2536 Cat 4 validation 
    * #1858 Secure OFA staff access to Kibana 
        * Unblocks #1350 when complete 
* DevOps:
    * #2790 - Update deployment code to support Kibana and integrate with Standing Elastic instance
* Design: 
    * Tie up current documentation work
    * Continue refinement of research roadmap


## Tickets
### Completed/Merged
* [#2781 As a developer,  I want to have documentation on django migration best practices](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2781)
* [#2813 Reduce dev environment count](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2813)
* [#2790 Kibana deployment](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2790)
* [#2824 Resolve issues raised in pen testing findings](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2824)
* [#2832 Accessibility Guide update](https://github.com/raft-tech/TANF-app/pull/2832)
* [#2794 Make Case Number validators accept spaces and special characters](https://github.com/raft-tech/TANF-app/issues/2794)
* [#2771 Update validateSSN to allow for all 0s, 1s,...9s as valid values except in cat3 scenarios](https://github.com/raft-tech/TANF-app/issues/2771)
* [#2855 Update Failed Deployment Troubleshooting](https://github.com/raft-tech/TANF-app/pull/2855)
* [#2768 Fix production OWASP scan reporting](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2768)
* [#2835 Handle elastic BulkIndexException in bulk create records](https://github.com/raft-tech/TANF-app/pull/2835)

### Ready to Merge







### Submitted (QASP Review, OCIO Review)
* [#2646 - Populate data file summary case aggregates differently per section](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2646)
* [#2820 [bug] Uncaught exception re: parsing error preventing feedback report generation](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2820)
* [#2746 As an STT, I need to know if there are issues with the DOBs reported in my data files](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2746)
* [#2729 As a developer, I want to move migration commands in the pipeline to CircleCI](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2729)
* [#2853 - Database Backup Bug](https://github.com/raft-tech/TANF-app/pull/2853)
* [#2681 TANF Section 1 Validation cleanup](https://github.com/raft-tech/TANF-app/issues/2681)





### Closed (not merged)
* N/A


---

## Moved to Next Sprint (In Progress, Blocked, Raft Review)
### In Progress
* [#2757 Generate preparser errors when multirecord rows are the wrong length](https://github.com/raft-tech/TANF-app/issues/2757)
* [#2509 As a data analyst I need to know when my data has been processed with or w/o errors](https://github.com/raft-tech/TANF-app/issues/2509)
* [#2814 Aggregate cloud.gov ES instances](https://github.com/raft-tech/TANF-app/issues/2814)
* [#2842 Complete cat4 validation implementation](https://github.com/raft-tech/TANF-app/issues/2842)
* [#1350 As an OFA staff member I want to access Kibana from TDP](https://github.com/raft-tech/TANF-app/issues/1350)




### Blocked
* [#2592 Deploy celery as a separate cloud.gov app](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2592)

### Raft Review
* [#2799 Generate error mismatching field rpt_month_year w/ header](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2799)
* [#2793 update dateYearIsLargerThan() validator logic for rpt_month_year](https://github.com/raft-tech/TANF-app/issues/2793)
* [#2536 [spike] Cat 4 validation](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2536)
* [#1441 As tech lead I need new permissions group for OFA data analysts](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1441)
* [#2536 Spike / Attempt to implement cat4 validation](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2536)
* [#2673 Cat 1 errors audit fixes](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2673)

