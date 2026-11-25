# Sprint Summary: Sep 30, 2026 - Oct 13, 2026

## Overview

- Closed parsing file-handle cleanup, the Admin read-only list and detail pattern, User Feedback page and Admin Dashboard design, ETL Grafana tables, the Tribal TANF WPR Knowledge Center guide update, and the FTANF AFN convention research handout. ([#2850](https://github.com/raft-tech/TANF-app/issues/2850), [#5844](https://github.com/raft-tech/TANF-app/issues/5844), [#5964](https://github.com/raft-tech/TANF-app/issues/5964), [#5966](https://github.com/raft-tech/TANF-app/issues/5966), [#6093](https://github.com/raft-tech/TANF-app/issues/6093), [#6132](https://github.com/raft-tech/TANF-app/issues/6132), [#6145](https://github.com/raft-tech/TANF-app/issues/6145))
- FRA FY25 submission disable moved into Raft (Dev) Review. ([#6096](https://github.com/raft-tech/TANF-app/issues/6096))
- Two items stayed blocked: SSP/STT frontend decoupling and the Request Param Mismatch investigation. ([#5376](https://github.com/raft-tech/TANF-app/issues/5376), [#6051](https://github.com/raft-tech/TANF-app/issues/6051))
- Design work held in QASP Review: feedback STT-mode panel, download statistics panel, optional upload notes, and User Requests authorization. ([#6002](https://github.com/raft-tech/TANF-app/issues/6002), [#6012](https://github.com/raft-tech/TANF-app/issues/6012), [#6033](https://github.com/raft-tech/TANF-app/issues/6033), [#5968](https://github.com/raft-tech/TANF-app/issues/5968))
- Keycloak canary and hardening, FTANF research, parsing service refactor, and no-caseload design and research continued in progress. ([#5757](https://github.com/raft-tech/TANF-app/issues/5757), [#6089](https://github.com/raft-tech/TANF-app/issues/6089), [#5683](https://github.com/raft-tech/TANF-app/issues/5683), [#5567](https://github.com/raft-tech/TANF-app/issues/5567), [#6020](https://github.com/raft-tech/TANF-app/issues/6020), [#6060](https://github.com/raft-tech/TANF-app/issues/6060))
- Knowledge Center domain migration and help-content naming stayed in flight alongside admin ETL trigger and DataFile lifecycle review work. ([#5916](https://github.com/raft-tech/TANF-app/issues/5916), [#5928](https://github.com/raft-tech/TANF-app/issues/5928), [#6035](https://github.com/raft-tech/TANF-app/issues/6035), [#5971](https://github.com/raft-tech/TANF-app/issues/5971))

---

⚪️ **Total Issues:** 37  
✅ **Closed:** 7  
➡️ **Moved:** 1  
⬛️ **Unchanged:** 27  
🛑 **Blocked:** 2  

---

## [Prioritized User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4624)

- ⬛️ [Design Ideation: Explore Help Content and Naming for Report Pages (#5928)](https://github.com/raft-tech/TANF-app/issues/5928)  
_Remained in **In Progress**_  


## [Operational Backlog](https://github.com/raft-tech/TANF-app/issues/4627)

- ✅ [Ensure proper file closure after parsing to prevent 'too many open files' error (#2850)](https://github.com/raft-tech/TANF-app/issues/2850)  
_**Closed**_ - _Moved from **Closed**_  

- ⬛️ [Add Django Admin Console trigger for ETL pipelines (#6035)](https://github.com/raft-tech/TANF-app/issues/6035)  
_Remained in **In Progress**_  

- ✅ [Add ETL tables to Grafana (#6093)](https://github.com/raft-tech/TANF-app/issues/6093)  
_**Closed**_ - _Moved from **Closed**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  

- ✅ [FTANF Research Handout for AFN Convention (#6145)](https://github.com/raft-tech/TANF-app/issues/6145)  
_**Closed**_ - _Moved from **Closed**_  


## [TDP Knowledge Center](https://github.com/raft-tech/TANF-app/issues/5455)

- ✅ [Update Tribal TANF WPR Feedback Reference Guide in Knowledge Center (#6132)](https://github.com/raft-tech/TANF-app/issues/6132)  
_**Closed**_ - _Moved from **Closed**_  


## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ⬛️ [Route DataFile State Changes Through Lifecycle Controls (#5971)](https://github.com/raft-tech/TANF-app/issues/5971)  
_Remained in **Raft (Dev) Review**_  

- ⬛️ [Make DataFile State Transitions Atomic and Race-Safe (#5972)](https://github.com/raft-tech/TANF-app/issues/5972)  
_Remained in **Current Sprint Backlog**_  


## [(RE)Parsing refactor](https://github.com/raft-tech/TANF-app/issues/5565)

- ⬛️ [Introduce `ParsingService` and refactor Celery task to use it (#5567)](https://github.com/raft-tech/TANF-app/issues/5567)  
_Remained in **In Progress**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ✅ [5. Build Admin Read-Only List and Detail View Pattern (#5844)](https://github.com/raft-tech/TANF-app/issues/5844)  
_**Closed**_ - _Moved from **Closed**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ⬛️ [[Bug] Investigate flaky go-parser tests (#6049)](https://github.com/raft-tech/TANF-app/issues/6049)  
_Remained in **Current Sprint Backlog**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ⬛️ [Configure Grafana SSO via production Keycloak instance (#5754)](https://github.com/raft-tech/TANF-app/issues/5754)  
_Remained in **Backlog**_  

- ⬛️ [Set up Keycloak Prometheus metrics, Grafana dashboards, and alerting (#5755)](https://github.com/raft-tech/TANF-app/issues/5755)  
_Remained in **Backlog**_  

- ⬛️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Remained in **In Progress**_  

- ⬛️ [Create GHCR robot accounts and CI/CD deployments for Keycloak (#5980)](https://github.com/raft-tech/TANF-app/issues/5980)  
_Remained in **Raft (Dev) Review**_  


## [TDP API access](https://github.com/raft-tech/TANF-app/issues/5786)

- ⬛️ [Infer `user` from session in DataFile submissions (#6123)](https://github.com/raft-tech/TANF-app/issues/6123)  
_Remained in **Current Sprint Backlog**_  


## [Design & Implement: Admin Dashboard View](https://github.com/raft-tech/TANF-app/issues/5951)

- ✅ [Design Admin Dashboard (#5966)](https://github.com/raft-tech/TANF-app/issues/5966)  
_**Closed**_ - _Moved from **Closed**_  


## [Design & Implement: Users Pages](https://github.com/raft-tech/TANF-app/issues/5952)

- ✅ [Design: User Feedback Page (#5964)](https://github.com/raft-tech/TANF-app/issues/5964)  
_**Closed**_ - _Moved from **Closed**_  

- ⬛️ [Design: User Requests and Authorization Page and Interaction (#5968)](https://github.com/raft-tech/TANF-app/issues/5968)  
_Remained in **QASP Review**_  


## [Allow admins to toggle Feedback Reports between STT and admin modes](https://github.com/raft-tech/TANF-app/issues/5991)

- ⬛️ [Design: Allow Regional Staff and Admin to view STT Mode for Feedback Reports via Statistics Panel (#6002)](https://github.com/raft-tech/TANF-app/issues/6002)  
_Remained in **QASP Review**_  

- ⬛️ [DEV: Allow admins to toggle Feedback Reports between STT and admin modes (#6003)](https://github.com/raft-tech/TANF-app/issues/6003)  
_Remained in **Raft (Dev) Review**_  


## [Migrate to tanfdata.acf.hhs.gov](https://github.com/raft-tech/TANF-app/issues/5993)

- ⬛️ [Migrate Knowledge Center to `.tanfdata.acf.hhs.gov` domain (#5916)](https://github.com/raft-tech/TANF-app/issues/5916)  
_Remained in **In Progress**_  


## [Support No-Caseload Reporting](https://github.com/raft-tech/TANF-app/issues/6000)

- ⬛️ [Design No-Caseload Reporting Experience (#6020)](https://github.com/raft-tech/TANF-app/issues/6020)  
_Remained in **In Progress**_  

- ⬛️ [Research: Planning & Facilitation for no caseload reporting (#6060)](https://github.com/raft-tech/TANF-app/issues/6060)  
_Remained in **In Progress**_  


## [Feedback Report Download Statistics](https://github.com/raft-tech/TANF-app/issues/6011)

- ⬛️ [Design Feedback Report Download Statistics Panel (#6012)](https://github.com/raft-tech/TANF-app/issues/6012)  
_Remained in **QASP Review**_  


## [Optional Notes field for uploads](https://github.com/raft-tech/TANF-app/issues/6015)

- ⬛️ [Dev - Optional Notes Field for Feedback Report Uploads (#6017)](https://github.com/raft-tech/TANF-app/issues/6017)  
_Remained in **Raft (Dev) Review**_  

- ⬛️ [Design Optional Notes Field for Uploads (#6033)](https://github.com/raft-tech/TANF-app/issues/6033)  
_Remained in **QASP Review**_  


## [ACF-204: UX research for STT form and narrative submission, validation, and admin audit](https://github.com/raft-tech/TANF-app/issues/6059)

- ⬛️ [ACF-204: Create a minimal UX research plan (feasibility, preliminary research, approaches) (#6056)](https://github.com/raft-tech/TANF-app/issues/6056)  
_Remained in **In Progress**_  


## [Decouple SSP and program participation from the STT model](https://github.com/raft-tech/TANF-app/issues/6062)

- 🛑 [Front end changes to decouple SSP data from the STT model. (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Remained in **Blocked**_  

- ➡️ [Disable FRA submissions for FY25 (#6096)](https://github.com/raft-tech/TANF-app/issues/6096)  
_Moved from **Current Sprint Backlog** to **Raft (Dev) Review**_  


## [Developer Experience and Tooling](https://github.com/raft-tech/TANF-app/issues/6064)

- ⬛️ [[SPIKE] Consolidate overlapping tests and establish test-writing rules for contributors and agents (#6102)](https://github.com/raft-tech/TANF-app/issues/6102)  
_Remained in **Current Sprint Backlog**_  


## [Security Improvements](https://github.com/raft-tech/TANF-app/issues/6065)

- 🛑 [Request Param Mismatch (#6051)](https://github.com/raft-tech/TANF-app/issues/6051)  
_Remained in **Blocked**_  

- ⬛️ [Use `fullmatch` for DataFile extension check (#6131)](https://github.com/raft-tech/TANF-app/issues/6131)  
_Remained in **Current Sprint Backlog**_  


## [Complete canonical Program and Section on DataFile](https://github.com/raft-tech/TANF-app/issues/6066)

- ⬛️ [Remove legacy DataFile program and section enum fields. (#5984)](https://github.com/raft-tech/TANF-app/issues/5984)  
_Remained in **Raft (Dev) Review**_  


## [Convert Buildpacks to Docker](https://github.com/raft-tech/TANF-app/issues/6074)

- ⬛️ [Migrate Keycloak to Docker Hardened Images (#6089)](https://github.com/raft-tech/TANF-app/issues/6089)  
_Remained in **In Progress**_  


## [Design & Implement: Data Table](https://github.com/raft-tech/TANF-app/issues/6136)

- ⬛️ [Design: Data Table (#6137)](https://github.com/raft-tech/TANF-app/issues/6137)  
_Remained in **In Progress**_