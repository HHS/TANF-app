# Sprint Summary: Jan 21, 2026 - Feb 03, 2026

## Overview

- Completed/closed several high-priority items, including Celery Apps not being Monitored, Refactor/transition of NavItem to React Router, TANF datafile Redux state bug, transient E2E test failures on develop, missing DAC file download links, and tribal STTs appearance bug. ([#5494](https://github.com/raft-tech/TANF-app/issues/5494), [#5497](https://github.com/raft-tech/TANF-app/issues/5497), [#5582](https://github.com/raft-tech/TANF-app/issues/5582), [#5577](https://github.com/raft-tech/TANF-app/issues/5577), [#5592](https://github.com/raft-tech/TANF-app/issues/5592), [#5597](https://github.com/raft-tech/TANF-app/issues/5597))
- Progressed key refactor/work items: parsing logic cleanup, time-between-parse spike moved to In Progress, E2E tests for admin feedback moving toward Dev Review, and E2E scope moving to Raft Dev Review. ([#5434](https://github.com/raft-tech/TANF-app/issues/5434), [#5474](https://github.com/raft-tech/TANF-app/issues/5474), [#5477](https://github.com/raft-tech/TANF-app/issues/5477))
- UX and training materials advanced: training materials iteration in progress; UX playbook templates in plan; journey mapping and knowledge center navigation/search moving forward. ([#4052](https://github.com/raft-tech/TANF-app/issues/4052), [#5369](https://github.com/raft-tech/TANF-app/issues/5369), [#5371](https://github.com/raft-tech/TANF-app/issues/5371), [#5429](https://github.com/raft-tech/TANF-app/issues/5429))
- Blockers persist for regional staff initiatives and onboarding work, with several items blocked; examples include project updates and training sessions stalled. ([#3461](https://github.com/raft-tech/TANF-app/issues/3461), [#3462](https://github.com/raft-tech/TANF-app/issues/3462), [#3523](https://github.com/raft-tech/TANF-app/issues/3523), [#3995](https://github.com/raft-tech/TANF-app/issues/3995), [#4045](https://github.com/raft-tech/TANF-app/issues/4045), [#4047](https://github.com/raft-tech/TANF-app/issues/4047), [#5269](https://github.com/raft-tech/TANF-app/issues/5269))

---

⚪️ **Total Issues:** 46  
✅ **Closed:** 6  
➡️ **Moved:** 13  
⬛️ **Unchanged:** 19  
🛑 **Blocked:** 8  

---

## [Goal 1: Grantees can easily submit data](https://github.com/raft-tech/TANF-app/issues/5447)

- ⬛️ [Plan initial research for FTANF replacement (#4989)](https://github.com/raft-tech/TANF-app/issues/4989)  
_Remained in **QASP Review**_  

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  


## [Goal 2: Grantees are confident about reporting compliance](https://github.com/raft-tech/TANF-app/issues/5448)

- ⬛️ [Complete In App Error Reports HTML Prototypes (#5300)](https://github.com/raft-tech/TANF-app/issues/5300)  
_Remained in **QASP Review**_  

- ➡️ [Update Research Protocol for In App Error Reporting (#5423)](https://github.com/raft-tech/TANF-app/issues/5423)  
_Moved from **In Progress** to **UX Review**_  

- ➡️ [Update Figma with Feedback & Error Report Examples (#5425)](https://github.com/raft-tech/TANF-app/issues/5425)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [E2E Test for Same FY/Q/STT Across Program Types (#5477)](https://github.com/raft-tech/TANF-app/issues/5477)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ⬛️ [Implement Updated email templates for STT data submissions re: status and error guidance (#5478)](https://github.com/raft-tech/TANF-app/issues/5478)  
_Remained in **Raft (Dev) Review**_  


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

- ➡️ [STT Feedback Report UI (#5417)](https://github.com/raft-tech/TANF-app/issues/5417)  
_Moved from **UX Review** to **In Progress**_  

- ⬛️ [Fully implement Knowledge Center component navigation & search (#5429)](https://github.com/raft-tech/TANF-app/issues/5429)  
_Remained in **QASP Review**_  

- ⬛️ [FeatureFlag Model and Admin Interface (#5531)](https://github.com/raft-tech/TANF-app/issues/5531)  
_Remained in **Raft (Dev) Review**_  

- ➡️ [Cache Service Implementation (#5532)](https://github.com/raft-tech/TANF-app/issues/5532)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Feature Flag Cache Integration with Django Signals (#5533)](https://github.com/raft-tech/TANF-app/issues/5533)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ⬛️ [Upgrade Backend Dependencies (#5535)](https://github.com/raft-tech/TANF-app/issues/5535)  
_Remained in **In Progress**_  


## [Goal 5: Improve data quality](https://github.com/raft-tech/TANF-app/issues/5451)

- ⬛️ [[Tech Memo]: Refactor and cleanup parsing logic (#5434)](https://github.com/raft-tech/TANF-app/issues/5434)  
_Remained in **In Progress**_  


## [Goal 6: Documentation is current and helpful](https://github.com/raft-tech/TANF-app/issues/5435)

- ⬛️ [Create research plan template for UX Playbook (#5369)](https://github.com/raft-tech/TANF-app/issues/5369)  
_Remained in **QASP Review**_  

- ⬛️ [Create a Journey Mapping template & document best practices (#5371)](https://github.com/raft-tech/TANF-app/issues/5371)  
_Remained in **QASP Review**_  

- ⬛️ [Create a QA Checklist for Completing UX & Dev Reviews (#5374)](https://github.com/raft-tech/TANF-app/issues/5374)  
_Remained in **QASP Review**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ✅ [[Bug]: Celery Apps not being Monitored (#5494)](https://github.com/raft-tech/TANF-app/issues/5494)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ➡️ [Refactor and optimize test_parse.py for better maintainability and performance (#2641)](https://github.com/raft-tech/TANF-app/issues/2641)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Replace axios with native Fetch API for HTTP requests (#3333)](https://github.com/raft-tech/TANF-app/issues/3333)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ⬛️ [Create email templates for reparsing (new error report & error resolution) (#3263)](https://github.com/raft-tech/TANF-app/issues/3263)  
_Remained in **QASP Review**_  


## Issues without Parent

- 🛑 [Implement E2E Tests for Admin Feedback Reports (#5421)](https://github.com/raft-tech/TANF-app/issues/5421)  
_Moved from **In Progress** to **Blocked**_  

- ➡️ [Spike: Investigate Time Between Parse Spikes (#5474)](https://github.com/raft-tech/TANF-app/issues/5474)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ➡️ [Display Requested Changes in Profile Page (#5490)](https://github.com/raft-tech/TANF-app/issues/5490)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ✅ [Transition NavItem component to React Router navigation (#5497)](https://github.com/raft-tech/TANF-app/issues/5497)  
_**Closed**_ - _Moved from **In Progress**_  

- ⬛️ [Rhode Island should be able to submit SSP data via TDP starting in FY2026 (#5521)](https://github.com/raft-tech/TANF-app/issues/5521)  
_Remained in **In Progress**_  

- ⬛️ [Re-start submission status polling on page navigation/refresh (#5525)](https://github.com/raft-tech/TANF-app/issues/5525)  
_Remained in **In Progress**_  

- ⬛️ [Upload Panel State Reset on Accepted Files (#5527)](https://github.com/raft-tech/TANF-app/issues/5527)  
_Remained in **In Progress**_  

- ✅ [Investigate and resolve transient E2E test failures on develop (#5577)](https://github.com/raft-tech/TANF-app/issues/5577)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Bug: TANF datafile feedback attachments not included due to stale Redux state (#5582)](https://github.com/raft-tech/TANF-app/issues/5582)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ⬛️ ["Parsing Complete" banner interrupts screenreader reading of "Successfully Submitted" (#5584)](https://github.com/raft-tech/TANF-app/issues/5584)  
_Remained in **Current Sprint Backlog**_  

- ⬛️ [Spike: Explore Rapid Research Methodologies to Capture Ongoing User Feedback (#5588)](https://github.com/raft-tech/TANF-app/issues/5588)  
_Remained in **UX Review**_  

- ⬛️ [Inconsistent File Status (#5591)](https://github.com/raft-tech/TANF-app/issues/5591)  
_Remained in **Current Sprint Backlog**_  

- ✅ [File Download Links Missing in DAC (#5592)](https://github.com/raft-tech/TANF-app/issues/5592)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Moved from **Product Backlog** to **In Progress**_  

- ✅ [Bug: Tribal STTs appear in STTCombobox on FRA Data Files page for non-regional staff users (#5597)](https://github.com/raft-tech/TANF-app/issues/5597)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Feature: Restore accessibility for Submit button on Data Files pages (#5598)](https://github.com/raft-tech/TANF-app/issues/5598)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [Enhancement: Submission Email Copy and Link Corrections (#5599)](https://github.com/raft-tech/TANF-app/issues/5599)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


