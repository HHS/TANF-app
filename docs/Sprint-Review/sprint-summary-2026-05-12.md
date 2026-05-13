# Sprint Summary: Apr 29, 2026 - May 12, 2026

## Overview

- Go Parser work closed: record rollback on parse failure, Celery/Redis task consumption, Local Docker integration, CI/CD pipeline, and test parity with Python parser. ([#5727](https://github.com/raft-tech/TANF-app/issues/5727), [#5730](https://github.com/raft-tech/TANF-app/issues/5730), [#5732](https://github.com/raft-tech/TANF-app/issues/5732), [#5734](https://github.com/raft-tech/TANF-app/issues/5734), [#5741](https://github.com/raft-tech/TANF-app/issues/5741))

- Closed critical bugs including login endpoint protection and E2E profile editing tests for non-FRA users. ([#5625](https://github.com/raft-tech/TANF-app/issues/5625), [#5793](https://github.com/raft-tech/TANF-app/issues/5793))

- DataFile parsing/AV workflow progressed: AV scan wiring to validated/scan_failed remains in Dev Review; parser state transitions moved Next Up → In Progress. ([#5547](https://github.com/raft-tech/TANF-app/issues/5547), [#5548](https://github.com/raft-tech/TANF-app/issues/5548))

- Planning and FTANF research advanced: How We Work Workshop remains in progress; recruitment for FTANF Replacement Research initiated and ongoing. ([#5593](https://github.com/raft-tech/TANF-app/issues/5593), [#5609](https://github.com/raft-tech/TANF-app/issues/5609))

- Release and dependency momentum: Release Tracker v4.18.0 moved to In Progress; libs upgrade now in Current Sprint Backlog; vendor PM contact update in progress. ([#5811](https://github.com/raft-tech/TANF-app/issues/5811), [#5804](https://github.com/raft-tech/TANF-app/issues/5804), [#5849](https://github.com/raft-tech/TANF-app/issues/5849))

---

⚪️ **Total Issues:** 35  
✅ **Closed:** 12  
➡️ **Moved:** 17  
⬛️ **Unchanged:** 6  
🛑 **Blocked:** 0  

---

## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ⬛️ [Wire AV scan completion to transition DataFile.state → validated / scan_failed (#5547)](https://github.com/raft-tech/TANF-app/issues/5547)  
_Remained in **Raft (Dev) Review**_  

- ➡️ [Wire parser task to transition DataFile.state → parsing / parsed_clean / parsed_with_errors (#5548)](https://github.com/raft-tech/TANF-app/issues/5548)  
_Moved from **Next Up: DEV** to **In Progress**_  


## [(RE)Parsing refactor](https://github.com/raft-tech/TANF-app/issues/5565)

- ➡️ [Add `ReparseService` and refactor orchestration to use it (#5568)](https://github.com/raft-tech/TANF-app/issues/5568)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  

- ➡️ [Document current parsing & reparsing flows (#5566)](https://github.com/raft-tech/TANF-app/issues/5566)  
_Moved from **Next Up: DEV** to **In Progress**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ✅ [Regional Staff presented STT request form after signing in with AMS flow (#5794)](https://github.com/raft-tech/TANF-app/issues/5794)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [FRA Post-MVP Enhancements](https://github.com/raft-tech/TANF-app/issues/4443)

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Initiate Recruitment and Finalize Participant List for FTANF Replacement Research (#5609)](https://github.com/raft-tech/TANF-app/issues/5609)  
_Remained in **In Progress**_  

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ✅ [Go Parser: Implement record rollback on parse failure (#5727)](https://github.com/raft-tech/TANF-app/issues/5727)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Go Parser: Audit validators against Python parser for completeness (#5728)](https://github.com/raft-tech/TANF-app/issues/5728)  
_Moved from **Product Backlog** to **In Progress**_  

- ✅ [Go Parser: Complete Celery/Redis task consumption (#5730)](https://github.com/raft-tech/TANF-app/issues/5730)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Go Parser: Enqueue post-parse tasks to Python Celery worker (#5731)](https://github.com/raft-tech/TANF-app/issues/5731)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ✅ [Go Parser: Local Docker Integration (#5732)](https://github.com/raft-tech/TANF-app/issues/5732)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Go Parser: Add CI/CD pipeline (#5734)](https://github.com/raft-tech/TANF-app/issues/5734)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Go Parser: Implement shadow table write mode (#5735)](https://github.com/raft-tech/TANF-app/issues/5735)  
_Moved from **Product Backlog** to **In Progress**_  

- ✅ [Go Parser: Integration test parity with Python parser tests (#5741)](https://github.com/raft-tech/TANF-app/issues/5741)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [In-App Error Reporting - Foundational Design & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4629)

- ⬛️ [Error Reporting Research Synthesis (#5763)](https://github.com/raft-tech/TANF-app/issues/5763)  
_Remained in **In Progress**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ✅ [Keycloak: Enable Keycloak in the Cloud.gov dev space (#5750)](https://github.com/raft-tech/TANF-app/issues/5750)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Keycloak: Promote Keycloak to Cloud.gov staging space (#5751)](https://github.com/raft-tech/TANF-app/issues/5751)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Implement bearer token authentication for external API clients (#5756)](https://github.com/raft-tech/TANF-app/issues/5756)  
_Moved from **In Progress** to **Raft (Dev) Review**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ✅ [React Admin High Level Architecture Document (#5746)](https://github.com/raft-tech/TANF-app/issues/5746)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ➡️ [Update pilot states and related validation logic for FY2026 (#3558)](https://github.com/raft-tech/TANF-app/issues/3558)  
_Moved from **Product Backlog** to **In Progress**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ✅ [Implement email templates for reparsing (new error report & error resolution) (#5689)](https://github.com/raft-tech/TANF-app/issues/5689)  
_**Closed**_ - _Moved from **UX Review**_  


## Issues without Parent

- ✅ [[BUG] - `/login/` endpoint allows requests that should be blocked by nginx (#5625)](https://github.com/raft-tech/TANF-app/issues/5625)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ✅ [Refactor upload flow to move AV scanning out of serializer validation and align submission-state transitions with runtime events (#5769)](https://github.com/raft-tech/TANF-app/issues/5769)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [[BUG] - E2E profile editing tests failing for non-FRA users in develop (#5793)](https://github.com/raft-tech/TANF-app/issues/5793)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Update ZAP (#5798)](https://github.com/raft-tech/TANF-app/issues/5798)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [Upgrade libs (#5804)](https://github.com/raft-tech/TANF-app/issues/5804)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Release Tracker v4.18.0 (#5811)](https://github.com/raft-tech/TANF-app/issues/5811)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Accept header/trailer-only active, aggregate, and stratum files (#5819)](https://github.com/raft-tech/TANF-app/issues/5819)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [[Tech Memo] Generic DataFile Orchestrator (Submission, Parse, Reparse, Tasks) (#5825)](https://github.com/raft-tech/TANF-app/issues/5825)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [Add parser-side validation for datafile program type mismatches (#5833)](https://github.com/raft-tech/TANF-app/issues/5833)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Update Python and Go T5/M5 OASDI age validators to use AGE_FIRST DOB calculation (#5848)](https://github.com/raft-tech/TANF-app/issues/5848)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [Update Vendor Product Manager contact on README (#5849)](https://github.com/raft-tech/TANF-app/issues/5849)  
_Moved from **Product Backlog** to **In Progress**_  


