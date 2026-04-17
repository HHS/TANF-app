# Sprint Summary: Feb 04, 2026 - Feb 17, 2026

## Overview

- Closed a batch of UX and knowledge-center deliverables, including templates, journey mapping, QA checklist, STT feedback UI, Knowledge Center navigation, and Rhode Island SSP submission, delivering tangible completed work this sprint. ([#5369](https://github.com/raft-tech/TANF-app/issues/5369), [#5371](https://github.com/raft-tech/TANF-app/issues/5371), [#5374](https://github.com/raft-tech/TANF-app/issues/5374), [#5417](https://github.com/raft-tech/TANF-app/issues/5417), [#5429](https://github.com/raft-tech/TANF-app/issues/5429), [#5521](https://github.com/raft-tech/TANF-app/issues/5521))

- Strengthened testing and research processes: E2E tests for Admin Feedback Reports progressed from Blocked to In Progress; update to research protocol moved to UX Review. ([#5421](https://github.com/raft-tech/TANF-app/issues/5421), [#5423](https://github.com/raft-tech/TANF-app/issues/5423))

- Parsing and data handling enhancements progressed: refactor of test_parse.py advanced and time-between-parse-spikes spike activity continued. ([#2641](https://github.com/raft-tech/TANF-app/issues/2641), [#5474](https://github.com/raft-tech/TANF-app/issues/5474))

- Backend and infrastructure improvements completed: backend dependencies upgrade closed. ([#5535](https://github.com/raft-tech/TANF-app/issues/5535))

- Blockers persisted across regional staff initiatives, limiting momentum on several onboarding/training efforts. ([#3461](https://github.com/raft-tech/TANF-app/issues/3461), [#3462](https://github.com/raft-tech/TANF-app/issues/3462), [#3523](https://github.com/raft-tech/TANF-app/issues/3523), [#3995](https://github.com/raft-tech/TANF-app/issues/3995), [#4045](https://github.com/raft-tech/TANF-app/issues/4045), [#4047](https://github.com/raft-tech/TANF-app/issues/4047), [#5269](https://github.com/raft-tech/TANF-app/issues/5269))

---

⚪️ **Total Issues:** 46  
✅ **Closed:** 8  
➡️ **Moved:** 12  
⬛️ **Unchanged:** 19  
🛑 **Blocked:** 7  

---

## [Goal 1: Grantees can easily submit data](https://github.com/raft-tech/TANF-app/issues/5447)

- ⬛️ [Plan initial research for FTANF replacement (#4989)](https://github.com/raft-tech/TANF-app/issues/4989)  
_Remained in **QASP Review**_  

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  


## [Goal 2: Grantees are confident about reporting compliance](https://github.com/raft-tech/TANF-app/issues/5448)

- ⬛️ [Complete In App Error Reports HTML Prototypes (#5300)](https://github.com/raft-tech/TANF-app/issues/5300)  
_Remained in **QASP Review**_  

- ➡️ [Update Research Protocol for In-app Error Reporting (#5423)](https://github.com/raft-tech/TANF-app/issues/5423)  
_Moved from **In Progress** to **UX Review**_  

- ⬛️ [Update Figma with Feedback & Error Report Examples (#5425)](https://github.com/raft-tech/TANF-app/issues/5425)  
_Remained in **In Progress**_  

- ⬛️ [E2E Test for Same FY/Q/STT Across Program Types (#5477)](https://github.com/raft-tech/TANF-app/issues/5477)  
_Remained in **Raft (Dev) Review**_  

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

- ✅ [STT Feedback Report UI (#5417)](https://github.com/raft-tech/TANF-app/issues/5417)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Fully implement Knowledge Center component navigation & search (#5429)](https://github.com/raft-tech/TANF-app/issues/5429)  
_**Closed**_ - _Moved from **QASP Review**_  

- ⬛️ [FeatureFlag Model and Admin Interface (#5531)](https://github.com/raft-tech/TANF-app/issues/5531)  
_Remained in **Raft (Dev) Review**_  

- ⬛️ [Cache Service Implementation (#5532)](https://github.com/raft-tech/TANF-app/issues/5532)  
_Remained in **In Progress**_  

- ➡️ [Feature Flag Cache Integration with Django Signals (#5533)](https://github.com/raft-tech/TANF-app/issues/5533)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Feature Flag REST API Endpoint (#5534)](https://github.com/raft-tech/TANF-app/issues/5534)  
_Moved from **Product Backlog** to **In Progress**_  

- ✅ [Upgrade Backend Dependencies (#5535)](https://github.com/raft-tech/TANF-app/issues/5535)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Feature Flag Auditing and Versioning (#5536)](https://github.com/raft-tech/TANF-app/issues/5536)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Feature Flags Redux State Management (#5540)](https://github.com/raft-tech/TANF-app/issues/5540)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Feature Flags Auth Integration, Hook, and FeatureGate Component (#5541)](https://github.com/raft-tech/TANF-app/issues/5541)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


## [Goal 5: Improve data quality](https://github.com/raft-tech/TANF-app/issues/5451)

- ⬛️ [[Tech Memo]: Refactor and cleanup parsing logic (#5434)](https://github.com/raft-tech/TANF-app/issues/5434)  
_Remained in **In Progress**_  


## [Goal 6: Documentation is current and helpful](https://github.com/raft-tech/TANF-app/issues/5435)

- ✅ [Create research plan template for UX Playbook (#5369)](https://github.com/raft-tech/TANF-app/issues/5369)  
_**Closed**_ - _Moved from **QASP Review**_  

- ✅ [Create a Journey Mapping template & document best practices (#5371)](https://github.com/raft-tech/TANF-app/issues/5371)  
_**Closed**_ - _Moved from **QASP Review**_  

- ✅ [Create a QA Checklist for Completing UX & Dev Reviews (#5374)](https://github.com/raft-tech/TANF-app/issues/5374)  
_**Closed**_ - _Moved from **QASP Review**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ⬛️ [Refactor and optimize test_parse.py for better maintainability and performance (#2641)](https://github.com/raft-tech/TANF-app/issues/2641)  
_Remained in **In Progress**_  

- ➡️ [Replace axios with native Fetch API for HTTP requests (#3333)](https://github.com/raft-tech/TANF-app/issues/3333)  
_Moved from **Current Sprint Backlog** to **In Progress**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ⬛️ [Create email templates for reparsing (new error report & error resolution) (#3263)](https://github.com/raft-tech/TANF-app/issues/3263)  
_Remained in **QASP Review**_  


## Issues without Parent

- ➡️ [Implement E2E Tests for Admin Feedback Reports (#5421)](https://github.com/raft-tech/TANF-app/issues/5421)  
_Moved from **Blocked** to **In Progress**_  

- ⬛️ [Spike: Investigate Time Between Parse Spikes (#5474)](https://github.com/raft-tech/TANF-app/issues/5474)  
_Remained in **In Progress**_  

- ⬛️ [Display Requested Changes in Profile Page (#5490)](https://github.com/raft-tech/TANF-app/issues/5490)  
_Remained in **Current Sprint Backlog**_  

- ➡️ [Migrate from NPM to Yarn (#5508)](https://github.com/raft-tech/TANF-app/issues/5508)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  

- ✅ [Rhode Island should be able to submit SSP data via TDP starting in FY2026 (#5521)](https://github.com/raft-tech/TANF-app/issues/5521)  
_**Closed**_ - _Moved from **In Progress**_  

- ⬛️ [Re-start submission status polling on page navigation/refresh (#5525)](https://github.com/raft-tech/TANF-app/issues/5525)  
_Remained in **In Progress**_  

- ⬛️ [Upload Panel State Reset on Accepted Files (#5527)](https://github.com/raft-tech/TANF-app/issues/5527)  
_Remained in **In Progress**_  

- ➡️ ["Parsing Complete" banner interrupts screenreader reading of "Successfully Submitted" (#5584)](https://github.com/raft-tech/TANF-app/issues/5584)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ⬛️ [Spike: Explore Rapid Research Methodologies to Capture Ongoing User Feedback (#5588)](https://github.com/raft-tech/TANF-app/issues/5588)  
_Remained in **UX Review**_  

- ⬛️ [Inconsistent File Status (#5591)](https://github.com/raft-tech/TANF-app/issues/5591)  
_Remained in **Current Sprint Backlog**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  

- ➡️ [Feature: Restore accessibility for Submit button on Data Files pages (#5598)](https://github.com/raft-tech/TANF-app/issues/5598)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ✅ [Enhancement: Submission Email Copy and Link Corrections (#5599)](https://github.com/raft-tech/TANF-app/issues/5599)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [Add Regional User Support for STT Feedback Reports Page (#5621)](https://github.com/raft-tech/TANF-app/issues/5621)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


