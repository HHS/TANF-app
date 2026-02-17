# Sprint Summary: Dec 03, 2025 - Dec 16, 2025

## Overview

- Significant closures across core delivery: E2E tests, FRA emails, and PI audit/internal UX outputs completed, moving several items from In Progress to Closed. ([#5316](https://github.com/raft-tech/TANF-app/issues/5316), [#5359](https://github.com/raft-tech/TANF-app/issues/5359), [#5363](https://github.com/raft-tech/TANF-app/issues/5363), [#5406](https://github.com/raft-tech/TANF-app/issues/5406), [#5407](https://github.com/raft-tech/TANF-app/issues/5407), [#5416](https://github.com/raft-tech/TANF-app/issues/5416))

- Stability and data integrity improvements advanced with backend fixes and vulnerability remediation: SSN_VALID logic updated, Postgres view issue resolved, NPM vulnerabilities addressed. ([#5475](https://github.com/raft-tech/TANF-app/issues/5475), [#5483](https://github.com/raft-tech/TANF-app/issues/5483), [#5507](https://github.com/raft-tech/TANF-app/issues/5507))

- Planning and prep tasks advanced to future sprint boundaries; design deliverables and parsing refactor moved from Current Sprint Backlog to Next Sprint Backlog. ([#5223](https://github.com/raft-tech/TANF-app/issues/5223), [#5434](https://github.com/raft-tech/TANF-app/issues/5434))

- Ongoing training materials progress is mixed; some iteration continues, while regional staff onboarding work remains blocked. ([#4047](https://github.com/raft-tech/TANF-app/issues/4047), [#4052](https://github.com/raft-tech/TANF-app/issues/4052), [#3461](https://github.com/raft-tech/TANF-app/issues/3461), [#3462](https://github.com/raft-tech/TANF-app/issues/3462), [#3523](https://github.com/raft-tech/TANF-app/issues/3523))

---

⚪️ **Total Issues:** 43  
✅ **Closed:** 15  
➡️ **Moved:** 8  
⬛️ **Unchanged:** 12  
🛑 **Blocked:** 8  

---

## [Goal 1: Grantees can easily submit data](https://github.com/raft-tech/TANF-app/issues/5447)

- ⬛️ [Design FRA successful processing email template (#3485)](https://github.com/raft-tech/TANF-app/issues/3485)  
_Remained in **Ready to merge into staging branch**_  

- ⬛️ [Plan initial research for FTANF replacement (#4989)](https://github.com/raft-tech/TANF-app/issues/4989)  
_Remained in **QASP Review**_  

- ➡️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Moved from **Current Sprint Backlog** to **Next Sprint Backlog**_  

- ✅ [Implement FRA Submission Emails (#5359)](https://github.com/raft-tech/TANF-app/issues/5359)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [[Design Deliverable] Email notification for confirming program integrity audit submissions (#5363)](https://github.com/raft-tech/TANF-app/issues/5363)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Enable and fix a11y e2e tests (#5407)](https://github.com/raft-tech/TANF-app/issues/5407)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Requirements Gathering and User Stories for Post-MVP Centralized Feedback Reports (#5443)](https://github.com/raft-tech/TANF-app/issues/5443)  
_**Closed**_ - _Moved from **QASP Review**_  


## [Goal 2: Grantees are confident about reporting compliance](https://github.com/raft-tech/TANF-app/issues/5448)

- ⬛️ [Plan research for in-app error reporting interface (#4721)](https://github.com/raft-tech/TANF-app/issues/4721)  
_Remained in **QASP Review**_  

- ⬛️ [Complete In App Error Reports HTML Prototypes (#5300)](https://github.com/raft-tech/TANF-app/issues/5300)  
_Remained in **QASP Review**_  

- ⬛️ [Update Research Protocol for In App Error Reporting Prototype (#5423)](https://github.com/raft-tech/TANF-app/issues/5423)  
_Remained in **QASP Review**_  

- ➡️ [Update Figma with Feedback & Error Report Examples (#5425)](https://github.com/raft-tech/TANF-app/issues/5425)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Implement Updated email templates for STT data submissions re: status and error guidance (#5478)](https://github.com/raft-tech/TANF-app/issues/5478)  
_Moved from **Product Backlog** to **Raft (Dev) Review**_  


## [Goal 3: Reduce the burden on users](https://github.com/raft-tech/TANF-app/issues/5449)

- 🛑 [Bump Grafana memory in prod by 4GB to support 1.5M record visualizations (#5269)](https://github.com/raft-tech/TANF-app/issues/5269)  
_Remained in **Blocked**_  


## [Goal 4: Free up staff time](https://github.com/raft-tech/TANF-app/issues/5450)

- 🛑 [Create and facilitate Project Updates meeting for regional staff  (#3461)](https://github.com/raft-tech/TANF-app/issues/3461)  
_Remained in **Blocked**_  

- 🛑 [Create and facilitate optional training session for regional staff (#3462)](https://github.com/raft-tech/TANF-app/issues/3462)  
_Remained in **Blocked**_  

- 🛑 [Refine research plan for regional staff MVP onboarding experience (#3523)](https://github.com/raft-tech/TANF-app/issues/3523)  
_Remained in **Blocked**_  

- 🛑 [Gather and iterate on OFA feedback (#3995)](https://github.com/raft-tech/TANF-app/issues/3995)  
_Remained in **Blocked**_  

- 🛑 [Gather final OFA feedback and iterate (#4045)](https://github.com/raft-tech/TANF-app/issues/4045)  
_Remained in **Blocked**_  

- 🛑 [Develop training materials, including slides, written instructions, and screenshots or screen recordings for visual guidance (#4047)](https://github.com/raft-tech/TANF-app/issues/4047)  
_Remained in **Blocked**_  

- ⬛️ [Iterate on training materials internally (#4052)](https://github.com/raft-tech/TANF-app/issues/4052)  
_Remained in **In Progress**_  

- ✅ [Develop E2E tests for Editing Profile/Access Request (#5316)](https://github.com/raft-tech/TANF-app/issues/5316)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Admin Feedback Reports UI (#5390)](https://github.com/raft-tech/TANF-app/issues/5390)  
_Moved from **Raft (Dev) Review** to **UX Review**_  

- ➡️ [Update Knowledge Center with Program Integrity Audit and Centralized Feedback Reports (#5391)](https://github.com/raft-tech/TANF-app/issues/5391)  
_Moved from **Current Sprint Backlog** to **Next Sprint Backlog**_  

- ✅ [Write KC Content for PI Audit and Centralized Feedback Reports (#5406)](https://github.com/raft-tech/TANF-app/issues/5406)  
_**Closed**_ - _Moved from **In Progress**_  

- 🛑 [STT Feedback Report UI (#5417)](https://github.com/raft-tech/TANF-app/issues/5417)  
_Moved from **In Progress** to **Blocked**_  

- ⬛️ [Fully implement Knowledge Center component navigation & search (#5429)](https://github.com/raft-tech/TANF-app/issues/5429)  
_Remained in **QASP Review**_  

- ✅ [[Tech Memo]: Feature Toggle (#5476)](https://github.com/raft-tech/TANF-app/issues/5476)  
_**Closed**_ - _Moved from **In Progress**_  


## [Goal 5: Improve data quality](https://github.com/raft-tech/TANF-app/issues/5451)

- ➡️ [[Tech Memo]: Refactor and cleanup parsing logic (#5434)](https://github.com/raft-tech/TANF-app/issues/5434)  
_Moved from **Current Sprint Backlog** to **Next Sprint Backlog**_  

- ✅ [Update education level validation for adults when family affiliation is 2 or 3 (#5461)](https://github.com/raft-tech/TANF-app/issues/5461)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [Fix cat 2 validation on SSP Item # 41 (WEI) (#5473)](https://github.com/raft-tech/TANF-app/issues/5473)  
_Remained in **In Progress**_  

- ✅ [Update SSN_VALID logic in SQL Views (#5475)](https://github.com/raft-tech/TANF-app/issues/5475)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  


## [Goal 6: Documentation is current and helpful](https://github.com/raft-tech/TANF-app/issues/5435)

- ⬛️ [Create research plan template for UX Playbook (#5369)](https://github.com/raft-tech/TANF-app/issues/5369)  
_Remained in **QASP Review**_  

- ⬛️ [Create a Journey Mapping template & document best practices (#5371)](https://github.com/raft-tech/TANF-app/issues/5371)  
_Remained in **QASP Review**_  

- ⬛️ [Create a QA Checklist for Completing UX & Dev Reviews (#5374)](https://github.com/raft-tech/TANF-app/issues/5374)  
_Remained in **QASP Review**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ✅ [Bug: OFA system admin users get stuck if region is assigned (#3515)](https://github.com/raft-tech/TANF-app/issues/3515)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [[Bug]: Postgres View Does Not Exist (#5483)](https://github.com/raft-tech/TANF-app/issues/5483)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [[Bug]: Celery Apps not being Monitored (#5494)](https://github.com/raft-tech/TANF-app/issues/5494)  
_Moved from **Current Sprint Backlog** to **Next Sprint Backlog**_  

- ✅ [[Bug]: Investigate e2e test failures in `develop` (#5495)](https://github.com/raft-tech/TANF-app/issues/5495)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ✅ [Delete vault integration from backend (#5416)](https://github.com/raft-tech/TANF-app/issues/5416)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Investigate and Resolve NPM Package Vulnerabilities (#5507)](https://github.com/raft-tech/TANF-app/issues/5507)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Optimize Docker base images to reduce size (#5512)](https://github.com/raft-tech/TANF-app/issues/5512)  
_Moved from **Product Backlog** to **Next Sprint Backlog**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ⬛️ [Create email templates for reparsing (new error report & error resolution) (#3263)](https://github.com/raft-tech/TANF-app/issues/3263)  
_Remained in **QASP Review**_  

- ✅ [Implement spinner for TANF / SSP data file submissions (#3564)](https://github.com/raft-tech/TANF-app/issues/3564)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


