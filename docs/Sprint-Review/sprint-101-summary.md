# sprint-101-summary

6/5/2024 - 6/18/2024

**Dev:**

_**Prioritized DAC and Notifications Work**_&#x20;

* As sys admin, I want to be able to reparse datafile sets #2978
* As a software engineer, I want to be able to test django-admin-508 #3008
* As tech lead, I need the STT filter for search\_indexes to be updated #2950
* As a data analyst I want to be notified of approaching data deadlines #2473
* add `SENDGRID_API_KEY` to deploy.backend.sh #2677
* Implement (small) data lifecycle (backup/archive ES) #3004
* As a developer I want to test django-508 repo #2980\


**DevOps:**

_**Successful deployments across environments and pipeline stability investments**_

* Application health monitoring #831

**Design:**

_**Close out error guide work, coordinate with dev on a plan for Cat 3 problems introduced by Cat 2 work, support spec-writing for upcoming work, and continued error audit dev ticket refinement.**_

* Error Report Guide #2847 is going through final edits&#x20;
  * Walk-on Dear Colleague letter link update to this PR (or spin up a separate ticket if deployment of the letter to OFA's website doesn't align to this)
* Deliver spec for #3014 (Blanked-out values in Submission History)
* \#3021 Updated KC Release Notes & Update Indicator FAQ - stretch goal for this sprint
* Write follow-on / spec tickets from #2909 findings - stretch/ongoing lift
* Category 3 error messages clean-up #2792 - stretch/ongoing lift

## Tickets

### Completed/Merged

* [#2980 As a developer I want to test django-508 repo](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2980)
* [#2892 Correct misleading error message for unaligned reporting year/q against header year/q](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2892)
* [#2909 \[Research Spike\] OOtB OFA Kibana Experience & DIGIT Data Access](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2909)
* [#2991 As tech lead, I need the sftp file transfer feature to be deprecated](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2991)
* [#2847 \[Design Deliverable\] Error Report Knowledge Center Explainer](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2847)
* [#3024 2897 follow-on for a11y-related enhancement ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3024)
* [#2897 As a data analyst I want finalized language and guidance resources in Submission History & Error Reports ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2897)

### Submitted (QASP Review, OCIO Review)

* [#2133 \[Dev\] Enhancement for Request Access form (Tribe discoverability) ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2133)
* [#3023 as STT approved user, I need my IP address whitelisted so i can access TDP](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3023)
* [#3000 \[Design Deliverable\] TDP Poster for summer 2024 conferences](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3000)
* [#2795 As tech lead, I need TDP to detect duplicate records within a file and not store them in the db. ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2795)
* [#2693 \[Error Audit\] Category 2 error messages clean-up ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2693)
* [#2801 Friendly name cleanup ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2801)
* [#2883 Pre-Made Reporting Dashboards on Kibana](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2883)
* [#3021 \[Design Deliverable\] Updated KC Release Notes & Update Indicator FAQ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3021)
* [#2954 Extend SESSION\_COOKIE\_AGE](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2954)

### Ready to Merge

*

### Closed (Not Merged)

* [#2491 Create root-level docker-compose configuration file(s)](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2491)
* [#1690 As a system admin, I need a way to be redirected to frontend from DAC](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1690)
* [#2351 As a user I want to be notified when the files are being scanned or uploaded when I push upload button](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2351)
* [#2591 Allow `manage.py` commands to be run by circleci](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2591)

### Moved to Next Sprint&#x20;

**In Progress**&#x20;

* [#3004 Implement (small) data lifecycle (backup/archive ES)](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3004)
* [#831 \[Spike\] As a Tech Lead, I want to get alerts when there is a backend or frontend error that affects an STT user ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/831)
* [#2978 As sys admin, I want to be able to reparse datafile sets](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2978)

#### Blocked

*

**Raft Review**

* [#2950 As tech lead, I need the STT filter for search\_indexes to be updated ](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2950)
* [#3008 As a software engineer, I want to be able to test django-admin-508](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3008)
* [#3016 Spike - Cat2 Validator Improvement](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3016)
* [#2473  As a data analyst I want to be notified of approaching data deadlines](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2473)
