# Sprint Summary: Feb 18, 2026 - Mar 03, 2026

## Overview

- Completed refactor and optimization of test_parse.py for maintainability and performance. ([#2641](https://github.com/raft-tech/TANF-app/issues/2641))

- Replaced Axios with native Fetch API for HTTP requests, eliminating dependency and closing the task. ([#3333](https://github.com/raft-tech/TANF-app/issues/3333))

- Re-started submission status polling on page navigation/refresh to reduce stale state and improve user feedback. ([#5525](https://github.com/raft-tech/TANF-app/issues/5525))

- Implemented Cache Service and integrated Feature Flag REST API; Grafana memory increased to support 1.5M record visualizations. ([#5532](https://github.com/raft-tech/TANF-app/issues/5532), [#5534](https://github.com/raft-tech/TANF-app/issues/5534), [#5269](https://github.com/raft-tech/TANF-app/issues/5269))

- Updated in-app error reporting protocol and improved accessibility around the "Parsing Complete" banner, addressing related feedback. ([#5423](https://github.com/raft-tech/TANF-app/issues/5423), [#5584](https://github.com/raft-tech/TANF-app/issues/5584), [#5474](https://github.com/raft-tech/TANF-app/issues/5474))

---

⚪️ **Total Issues:** 51  
✅ **Closed:** 14  
➡️ **Moved:** 18  
⬛️ **Unchanged:** 13  
🛑 **Blocked:** 6  

---

## [Goal 1: Grantees can easily submit data](https://github.com/raft-tech/TANF-app/issues/5447)

- ⬛️ [Plan initial research for FTANF replacement (#4989)](https://github.com/raft-tech/TANF-app/issues/4989)  
_Remained in **QASP Review**_  

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  


## [Goal 2: Grantees are confident about reporting compliance](https://github.com/raft-tech/TANF-app/issues/5448)

- ⬛️ [Complete In App Error Reports HTML Prototypes (#5300)](https://github.com/raft-tech/TANF-app/issues/5300)  
_Remained in **QASP Review**_  

- ✅ [Update Research Protocol for In-app Error Reporting (#5423)](https://github.com/raft-tech/TANF-app/issues/5423)  
_**Closed**_ - _Moved from **QASP Review**_  

- ⬛️ [Update Figma with Feedback & Error Report Examples (#5425)](https://github.com/raft-tech/TANF-app/issues/5425)  
_Remained in **In Progress**_  

- ✅ [E2E Test for Same FY/Q/STT Across Program Types (#5477)](https://github.com/raft-tech/TANF-app/issues/5477)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [Implement Updated email templates for STT data submissions re: status and error guidance (#5478)](https://github.com/raft-tech/TANF-app/issues/5478)  
_Remained in **Raft (Dev) Review**_  


## [Goal 3: Reduce the burden on users](https://github.com/raft-tech/TANF-app/issues/5449)

- ✅ [Bump Grafana memory in prod by 4GB to support 1.5M record visualizations (#5269)](https://github.com/raft-tech/TANF-app/issues/5269)  
_**Closed**_ - _Moved from **Blocked**_  


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

- ⬛️ [FeatureFlag Model and Admin Interface (#5531)](https://github.com/raft-tech/TANF-app/issues/5531)  
_Remained in **Raft (Dev) Review**_  

- ✅ [Cache Service Implementation (#5532)](https://github.com/raft-tech/TANF-app/issues/5532)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Feature Flag Cache Integration with Django Signals (#5533)](https://github.com/raft-tech/TANF-app/issues/5533)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Feature Flag REST API Endpoint (#5534)](https://github.com/raft-tech/TANF-app/issues/5534)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Feature Flag Auditing and Versioning (#5536)](https://github.com/raft-tech/TANF-app/issues/5536)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Feature Flags Redux State Management (#5540)](https://github.com/raft-tech/TANF-app/issues/5540)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ⬛️ [Feature Flags Auth Integration, Hook, and FeatureGate Component (#5541)](https://github.com/raft-tech/TANF-app/issues/5541)  
_Remained in **Current Sprint Backlog**_  


## [Goal 5: Improve data quality](https://github.com/raft-tech/TANF-app/issues/5451)

- ⬛️ [[Tech Memo]: Refactor and cleanup parsing logic (#5434)](https://github.com/raft-tech/TANF-app/issues/5434)  
_Remained in **In Progress**_  


## [[EPIC]: (Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ➡️ [Add SubmissionState enum with default uploaded and migration (#5544)](https://github.com/raft-tech/TANF-app/issues/5544)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Add SubmissionLifecycle transition helpers for DataFile.state (with validation + tests) (#5545)](https://github.com/raft-tech/TANF-app/issues/5545)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ✅ [Refactor and optimize test_parse.py for better maintainability and performance (#2641)](https://github.com/raft-tech/TANF-app/issues/2641)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Replace axios with native Fetch API for HTTP requests (#3333)](https://github.com/raft-tech/TANF-app/issues/3333)  
_**Closed**_ - _Moved from **In Progress**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ⬛️ [Create email templates for reparsing (new error report & error resolution) (#3263)](https://github.com/raft-tech/TANF-app/issues/3263)  
_Remained in **QASP Review**_  


## Issues without Parent

- ➡️ [Implement E2E Tests for Admin Feedback Reports (#5421)](https://github.com/raft-tech/TANF-app/issues/5421)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ✅ [Spike: Investigate Time Between Parse Spikes (#5474)](https://github.com/raft-tech/TANF-app/issues/5474)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Display Requested Changes in Profile Page (#5490)](https://github.com/raft-tech/TANF-app/issues/5490)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Migrate from NPM to Yarn (#5508)](https://github.com/raft-tech/TANF-app/issues/5508)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ✅ [Re-start submission status polling on page navigation/refresh (#5525)](https://github.com/raft-tech/TANF-app/issues/5525)  
_**Closed**_ - _Moved from **In Progress**_  

- ⬛️ [Upload Panel State Reset on Accepted Files (#5527)](https://github.com/raft-tech/TANF-app/issues/5527)  
_Remained in **In Progress**_  

- ➡️ [[Bug]: Loki dashboard level variable not displaying log error levels (#5576)](https://github.com/raft-tech/TANF-app/issues/5576)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  

- ✅ ["Parsing Complete" banner interrupts screenreader reading of "Successfully Submitted" (#5584)](https://github.com/raft-tech/TANF-app/issues/5584)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [Spike: Explore Rapid Research Methodologies to Capture Ongoing User Feedback (#5588)](https://github.com/raft-tech/TANF-app/issues/5588)  
_Remained in **UX Review**_  

- ✅ [[Bug] Inconsistent File Status (#5591)](https://github.com/raft-tech/TANF-app/issues/5591)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  

- ✅ [Feature: Restore accessibility for Submit button on Data Files pages (#5598)](https://github.com/raft-tech/TANF-app/issues/5598)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Assign unique S3 log file per parse to improve log file accessibility (#5602)](https://github.com/raft-tech/TANF-app/issues/5602)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Add Regional User Support for STT Feedback Reports Page (#5621)](https://github.com/raft-tech/TANF-app/issues/5621)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ✅ [React Admin: Requirements Gathering with Dev (#5631)](https://github.com/raft-tech/TANF-app/issues/5631)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Write high-level architecture plan for Go parser integration (#5634)](https://github.com/raft-tech/TANF-app/issues/5634)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [[Knowledge Center Spike] Excel file hotfix & research into solutions for chrome cache compatibility (#5636)](https://github.com/raft-tech/TANF-app/issues/5636)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Create `digit_sensitive` Grafana user group with admin view access (#5640)](https://github.com/raft-tech/TANF-app/issues/5640)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Bug: Reparsing FRA files does not show reparse indicator in submission history (#5642)](https://github.com/raft-tech/TANF-app/issues/5642)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Remove redundant RPT_MONTH_YEAR validators from Section 3 and Section 4 records (#5644)](https://github.com/raft-tech/TANF-app/issues/5644)  
_Moved from **Product Backlog** to **Raft (Dev) Review**_  

- ➡️ [Bug: HEADER Update Indicator error incorrectly classified as pre-check error (#5646)](https://github.com/raft-tech/TANF-app/issues/5646)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [[Spike] TDP Data Retention (#5649)](https://github.com/raft-tech/TANF-app/issues/5649)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Write high-level architecture plan for Keycloak integration (#5653)](https://github.com/raft-tech/TANF-app/issues/5653)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


