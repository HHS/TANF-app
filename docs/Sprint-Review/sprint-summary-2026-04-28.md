# Sprint Summary: Apr 15, 2026 - Apr 28, 2026

## Overview

- Completed a batch of fixes and spikes, removing bottlenecks and improving data reliability. ([#5484](https://github.com/raft-tech/TANF-app/issues/5484), [#5485](https://github.com/raft-tech/TANF-app/issues/5485), [#5542](https://github.com/raft-tech/TANF-app/issues/5542), [#5665](https://github.com/raft-tech/TANF-app/issues/5665), [#5689](https://github.com/raft-tech/TANF-app/issues/5689), [#5770](https://github.com/raft-tech/TANF-app/issues/5770))

- Advancements in Go Parser tooling and infrastructure, with CI/CD, local Docker integration, and test parity work progressing toward stabilization. ([#5726](https://github.com/raft-tech/TANF-app/issues/5726), [#5734](https://github.com/raft-tech/TANF-app/issues/5734), [#5732](https://github.com/raft-tech/TANF-app/issues/5732), [#5741](https://github.com/raft-tech/TANF-app/issues/5741))

- FTANF replacement research and planning activities progressed, including recruitment initiation and planning workshops. ([#5609](https://github.com/raft-tech/TANF-app/issues/5609), [#5593](https://github.com/raft-tech/TANF-app/issues/5593), [#5683](https://github.com/raft-tech/TANF-app/issues/5683))

- Backlog-to-In-Progress movements and blockers identified, including refactor/upload flow work entering active sprint and a key blocker on TDP Data Retention. ([#5769](https://github.com/raft-tech/TANF-app/issues/5769), [#5649](https://github.com/raft-tech/TANF-app/issues/5649))

---

⚪️ **Total Issues:** 22  
✅ **Closed:** 8  
➡️ **Moved:** 4  
⬛️ **Unchanged:** 9  
🛑 **Blocked:** 1  

---

## [(Re)Parse refactor - State machine](https://github.com/raft-tech/TANF-app/issues/5543)

- ⬛️ [Wire AV scan completion to transition DataFile.state → validated / scan_failed (#5547)](https://github.com/raft-tech/TANF-app/issues/5547)  
_Remained in **Raft (Dev) Review**_  


## [Bug Reports](https://github.com/raft-tech/TANF-app/issues/4441)

- ✅ [[Bug] LogEntry admin is causing N+1 query of admin model (#5484)](https://github.com/raft-tech/TANF-app/issues/5484)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ✅ [Optimize DataFile & Report APIs to avoid N+1 queries using select_related (#5485)](https://github.com/raft-tech/TANF-app/issues/5485)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## [FRA Post-MVP Enhancements](https://github.com/raft-tech/TANF-app/issues/4443)

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **Current Sprint Backlog**_  

- ✅ [Frontend FRA Feedback Reports Implementation (#5665)](https://github.com/raft-tech/TANF-app/issues/5665)  
_**Closed**_ - _Moved from **In Progress**_  


## [fTANF Replacement - Foundational Research & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4628)

- ⬛️ [Initiate Recruitment and Finalize Participant List for FTANF Replacement Research (#5609)](https://github.com/raft-tech/TANF-app/issues/5609)  
_Remained in **In Progress**_  

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **In Progress**_  


## [Go Parser](https://github.com/raft-tech/TANF-app/issues/5702)

- ✅ [Go Parser: Add max records per case validation (#5726)](https://github.com/raft-tech/TANF-app/issues/5726)  
_**Closed**_ - _Moved from **Next Up: DEV**_  

- ⬛️ [Go Parser: Complete Celery/Redis task consumption (#5730)](https://github.com/raft-tech/TANF-app/issues/5730)  
_Remained in **Raft (Dev) Review**_  

- ⬛️ [Go Parser: Local Docker Integration (#5732)](https://github.com/raft-tech/TANF-app/issues/5732)  
_Remained in **Raft (Dev) Review**_  

- ✅ [Go Parser: Add CI/CD pipeline (#5734)](https://github.com/raft-tech/TANF-app/issues/5734)  
_**Closed**_ - _Moved from **Next Up: DEV**_  

- ➡️ [Go Parser: Integration test parity with Python parser tests (#5741)](https://github.com/raft-tech/TANF-app/issues/5741)  
_Moved from **Next Up: DEV** to **In Progress**_  


## [In-App Error Reporting - Foundational Design & Concept Validation](https://github.com/raft-tech/TANF-app/issues/4629)

- ⬛️ [Error Reporting Research Synthesis (#5763)](https://github.com/raft-tech/TANF-app/issues/5763)  
_Remained in **In Progress**_  


## [Keycloak](https://github.com/raft-tech/TANF-app/issues/5703)

- ➡️ [Keycloak: Enable Keycloak in the Cloud.gov dev space (#5750)](https://github.com/raft-tech/TANF-app/issues/5750)  
_Moved from **Next Up: DEV** to **In Progress**_  

- ➡️ [Implement bearer token authentication for external API clients (#5756)](https://github.com/raft-tech/TANF-app/issues/5756)  
_Moved from **Next Up: DEV** to **In Progress**_  


## [New React Admin](https://github.com/raft-tech/TANF-app/issues/5700)

- ⬛️ [React Admin High Level Architecture Document (#5746)](https://github.com/raft-tech/TANF-app/issues/5746)  
_Remained in **Raft (Dev) Review**_  


## [Operations & Maintenance](https://github.com/raft-tech/TANF-app/issues/4445)

- ✅ [[Spike] Explore Transitioning TDP Deployments from Cloud.gov Buildpacks to Docker Containers (#5542)](https://github.com/raft-tech/TANF-app/issues/5542)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **In Progress**_  


## [Release Tracking](https://github.com/raft-tech/TANF-app/issues/5789)

- ✅ [Release Tracker v4.16.0 (#5770)](https://github.com/raft-tech/TANF-app/issues/5770)  
_**Closed**_ - _Moved from **QASP Review**_  


## [TDP Data Retention](https://github.com/raft-tech/TANF-app/issues/5790)

- 🛑 [[Spike] TDP Data Retention (#5649)](https://github.com/raft-tech/TANF-app/issues/5649)  
_Remained in **Blocked**_  


## [User Experience Enhancements](https://github.com/raft-tech/TANF-app/issues/4444)

- ✅ [Implement email templates for reparsing (new error report & error resolution) (#5689)](https://github.com/raft-tech/TANF-app/issues/5689)  
_**Closed**_ - _Moved from **Raft (Dev) Review**_  


## Issues without Parent

- ➡️ [Refactor upload flow to move AV scanning out of serializer validation and align submission-state transitions with runtime events (#5769)](https://github.com/raft-tech/TANF-app/issues/5769)  
_Moved from **Product Backlog** to **In Progress**_  


