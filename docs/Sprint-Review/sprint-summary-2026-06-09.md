# Sprint Summary: May 27, 2026 - Jun 09, 2026

## Overview

- Completed recruitment and finalized participant list for FTANF replacement research. ([#5609](https://github.com/raft-tech/TANF-app/issues/5609))

- Finished key Go parser improvements, including in-memory duplicate detection parity, enqueuing post-parse tasks to Python workers, and implementing shadow table write mode. ([#5724](https://github.com/raft-tech/TANF-app/issues/5724), [#5731](https://github.com/raft-tech/TANF-app/issues/5731), [#5735](https://github.com/raft-tech/TANF-app/issues/5735))

- Fixed a bug where the Go parser could overwrite Python reports, even with shadow mode on. ([#5880](https://github.com/raft-tech/TANF-app/issues/5880))

- Added bearer token authentication for external API clients to improve security and reliability. ([#5756](https://github.com/raft-tech/TANF-app/issues/5756))

- Completed design work to separate the Readme tab in error reports, making reports clearer. ([#5795](https://github.com/raft-tech/TANF-app/issues/5795))

---

⚪️ **Total Issues:** 34  
✅ **Closed:** 7  
➡️ **Moved:** 0  
⬛️ **Unchanged:** 27  
🛑 **Blocked:** 0  

---

## Issues without Parent

- ⬛️ [Design ideation for post-MVP centralized feedback reports: Plain Language and Interpretability (#5223)](https://github.com/raft-tech/TANF-app/issues/5223)  
_Remained in **GraphQL Error**_  

- ⬛️ [Wire AV scan completion to transition DataFile.state → validated / scan_failed (#5547)](https://github.com/raft-tech/TANF-app/issues/5547)  
_Remained in **GraphQL Error**_  

- ⬛️ [Wire parser task to transition DataFile.state → parsing / parsed_clean / parsed_with_errors (#5548)](https://github.com/raft-tech/TANF-app/issues/5548)  
_Remained in **GraphQL Error**_  

- ⬛️ [Add `ReparseService` and refactor orchestration to use it (#5568)](https://github.com/raft-tech/TANF-app/issues/5568)  
_Remained in **GraphQL Error**_  

- ⬛️ [Document current parsing & reparsing flows (#5566)](https://github.com/raft-tech/TANF-app/issues/5566)  
_Remained in **GraphQL Error**_  

- ⬛️ [Planning & Facilitation: How We Work Workshop (#5593)](https://github.com/raft-tech/TANF-app/issues/5593)  
_Remained in **GraphQL Error**_  

- ✅ [Initiate Recruitment and Finalize Participant List for FTANF Replacement Research (#5609)](https://github.com/raft-tech/TANF-app/issues/5609)  
_**Closed**_ - _Moved from **GraphQL Error**_  

- ⬛️ [React Admin: UX Design Exploration & IA Improvements (#5651)](https://github.com/raft-tech/TANF-app/issues/5651)  
_Remained in **GraphQL Error**_  

- ⬛️ [Create or modify maintenance page / error page (#5660)](https://github.com/raft-tech/TANF-app/issues/5660)  
_Remained in **GraphQL Error**_  

- ⬛️ [Conduct FTANF Replacement Research (#5683)](https://github.com/raft-tech/TANF-app/issues/5683)  
_Remained in **GraphQL Error**_  

- ✅ [Go Parser: Verify in-memory duplicate detection parity (#5724)](https://github.com/raft-tech/TANF-app/issues/5724)  
_**Closed**_ - _Moved from **GraphQL Error**_  

- ✅ [Go Parser: Enqueue post-parse tasks to Python Celery worker (#5731)](https://github.com/raft-tech/TANF-app/issues/5731)  
_**Closed**_ - _Moved from **GraphQL Error**_  

- ✅ [Go Parser: Implement shadow table write mode (#5735)](https://github.com/raft-tech/TANF-app/issues/5735)  
_**Closed**_ - _Moved from **GraphQL Error**_  

- ⬛️ [Go Parser: Add structured JSON logging via log/slog (#5738)](https://github.com/raft-tech/TANF-app/issues/5738)  
_Remained in **GraphQL Error**_  

- ⬛️ [Keycloak: Promote Keycloak to Cloud.gov staging space (#5751)](https://github.com/raft-tech/TANF-app/issues/5751)  
_Remained in **GraphQL Error**_  

- ✅ [Implement bearer token authentication for external API clients (#5756)](https://github.com/raft-tech/TANF-app/issues/5756)  
_**Closed**_ - _Moved from **GraphQL Error**_  

- ⬛️ [Error Reporting Research Synthesis (#5763)](https://github.com/raft-tech/TANF-app/issues/5763)  
_Remained in **GraphQL Error**_  

- ✅ [Design for separating "Readme" tab in error reports (#5795)](https://github.com/raft-tech/TANF-app/issues/5795)  
_**Closed**_ - _Moved from **GraphQL Error**_  

- ⬛️ [Update ZAP (#5798)](https://github.com/raft-tech/TANF-app/issues/5798)  
_Remained in **GraphQL Error**_  

- ⬛️ [Release Tracker v4.18.0 (#5811)](https://github.com/raft-tech/TANF-app/issues/5811)  
_Remained in **GraphQL Error**_  

- ⬛️ [Accept header/trailer-only active, aggregate, and stratum files (#5819)](https://github.com/raft-tech/TANF-app/issues/5819)  
_Remained in **GraphQL Error**_  

- ⬛️ [[Tech Memo] Generic DataFile Orchestrator (Submission, Parse, Reparse, Tasks) (#5825)](https://github.com/raft-tech/TANF-app/issues/5825)  
_Remained in **GraphQL Error**_  

- ⬛️ [Add parser-side validation for datafile program type mismatches (#5833)](https://github.com/raft-tech/TANF-app/issues/5833)  
_Remained in **GraphQL Error**_  

- ⬛️ [Update Python and Go T5/M5 OASDI age validators to use AGE_FIRST DOB calculation (#5848)](https://github.com/raft-tech/TANF-app/issues/5848)  
_Remained in **GraphQL Error**_  

- ⬛️ [Update Vendor Product Manager contact on README (#5849)](https://github.com/raft-tech/TANF-app/issues/5849)  
_Remained in **GraphQL Error**_  

- ⬛️ [Release Tracker v4.19.0 (#5854)](https://github.com/raft-tech/TANF-app/issues/5854)  
_Remained in **GraphQL Error**_  

- ⬛️ [Transition TDP applications from app.cloud.gov to tanfdata.acf.hhs.gov domains (#5855)](https://github.com/raft-tech/TANF-app/issues/5855)  
_Remained in **GraphQL Error**_  

- ⬛️ [BUG KeyError Events: Error 'state_nonce_tracker' in Sentry (#5859)](https://github.com/raft-tech/TANF-app/issues/5859)  
_Remained in **GraphQL Error**_  

- ⬛️ [CRM for STT info and behavior (#25)]()  
_Remained in **No Pipeline Info**_  

- ⬛️ [Plan & Prepare Summer 2026 STT Office Hours Webinar (#26)]()  
_Remained in **No Pipeline Info**_  

- ⬛️ [Feedback report upload support for subfolders (#5870)](https://github.com/raft-tech/TANF-app/issues/5870)  
_Remained in **GraphQL Error**_  

- ⬛️ [Feedback Reports tribal TANF selector support (#5873)](https://github.com/raft-tech/TANF-app/issues/5873)  
_Remained in **GraphQL Error**_  

- ⬛️ [[BUG] Support admin reparse for legacy submitted DataFiles stuck in uploaded state (#5875)](https://github.com/raft-tech/TANF-app/issues/5875)  
_Remained in **GraphQL Error**_  

- ✅ [[Bug] Go parser error report overwrites python report despite `GO_PARSER_SHADOW_MODE` (#5880)](https://github.com/raft-tech/TANF-app/issues/5880)  
_**Closed**_ - _Moved from **GraphQL Error**_  


