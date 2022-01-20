_updated January 2022_
# Product Roadmap
Our [roadmap](https://app.mural.co/invitation/mural/raft2792/1629476801275?sender=laurenfrohlich3146&key=5328c2c6-a097-4b3d-bcf7-f2e551a01a72) :lock: represents our latest thinking about the order in which we’ll tackle the various pieces of the overarching problem.

This roadmap provides a high level plan through Release 4. There might be a few shifts in approach, timing or scope, but in general, these outcomes will be worked on by the team. Metrics for success will be added as they are defined for releases.

Beyond that, we're still discovering and planning on what best serves our users. This doc will continue to be updated as we make decisions and scope releases. 

## ATO  
Value Delivered: Get approval for the authority to operate and create a production environment. 

| Outcome | Status | 
| -------- | ------- | 
| User can log in using login.gov | Complete
| Users with appropriate privileges can manage users | Complete
| Users can upload data files by section and quarter | Complete
| Users with appropriate privileges can download files that were previously uploaded     | Complete
|Create production environment | In Progress

## Release 1: Secure access and upload to TDP
Our first release to production will include the functionality built for ATO (above) and also include secure ways for users to access the system via ACF AMS for ACF users and NextGen XMS/Login.gov for non-ACF users. It is important that these measures are put into place before sensitive production data is uploaded to the system.
 
| Outcome | Status | 
| -------- | ------- | 
| TDP is secure and compliant as a system and for all users. | Nearly Complete
| TDP Users have a smooth onboarding and login experience that is secure. | Nearly Complete
| TDP platform is hardened and stable and robust for deployment and live in a production environment. | In Progress


## Release 2: Early Secure Release
This release will allow users to securely upload data into our system in production, replacing a less secure way of doing so, while increasing communication with the users and not increasing burden for OFA Admin staff. This release will allow approximately 8 tribes to pilot the use of login, upload, and download of files, while maintaining TDRS on the backend. While this type of workflow isn't our long term workflow, including it at this point delivers value to the users more quickly. 

_Risks:_ The users who would be onboarded to this process would potentially have to learn and adjust with future releases and changes in functionality and workflow. Increased communication with them should help here.
| Outcome | Status | 
| -------- | ------- | 
| Tribal users are engaged with OFA and communication channels are clear. | In Progress| 
| Users know how to access and onboard TDP easily. | In Progress| 
| Users can upload and transmit files securely to TDRS database. |Not Started|
| Early Tribe and State users can securely upload reports with TDP instead of using unsecured email. |Not Started|
| Users can resubmit files with error fixes |Not Started|


## Release 3: Parity, Data Parsing, Automated Status, Notifications
This release will parse and validate submitted data and store accepted data in a database. This workflow will include automated email notifications and user-friendly in-app error messages to help users better understand their data errors and submission history. This release will also include onboarding more users and will eventually deprecate the legacy TANF Data Reporting System.

## Release 4 and Beyond
In Release 4, we will begin to deliver features beyond parity with TDRS to address user needs, including (but not limited to) pre-submission data cleansing and validation, additional user access management tools, user interface enhancements based on usability testing, and reports and analytics. 

## Backlog
The backlog can be found in the [raft-tech fork of the TANF-app GitHub public repository](https://github.com/raft-tech/TANF-app/issues).