# Sprint Summary: Jul 08, 2026 - Jul 21, 2026

## Overview

- Finalized the descriptions for centralized feedback reports in Knowledge Center, so users get clearer feedback. ([#5504](https://github.com/raft-tech/TANF-app/issues/5504))

- Added a cancel hook to stop data-file submission processing when canceled, preventing downstream work. ([#5550](https://github.com/raft-tech/TANF-app/issues/5550))

- Completed the Statistical Weights Dataset for TANF Active Report Measures, enabling more accurate metrics. ([#5699](https://github.com/raft-tech/TANF-app/issues/5699))

- Wrapped up the spike to improve Django model validation for Go parser schemas, strengthening data checks. ([#5866](https://github.com/raft-tech/TANF-app/issues/5866))

- Released Tracker version 4.20.0, completing that release. ([#5897](https://github.com/raft-tech/TANF-app/issues/5897))

- Fixed the Admin STT switch rendering issue that could misrender Section 4 inputs; the fix is done. ([#5919](https://github.com/raft-tech/TANF-app/issues/5919))

---

⚪️ **Total Issues:** 31  
✅ **Closed:** 6  
➡️ **Moved:** 20  
⬛️ **Unchanged:** 5  
🛑 **Blocked:** 0  

---

## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ✅ [Add cancel hook to transition DataFile.state → canceled and stop downstream processing (#5550)](https://github.com/raft-tech/TANF-app/issues/5550)  
_**Closed**_ - _Moved from **Product Backlog**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ➡️ [BUG KeyError Events: Error 'state_nonce_tracker' in Sentry (#5859)](https://github.com/raft-tech/TANF-app/issues/5859)  
_Moved from **Next Up: DEV** to **In Progress**_  


## [FRA Post-MVP Enhancements](https://github.com/raft-tech/TANF-app/issues/4443)

- ✅ [Finalize Descriptions for Centralized Feedback Reports in KC (#5504)](https://github.com/raft-tech/TANF-app/issues/5504)  
_**Closed**_ - _Moved from **In Progress**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ➡️ [Go Parser: Add Prometheus metrics (#5739)](https://github.com/raft-tech/TANF-app/issues/5739)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Deploy the Go parser through the standard CI/CD process (#5909)](https://github.com/raft-tech/TANF-app/issues/5909)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ➡️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ⬛️ [Keycloak: Promote Keycloak into the Production Space (#5761)](https://github.com/raft-tech/TANF-app/issues/5761)  
_Remained in **In Progress**_  

- ➡️ [Track direct API client request metrics in Grafana (#5900)](https://github.com/raft-tech/TANF-app/issues/5900)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  


## [Migrate Knowledge Center to `.tanfdata.acf.hhs.gov` domain](https://github.com/raft-tech/TANF-app/issues/5916)

- ➡️ [Knowledge Center Audit/Remove absolute links (#5929)](https://github.com/raft-tech/TANF-app/issues/5929)  
_Moved from **Product Backlog** to **In Progress**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Remained in **In Progress**_  

- ➡️ [2. Configure Admin Authentication, Session, and CSRF Boundaries (#5836)](https://github.com/raft-tech/TANF-app/issues/5836)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ➡️ [3. Establish Admin API Boundary (#5837)](https://github.com/raft-tech/TANF-app/issues/5837)  
_Moved from **Product Backlog** to **In Progress**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  

- ➡️ [Update ZAP (#5798)](https://github.com/raft-tech/TANF-app/issues/5798)  
_Moved from **Current Sprint Backlog** to **In Progress**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ➡️ [[Spike]: Design proper pagination for History tables (#5538)](https://github.com/raft-tech/TANF-app/issues/5538)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


## Issues without Parent

- ➡️ [Create new models to define an STTs participation in a particular Program (#5370)](https://github.com/raft-tech/TANF-app/issues/5370)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ➡️ [Front end changes to decouple SSP data from the STT model. (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ➡️ [Django query optimization (#5383)](https://github.com/raft-tech/TANF-app/issues/5383)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  

- ➡️ [Fix Callback state_nonce_tracker KeyError and Return Friendly “Session Expired” Message (#5574)](https://github.com/raft-tech/TANF-app/issues/5574)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ➡️ [File submission error message and form reset (#5603)](https://github.com/raft-tech/TANF-app/issues/5603)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ✅ [Create Statistical Weights Dataset for TANF Active Report Measures (#5699)](https://github.com/raft-tech/TANF-app/issues/5699)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Parser task cleanup can mask root failures when dfs is not created (#5806)](https://github.com/raft-tech/TANF-app/issues/5806)  
_Moved from **Product Backlog** to **In Progress**_  

- ⬛️ [CRM for STT info and behavior (#25)]()  
_Remained in **No Pipeline Info**_  

- ✅ [[Spike] Create better Django model validation for Go parser schemas (#5866)](https://github.com/raft-tech/TANF-app/issues/5866)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Combine Submission History and File Upload tabs for Data File Submissions (#5885)](https://github.com/raft-tech/TANF-app/issues/5885)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ✅ [Release Tracker v4.20.0 (#5897)](https://github.com/raft-tech/TANF-app/issues/5897)  
_**Closed**_ - _Moved from **In Progress**_  

- ➡️ [Deploy Celery, backend, and Go parser apps in parallel via CI/CD (#5910)](https://github.com/raft-tech/TANF-app/issues/5910)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [[BUG] Keycloak configure script fails when tdp-api-audience client scope already exists (#5911)](https://github.com/raft-tech/TANF-app/issues/5911)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ✅ [[BUG] Admin STT switch can leave Section 4 Stratum file input misrendered (#5919)](https://github.com/raft-tech/TANF-app/issues/5919)  
_**Closed**_ - _Moved from **Next Up: DEV**_  

- ➡️ [Replace configure-idps.sh with declarative Keycloak configuration management (#5958)](https://github.com/raft-tech/TANF-app/issues/5958)  
_Moved from **Product Backlog** to **Current Sprint Backlog**_  


