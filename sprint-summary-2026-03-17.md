# Sprint Summary: Mar 04, 2026 - Mar 17, 2026

## Overview

- Progressed major initiative work on feature flags across admin UI, auditing, Redux state management, and integration, moving key items to Done. ( #5531, #5536, #5540, #5541 )

- Delivered E2E testing and templates for critical reporting flows: Admin Feedback Reports tests completed, reparsing email templates, and updated status/error emails implemented. ( #5421, #3263, #5300, #5478 )

- Completed architecture and tooling improvements: Yarn migration, PIA feature-flag refactor, and Go parser integration architecture plan finalized. ( #5508, #5661, #5634 )

- Improved parser reliability and log handling: faster reparses via index enhancements and log cleanup routines completed. ( #5662, #5681 )

- Maintained observability momentum with backlog movement: monitoring-related items advanced into current sprint backlog from Next Up DEV for Grafana/Tempo dashboards. ( #5514, #5523 )

---

⚪️ **Total Issues:** 58  
✅ **Closed:** 27  
➡️ **Moved:** 19  
⬛️ **Unchanged:** 8  
🛑 **Blocked:** 4  

---

## [Goal 1: Grantees can easily submit data](https://github.com/raft-tech/TANF-app/issues/5447)

- ⬛️ [Plan initial research for FTANF replacement (#4989)](https://github.com/raft-tech/TANF-app/issues/4989)  
_Remained in **QASP Review**_  

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  

- ➡️ [Implement E2E Tests for Program Integrity Audit Frontend (#5420)](https://github.com/raft-tech/TANF-app/issues/5420)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  


## [Goal 2: Grantees are confident about reporting compliance](https://github.com/raft-tech/TANF-app/issues/5448)

- ✅ [Complete In App Error Reports HTML Prototypes (#5300)](https://github.com/raft-tech/TANF-app/issues/5300)  
_**Closed**_ - _Moved from **QASP Review**_  

- ✅ [Implement Updated email templates for STT data submissions re: status and error guidance (#5478)](https://github.com/raft-tech/TANF-app/issues/5478)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [Goal 4: Free up staff time](https://github.com/raft-tech/TANF-app/issues/5450)

- ✅ [Create and facilitate Project Updates meeting for regional staff  (#3461)](https://github.com/raft-tech/TANF-app/issues/3461)  
_**Closed**_ - _Moved from **Blocked**_  

- 🛑 [Create and facilitate optional training session for regional staff (#3462)](https://github.com/raft-tech/TANF-app/issues/3462)  
_Remained in **Blocked**_  

- 🛑 [Refine research plan for regional staff MVP onboarding experience (#3523)](https://github.com/raft-tech/TANF-app/issues/3523)  
_Remained in **Blocked**_  

- ✅ [Gather and iterate on OFA feedback (#3995)](https://github.com/raft-tech/TANF-app/issues/3995)  
_**Closed**_ - _Moved from **Blocked**_  

- 🛑 [Gather final OFA feedback and iterate (#4045)](https://github.com/raft-tech/TANF-app/issues/4045)  
_Remained in **Blocked**_  

- 🛑 [Develop training materials, including slides, written instructions, and screenshots or screen recordings for visual guidance (#4047)](https://github.com/raft-tech/TANF-app/issues/4047)  
_Remained in **Blocked**_  

- ⬛️ [Iterate on training materials internally (#4052)](https://github.com/raft-tech/TANF-app/issues/4052)  
_Remained in **In Progress**_  

- ✅ [FeatureFlag Model and Admin Interface (#5531)](https://github.com/raft-tech/TANF-app/issues/5531)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Feature Flag Auditing and Versioning (#5536)](https://github.com/raft-tech/TANF-app/issues/5536)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Feature Flags Redux State Management (#5540)](https://github.com/raft-tech/TANF-app/issues/5540)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Feature Flags Auth Integration, Hook, and FeatureGate Component (#5541)](https://github.com/raft-tech/TANF-app/issues/5541)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  


## [Goal 5: Improve data quality](https://github.com/raft-tech/TANF-app/issues/5451)

- ⬛️ [[Tech Memo]: Refactor and cleanup parsing logic (#5434)](https://github.com/raft-tech/TANF-app/issues/5434)  
_Remained in **In Progress**_  


## [[EPIC]: (Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ⬛️ [Add SubmissionState enum with default uploaded and migration (#5544)](https://github.com/raft-tech/TANF-app/issues/5544)  
_Remained in **Current Sprint Backlog**_  

- ⬛️ [Add SubmissionLifecycle transition helpers for DataFile.state (with validation + tests) (#5545)](https://github.com/raft-tech/TANF-app/issues/5545)  
_Remained in **Current Sprint Backlog**_  

- ➡️ [Wire upload flow to transition DataFile.state → virus_scanning (#5546)](https://github.com/raft-tech/TANF-app/issues/5546)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Wire AV scan completion to transition DataFile.state → validated / scan_failed (#5547)](https://github.com/raft-tech/TANF-app/issues/5547)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


## [FRA Feedback Reports](https://github.com/raft-tech/TANF-app/issues/5663)

- ➡️ [Backend FRA Feedback Reports Implementation (#5664)](https://github.com/raft-tech/TANF-app/issues/5664)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ➡️ [Fix health dashboard to respect environment filters (#3611)](https://github.com/raft-tech/TANF-app/issues/3611)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ✅ [Create email templates for reparsing (new error report & error resolution) (#3263)](https://github.com/raft-tech/TANF-app/issues/3263)  
_**Closed**_ - _Moved from **QASP Review**_  


## Issues without Parent

- ✅ [Implement E2E Tests for Admin Feedback Reports (#5421)](https://github.com/raft-tech/TANF-app/issues/5421)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [LogEntry admin is causing N+1 query of admin model (#5484)](https://github.com/raft-tech/TANF-app/issues/5484)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Optimize DataFile & Report APIs to avoid N+1 queries using select_related (#5485)](https://github.com/raft-tech/TANF-app/issues/5485)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ✅ [Display Requested Changes in Profile Page (#5490)](https://github.com/raft-tech/TANF-app/issues/5490)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Provide Additional Descriptions for Centralized Feedback Reports in KC (#5504)](https://github.com/raft-tech/TANF-app/issues/5504)  
_Moved from **Next Up: UX** to **In Progress**_  

- ✅ [Migrate from NPM to Yarn (#5508)](https://github.com/raft-tech/TANF-app/issues/5508)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Postgres Grafana Dashboard Cannot Query Historical Metrics When Database is Offline (#5514)](https://github.com/raft-tech/TANF-app/issues/5514)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  

- ➡️ [Enable Prometheus remote write receiver for Tempo metrics (#5523)](https://github.com/raft-tech/TANF-app/issues/5523)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  

- ✅ [Upload Panel State Reset on Accepted Files (#5527)](https://github.com/raft-tech/TANF-app/issues/5527)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Handle PIA files separately from TANF active case data in submission emails (#5563)](https://github.com/raft-tech/TANF-app/issues/5563)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ✅ [[Bug]: Loki dashboard level variable not displaying log error levels (#5576)](https://github.com/raft-tech/TANF-app/issues/5576)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [Downgrade or elimate mattermost notifications for local environments (#5578)](https://github.com/raft-tech/TANF-app/issues/5578)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ➡️ [Times in emails represented as UTC (#5585)](https://github.com/raft-tech/TANF-app/issues/5585)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  

- ✅ [Spike: Explore Rapid Research Methodologies to Capture Ongoing User Feedback (#5588)](https://github.com/raft-tech/TANF-app/issues/5588)  
_**Closed**_ - _Moved from **UX Review**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  

- ✅ [Assign unique S3 log file per parse to improve log file accessibility (#5602)](https://github.com/raft-tech/TANF-app/issues/5602)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [Initiate Recruitment and Finalize Participant List for FTANF Replacement Research (#5609)](https://github.com/raft-tech/TANF-app/issues/5609)  
_Moved from **Next Up: UX** to **In Progress**_  

- ➡️ [Add Regional User Support for STT Feedback Reports Page (#5621)](https://github.com/raft-tech/TANF-app/issues/5621)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ✅ [Write high-level architecture plan for Go parser integration (#5634)](https://github.com/raft-tech/TANF-app/issues/5634)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [[Knowledge Center Spike] Excel file hotfix & research into solutions for chrome cache compatibility (#5636)](https://github.com/raft-tech/TANF-app/issues/5636)  
_**Closed**_ - _Moved from **QASP Review**_  

- ✅ [Create `digit_sensitive` Grafana user group with admin view access (#5640)](https://github.com/raft-tech/TANF-app/issues/5640)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Initiate Recruitment and Finalize Participant List for Error Reporting Research (#5641)](https://github.com/raft-tech/TANF-app/issues/5641)  
_**Closed**_ - _Moved from **Next Up: UX**_  

- ✅ [Bug: Reparsing FRA files does not show reparse indicator in submission history (#5642)](https://github.com/raft-tech/TANF-app/issues/5642)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Remove redundant RPT_MONTH_YEAR validators from Section 3 and Section 4 records (#5644)](https://github.com/raft-tech/TANF-app/issues/5644)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Bug: HEADER Update Indicator error incorrectly classified as pre-check error (#5646)](https://github.com/raft-tech/TANF-app/issues/5646)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [[Spike] TDP Data Retention (#5649)](https://github.com/raft-tech/TANF-app/issues/5649)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Moved from **Next Up: UX** to **In Progress**_  

- ➡️ [Write high-level architecture plan for Keycloak integration (#5653)](https://github.com/raft-tech/TANF-app/issues/5653)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ✅ [Convert PIA env-based feature flag to new FeatureFlag (#5661)](https://github.com/raft-tech/TANF-app/issues/5661)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ✅ [Slow reparse due to missing indexes on parser_error table (#5662)](https://github.com/raft-tech/TANF-app/issues/5662)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ✅ [Celery metrics unavailable - REDIS_URI missing TLS scheme and database number (#5673)](https://github.com/raft-tech/TANF-app/issues/5673)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Conduct Error Reporting Research with STTs (#5675)](https://github.com/raft-tech/TANF-app/issues/5675)  
_Moved from **Product Backlog** to **In Progress**_  

- ✅ [Parser log files not cleaned up from disk after S3 upload (#5681)](https://github.com/raft-tech/TANF-app/issues/5681)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ⬛️ [Mandatory Training: Plain Language (#24)]()  
_Remained in **No Pipeline Info**_  


