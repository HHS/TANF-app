# Sprint Summary: May 13, 2026 - May 26, 2026

## Overview

- Closed key Go Parser tasks: record rollback on parse failure; audit validators; implement shadow table write mode. ([#5727](https://github.com/raft-tech/TANF-app/issues/5727), [#5728](https://github.com/raft-tech/TANF-app/issues/5728), [#5735](https://github.com/raft-tech/TANF-app/issues/5735))

- Lib upgrades and KC/docs stabilization completed: libs upgraded; remaining notifications & guidance for KC finalized. ([#5804](https://github.com/raft-tech/TANF-app/issues/5804), [#5808](https://github.com/raft-tech/TANF-app/issues/5808))

- Parser/infrastructure work advanced into active development: Enqueue post-parse tasks; Accept header/trailer files; Tech Memo DataFile Orchestrator moving toward Raft Review. ([#5731](https://github.com/raft-tech/TANF-app/issues/5731), [#5819](https://github.com/raft-tech/TANF-app/issues/5819), [#5825](https://github.com/raft-tech/TANF-app/issues/5825))

- FTANF Replacement research and recruitment tasks progressed: planning and participant coordination ongoing. ([#5609](https://github.com/raft-tech/TANF-app/issues/5609), [#5683](https://github.com/raft-tech/TANF-app/issues/5683))

- Release tracking momentum: Release Tracker v4.18.0 remains in progress; v4.19.0 moved from backlog to in progress. ([#5811](https://github.com/raft-tech/TANF-app/issues/5811), [#5854](https://github.com/raft-tech/TANF-app/issues/5854))

---

⚪️ **Total Issues:** 35  
✅ **Closed:** 6  
➡️ **Moved:** 16  
⬛️ **Unchanged:** 13  
🛑 **Blocked:** 0  

---

## [Goal 6: Documentation is current and helpful](https://github.com/raft-tech/TANF-app/issues/5435)

- ➡️ [Create or modify maintenance page / error page (#5660)](https://github.com/raft-tech/TANF-app/issues/5660)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ⬛️ [Wire AV scan completion to transition DataFile.state → validated / scan_failed (#5547)](https://github.com/raft-tech/TANF-app/issues/5547)  
_Remained in **Raft (Dev) Review**_  

- ➡️ [Wire parser task to transition DataFile.state → parsing / parsed_clean / parsed_with_errors (#5548)](https://github.com/raft-tech/TANF-app/issues/5548)  
_Moved from **In Progress** to **Raft (Dev) Review**_  


## [(RE)Parsing refactor](https://github.com/raft-tech/TANF-app/issues/5565)

- ⬛️ [Add `ReparseService` and refactor orchestration to use it (#5568)](https://github.com/raft-tech/TANF-app/issues/5568)  
_Remained in **Current Sprint Backlog**_  

- ➡️ [Document current parsing & reparsing flows (#5566)](https://github.com/raft-tech/TANF-app/issues/5566)  
_Moved from **In Progress** to **Raft (Dev) Review**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ➡️ [BUG KeyError Events: Error 'state_nonce_tracker' in Sentry (#5859)](https://github.com/raft-tech/TANF-app/issues/5859)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [FRA Post-MVP Enhancements](https://github.com/raft-tech/TANF-app/issues/4443)

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Initiate Recruitment and Finalize Participant List for FTANF Replacement Research (#5609)](https://github.com/raft-tech/TANF-app/issues/5609)  
_Remained in **In Progress**_  

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ➡️ [Go Parser: Verify in-memory duplicate detection parity (#5724)](https://github.com/raft-tech/TANF-app/issues/5724)  
_Moved from **Product Backlog** to **In Progress**_  

- ✅ [Go Parser: Implement record rollback on parse failure (#5727)](https://github.com/raft-tech/TANF-app/issues/5727)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Go Parser: Audit validators against Python parser for completeness (#5728)](https://github.com/raft-tech/TANF-app/issues/5728)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Go Parser: Enqueue post-parse tasks to Python Celery worker (#5731)](https://github.com/raft-tech/TANF-app/issues/5731)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ✅ [Go Parser: Implement shadow table write mode (#5735)](https://github.com/raft-tech/TANF-app/issues/5735)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Go Parser: Add structured JSON logging via log/slog (#5738)](https://github.com/raft-tech/TANF-app/issues/5738)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [In-App Error Reporting - Foundational Design & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4629)

- ➡️ [Error Reporting Research Synthesis (#5763)](https://github.com/raft-tech/TANF-app/issues/5763)  
_Moved from **In Progress** to **UX Review**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ⬛️ [Keycloak: Promote Keycloak to Cloud.gov staging space (#5751)](https://github.com/raft-tech/TANF-app/issues/5751)  
_Remained in **Current Sprint Backlog**_  

- ⬛️ [Implement bearer token authentication for external API clients (#5756)](https://github.com/raft-tech/TANF-app/issues/5756)  
_Remained in **Raft (Dev) Review**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ➡️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Moved from **Next Up: UX** to **In Progress**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ✅ [Update pilot states and related validation logic for FY2026 (#3558)](https://github.com/raft-tech/TANF-app/issues/3558)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  


## [Release Tracking](https://github.com/raft-tech/TANF-app/issues/5789)

- ⬛️ [Release Tracker v4.18.0 (#5811)](https://github.com/raft-tech/TANF-app/issues/5811)  
_Remained in **In Progress**_  

- ➡️ [Release Tracker v4.19.0 (#5854)](https://github.com/raft-tech/TANF-app/issues/5854)  
_Moved from **Product Backlog** to **In Progress**_  


## [TDP Knowledge Center](https://github.com/raft-tech/TANF-app/issues/5455)

- ✅ [Add remaining notifications & remaining feedback report guidance to KC (#5808)](https://github.com/raft-tech/TANF-app/issues/5808)  
_**Closed**_ - _Moved from **Product Backlog**_  


## Issues without Parent

- ➡️ [Design for separating "Readme" tab in error reports (#5795)](https://github.com/raft-tech/TANF-app/issues/5795)  
_Moved from **Product Backlog** to **In Progress**_  

- ⬛️ [Update ZAP (#5798)](https://github.com/raft-tech/TANF-app/issues/5798)  
_Remained in **Current Sprint Backlog**_  

- ✅ [Upgrade libs (#5804)](https://github.com/raft-tech/TANF-app/issues/5804)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [Accept header/trailer-only active, aggregate, and stratum files (#5819)](https://github.com/raft-tech/TANF-app/issues/5819)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [[Tech Memo] Generic DataFile Orchestrator (Submission, Parse, Reparse, Tasks) (#5825)](https://github.com/raft-tech/TANF-app/issues/5825)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ➡️ [Add parser-side validation for datafile program type mismatches (#5833)](https://github.com/raft-tech/TANF-app/issues/5833)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Update Python and Go T5/M5 OASDI age validators to use AGE_FIRST DOB calculation (#5848)](https://github.com/raft-tech/TANF-app/issues/5848)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ⬛️ [Update Vendor Product Manager contact on README (#5849)](https://github.com/raft-tech/TANF-app/issues/5849)  
_Remained in **In Progress**_  

- ➡️ [Transition TDP applications from app.cloud.gov to tanfdata.acf.hhs.gov domains (#5855)](https://github.com/raft-tech/TANF-app/issues/5855)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ⬛️ [CRM for STT info and behavior (#25)]()  
_Remained in **No Pipeline Info**_  

- ⬛️ [Plan & Prepare Summer 2026 STT Office Hours Webinar (#26)]()  
_Remained in **No Pipeline Info**_  


