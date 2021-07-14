# Sprint 24 Summary
**06/22/2021- 07/06/2021**

### Updates
 - For the week of 6/22 was impacted by Raft team having an onsite all-hands. This resulted in less productivity due to folks being out for travel and the all hands meetings, effectively rendering our sprint a little over 50% productivity.
- NextGen XMS decisions are still blocked by having information from the NextGen Team. We requested documentation by 7/12 and are planning to deprioritizing this work until it is unblocked, continuing to use login.gov in the meantime.
- The team is able to assess and move forward on planning for ACF AMS as of end of this sprint.


## Sprint Goals

Continue work from Sprint 23...
Finish up ATO Functionality

- Finish up file download & storage (#416, #818, #833, #834)
- Wrap up OWASP Scan tickets (#879, #865, #907,  #1032)
- Make decisions on upcoming releases
- Cron Job options for release 2 (#1011)
- NextGen XMS direction for release 1 (Epic #902, #638)
- Document feasibility and high level estimated tasks that would be needed for (1) ACF AMS or (2) ACF AMS/Next Gen (Blocked) implementation.

...Then
Attend to Permissions for OFA Admins epic

and then....
Work on DevOPs work for Production readiness

## Merged/Completed (Done/Demo, Closed)
- Dependabot Mass Merge / Improvements [#1023](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1023)
- Set up new dev environments: sandbox, raft-review, qasp-review, a11y [#848](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/848)

## Submitted (QASP Review, OCIO Review)
-[Frontend] Add a download button to the Data Files view [#416](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/416)
- [Backend] Add endpoint to download a file from S3[#833](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/833)
- Move vendor-staging in the dev space to staging in the staging space [#847](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/847)
- As a dev, I want an automated, documented CI process to provision Cloud.gov brokered services[#609](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/609)
- Issue 416: [Frontend] Add a download button to the Data Files view[#859](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/859)


## Moving to Next Sprint (Raft Review, In Progress, Current Sprint Backlog)
**Raft Review**
- Django Admin a11y Fixes (Sprint 1) [#973](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/973)

**Blocked**
- As a dev, I need to know which authentication service we're using (login.gov vs. NextGen XMS)[#638](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/638)
- SPIKE: File transfer options for Tribal MVP [#1011](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1011)

**In Progress**
- [EPIC] Round 7 (Sprint 24-26) UX Research and Design [#1017](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1017)
- As a tadpole, I want to know the platform I use to login to TDP (new TDRS) [#379](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/379)
- [Frontend] Hook upload and download to real API endpoints [#834](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/834)
- Documentation of current staging evironments for TDP [#1051](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1051)
- As an OFA Admin, I want an accessible, 508-compliant user interface for managing permissions [#892](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/892)
- (UX Sprint 24) Current State Analysis of Error Communication and Regional Staff Workflow Validation [#1018](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1018)
- SPIKE: Authentication Feasibility Research [#1046](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1046)
- Verify Admin Permissions Hierarchy and Roles[#1058](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1058)
- [Devops] Create a pa11y script which can login to the app to capture pages that require authentication [#1044](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1044)
- Update ATO docs and corresponding code docs [#962](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/962)
- [EPIC] As an OFA admin, I can download raw file [#89](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/89)


**Sprint To Do**
- As a developer/PO, I want a production site [#721](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/721)
- As tech lead, I want to know the steps that will be followed to use updated buildpacks for TDP apps [#1045](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1045)
- I want a client-side Content Security Policy to protect me from XSS and other client side attacks [#907](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/907)
- As TDP SO/TL, I need a basic security awareness training developed for IS users (AT-02) [#953](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/953)
- [DevOps] Perform validation on Codecov Bash Uploader script during CI steps [#968](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/968)
- Perform scheduled OWASP scans against deployed site(s) [#1032](Perform scheduled OWASP scans against deployed site(s)#1032)
- Deployed environments should pull AWS credentials from Cloud.gov provided environment variables [#971](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/971)


## Agenda for Sprint 24 Demo 
- Staging Evironment Setups [848](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/848) (Aaron) 
- OWASP: Exclude false positive alerts during CI/CD [#879](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/879)
- [Backend] Add endpoint to download a file from S3 [#833](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/833)(John/Aaron)
- [Frontend] Communicate to user if they are inactive [#829](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/829)(Jorge)

[Link to Sprint 24 Milestone Details](https://github.com/raft-tech/TANF-app/milestone/26)
