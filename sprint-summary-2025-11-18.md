# Sprint Summary: Nov 05, 2025 - Nov 18, 2025

## Overview

- Closed several high-priority back-end/UX items, including email templates for STT submissions, migration of Promtail to Alloy, and restricting FRA submission history to participating STTs. ([#3251](https://github.com/raft-tech/TANF-app/issues/3251), [#3258](https://github.com/raft-tech/TANF-app/issues/3258), [#3571](https://github.com/raft-tech/TANF-app/issues/3571))

- Improved navigation and readability with KC NavBar item completion and admin 'acked' column renamed to 'read'. ([#5428](https://github.com/raft-tech/TANF-app/issues/5428), [#5432](https://github.com/raft-tech/TANF-app/issues/5432))

- Boosted data reliability by fixing EXIT_MONTH parsing in XLSX and cleaning PIA submission history of non-PIA entries. ([#5463](https://github.com/raft-tech/TANF-app/issues/5463), [#5469](https://github.com/raft-tech/TANF-app/issues/5469))

- Progress on data/knowledge center workflows with Refresh Tolerant Data Files Pages completed for faster documentation access. ([#5418](https://github.com/raft-tech/TANF-app/issues/5418))

- Advancement in testing and regional onboarding planning: E2E tests for Admin Feedback Reports and Program Integrity Frontend moved toward Next Sprint Backlog, while regional onboarding items were blocked. ([#5420](https://github.com/raft-tech/TANF-app/issues/5420), [#5421](https://github.com/raft-tech/TANF-app/issues/5421), [#3461](https://github.com/raft-tech/TANF-app/issues/3461), [#3462](https://github.com/raft-tech/TANF-app/issues/3462), [#3523](https://github.com/raft-tech/TANF-app/issues/3523))

---

⚪️ **Total Issues:** 59  
✅ **Closed:** 12  
➡️ **Moved:** 19  
⬛️ **Unchanged:** 21  
🛑 **Blocked:** 7  

---

## [Goal 1: Grantees can easily submit data](https://github.com/raft-tech/TANF-app/issues/5447)

- ⬛️ [Design FRA successful processing email template (#3485)](https://github.com/raft-tech/TANF-app/issues/3485)  
_Remained in **Ready to merge into staging branch**_  

- ⬛️ [Update minimum year in FRA reporting dropdown (#3500)](https://github.com/raft-tech/TANF-app/issues/3500)  
_Remained in **Next Sprint Backlog**_  

- ⬛️ [Plan initial research for FTANF replacement (#4989)](https://github.com/raft-tech/TANF-app/issues/4989)  
_Remained in **QASP Review**_  

- ➡️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Moved from **In Progress** to **Current Sprint Backlog**_  

- ➡️ [Implement FRA Submission Emails (#5359)](https://github.com/raft-tech/TANF-app/issues/5359)  
_Moved from **Product Backlog** to **Next Sprint Backlog**_  

- ⬛️ [[Design Deliverable] Email notification for confirming program integrity audit submissions (#5363)](https://github.com/raft-tech/TANF-app/issues/5363)  
_Remained in **QASP Review**_  

- ⬛️ [Enable and fix a11y e2e tests (#5407)](https://github.com/raft-tech/TANF-app/issues/5407)  
_Remained in **In Progress**_  

- ➡️ [Implement E2E Tests for Program Integrity Audit Frontend (#5420)](https://github.com/raft-tech/TANF-app/issues/5420)  
_Moved from **Product Backlog** to **Next Sprint Backlog**_  

- ➡️ [Requirements Gathering and User Stories for Post-MVP Centralized Feedback Reports (#5443)](https://github.com/raft-tech/TANF-app/issues/5443)  
_Moved from **In Progress** to **UX Review**_  


## [Goal 2: Grantees are confident about reporting compliance](https://github.com/raft-tech/TANF-app/issues/5448)

- ⬛️ [Plan research for in-app error reporting interface (#4721)](https://github.com/raft-tech/TANF-app/issues/4721)  
_Remained in **QASP Review**_  

- ⬛️ [Complete In App Error Reports HTML Prototypes (#5300)](https://github.com/raft-tech/TANF-app/issues/5300)  
_Remained in **QASP Review**_  

- ➡️ [Update Research Protocol for In App Error Reporting Prototype (#5423)](https://github.com/raft-tech/TANF-app/issues/5423)  
_Moved from **UX Review** to **QASP Review**_  


## [Goal 3: Reduce the burden on users](https://github.com/raft-tech/TANF-app/issues/5449)

- 🛑 [Bump Grafana memory in prod by 4GB to support 1.5M record visualizations (#5269)](https://github.com/raft-tech/TANF-app/issues/5269)  
_Remained in **Blocked**_  

- ➡️ [Feedback module - submit when score is selected (rather than when "submit" is clicked) (#5431)](https://github.com/raft-tech/TANF-app/issues/5431)  
_Moved from **Current Sprint Backlog** to **In Progress**_  


## [Goal 4: Free up staff time](https://github.com/raft-tech/TANF-app/issues/5450)

- ✅ [Migrate Promtail to Alloy (#3258)](https://github.com/raft-tech/TANF-app/issues/3258)  
_**Closed**_ - _Moved from **Product Backlog**_  

- 🛑 [Create and facilitate Project Updates meeting for regional staff  (#3461)](https://github.com/raft-tech/TANF-app/issues/3461)  
_Remained in **Blocked**_  

- 🛑 [Create and facilitate optional training session for regional staff (#3462)](https://github.com/raft-tech/TANF-app/issues/3462)  
_Remained in **Blocked**_  

- 🛑 [Refine research plan for regional staff MVP onboarding experience (#3523)](https://github.com/raft-tech/TANF-app/issues/3523)  
_Remained in **Blocked**_  

- ✅ [Restrict regional staff FRA submission history to participating STTs (#3571)](https://github.com/raft-tech/TANF-app/issues/3571)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- 🛑 [Gather and iterate on OFA feedback (#3995)](https://github.com/raft-tech/TANF-app/issues/3995)  
_Remained in **Blocked**_  

- 🛑 [Gather final OFA feedback and iterate (#4045)](https://github.com/raft-tech/TANF-app/issues/4045)  
_Remained in **Blocked**_  

- 🛑 [Develop training materials, including slides, written instructions, and screenshots or screen recordings for visual guidance (#4047)](https://github.com/raft-tech/TANF-app/issues/4047)  
_Remained in **Blocked**_  

- ⬛️ [Iterate on training materials internally (#4052)](https://github.com/raft-tech/TANF-app/issues/4052)  
_Remained in **In Progress**_  

- ➡️ [Develop E2E tests for Editing Profile/Access Request (#5316)](https://github.com/raft-tech/TANF-app/issues/5316)  
_Moved from **Next Sprint Backlog** to **Current Sprint Backlog**_  

- ⬛️ [Admin Feedback Reports UI (#5390)](https://github.com/raft-tech/TANF-app/issues/5390)  
_Remained in **In Progress**_  

- ➡️ [Update Knowledge Center with Program Integrity Audit and Centralized Feedback Reports (#5391)](https://github.com/raft-tech/TANF-app/issues/5391)  
_Moved from **Next Sprint Backlog** to **Current Sprint Backlog**_  

- ✅ [Feedback Reports Backend (#5397)](https://github.com/raft-tech/TANF-app/issues/5397)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Add alert banner to knowledge center regarding government shutdown (#5398)](https://github.com/raft-tech/TANF-app/issues/5398)  
_**Closed**_ - _Moved from **Blocked**_  

- ➡️ [Write KC Content for PI Audit and Centralized Feedback Reports (#5406)](https://github.com/raft-tech/TANF-app/issues/5406)  
_Moved from **UX Review** to **QASP Review**_  

- ➡️ [STT Feedback Report UI (#5417)](https://github.com/raft-tech/TANF-app/issues/5417)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ✅ [Refresh Tolerant Data Files Pages (#5418)](https://github.com/raft-tech/TANF-app/issues/5418)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [KC NavBar Item (#5428)](https://github.com/raft-tech/TANF-app/issues/5428)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Fully implement Knowledge Center component navigation & search (#5429)](https://github.com/raft-tech/TANF-app/issues/5429)  
_Moved from **In Progress** to **UX Review**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ⬛️ [Bug: OFA system admin users get stuck if region is assigned (#3515)](https://github.com/raft-tech/TANF-app/issues/3515)  
_Remained in **Raft (Dev) Review**_  

- ✅ [Bug: Regional Access Request – Pre-selected option & typo (#4924)](https://github.com/raft-tech/TANF-app/issues/4924)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [[BUG] User STT and Region assignment validation on user group change (#5368)](https://github.com/raft-tech/TANF-app/issues/5368)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ⬛️ [Switch to React Router links for internal navigation (#2008)](https://github.com/raft-tech/TANF-app/issues/2008)  
_Remained in **Next Sprint Backlog**_  

- ⬛️ [Implement user deletion support in DAC while retaining associated objects (#3089)](https://github.com/raft-tech/TANF-app/issues/3089)  
_Remained in **In Progress**_  

- ➡️ [Add bulk user deactivation and inactivity filter for system admins (#3090)](https://github.com/raft-tech/TANF-app/issues/3090)  
_Moved from **Current Sprint Backlog** to **Next Sprint Backlog**_  

- ⬛️ [Fix health dashboard to respect environment filters (#3611)](https://github.com/raft-tech/TANF-app/issues/3611)  
_Remained in **Next Sprint Backlog**_  

- ⬛️ [Reorganize the parser (#5414)](https://github.com/raft-tech/TANF-app/issues/5414)  
_Remained in **Next Sprint Backlog**_  

- ➡️ [Delete vault integration from backend (#5416)](https://github.com/raft-tech/TANF-app/issues/5416)  
_Moved from **Next Sprint Backlog** to **Current Sprint Backlog**_  

- ✅ [Change admin "acked" column to "read" (#5432)](https://github.com/raft-tech/TANF-app/issues/5432)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ⬛️ [Implement automated past due submission email notifications (#2984)](https://github.com/raft-tech/TANF-app/issues/2984)  
_Remained in **Next Sprint Backlog**_  

- ✅ [Update email templates for STT data submissions re: status and error guidance (#3251)](https://github.com/raft-tech/TANF-app/issues/3251)  
_**Closed**_ - _Moved from **QASP Review**_  

- ⬛️ [Create email templates for reparsing (new error report & error resolution) (#3263)](https://github.com/raft-tech/TANF-app/issues/3263)  
_Remained in **QASP Review**_  

- ⬛️ [Implement spinner for TANF / SSP data file submissions (#3564)](https://github.com/raft-tech/TANF-app/issues/3564)  
_Remained in **In Progress**_  

- ⬛️ [Create research plan template for UX Playbook (#5369)](https://github.com/raft-tech/TANF-app/issues/5369)  
_Remained in **QASP Review**_  

- ⬛️ [Create a Journey Mapping template & document best practices (#5371)](https://github.com/raft-tech/TANF-app/issues/5371)  
_Remained in **QASP Review**_  

- ⬛️ [Create a QA Checklist for Completing UX & Dev Reviews (#5374)](https://github.com/raft-tech/TANF-app/issues/5374)  
_Remained in **QASP Review**_  

- ⬛️ [Create a guide for Conducting a Heuristic Evaluation (Checklist + Best Practices) (#5375)](https://github.com/raft-tech/TANF-app/issues/5375)  
_Remained in **Next Sprint Backlog**_  


## Issues without Parent

- ➡️ [Implement E2E Tests for Admin Feedback Reports (#5421)](https://github.com/raft-tech/TANF-app/issues/5421)  
_Moved from **Product Backlog** to **Next Sprint Backlog**_  

- ➡️ [Refactor and cleanup parsing logic tech memo (#5434)](https://github.com/raft-tech/TANF-app/issues/5434)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Update education level validation for adults when family affiliation is 2 or 3 (#5461)](https://github.com/raft-tech/TANF-app/issues/5461)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ✅ [Datetime Field Type for EXIT_MONTH in Xlsx Files Causing Parsing Failure (#5463)](https://github.com/raft-tech/TANF-app/issues/5463)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ✅ [PIA Submission History Contains Non-PIA Submissions (#5469)](https://github.com/raft-tech/TANF-app/issues/5469)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Fix cat 2 validation on SSP Item # 41 (WEI) (#5473)](https://github.com/raft-tech/TANF-app/issues/5473)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Update SSN_VALID logic in SQL Views (#5475)](https://github.com/raft-tech/TANF-app/issues/5475)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Feature Toggle Tech Memo (#5476)](https://github.com/raft-tech/TANF-app/issues/5476)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


