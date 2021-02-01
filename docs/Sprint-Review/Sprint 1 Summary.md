# Sprint 1 Summary
The sprint 1 summary was delivered as a [pull request note.](https://github.com/HHS/TANF-app/pull/48)  

--- 
## Overview
PR to merge the user stories that were completed in Sprint 1. 

### Deliverable 1: Accepted Features
Outside of the scope of this review for Sprint 1 since this sprint focussed on Backend Scaffolding, CircleCI/CD Pipeline, addressing the comments provided in Sprint 0.
### Deliverable 2: Tested Code
Test coverage is 58%. However, a new [user story](https://github.com/raft-tech/TANF-app/issues/179) has been created to bring the test coverage up to 90% in Sprint 2. 

### Deliverable 3: Properly Styled code
Frontend ESLint is passing.

Our original settings were derived from  cookie-cutter flake8 implementations. Our `setup.cfg` file is now documented with an explanation of each setting and we've included the default settings as recommended. 

### Deliverable 4: Accessible
Pa11y is passing.

### Deliverable 5: Deployed

- The backend is currently deployed to :
https://tdp-backend.app.cloud.gov/v1/login/oidc

- The frontend is currently deployed to :
https://tdp-frontend.app.cloud.gov

- Notes on the deployment instructions : 

  - TANF/tdrs-backend/README.md#cloudgov-deployments
  - TANF/tdrs-frontend/README.md#cloudgov-deployments 


### Deliverable 6: Documentation
List of user stories completed in Sprint 1:
* [As a developer I need scaffolding for the UI so I can contribute to the project](https://github.com/raft-tech/TANF-app/issues/1)
* [As a user I need to log in (backend)](https://github.com/raft-tech/TANF-app/issues/57)
* [As a user I can log out (backend)](https://github.com/raft-tech/TANF-app/issues/65)
* [Create user research plan for OFA](https://github.com/raft-tech/TANF-app/issues/62)
   - * [User research plan for Round 1 (August 2020)](https://teams.microsoft.com/l/file/a3cf3f64-692f-4895-9bee-530f22cfc212?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared%2520Documents%2FDesign%2FUser%2520Research%2520Plan%2520-%2520OFA_08112020.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=aggregatefiles)🔒
   - * [Conversation guide for Round 1 (August 2020)](https://teams.microsoft.com/l/file/c47b0589-5438-497d-94bc-7478080c25f7?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared%2520Documents%2FDesign%2FConveration%2520Guide%2520-%2520OFA%2520Research%2520-%2520August%25202020_08112020.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=aggregatefiles)🔒
* [Plan and schedule OFA interviews](https://github.com/raft-tech/TANF-app/issues/50)
* [Create design components for login screen](https://github.com/raft-tech/TANF-app/issues/7)
   - * [Mockups](https://teams.microsoft.com/_#/files/Design?threadId=19%3Ae92913e3e7d443adb823e6497dff1fb3%40thread.skype&ctx=channel&context=Sprint%25201%2520UI%2520Deliverables&rootfolder=%252Fsites%252FTANFDataPortalOFA%252FShared%2520Documents%252FDesign%252FSprint%25201%2520UI%2520Deliverables)🔒
* [Create Admin Settings UI](https://github.com/raft-tech/TANF-app/issues/8)
*    - * [Mockups](https://teams.microsoft.com/_#/files/Design?threadId=19%3Ae92913e3e7d443adb823e6497dff1fb3%40thread.skype&ctx=channel&context=Sprint%25201%2520UI%2520Deliverables&rootfolder=%252Fsites%252FTANFDataPortalOFA%252FShared%2520Documents%252FDesign%252FSprint%25201%2520UI%2520Deliverables)🔒
* [Set up CI/CD pipeline for OWASP Zap, Pa11y, and Code Coverage Reporting](https://github.com/raft-tech/TANF-app/issues/18)
* [Migrate product roadmap from Mural](https://github.com/raft-tech/TANF-app/issues/42)
* [Reorganize workspaces](https://github.com/raft-tech/TANF-app/issues/44)
* [Update Wiki](https://github.com/raft-tech/TANF-app/issues/19)

### Deliverable 7: Security
 - Zap running against the Backend API  produces the following: 
   - FAIL-NEW: 0	
   - FAIL-INPROG: 0	
   - WARN-NEW: 3	
   - WARN-INPROG: 0	
   - INFO: 0	
   - IGNORE: 0	
   - PASS: 104  

 - Zap running against the Frontend  produces the following: 
    - FAIL-NEW: 0	
    - FAIL-INPROG: 0	
    - WARN-NEW: 7	
    - WARN-INPROG: 0
    - INFO: 0	
    - IGNORE: 0	
    - PASS: 99

* There appears to be a benign error when executing the frontend zap scan: 
`_XSERVTransmkdir: ERROR: euid != 0,directory /tmp/.X11-unix will not be created.` This error does not interfere with any of the tests. For reference, Zap contributors discuss it [here](https://github.com/zaproxy/zaproxy/issues/5230). 



### Deliverable 8
User research artifacts delivered:
* [User research plan for Round 1 (August 2020)](https://teams.microsoft.com/l/file/a3cf3f64-692f-4895-9bee-530f22cfc212?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared%2520Documents%2FDesign%2FUser%2520Research%2520Plan%2520-%2520OFA_08112020.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=aggregatefiles)🔒
* [Conversation guide for Round 1 (August 2020)](https://teams.microsoft.com/l/file/c47b0589-5438-497d-94bc-7478080c25f7?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared%2520Documents%2FDesign%2FConveration%2520Guide%2520-%2520OFA%2520Research%2520-%2520August%25202020_08112020.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=aggregatefiles)🔒
* [Mockups for login and admin user interfaces](https://teams.microsoft.com/_#/files/Design?threadId=19%3Ae92913e3e7d443adb823e6497dff1fb3%40thread.skype&ctx=channel&context=Sprint%25201%2520UI%2520Deliverables&rootfolder=%252Fsites%252FTANFDataPortalOFA%252FShared%2520Documents%252FDesign%252FSprint%25201%2520UI%2520Deliverables)🔒

