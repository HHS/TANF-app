# Sprint Summary: Aug 19, 2026 - Sep 01, 2026

## Overview

- Front-end work to decouple SSP data from the STT model moved from blocked to in progress, signaling renewed momentum. ([#5376](https://github.com/raft-tech/TANF-app/issues/5376))
- Several high-priority fixes were completed and closed, including removing SUB characters before parsing and fixes for SVD1, SVD2, plus a frontend ZAP issue. ([#6026](https://github.com/raft-tech/TANF-app/issues/6026), [#6031](https://github.com/raft-tech/TANF-app/issues/6031), [#6032](https://github.com/raft-tech/TANF-app/issues/6032), [#6004](https://github.com/raft-tech/TANF-app/issues/6004))
- History table pagination design was finalized and closed, along with the admin form contract implementation. ([#5538](https://github.com/raft-tech/TANF-app/issues/5538), [#5842](https://github.com/raft-tech/TANF-app/issues/5842))
- Knowledge Center guidance on timely data submission was published, and release materials and tracker updates were released. ([#5940](https://github.com/raft-tech/TANF-app/issues/5940), [#5989](https://github.com/raft-tech/TANF-app/issues/5989), [#5988](https://github.com/raft-tech/TANF-app/issues/5988))
- Go Parser work progressed toward active development with the canary routing in Django moving from planning toward next steps. ([#5737](https://github.com/raft-tech/TANF-app/issues/5737))

---

⚪️ **Total Issues:** 33  
✅ **Closed:** 11  
➡️ **Moved:** 12  
⬛️ **Unchanged:** 10  
🛑 **Blocked:** 0  

---

## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ➡️ [Add transition log for file state (#5946)](https://github.com/raft-tech/TANF-app/issues/5946)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ⬛️ [Expose DataFile Lifecycle State in the API -> Need this for Admin App (#5973)](https://github.com/raft-tech/TANF-app/issues/5973)  
_Remained in **Current Sprint Backlog**_  

- ➡️ [Update stuck files admin email to report only current-year stuck submissions (#5987)](https://github.com/raft-tech/TANF-app/issues/5987)  
_Moved from **Current Sprint Backlog** to **In Progress**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ⬛️ [BUG KeyError Events: Error 'state_nonce_tracker' in Sentry (#5859)](https://github.com/raft-tech/TANF-app/issues/5859)  
_Remained in **Raft (Dev) Review**_  

- ✅ [[Bug] Resolve new frontend ZAP failure (#6004)](https://github.com/raft-tech/TANF-app/issues/6004)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ➡️ [Go Parser: Implement canary routing in Django (#5737)](https://github.com/raft-tech/TANF-app/issues/5737)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ➡️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ➡️ [Create GHCR robot accounts and CI/CD deployments for Keycloak (#5980)](https://github.com/raft-tech/TANF-app/issues/5980)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Isolate TDP Admin Authentication in a Separate Keycloak Realm (#5986)](https://github.com/raft-tech/TANF-app/issues/5986)  
_Moved from **In Progress** to **Raft (Dev) Review**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Remained in **In Progress**_  

- ✅ [4. Implement Metadata-Driven Admin Form Contract (#5842)](https://github.com/raft-tech/TANF-app/issues/5842)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Design Admin Dashboard (#5966)](https://github.com/raft-tech/TANF-app/issues/5966)  
_Moved from **QASP Review** to **UX Review**_  

- ⬛️ [Design: User Requests and Authorization Page and Interaction (#5968)](https://github.com/raft-tech/TANF-app/issues/5968)  
_Remained in **In Progress**_  

- ✅ [Implement Admin Navigation and Interactivity (#5983)](https://github.com/raft-tech/TANF-app/issues/5983)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ➡️ [Front end changes to decouple SSP data from the STT model. (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Moved from **Blocked** to **In Progress**_  

- ➡️ [Remove legacy DataFile program and section enum fields. (#5984)](https://github.com/raft-tech/TANF-app/issues/5984)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ➡️ [Request Param Mismatch (#6051)](https://github.com/raft-tech/TANF-app/issues/6051)  
_Moved from **Product Backlog** to **In Progress**_  


## [Release Tracking](https://github.com/raft-tech/TANF-app/issues/5789)

- ✅ [Release Tracker v4.23.0 (#5988)](https://github.com/raft-tech/TANF-app/issues/5988)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [v4.23.0 Release Notes and Knowledge Center updates (#5989)](https://github.com/raft-tech/TANF-app/issues/5989)  
_**Closed**_ - _Moved from **QASP Review**_  


## [Smart Upload / One-Stop Submission Flow](https://github.com/raft-tech/TANF-app/issues/5924)

- ✅ [File submission error message and form reset (#5603)](https://github.com/raft-tech/TANF-app/issues/5603)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [Design No-Caseload Reporting Experience (#6020)](https://github.com/raft-tech/TANF-app/issues/6020)  
_Moved from **Product Backlog** to **In Progress**_  


## [Upload Feedback Reports](https://github.com/raft-tech/TANF-app/issues/6014)

- ⬛️ [Design: Allow Regional Staff and Admin to view STT Mode for Feedback Reports via Statistics Panel (#6002)](https://github.com/raft-tech/TANF-app/issues/6002)  
_Remained in **In Progress**_  

- ⬛️ [Feedback Report Download Statistics (#6011)](https://github.com/raft-tech/TANF-app/issues/6011)  
_Remained in **In Progress**_  

- ⬛️ [Design Feedback Report Download Statistics Panel (#6012)](https://github.com/raft-tech/TANF-app/issues/6012)  
_Remained in **In Progress**_  

- ➡️ [Dev - Feedback Report Download Statistics (#6013)](https://github.com/raft-tech/TANF-app/issues/6013)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ⬛️ [Design Optional Notes Field for Uploads (#6033)](https://github.com/raft-tech/TANF-app/issues/6033)  
_Remained in **In Progress**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ✅ [[Spike]: Design proper pagination for History tables (#5538)](https://github.com/raft-tech/TANF-app/issues/5538)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## Issues without Parent

- ⬛️ [CRM for STT info and behavior (#25)]()  
_Remained in **No Pipeline Info**_  

- ✅ [Knowledge Center Update: Add Guidance on Timely Data Submission Expectations (#5940)](https://github.com/raft-tech/TANF-app/issues/5940)  
_**Closed**_ - _Moved from **QASP Review**_  

- ✅ [[Bug] Remove `SUB` characters from files before parsing (#6026)](https://github.com/raft-tech/TANF-app/issues/6026)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [[Bug] SVD1 (#6031)](https://github.com/raft-tech/TANF-app/issues/6031)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [[Bug] SVD2 (#6032)](https://github.com/raft-tech/TANF-app/issues/6032)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


