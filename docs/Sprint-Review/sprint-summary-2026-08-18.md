# Sprint Summary: Aug 05, 2026 - Aug 18, 2026

## Overview

- Completed backend work to define STT participation in programs and improved data access for reporting. ([#5370](https://github.com/raft-tech/TANF-app/issues/5370), [#5383](https://github.com/raft-tech/TANF-app/issues/5383))
- Finished performance and monitoring improvements: added metrics for the Go parser, started tracking API requests in Grafana, and deployed the Go parser via CI/CD. ([#5739](https://github.com/raft-tech/TANF-app/issues/5739), [#5900](https://github.com/raft-tech/TANF-app/issues/5900), [#5909](https://github.com/raft-tech/TANF-app/issues/5909))
- Advanced production readiness for Keycloak and security: promoted Keycloak to production, fixed the configure script, and moved to declarative configuration management. ([#5761](https://github.com/raft-tech/TANF-app/issues/5761), [#5911](https://github.com/raft-tech/TANF-app/issues/5911), [#5958](https://github.com/raft-tech/TANF-app/issues/5958))
- Bug fixes and cleanup improved reliability: fixed duplicated counts in the reparse model and cleaned up error reports. ([#5985](https://github.com/raft-tech/TANF-app/issues/5985), [#5927](https://github.com/raft-tech/TANF-app/issues/5927))
- Planning and design work progressed, including the How We Work workshop and ongoing admin dashboard/history pagination design. ([#5593](https://github.com/raft-tech/TANF-app/issues/5593), [#5538](https://github.com/raft-tech/TANF-app/issues/5538))

---

⚪️ **Total Issues:** 44  
✅ **Closed:** 15  
➡️ **Moved:** 21  
⬛️ **Unchanged:** 7  
🛑 **Blocked:** 1  

---

## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ⬛️ [BUG KeyError Events: Error 'state_nonce_tracker' in Sentry (#5859)](https://github.com/raft-tech/TANF-app/issues/5859)  
_Remained in **Raft (Dev) Review**_  

- ➡️ [[Bug] Resolve new frontend ZAP failure (#6004)](https://github.com/raft-tech/TANF-app/issues/6004)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ✅ [Go Parser: Add Prometheus metrics (#5739)](https://github.com/raft-tech/TANF-app/issues/5739)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Deploy the Go parser through the standard CI/CD process (#5909)](https://github.com/raft-tech/TANF-app/issues/5909)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ⬛️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Remained in **In Progress**_  

- ✅ [Keycloak: Promote Keycloak into the Production Space (#5761)](https://github.com/raft-tech/TANF-app/issues/5761)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Track direct API client request metrics in Grafana (#5900)](https://github.com/raft-tech/TANF-app/issues/5900)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Remained in **In Progress**_  

- ➡️ [4. Implement Metadata-Driven Admin Form Contract (#5842)](https://github.com/raft-tech/TANF-app/issues/5842)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ➡️ [Design Admin Dashboard (#5966)](https://github.com/raft-tech/TANF-app/issues/5966)  
_Moved from **In Progress** to **UX Review**_  

- ➡️ [Design: User Requests and Authorization Page and Interaction (#5968)](https://github.com/raft-tech/TANF-app/issues/5968)  
_Moved from **Product Backlog** to **In Progress**_  

- ✅ [Implement Admin Navigation and Interactivity (#5983)](https://github.com/raft-tech/TANF-app/issues/5983)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ✅ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [Update ZAP (#5798)](https://github.com/raft-tech/TANF-app/issues/5798)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [Release Tracking](https://github.com/raft-tech/TANF-app/issues/5789)

- ⬛️ [Release Tracker v4.23.0 (#5988)](https://github.com/raft-tech/TANF-app/issues/5988)  
_Remained in **In Progress**_  

- ➡️ [v4.23.0 Release Notes and Knowledge Center updates (#5989)](https://github.com/raft-tech/TANF-app/issues/5989)  
_Moved from **In Progress** to **QASP Review**_  


## [Upload Feedback Reports](https://github.com/raft-tech/TANF-app/issues/6014)

- ➡️ [Design: Allow Regional Staff and Admin to view STT Mode for Feedback Reports via Statistics Panel (#6002)](https://github.com/raft-tech/TANF-app/issues/6002)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Feedback Report Download Statistics (#6011)](https://github.com/raft-tech/TANF-app/issues/6011)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Design Feedback Report Download Statistics Panel (#6012)](https://github.com/raft-tech/TANF-app/issues/6012)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Dev - Feedback Report Download Statistics (#6013)](https://github.com/raft-tech/TANF-app/issues/6013)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [Design Optional Notes Field for Uploads (#6033)](https://github.com/raft-tech/TANF-app/issues/6033)  
_Moved from **Product Backlog** to **In Progress**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ➡️ [[Spike]: Design proper pagination for History tables (#5538)](https://github.com/raft-tech/TANF-app/issues/5538)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ✅ [Validate Feedback Reports source uploads match selected program type (#5992)](https://github.com/raft-tech/TANF-app/issues/5992)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  


## Issues without Parent

- ✅ [Create new models to define an STTs participation in a particular Program (#5370)](https://github.com/raft-tech/TANF-app/issues/5370)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- 🛑 [Front end changes to decouple SSP data from the STT model. (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Moved from **Raft (Dev) Review** to **Blocked**_  

- ✅ [Django query optimization (#5383)](https://github.com/raft-tech/TANF-app/issues/5383)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [File submission error message and form reset (#5603)](https://github.com/raft-tech/TANF-app/issues/5603)  
_Remained in **Raft (Dev) Review**_  

- ⬛️ [CRM for STT info and behavior (#25)]()  
_Remained in **No Pipeline Info**_  

- ✅ [[BUG] Keycloak configure script fails when tdp-api-audience client scope already exists (#5911)](https://github.com/raft-tech/TANF-app/issues/5911)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Remove Internal Variable Name Column and Adjust Widths in Generated Error Reports (#5927)](https://github.com/raft-tech/TANF-app/issues/5927)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Knowledge Center Update: Add Guidance on Timely Data Submission Expectations (#5940)](https://github.com/raft-tech/TANF-app/issues/5940)  
_Moved from **In Progress** to **QASP Review**_  

- ➡️ [Add transition log for file state (#5946)](https://github.com/raft-tech/TANF-app/issues/5946)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ✅ [Replace configure-idps.sh with declarative Keycloak configuration management (#5958)](https://github.com/raft-tech/TANF-app/issues/5958)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [Expose DataFile Lifecycle State in the API -> Need this for Admin App (#5973)](https://github.com/raft-tech/TANF-app/issues/5973)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [Create GHCR robot accounts and CI/CD deployments for Keycloak (#5980)](https://github.com/raft-tech/TANF-app/issues/5980)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  

- ➡️ [Remove legacy DataFile program and section enum fields. (#5984)](https://github.com/raft-tech/TANF-app/issues/5984)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ✅ [[BUG] Duplicated counts in the reparse model (#5985)](https://github.com/raft-tech/TANF-app/issues/5985)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Isolate TDP Admin Authentication in a Separate Keycloak Realm (#5986)](https://github.com/raft-tech/TANF-app/issues/5986)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Update stuck files admin email to report only current-year stuck submissions (#5987)](https://github.com/raft-tech/TANF-app/issues/5987)  
_Moved from **Next Up: DEV** to **Current Sprint Backlog**_  

- ✅ [Remediate parent-domain scope on sessionid cookie (#5999)](https://github.com/raft-tech/TANF-app/issues/5999)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ➡️ [[Bug] Remove `SUB` characters from files before parsing (#6026)](https://github.com/raft-tech/TANF-app/issues/6026)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [[Bug] SVD1 (#6031)](https://github.com/raft-tech/TANF-app/issues/6031)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [[Bug] SVD2 (#6032)](https://github.com/raft-tech/TANF-app/issues/6032)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


