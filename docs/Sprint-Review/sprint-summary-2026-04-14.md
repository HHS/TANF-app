# Sprint Summary: Apr 01, 2026 - Apr 14, 2026

## Overview

- Closed major FRA and release initiatives, delivering backend/frontend FRA Feedback Reports, error reporting research, architecture planning for Keycloak, and release-tracking upgrades. (5664, 5665, 5675, 5653, 5693, 5770)

- Resolved performance gaps by completing N+1 query fixes for LogEntry admin and DataFile APIs, improving data fetch efficiency. (5484, 5485)

- Advanced the DataFile state machine: added SubmissionState enum and lifecycle helpers, and wired the upload flow to virus scanning, enabling multiple state-transition closures. (5544, 5545, 5546)

- Progressed the AV scan workflow, with AV scan completion linked to DataFile state validation and moved to Raft (Dev) Review for final validation. (5547)

- Implemented Go Parser header validation, a concrete architectural improvement and milestone achievement. (5723)

---

⚪️ **Total Issues:** 30  
✅ **Closed:** 20  
➡️ **Moved:** 6  
⬛️ **Unchanged:** 3  
🛑 **Blocked:** 1  

---

## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ✅ [Add SubmissionState enum with default uploaded and migration (#5544)](https://github.com/raft-tech/TANF-app/issues/5544)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Add SubmissionLifecycle transition helpers for DataFile.state (with validation + tests) (#5545)](https://github.com/raft-tech/TANF-app/issues/5545)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Wire upload flow to transition DataFile.state → virus_scanning (#5546)](https://github.com/raft-tech/TANF-app/issues/5546)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Wire AV scan completion to transition DataFile.state → validated / scan_failed (#5547)](https://github.com/raft-tech/TANF-app/issues/5547)  
_Moved from **In Progress** to **Raft (Dev) Review**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ✅ [[Bug] LogEntry admin is causing N+1 query of admin model (#5484)](https://github.com/raft-tech/TANF-app/issues/5484)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Optimize DataFile & Report APIs to avoid N+1 queries using select_related (#5485)](https://github.com/raft-tech/TANF-app/issues/5485)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [[BUG] - E2E authentication failures in `develop` (#5624)](https://github.com/raft-tech/TANF-app/issues/5624)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Bug: remove_all_old_versions takes ~6 hours before first deletion in production (#5686)](https://github.com/raft-tech/TANF-app/issues/5686)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [FRA Post-MVP Enhancements](https://github.com/raft-tech/TANF-app/issues/4443)

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  

- ✅ [Backend FRA Feedback Reports Implementation (#5664)](https://github.com/raft-tech/TANF-app/issues/5664)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Frontend FRA Feedback Reports Implementation (#5665)](https://github.com/raft-tech/TANF-app/issues/5665)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ✅ [Celery Task FRA Feedback Reports Implementation (#5704)](https://github.com/raft-tech/TANF-app/issues/5704)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Initiate Recruitment and Finalize Participant List for FTANF Replacement Research (#5609)](https://github.com/raft-tech/TANF-app/issues/5609)  
_Remained in **In Progress**_  

- ➡️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Moved from **Next Up: UX** to **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ✅ [Go Parser: Implement header validation (#5723)](https://github.com/raft-tech/TANF-app/issues/5723)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Go Parser: Complete Celery/Redis task consumption (#5730)](https://github.com/raft-tech/TANF-app/issues/5730)  
_Moved from **Product Backlog** to **Raft (Dev) Review**_  

- ➡️ [Go Parser: Local Docker Integration (#5732)](https://github.com/raft-tech/TANF-app/issues/5732)  
_Moved from **Product Backlog** to **Raft (Dev) Review**_  


## [In-App Error Reporting - Foundational Design & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4629)

- ✅ [Conduct Error Reporting Research with STTs (#5675)](https://github.com/raft-tech/TANF-app/issues/5675)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Error Reporting Research Synthesis (#5763)](https://github.com/raft-tech/TANF-app/issues/5763)  
_Moved from **Next Up: UX** to **In Progress**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ✅ [Write high-level architecture plan for Keycloak integration (#5653)](https://github.com/raft-tech/TANF-app/issues/5653)  
_**Closed**_ - _Moved from **In Progress**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ➡️ [React Admin High Level Architecture Document (#5746)](https://github.com/raft-tech/TANF-app/issues/5746)  
_Moved from **Current Sprint Backlog** to **In Progress**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ✅ [[Spike] Explore Transitioning TDP Deployments from Cloud.gov Buildpacks to Docker Containers (#5542)](https://github.com/raft-tech/TANF-app/issues/5542)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  


## [Program Integrity Audit](https://github.com/raft-tech/TANF-app/issues/5356)

- ✅ [Hide the Program Integrity Audit file type option for tribe locations (#5697)](https://github.com/raft-tech/TANF-app/issues/5697)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Update PIA Submission Due Dates (#5767)](https://github.com/raft-tech/TANF-app/issues/5767)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [Release Tracking](https://github.com/raft-tech/TANF-app/issues/5789)

- ✅ [Release Tracker v4.15.0 (#5693)](https://github.com/raft-tech/TANF-app/issues/5693)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Release Tracker v4.16.0 (#5770)](https://github.com/raft-tech/TANF-app/issues/5770)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [TDP Data Retention](https://github.com/raft-tech/TANF-app/issues/5790)

- 🛑 [[Spike] TDP Data Retention (#5649)](https://github.com/raft-tech/TANF-app/issues/5649)  
_Remained in **Blocked**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ✅ [Implement email templates for reparsing (new error report & error resolution) (#5689)](https://github.com/raft-tech/TANF-app/issues/5689)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  


## Issues without Parent

- ✅ [Mandatory Training: Plain Language (#24)]()  
_**Closed**_ - _Moved from **No Pipeline Info**_  


