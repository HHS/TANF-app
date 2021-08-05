# Sprint 26 Summary
**07/20/2021 - 08/03/2021**

### Summary Updates
- Finish up Secret Key Leakage Mitigation
- Present recommendation re: authentication
- Continue work on Production readiness
- UX Test Error Communication for Parsing
- Blockers + Authentication Request Workflow


## Sprint 26 Goals

- Finish closing ATO functionality tickets
- Focus on Secret Key Leakage Mitigation Epic
- UX Ideation for Parsing Blocker Communications

[**Next Sprint (27) Goals:**](https://github.com/raft-tech/TANF-app/milestone/30) 
- TDP Permissions Epics (TDP Permissions Matrix, OFA Admins, PIV/CAC)
- Continue work on Production readiness
- UX:
 - 1. Access Request UX/UI
 - 2. Continue Error UX/UI, parsing + other errors


## Closed/Merged/Completed (Done/Demo, Closed)
- As an OFA admin, I can download raw file [#89](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/89)
- Django Admin a11y Fixes (Sprint 1)[#973](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/973)
- Verify Admin Permissions Hierarchy and Roles [#1058](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1058)
- Deployed environments should pull AWS credentials from Cloud.gov provided environment variables [#971](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/971)
- Perform scheduled OWASP scans against deployed site(s)[#1032](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1032)
- [DevOps] Perform validation on Codecov Bash Uploader script during CI steps [#968](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/968)
- [Frontend] Hook upload and download to real API endpoints [#834](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/834)
- As tech lead, I want to know the steps that will be followed to use updated buildpacks for TDP apps [#1045](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1045)
- Groups: Rename `Data Prepper` to `Data Analyst`[#1071](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1071)
- (UX Sprint 24) Current State Analysis of Error Communication and Regional Staff Workflow Validation [#1018](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1018)
- Dependabot Mass Merge / Improvements [#1023](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1023)


## Submitted (QASP Review, OCIO Review)
- As a dev, I want an automated tool to prevent me from committing secret keys to the repo [#965](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/965)
- [DevOps] Generate a new, random DJANGO_SECRET_KEY on initial Cloud.gov deployments or rebuilds [#967](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/967)

## Moving to Next Sprint (Raft Review, In Progress, Current Sprint Backlog)
**Raft Review**
- I want a Content Security Policy to protect me from XSS and other client side attacks [#907](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/907)
- Django Admin a11y Fixes (Sprint 2)  [#1053](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1053)
- (UX Sprint 26) Test Error Communication for Parsing Blockers [#1020](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1020)
- (UX Sprint 25) Ideation for Parsing Blocker Communication [#1019](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1019)
- [Devops] Allow pa11y to scan views that require authorization [#1044](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1044)
- SPIKE: Authentication Feasibility Research [#1046](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1046)
- Update ATO docs and corresponding code docs [#962](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/962)


**Blocked**
- As a dev, I want Terraform changes to be reflected in label driven deployments (GitHub Action) [#1059](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1059)

**In Progress**
- Secret Key Leakage Mitigation [#972](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/972)
- Round 7 (Sprint 24-26) UX Research and Design [#1017](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1017)
- [Backend] Change reports to data files [#755](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/755)
- As an OFA Admin, I want an accessible, 508-compliant user interface for managing permissions [#892](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/892)
- [Backend] Utilize Django settings modules for non-sensitive environment variables that differ between deployed environments [#970](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/970)
- Round 7 (Sprint 24-26) UX Research and Design#1017

**Current Sprint Backlog**
- As a dev, I need to know which authentication service we're using (login.gov vs. NextGen XMS) [#638](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/638)
- As a TDP user, I want to see a picture that better represents the program [#640](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/640)


## Agenda for Sprint 26 Demo 
- As a dev, I want an automated tool to prevent me from committing secret keys to the repo [#965](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/965) Andrew
- [DevOps] Generate a new, random DJANGO_SECRET_KEY on initial Cloud.gov deployments or rebuilds [#967](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/967) - Andrew/John
- (From Last Sprint) Perform scheduled OWASP scans against deployed site(s)[#1032](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1032)- Aaron
- (UX Sprint 26) Test Error Communication for Parsing Blockers [#1020](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1020) - Miles/Dmitri
- Round 7 (Sprint 24-26) UX Research and Design [#1017](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1017)
- Django Admin a11y Fixes (Sprint 3) [#1054](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1054)
- UX Roadmap prep [#1147](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1147)


[Link to Sprint 26 Milestone Details](https://github.com/raft-tech/TANF-app/milestone/29)
