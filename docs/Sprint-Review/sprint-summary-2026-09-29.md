# Sprint Summary: Sep 16, 2026 - Sep 29, 2026

## Overview

- Closed the DataFile lifecycle cluster: stuck-file detection, API lifecycle exposure, and current-year stuck-submission email reporting. ([#5945](https://github.com/raft-tech/TANF-app/issues/5945), [#5973](https://github.com/raft-tech/TANF-app/issues/5973), [#5987](https://github.com/raft-tech/TANF-app/issues/5987))
- Security and auth hardening finished: Keycloak CVE update, staging ZAP CORS and security-header fixes, feedback login requirement, and the EMAIL_CHANGED investigation. ([#6046](https://github.com/raft-tech/TANF-app/issues/6046), [#6134](https://github.com/raft-tech/TANF-app/issues/6134), [#6048](https://github.com/raft-tech/TANF-app/issues/6048), [#6047](https://github.com/raft-tech/TANF-app/issues/6047))
- Go Parser canary routing in Django closed, and v4.25.0 release notes shipped. Feedback report download statistics development also closed while the design panel stays in QASP Review. ([#5737](https://github.com/raft-tech/TANF-app/issues/5737), [#6069](https://github.com/raft-tech/TANF-app/issues/6069), [#6013](https://github.com/raft-tech/TANF-app/issues/6013), [#6012](https://github.com/raft-tech/TANF-app/issues/6012))
- Admin and UX design moved forward: the Admin Dashboard reached Closed status, User Requests moved into UX Review, and help-content naming work entered the current sprint backlog. ([#5966](https://github.com/raft-tech/TANF-app/issues/5966), [#5968](https://github.com/raft-tech/TANF-app/issues/5968), [#5928](https://github.com/raft-tech/TANF-app/issues/5928))
- Two items stayed blocked (SSP/STT frontend decoupling and the Tribal TANF WPR Knowledge Center guide). Keycloak canary, FTANF research, and no-caseload design work continued. ([#5376](https://github.com/raft-tech/TANF-app/issues/5376), [#6132](https://github.com/raft-tech/TANF-app/issues/6132), [#5757](https://github.com/raft-tech/TANF-app/issues/5757), [#5683](https://github.com/raft-tech/TANF-app/issues/5683), [#6020](https://github.com/raft-tech/TANF-app/issues/6020))

---

⚪️ **Total Issues:** 38  
✅ **Closed:** 11  
➡️ **Moved:** 4  
⬛️ **Unchanged:** 21  
🛑 **Blocked:** 2  

---

## [Prioritized User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4624)

- ➡️ [Design Ideation: Explore Help Content and Naming for Report Pages (#5928)](https://github.com/raft-tech/TANF-app/issues/5928)  
_Moved from **Planned for Next Sprint** to **Current Sprint Backlog**_  


## [Operational Backlog](https://github.com/raft-tech/TANF-app/issues/4627)

- ⬛️ [Ensure proper file closure after parsing to prevent 'too many open files' error (#2850)](https://github.com/raft-tech/TANF-app/issues/2850)  
_Remained in **Raft (Dev) Review**_  

- ⬛️ [Add Django Admin Console trigger for ETL pipelines (#6035)](https://github.com/raft-tech/TANF-app/issues/6035)  
_Remained in **In Progress**_  

- ✅ [Allow logged-out deeplinking (#6045)](https://github.com/raft-tech/TANF-app/issues/6045)  
_**Closed**_ - _Moved from **Closed**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Prioritized Bug Reports](https://github.com/raft-tech/TANF-app/issues/4968)

- ⬛️ [BUG KeyError Events: Error 'state_nonce_tracker' in Sentry (#5859)](https://github.com/raft-tech/TANF-app/issues/5859)  
_Remained in **Backlog**_  


## [TDP Knowledge Center](https://github.com/raft-tech/TANF-app/issues/5455)

- 🛑 [Update Tribal TANF WPR Feedback Reference Guide in Knowledge Center (#6132)](https://github.com/raft-tech/TANF-app/issues/6132)  
_Remained in **Blocked**_  


## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ✅ [Improve and update stuck file detection to use DataFile lifecycle state machine (#5945)](https://github.com/raft-tech/TANF-app/issues/5945)  
_**Closed**_ - _Moved from **Closed**_  

- ✅ [Expose DataFile Lifecycle State in the API -> Need this for Admin App (#5973)](https://github.com/raft-tech/TANF-app/issues/5973)  
_**Closed**_ - _Moved from **Closed**_  

- ✅ [Update stuck files admin email to report only current-year stuck submissions (#5987)](https://github.com/raft-tech/TANF-app/issues/5987)  
_**Closed**_ - _Moved from **Closed**_  


## [(RE)Parsing refactor](https://github.com/raft-tech/TANF-app/issues/5565)

- ⬛️ [Introduce `ParsingService` and refactor Celery task to use it (#5567)](https://github.com/raft-tech/TANF-app/issues/5567)  
_Remained in **In Progress**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [5. Build Admin Read-Only List and Detail View Pattern (#5844)](https://github.com/raft-tech/TANF-app/issues/5844)  
_Remained in **Raft (Dev) Review**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ✅ [Go Parser: Implement canary routing in Django (#5737)](https://github.com/raft-tech/TANF-app/issues/5737)  
_**Closed**_ - _Moved from **Closed**_  

- ⬛️ [[Bug] Investigate flaky go-parser tests (#6049)](https://github.com/raft-tech/TANF-app/issues/6049)  
_Remained in **Current Sprint Backlog**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ⬛️ [Configure Grafana SSO via production Keycloak instance (#5754)](https://github.com/raft-tech/TANF-app/issues/5754)  
_Remained in **Backlog**_  

- ⬛️ [Set up Keycloak Prometheus metrics, Grafana dashboards, and alerting (#5755)](https://github.com/raft-tech/TANF-app/issues/5755)  
_Remained in **Backlog**_  

- ⬛️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Remained in **Raft (Dev) Review**_  

- ⬛️ [Create GHCR robot accounts and CI/CD deployments for Keycloak (#5980)](https://github.com/raft-tech/TANF-app/issues/5980)  
_Remained in **Raft (Dev) Review**_  

- ✅ [Update keycloak to resolve CVE (#6046)](https://github.com/raft-tech/TANF-app/issues/6046)  
_**Closed**_ - _Moved from **Closed**_  


## [Design & Implement: Admin Dashboard View](https://github.com/raft-tech/TANF-app/issues/5951)

- ➡️ [Design Admin Dashboard (#5966)](https://github.com/raft-tech/TANF-app/issues/5966)  
_Moved from **Done and Ready for Demo** to **Closed**_  


## [Design & Implement: Users Pages](https://github.com/raft-tech/TANF-app/issues/5952)

- ⬛️ [Design: User Feedback Page (#5964)](https://github.com/raft-tech/TANF-app/issues/5964)  
_Remained in **UX Review**_  

- ➡️ [Design: User Requests and Authorization Page and Interaction (#5968)](https://github.com/raft-tech/TANF-app/issues/5968)  
_Moved from **In Progress** to **UX Review**_  


## [Allow admins to toggle Feedback Reports between STT and admin modes](https://github.com/raft-tech/TANF-app/issues/5991)

- ⬛️ [Design: Allow Regional Staff and Admin to view STT Mode for Feedback Reports via Statistics Panel (#6002)](https://github.com/raft-tech/TANF-app/issues/6002)  
_Remained in **In Progress**_  


## [Migrate to tanfdata.acf.hhs.gov](https://github.com/raft-tech/TANF-app/issues/5993)

- ➡️ [Migrate Knowledge Center to `.tanfdata.acf.hhs.gov` domain (#5916)](https://github.com/raft-tech/TANF-app/issues/5916)  
_Moved from **Planned for Next Sprint** to **Current Sprint Backlog**_  


## [Support No-Caseload Reporting](https://github.com/raft-tech/TANF-app/issues/6000)

- ⬛️ [Design No-Caseload Reporting Experience (#6020)](https://github.com/raft-tech/TANF-app/issues/6020)  
_Remained in **In Progress**_  

- ⬛️ [Research: Planning & Facilitation for no caseload reporting (#6060)](https://github.com/raft-tech/TANF-app/issues/6060)  
_Remained in **Backlog**_  


## [Feedback Report Download Statistics](https://github.com/raft-tech/TANF-app/issues/6011)

- ⬛️ [Design Feedback Report Download Statistics Panel (#6012)](https://github.com/raft-tech/TANF-app/issues/6012)  
_Remained in **QASP Review**_  

- ✅ [Dev - Feedback Report Download Statistics (#6013)](https://github.com/raft-tech/TANF-app/issues/6013)  
_**Closed**_ - _Moved from **Closed**_  


## [Upload Feedback Reports](https://github.com/raft-tech/TANF-app/issues/6014)

- ⬛️ [Feedback Report Download Statistics (#6011)](https://github.com/raft-tech/TANF-app/issues/6011)  
_Remained in **Backlog**_  


## [Optional Notes field for uploads](https://github.com/raft-tech/TANF-app/issues/6015)

- ⬛️ [Design Optional Notes Field for Uploads (#6033)](https://github.com/raft-tech/TANF-app/issues/6033)  
_Remained in **QASP Review**_  


## [ACF-204: UX research for STT form and narrative submission, validation, and admin audit](https://github.com/raft-tech/TANF-app/issues/6059)

- ⬛️ [ACF-204: Create a minimal UX research plan (feasibility, preliminary research, approaches) (#6056)](https://github.com/raft-tech/TANF-app/issues/6056)  
_Remained in **In Progress**_  


## [Decouple SSP and program participation from the STT model](https://github.com/raft-tech/TANF-app/issues/6062)

- 🛑 [Front end changes to decouple SSP data from the STT model. (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Remained in **Blocked**_  


## [In-app User Feedback](https://github.com/raft-tech/TANF-app/issues/6063)

- ✅ [Require login for feedback submissions (#6048)](https://github.com/raft-tech/TANF-app/issues/6048)  
_**Closed**_ - _Moved from **Closed**_  


## [Security Improvements](https://github.com/raft-tech/TANF-app/issues/6065)

- ✅ [[Bug] Investigate `EMAIL_CHANGED` SET associated with no user (#6047)](https://github.com/raft-tech/TANF-app/issues/6047)  
_**Closed**_ - _Moved from **Closed**_  

- ⬛️ [Request Param Mismatch (#6051)](https://github.com/raft-tech/TANF-app/issues/6051)  
_Remained in **Raft (Dev) Review**_  

- ✅ [Remediate staging ZAP CORS and security-header findings (#6134)](https://github.com/raft-tech/TANF-app/issues/6134)  
_**Closed**_ - _Moved from **Closed**_  


## [Complete canonical Program and Section on DataFile](https://github.com/raft-tech/TANF-app/issues/6066)

- ⬛️ [Remove legacy DataFile program and section enum fields. (#5984)](https://github.com/raft-tech/TANF-app/issues/5984)  
_Remained in **Raft (Dev) Review**_  


## [Release Tracker v4.25.0](https://github.com/raft-tech/TANF-app/issues/6068)

- ✅ [Release Notes v4.25.0 (#6069)](https://github.com/raft-tech/TANF-app/issues/6069)  
_**Closed**_ - _Moved from **Closed**_
