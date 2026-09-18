# Sprint Summary: Jul 22, 2026 - Aug 04, 2026

## Overview

- Tightened admin access by finalizing authentication, session handling, and CSRF boundaries to boost security and reduce risk. ([#5836](https://github.com/raft-tech/TANF-app/issues/5836), [#5837](https://github.com/raft-tech/TANF-app/issues/5837))

- Enabled parallel deployments and formalized releases by automating Celery, backend, and Go parser deployments, plus publishing release notes. ([#5910](https://github.com/raft-tech/TANF-app/issues/5910), [#5969](https://github.com/raft-tech/TANF-app/issues/5969))

- Simplified the data file submission experience by merging the submission history with the file upload tabs. ([#5885](https://github.com/raft-tech/TANF-app/issues/5885))

- Fixed a session-related error and added friendlier messaging when a session expires to improve user experience. ([#5574](https://github.com/raft-tech/TANF-app/issues/5574))

- Gained momentum on the Go parser effort by adding metrics and advancing deployment tasks toward review and readiness. ([#5739](https://github.com/raft-tech/TANF-app/issues/5739), [#5909](https://github.com/raft-tech/TANF-app/issues/5909))

---

⚪️ **Total Issues:** 38  
✅ **Closed:** 9  
➡️ **Moved:** 17  
⬛️ **Unchanged:** 12  
🛑 **Blocked:** 0  

---

## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ➡️ [BUG KeyError Events: Error 'state_nonce_tracker' in Sentry (#5859)](https://github.com/raft-tech/TANF-app/issues/5859)  
_Moved from **In Progress** to **Raft (Dev) Review**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ➡️ [Go Parser: Add Prometheus metrics (#5739)](https://github.com/raft-tech/TANF-app/issues/5739)  
_Moved from **Current Sprint Backlog** to **Raft (Dev) Review**_  

- ⬛️ [Deploy the Go parser through the standard CI/CD process (#5909)](https://github.com/raft-tech/TANF-app/issues/5909)  
_Remained in **Raft (Dev) Review**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ⬛️ [Execute canary rollout of Keycloak auth (0% to 100%) per environment (#5757)](https://github.com/raft-tech/TANF-app/issues/5757)  
_Remained in **In Progress**_  

- ⬛️ [Keycloak: Promote Keycloak into the Production Space (#5761)](https://github.com/raft-tech/TANF-app/issues/5761)  
_Remained in **In Progress**_  

- ➡️ [Track direct API client request metrics in Grafana (#5900)](https://github.com/raft-tech/TANF-app/issues/5900)  
_Moved from **Current Sprint Backlog** to **Raft (Dev) Review**_  


## [Migrate to tanfdata.acf.hhs.gov](https://github.com/raft-tech/TANF-app/issues/5993)

- ✅ [Knowledge Center Audit/Remove absolute links (#5929)](https://github.com/raft-tech/TANF-app/issues/5929)  
_**Closed**_ - _Moved from **In Progress**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Remained in **In Progress**_  

- ✅ [2. Configure Admin Authentication, Session, and CSRF Boundaries (#5836)](https://github.com/raft-tech/TANF-app/issues/5836)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [3. Establish Admin API Boundary (#5837)](https://github.com/raft-tech/TANF-app/issues/5837)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [4. Implement Metadata-Driven Admin Form Contract (#5842)](https://github.com/raft-tech/TANF-app/issues/5842)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Design Admin Dashboard (#5966)](https://github.com/raft-tech/TANF-app/issues/5966)  
_Moved from **Product Backlog** to **In Progress**_  

- ✅ [Create Admin Navigation and Interactivity (#5970)](https://github.com/raft-tech/TANF-app/issues/5970)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Implement Admin Navigation and Interactivity (#5983)](https://github.com/raft-tech/TANF-app/issues/5983)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  

- ⬛️ [Update ZAP (#5798)](https://github.com/raft-tech/TANF-app/issues/5798)  
_Remained in **Raft (Dev) Review**_  


## [Release Tracking](https://github.com/raft-tech/TANF-app/issues/5789)

- ✅ [4.21.0 Release Notes (#5969)](https://github.com/raft-tech/TANF-app/issues/5969)  
_**Closed**_ - _Moved from **Product Backlog**_  

- ➡️ [Release Tracker v4.23.0 (#5988)](https://github.com/raft-tech/TANF-app/issues/5988)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [v4.23.0 Release Notes and Knowledge Center updates (#5989)](https://github.com/raft-tech/TANF-app/issues/5989)  
_Moved from **Product Backlog** to **In Progress**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ➡️ [[Spike]: Design proper pagination for History tables (#5538)](https://github.com/raft-tech/TANF-app/issues/5538)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ➡️ [Validate Feedback Reports source uploads match selected program type (#5992)](https://github.com/raft-tech/TANF-app/issues/5992)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


## Issues without Parent

- ⬛️ [Create new models to define an STTs participation in a particular Program (#5370)](https://github.com/raft-tech/TANF-app/issues/5370)  
_Remained in **Raft (Dev) Review**_  

- ⬛️ [Front end changes to decouple SSP data from the STT model. (#5376)](https://github.com/raft-tech/TANF-app/issues/5376)  
_Remained in **Raft (Dev) Review**_  

- ➡️ [Django query optimization (#5383)](https://github.com/raft-tech/TANF-app/issues/5383)  
_Moved from **Current Sprint Backlog** to **In Progress**_  

- ✅ [Fix Callback state_nonce_tracker KeyError and Return Friendly “Session Expired” Message (#5574)](https://github.com/raft-tech/TANF-app/issues/5574)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ➡️ [File submission error message and form reset (#5603)](https://github.com/raft-tech/TANF-app/issues/5603)  
_Moved from **In Progress** to **Raft (Dev) Review**_  

- ✅ [Parser task cleanup can mask root failures when dfs is not created (#5806)](https://github.com/raft-tech/TANF-app/issues/5806)  
_**Closed**_ - _Moved from **In Progress**_  

- ⬛️ [CRM for STT info and behavior (#25)]()  
_Remained in **No Pipeline Info**_  

- ✅ [Combine Submission History and File Upload tabs for Data File Submissions (#5885)](https://github.com/raft-tech/TANF-app/issues/5885)  
_**Closed**_ - _Moved from **UX Review**_  

- ✅ [Deploy Celery, backend, and Go parser apps in parallel via CI/CD (#5910)](https://github.com/raft-tech/TANF-app/issues/5910)  
_**Closed**_ - _Moved from **QASP Review**_  

- ⬛️ [[BUG] Keycloak configure script fails when tdp-api-audience client scope already exists (#5911)](https://github.com/raft-tech/TANF-app/issues/5911)  
_Remained in **Current Sprint Backlog**_  

- ➡️ [Remove Internal Variable Name Column and Adjust Widths in Generated Error Reports (#5927)](https://github.com/raft-tech/TANF-app/issues/5927)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [Knowledge Center Update: Add Guidance on Timely Data Submission Expectations (#5940)](https://github.com/raft-tech/TANF-app/issues/5940)  
_Moved from **Product Backlog** to **In Progress**_  

- ⬛️ [Replace configure-idps.sh with declarative Keycloak configuration management (#5958)](https://github.com/raft-tech/TANF-app/issues/5958)  
_Remained in **Current Sprint Backlog**_  

- ➡️ [[BUG] Duplicated counts in the reparse model (#5985)](https://github.com/raft-tech/TANF-app/issues/5985)  
_Moved from **Product Backlog** to **In Progress**_  

- ➡️ [Isolate TDP Admin Authentication in a Separate Keycloak Realm (#5986)](https://github.com/raft-tech/TANF-app/issues/5986)  
_Moved from **Product Backlog** to **Next Up: DEV**_  

- ➡️ [Remediate parent-domain scope on sessionid cookie (#5999)](https://github.com/raft-tech/TANF-app/issues/5999)  
_Moved from **Product Backlog** to **Next Up: DEV**_  


