# Sprint Summary: Sep 02, 2026 - Sep 15, 2026

## Overview

- Closed a strong set of delivery items: Smart Upload file-submission error handling and form reset, React Admin UX/IA exploration, and the metadata-driven admin form contract. ([#5603](https://github.com/raft-tech/TANF-app/issues/5603), [#5651](https://github.com/raft-tech/TANF-app/issues/5651), [#5842](https://github.com/raft-tech/TANF-app/issues/5842))
- Advanced (Re)Parse data-path work by adding a file-state transition log and narrowing stuck-submission admin email reporting to current-year cases. ([#5946](https://github.com/raft-tech/TANF-app/issues/5946), [#5987](https://github.com/raft-tech/TANF-app/issues/5987))
- Hardened admin auth by isolating TDP Admin authentication into a separate Keycloak realm. ([#5986](https://github.com/raft-tech/TANF-app/issues/5986))
- Feedback Report Download Statistics development closed; related design and statistics-panel work remained in progress. ([#6013](https://github.com/raft-tech/TANF-app/issues/6013), [#6002](https://github.com/raft-tech/TANF-app/issues/6002), [#6011](https://github.com/raft-tech/TANF-app/issues/6011), [#6012](https://github.com/raft-tech/TANF-app/issues/6012))
- Backend and platform work continued on FTANF replacement research, Go Parser canary routing, and staged Keycloak rollout; Operations also advanced file-handle closure and request-param mismatch through review. ([#5683](https://github.com/raft-tech/TANF-app/issues/5683), [#5737](https://github.com/raft-tech/TANF-app/issues/5737), [#5757](https://github.com/raft-tech/TANF-app/issues/5757), [#2850](https://github.com/raft-tech/TANF-app/issues/2850), [#6051](https://github.com/raft-tech/TANF-app/issues/6051))

---

⚪️ **Total Issues:** 24  
✅ **Closed:** 8  
➡️ **Moved:** 3  
⬛️ **Unchanged:** 12  
🛑 **Blocked:** 1  

---

## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ✅ [Add transition log for file state (#5946)](https://github.com/raft-tech/TANF-app/issues/5946)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Expose DataFile Lifecycle State in the API -> Need this for Admin App (#5973)](https://github.com/raft-tech/TANF-app/issues/5973)  
_**Closed**_ - _Moved from **Current Sprint Backlog**_  

- ✅ [Update stuck files admin email to report only current-year stuck submissions (#5987)](https://github.com/raft-tech/TANF-app/issues/5987)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ⬛️ [BUG KeyError Events: Error 'state_nonce_tracker' in Sentry (#5859)](https://github.com/raft-tech/TANF-app/issues/5859)  
_Remained in **Raft (Dev) Review**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ⬛️ [Go Parser: Implement canary routing in Django (#5737)](https://github.com/raft-tech/TANF-app/issues/5737)  
_Remained in **Raft (Dev) Review**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ⬛️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Remained in **In Progress**_  

- 🛑 [Create GHCR robot accounts and CI/CD deployments for Keycloak (#5980)](https://github.com/raft-tech/TANF-app/issues/5980)  
_Moved from **In Progress** to **Blocked**_  

- ✅ [Isolate TDP Admin Authentication in a Separate Keycloak Realm (#5986)](https://github.com/raft-tech/TANF-app/issues/5986)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ✅ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_**Closed**_ - _Moved from **In Progress**_  

- ✅ [4. Implement Metadata-Driven Admin Form Contract (#5842)](https://github.com/raft-tech/TANF-app/issues/5842)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [Design Admin Dashboard (#5966)](https://github.com/raft-tech/TANF-app/issues/5966)  
_Remained in **UX Review**_  

- ⬛️ [Design: User Requests and Authorization Page and Interaction (#5968)](https://github.com/raft-tech/TANF-app/issues/5968)  
_Remained in **In Progress**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ➡️ [Ensure proper file closure after parsing to prevent 'too many open files' error (#2850)](https://github.com/raft-tech/TANF-app/issues/2850)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ⬛️ [Front end changes to decouple SSP data from the STT model. (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Remained in **In Progress**_  

- ➡️ [Remove legacy DataFile program and section enum fields. (#5984)](https://github.com/raft-tech/TANF-app/issues/5984)  
_Moved from **Raft (Dev) Review** to **Current Sprint Backlog**_  

- ➡️ [Request Param Mismatch (#6051)](https://github.com/raft-tech/TANF-app/issues/6051)  
_Moved from **In Progress** to **Raft (Dev) Review**_  


## [Smart Upload / One-Stop Submission Flow](https://github.com/raft-tech/TANF-app/issues/5924)

- ✅ [File submission error message and form reset (#5603)](https://github.com/raft-tech/TANF-app/issues/5603)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [Design No-Caseload Reporting Experience (#6020)](https://github.com/raft-tech/TANF-app/issues/6020)  
_Remained in **QASP Review**_  


## [Upload Feedback Reports](https://github.com/raft-tech/TANF-app/issues/6014)

- ⬛️ [Design: Allow Regional Staff and Admin to view STT Mode for Feedback Reports via Statistics Panel (#6002)](https://github.com/raft-tech/TANF-app/issues/6002)  
_Remained in **In Progress**_  

- ⬛️ [Feedback Report Download Statistics (#6011)](https://github.com/raft-tech/TANF-app/issues/6011)  
_Remained in **In Progress**_  

- ⬛️ [Design Feedback Report Download Statistics Panel (#6012)](https://github.com/raft-tech/TANF-app/issues/6012)  
_Remained in **In Progress**_  

- ✅ [Dev - Feedback Report Download Statistics (#6013)](https://github.com/raft-tech/TANF-app/issues/6013)  
_**Closed**_ - _Moved from **In Progress**_  

- ⬛️ [Design Optional Notes Field for Uploads (#6033)](https://github.com/raft-tech/TANF-app/issues/6033)  
_Remained in **In Progress**_
