# Sprint Summary: Jun 10, 2026 - Jun 23, 2026

## Overview

- We finished tying antivirus scan results to data file status and clarified how parsing works, with updated checks for data type mismatches ([#5547](https://github.com/raft-tech/TANF-app/issues/5547), [#5566](https://github.com/raft-tech/TANF-app/issues/5566))
- We improved the Go parser by adding structured JSON logs to make debugging easier ([#5738](https://github.com/raft-tech/TANF-app/issues/5738))
- Keycloak authentication work moved forward, with the system promoted to a staging environment and planning for production rollout ([#5751](https://github.com/raft-tech/TANF-app/issues/5751), [#5761](https://github.com/raft-tech/TANF-app/issues/5761))
- Release tracking and maintenance moved ahead, including completing releases 4.18 and 4.19, plus fixes and documentation updates that improve reliability ([#5811](https://github.com/raft-tech/TANF-app/issues/5811), [#5819](https://github.com/raft-tech/TANF-app/issues/5819), [#5825](https://github.com/raft-tech/TANF-app/issues/5825), [#5853](https://github.com/raft-tech/TANF-app/issues/5853), [#5854](https://github.com/raft-tech/TANF-app/issues/5854), [#5872](https://github.com/raft-tech/TANF-app/issues/5872), [#5873](https://github.com/raft-tech/TANF-app/issues/5873), [#5875](https://github.com/raft-tech/TANF-app/issues/5875), [#5849](https://github.com/raft-tech/TANF-app/issues/5849))
- We updated age validators and added parser-type validations to tighten data checks ([#5848](https://github.com/raft-tech/TANF-app/issues/5848), [#5833](https://github.com/raft-tech/TANF-app/issues/5833))

---

⚪️ **Total Issues:** 38  
✅ **Closed:** 16  
➡️ **Moved:** 12  
⬛️ **Unchanged:** 10  
🛑 **Blocked:** 0  

---

## [Goal 6: Documentation is current and helpful](https://github.com/raft-tech/TANF-app/issues/5435)

- ✅ [Create or modify maintenance page / error page (#5660)](https://github.com/raft-tech/TANF-app/issues/5660)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  


## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ✅ [Wire AV scan completion to transition DataFile.state → validated / scan_failed (#5547)](https://github.com/raft-tech/TANF-app/issues/5547)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [Wire parser task to transition DataFile.state → parsing / parsed_clean / parsed_with_errors (#5548)](https://github.com/raft-tech/TANF-app/issues/5548)  
_Remained in **Raft (Dev) Review**_  


## [(RE)Parsing refactor](https://github.com/raft-tech/TANF-app/issues/5565)

- ✅ [Document current parsing & reparsing flows (#5566)](https://github.com/raft-tech/TANF-app/issues/5566)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [FRA Post-MVP Enhancements](https://github.com/raft-tech/TANF-app/issues/4443)

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ✅ [Go Parser: Add structured JSON logging via log/slog (#5738)](https://github.com/raft-tech/TANF-app/issues/5738)  
_**Closed**_ - _Moved from **In Progress**_  


## [In-App Error Reporting - Foundational Design & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4629)

- ⬛️ [Error Reporting Research Synthesis (#5763)](https://github.com/raft-tech/TANF-app/issues/5763)  
_Remained in **UX Review**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ✅ [Keycloak: Promote Keycloak to Cloud.gov staging space (#5751)](https://github.com/raft-tech/TANF-app/issues/5751)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Keycloak: Promote Keycloak into the Production Space (#5761)](https://github.com/raft-tech/TANF-app/issues/5761)  
_Moved from **Product Backlog** to **In Progress**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Remained in **In Progress**_  

- ➡️ [1. Scaffold Standalone Next.js Admin Console (#5835)](https://github.com/raft-tech/TANF-app/issues/5835)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ➡️ [2. Configure Admin Authentication, Session, and CSRF Boundaries (#5836)](https://github.com/raft-tech/TANF-app/issues/5836)  
_Moved from **Product Backlog** to **In Progress**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  


## [Release Tracking](https://github.com/raft-tech/TANF-app/issues/5789)

- ✅ [Release Tracker v4.18.0 (#5811)](https://github.com/raft-tech/TANF-app/issues/5811)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Release Tracker v4.19.0 (#5854)](https://github.com/raft-tech/TANF-app/issues/5854)  
_**Closed**_ - _Moved from **In Progress**_  


## Issues without Parent

- ➡️ [Create new models to define an STTs participation in a particular Program (#5370)](https://github.com/raft-tech/TANF-app/issues/5370)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Create Statistical Weights Dataset for TANF Active Report Measures (#5699)](https://github.com/raft-tech/TANF-app/issues/5699)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ⬛️ [Update ZAP (#5798)](https://github.com/raft-tech/TANF-app/issues/5798)  
_Remained in **Current Sprint Backlog**_  

- ➡️ [Deindex dev environments from search engines (#5816)](https://github.com/raft-tech/TANF-app/issues/5816)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ✅ [Accept header/trailer-only active, aggregate, and stratum files (#5819)](https://github.com/raft-tech/TANF-app/issues/5819)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [[Tech Memo] Generic DataFile Orchestrator (Submission, Parse, Reparse, Tasks) (#5825)](https://github.com/raft-tech/TANF-app/issues/5825)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Add parser-side validation for datafile program type mismatches (#5833)](https://github.com/raft-tech/TANF-app/issues/5833)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Update Python and Go T5/M5 OASDI age validators to use AGE_FIRST DOB calculation (#5848)](https://github.com/raft-tech/TANF-app/issues/5848)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Update Vendor Product Manager contact on README (#5849)](https://github.com/raft-tech/TANF-app/issues/5849)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Implement Error Report Readme (#5853)](https://github.com/raft-tech/TANF-app/issues/5853)  
_**Closed**_ - _Moved from **Next Up: DEV**_  

- ➡️ [Transition TDP applications from app.cloud.gov to tanfdata.acf.hhs.gov domains (#5855)](https://github.com/raft-tech/TANF-app/issues/5855)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ⬛️ [CRM for STT info and behavior (#25)]()  
_Remained in **No Pipeline Info**_  

- ⬛️ [Plan & Prepare Summer 2026 STT Office Hours Webinar (#26)]()  
_Remained in **No Pipeline Info**_  

- ➡️ [[Spike] Create better Django model validation for Go parser schemas (#5866)](https://github.com/raft-tech/TANF-app/issues/5866)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ⬛️ [Feedback report upload support for subfolders (#5870)](https://github.com/raft-tech/TANF-app/issues/5870)  
_Remained in **Raft (Dev) Review**_  

- ✅ [[Bug] Downloaded submission filenames are missing program type (#5872)](https://github.com/raft-tech/TANF-app/issues/5872)  
_**Closed**_ - _Moved from **Next Up: DEV**_  

- ✅ [Feedback Reports tribal TANF selector support (#5873)](https://github.com/raft-tech/TANF-app/issues/5873)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [[BUG] Support admin reparse for legacy submitted DataFiles stuck in uploaded state (#5875)](https://github.com/raft-tech/TANF-app/issues/5875)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Error Research Next Step Ideation (#5883)](https://github.com/raft-tech/TANF-app/issues/5883)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Combine Submission History and File Upload tabs for Data File Submissions (#5885)](https://github.com/raft-tech/TANF-app/issues/5885)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Release Tracker v4.20.0 (#5897)](https://github.com/raft-tech/TANF-app/issues/5897)  
_Moved from **Product Backlog** to **In Progress**_  


