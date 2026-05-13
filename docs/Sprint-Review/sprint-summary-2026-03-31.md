# Sprint Summary: Mar 18, 2026 - Mar 31, 2026

## Overview

- Completed a wave of critical backend/data quality work, moving multiple items to Done and delivering substantial progress across parsing, datafile state transitions, and frontend test coverage. ( #5420, #5434, #5544, #5545, #5546, #5664 )

- Advanced training and onboarding efforts, with training materials finalized/iterated and an optional regional staff session closed, reflecting improved readiness for rollout. ( #3462, #4047, #4052 )

- Strengthened observability and metrics reliability by closing key dashboard and metric work, including fixes to the Loki dashboard, offline Grafana queries, and Prometheus remote-write enablement. ( #5576, #5514, #5523 )

- One sprint blocker remained, highlighting risk to FTANF-related initiatives due to the TDP Data Retention work being blocked. ( #5649 )

---

⚪️ **Total Issues:** 47  
✅ **Closed:** 38  
➡️ **Moved:** 3  
⬛️ **Unchanged:** 5  
🛑 **Blocked:** 1  

---

## [Goal 5: Improve data quality](https://github.com/raft-tech/TANF-app/issues/5451)

- ✅ [[Tech Memo]: Refactor and cleanup parsing logic (#5434)](https://github.com/raft-tech/TANF-app/issues/5434)  
_**Closed**_ - _Moved from **In Progress**_  


## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ✅ [Add SubmissionState enum with default uploaded and migration (#5544)](https://github.com/raft-tech/TANF-app/issues/5544)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Add SubmissionLifecycle transition helpers for DataFile.state (with validation + tests) (#5545)](https://github.com/raft-tech/TANF-app/issues/5545)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Wire upload flow to transition DataFile.state → virus_scanning (#5546)](https://github.com/raft-tech/TANF-app/issues/5546)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [Wire AV scan completion to transition DataFile.state → validated / scan_failed (#5547)](https://github.com/raft-tech/TANF-app/issues/5547)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Wire parser task to transition DataFile.state → parsing / parsed_clean / parsed_with_errors (#5548)](https://github.com/raft-tech/TANF-app/issues/5548)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ✅ [[Bug] LogEntry admin is causing N+1 query of admin model (#5484)](https://github.com/raft-tech/TANF-app/issues/5484)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Optimize DataFile & Report APIs to avoid N+1 queries using select_related (#5485)](https://github.com/raft-tech/TANF-app/issues/5485)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [[BUG] - E2E authentication failures in `develop` (#5624)](https://github.com/raft-tech/TANF-app/issues/5624)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ✅ [Bug: remove_all_old_versions takes ~6 hours before first deletion in production (#5686)](https://github.com/raft-tech/TANF-app/issues/5686)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [FRA Post-MVP Enhancements](https://github.com/raft-tech/TANF-app/issues/4443)

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  

- ⬛️ [Provide Additional Descriptions for Centralized Feedback Reports in KC (#5504)](https://github.com/raft-tech/TANF-app/issues/5504)  
_Remained in **In Progress**_  

- ✅ [Backend FRA Feedback Reports Implementation (#5664)](https://github.com/raft-tech/TANF-app/issues/5664)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Celery Task FRA Feedback Reports Implementation (#5704)](https://github.com/raft-tech/TANF-app/issues/5704)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ✅ [Plan initial research for FTANF replacement (#4989)](https://github.com/raft-tech/TANF-app/issues/4989)  
_**Closed**_ - _Moved from **QASP Review**_  

- ⬛️ [Initiate Recruitment and Finalize Participant List for FTANF Replacement Research (#5609)](https://github.com/raft-tech/TANF-app/issues/5609)  
_Remained in **In Progress**_  


## [In-App Error Reporting - Foundational Design & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4629)

- ✅ [Conduct Error Reporting Research with STTs (#5675)](https://github.com/raft-tech/TANF-app/issues/5675)  
_**Closed**_ - _Moved from **In Progress**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ✅ [Write high-level architecture plan for Keycloak integration (#5653)](https://github.com/raft-tech/TANF-app/issues/5653)  
_**Closed**_ - _Moved from **In Progress**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Remained in **In Progress**_  

- ➡️ [React Admin High Level Architecture Document (#5746)](https://github.com/raft-tech/TANF-app/issues/5746)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ✅ [Fix health dashboard to respect environment filters (#3611)](https://github.com/raft-tech/TANF-app/issues/3611)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [[Spike] Explore Transitioning TDP Deployments from Cloud.gov Buildpacks to Docker Containers (#5542)](https://github.com/raft-tech/TANF-app/issues/5542)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  


## [Program Integrity Audit](https://github.com/raft-tech/TANF-app/issues/5356)

- ✅ [Implement E2E Tests for Program Integrity Audit Frontend (#5420)](https://github.com/raft-tech/TANF-app/issues/5420)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Hide the Program Integrity Audit file type option for tribe locations (#5697)](https://github.com/raft-tech/TANF-app/issues/5697)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [Regional Staff TDP Access & Onboarding (RSAO)](https://github.com/raft-tech/TANF-app/issues/4395)

- ✅ [Create and facilitate optional training session for regional staff (#3462)](https://github.com/raft-tech/TANF-app/issues/3462)  
_**Closed**_ - _Moved from **Blocked**_  

- ✅ [Refine research plan for regional staff MVP onboarding experience (#3523)](https://github.com/raft-tech/TANF-app/issues/3523)  
_**Closed**_ - _Moved from **Blocked**_  

- ✅ [Gather final OFA feedback and iterate (#4045)](https://github.com/raft-tech/TANF-app/issues/4045)  
_**Closed**_ - _Moved from **Blocked**_  

- ✅ [Develop training materials, including slides, written instructions, and screenshots or screen recordings for visual guidance (#4047)](https://github.com/raft-tech/TANF-app/issues/4047)  
_**Closed**_ - _Moved from **Blocked**_  

- ✅ [Iterate on training materials internally (#4052)](https://github.com/raft-tech/TANF-app/issues/4052)  
_**Closed**_ - _Moved from **In Progress**_  


## [Release Tracking](https://github.com/raft-tech/TANF-app/issues/5789)

- ✅ [Release Tracker v4.15.0 (#5693)](https://github.com/raft-tech/TANF-app/issues/5693)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [TDP Data Retention](https://github.com/raft-tech/TANF-app/issues/5790)

- 🛑 [[Spike] TDP Data Retention (#5649)](https://github.com/raft-tech/TANF-app/issues/5649)  
_Moved from **In Progress** to **Blocked**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ✅ [Create email templates for reparsing (new error report & error resolution) (#3263)](https://github.com/raft-tech/TANF-app/issues/3263)  
_**Closed**_ - _Moved from **QASP Review**_  

- ✅ [Times in emails represented as UTC (#5585)](https://github.com/raft-tech/TANF-app/issues/5585)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Implement email templates for reparsing (new error report & error resolution) (#5689)](https://github.com/raft-tech/TANF-app/issues/5689)  
_**Closed**_ - _Moved from **Product Backlog**_  


## Issues without Parent

- ✅ [Display Requested Changes in Profile Page (#5490)](https://github.com/raft-tech/TANF-app/issues/5490)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Postgres Grafana Dashboard Cannot Query Historical Metrics When Database is Offline (#5514)](https://github.com/raft-tech/TANF-app/issues/5514)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Enable Prometheus remote write receiver for Tempo metrics (#5523)](https://github.com/raft-tech/TANF-app/issues/5523)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Handle PIA files separately from TANF active case data in submission emails (#5563)](https://github.com/raft-tech/TANF-app/issues/5563)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [[Bug]: Loki dashboard level variable not displaying log error levels (#5576)](https://github.com/raft-tech/TANF-app/issues/5576)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Downgrade or elimate mattermost notifications for local environments (#5578)](https://github.com/raft-tech/TANF-app/issues/5578)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Add Regional User Support for STT Feedback Reports Page (#5621)](https://github.com/raft-tech/TANF-app/issues/5621)  
_**Closed**_ - _Moved from **UX Review**_  

- ✅ [Slow reparse due to missing indexes on parser_error table (#5662)](https://github.com/raft-tech/TANF-app/issues/5662)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Celery metrics unavailable - REDIS_URI missing TLS scheme and database number (#5673)](https://github.com/raft-tech/TANF-app/issues/5673)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Parser log files not cleaned up from disk after S3 upload (#5681)](https://github.com/raft-tech/TANF-app/issues/5681)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Mandatory Training: Plain Language (#24)]()  
_**Closed**_ - _Moved from **No Pipeline Info**_  

- ✅ [Zero Allowed for TANF SNAP Assistance & Subsidized CC (#5745)](https://github.com/raft-tech/TANF-app/issues/5745)  
_**Closed**_ - _Moved from **Product Backlog**_  


