# Sprint 23 Summary
**06/08/2021 - 06/22/2021**

### Updates
 - Lauren is out this week and Alex is acting as PO for Backlog grooming
 - Raft has an in person allhands the 23 and 24th which means our sprint will be impacted by folks travelling and being out
 - John Willis is out ~4 days this week due to ^.
 - UX Team shifts - Dmitri assuming UX Lead role. Shubhi to roll off project except for in supervisory role. Now have budget for a supporting Jr UX Researcher as needed.


## Sprint Goals

Finish up ATO Functionality
- Finish up file download & storage (#416, #818, #833, #834)
- Wrap up OWASP Scan tickets (#879, #865)

Make decisions on upcoming releases
- File transfer options for release 2 (#1011)
- NextGen XMS direction for release 1 (Epic #902, #638)

UX Planning sprint (#993)

## Merged/Completed (Done/Demo, Closed)


## Submitted (QASP Review, OCIO Review)
- Evil journey map for security design guidance [#954](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/954)
- [Backend] Add endpoint to scan and upload a Data File to S3 [#818](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/818)
- [Frontend] Communicate to user if they are inactive [#829](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/829)
- Update Pa11y configuration to check more URLs and store artifacts from screenshots [#872](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/872)


## Moving to Next Sprint (Raft Review, In Progress, Current Sprint Backlog)
Raft Review
- [Backend] Add endpoint to download a file from S3 [#833](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/833)
- OWASP: Exclude false positive alerts during CI/CD [#879](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/879)
- [Frontend] Add a download button to the Data Files view [#416](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/416)
- Issue 829: Communicate to user if they are inactive [#930](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/930)
- Add zap configs to ignore false positives [#941](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/941)
- Move vendor-staging in the dev space to staging in the staging space [#847](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/847)
- As a dev, I want an automated, documented CI process to provision Cloud.gov brokered services [#609](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/609)

In Progress
- (Sprint 23) Round 7 UX Research Planning [#993](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/993)
- Update ATO docs and corresponding code docs [#962](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/962)
- Priority Django Admin A11y Fixes[#973](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/973)
- SPIKE: Does a cron job still make sense?  [#1011](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1011)


Sprint To Do
- [Frontend] Hook upload and download to real API endpoints[#834](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/834) 
- Set up new dev environments: sandbox, raft-review, qasp-review, a11y[#848](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/848)
- As a dev, I need to know which authentication service we're using (login.gov vs. NextGen XMS) [#638](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/638) 
- Refactor backend to use default model permissions[#898](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/898)
- Add migrations to configure groups to add permissions to different models[#899](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/899)
- I want a client-side Content Security Policy to protect me from XSS and other client side attacks [#907](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/907)
- Set correct ENV variables on frontend/backend Cloud.gov apps + HHS CircleCI project settings [#896](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/896)


## Agenda for Sprint 23 Demo 
- Evil User Personas, Journey Maps (5) (Dmitri/Miles)
- UX Research Plan for comming sprints (Dmitri/Miles)
- [Frontend] Communicate to user if they are inactive [#829](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/829) (Jorge)
- Update Pa11y configuration to check more URLs and store artifacts from screenshots [#872](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/872) (Aaron)

[Link to Sprint 23 Milestone Details](https://github.com/raft-tech/TANF-app/milestone/26)
