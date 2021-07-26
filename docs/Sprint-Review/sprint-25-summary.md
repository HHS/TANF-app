# Sprint 25 Summary
**07/06/2021- 07/20/2021**

### Summary Updates
- The Engineering team continued to work on Secret Key Epic tickets and various devops related tickets to finishing out ATO functionality as well as accessibility work for Django admin and other areas.
- The UX Research team focused on Parsing Error blockers and understanding Regional Staff user journeys, and began investigations into the user access request journey
- NextGen XMS and ACF AMS teams have given us technical information in order to assess and estimate our technical implimentation and recommendation to TDP Product Owner and tech lead. Our next task is to write integration tickets and estimate this work and provide a recommendation to OFA.


## Sprint 25 Goals
- Finish closing ATO functionality tickets
- Focus on Secret Key Leakage Mitigation Epic
- UX Ideation for Parsing Blocker Communications

**[Next Sprint (26) Goals](https://github.com/raft-tech/TANF-app/milestone/29)** 
- 

## Merged/Completed (Done/Demo, Closed)
- Django Admin a11y Fixes (Sprint 1) [#973](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/973)
- (UX Sprint 24) Current State Analysis of Error Communication and Regional Staff Workflow Validation [#1018](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1018)
- Documentation of current staging environments for TDP [#1051](https://app.zenhub.com/workspaces/tdrs-product-backlog-5f2c6cdc7c0bb1001bdc43a5/issues/raft-tech/tanf-app/1051)
SPIKE: File transfer options for Tribal MVP [#1011](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1011)
## Submitted (QASP Review, OCIO Review)
- Dependabot Mass Merge / Improvements [#1023](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1023)
- Verify Admin Permissions Hierarchy and Roles [#1058](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1058)

## Moving to Next Sprint (Raft Review, In Progress, Current Sprint Backlog)
**Raft Review**
- [EPIC] As an OFA admin, I can download raw file [#89](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/89)
- Groups: Rename `Data Prepper` to `Data Analyst` [#1071](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1071)
- Perform scheduled OWASP scans against deployed site(s) [#1032](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1032)
- [Devops] Allow pa11y to scan views that require authorization [#1044](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1044)
- [Frontend] Hook upload and download to real API endpoints [#834](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/834)


**Blocked**
- Update ATO docs and corresponding code docs [#962](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/962)
- 

**In Progress**
- Django Admin a11y Fixes (Sprint 2)[#1053](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1053)
- As a tadpole, I want to know the platform I use to login to TDP (new TDRS)[#379](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/379)
- As tech lead, I want to know the steps that will be followed to use updated buildpacks for TDP apps [#1045](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1045)
- As an OFA Admin, I want an accessible, 508-compliant user interface for managing permissions [#892](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/892)
- Deployed environments should pull AWS credentials from Cloud.gov provided environment variables [#971](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/971)
- SPIKE: Authentication Feasibility Research [#1046](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1046)

**Current Sprint Backlog**
- As a dev, I need to know which authentication service we're using (login.gov vs. NextGen XMS) [#638](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/638)
- [DevOps] Generate a new, random DJANGO_SECRET_KEY on initial Cloud.gov deployments or rebuilds [#967](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/967)
- As a dev, I want an automated tool to prevent me from committing secret keys to the repo [#965](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/965)
- [EPIC] Secret Key Leakage Mitigation [#972](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/972)
- As TDP SO/TL, I need a basic security awareness training developed for IS users (AT-02)[#953](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/953)
- I want a client-side Content Security Policy to protect me from XSS and other client side attacks [#907](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/907)
- Audit Config & Inspection for Production Environment [#897](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/897)
- As a dev, I want Terraform changes to be reflected in label driven deployments (GitHub Action) [#1059](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1059)
- [DevOps] Perform validation on Codecov Bash Uploader script during CI steps [#968](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/968)


## Agenda for Sprint 25 Demo 
- (UX Sprint 24) Current State Analysis of Error Communication and Regional Staff Workflow Validation [#1018](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1018) - Miles/ Dmitri
- TDP Staging Site [#1051](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1051) - Jorge
- Django Admin a11y Fixes (Sprint 1) [#973](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/973) - Jorge, locally 
- (Pre QASP)[Frontend] Hook upload and download to real API endpoints [#834](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/834) - John
- (Pre QASP)[Devops] Allow pa11y to scan views that require authorization [#1044](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1044) - Aaron


[Link to Sprint 25 Milestone Details](https://github.com/raft-tech/TANF-app/milestone/28)
