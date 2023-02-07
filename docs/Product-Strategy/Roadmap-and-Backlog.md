_updated July 2022_
# Product Roadmap
Our [roadmap](https://app.mural.co/t/raft2792/m/raft2792/1649193957647/f8656ffaae4f5dfd47017eb981b04ff2ab7e792d?fromVisitorModal=true&sender=uc514273731b3f70763f30539) : represents our latest thinking about the order in which we’ll tackle the various pieces of the overarching problem.

This roadmap provides a high level plan through Release 4. There might be a few shifts in approach, timing or scope, but in general, these outcomes will be worked on by the team. Metrics for success will be added as they are defined for releases.

Beyond that, our iterative agile framework will lend itself to feature sets that best serve our users. This doc will continue to be updated as we make decisions and scope releases. 

## ATO  
Approval for the authority to operate. 

| Outcome | 
| -------- |
| User can log in using login.gov |
| Users with appropriate privileges can manage users | 
| Users can upload data files by section and quarter | 
| Users with appropriate privileges can download files that were previously uploaded     | 
| Approval to create a production environment |

## Release 1  
This is the first release to the production environment including the ATO and reliable application access to internal and external users in a secure production environment. Additionally it includes user management interface for OFA and System Admin. It is important that these measures are put into place before sensitive production data is uploaded to the system.

| Outcome | 
| -------- | 
| TDP is secure and compliant as a system and for all users. |
| TDP platform is hardened and stable and robust for deployment and live in a production environment. |
| TDP Users have a secure login experience. |
| Users with appropriate privileges can download files that were previously uploaded     |


## Release 2: Pilot Release
This release will allow users to securely upload data into our system in production, replacing a less secure way of doing so, while increasing communication with the users and not increasing burden for OFA Admin staff. This release will allow approximately 20 STTs to pilot the use of login, upload, and download of files, while maintaining TDRS on the backend. While this type of workflow isn't our long term workflow, including it at this point delivers value to the users more quickly and provides the team valuable user feedback to validate and improve the application features. 


| Outcome |
| -------- | 
| Tribal users are engaged with OFA and communication channels are clear. |
| Users know how to access and onboard TDP easily. |
| Users can upload and transmit files securely to TDRS database. |
| Users can resubmit files with error fixes. |
| Users will receive email notifications on the status of their account and data. |
| Users can differentiate TANF and SSP files upon submission. |



## Release 3: Parity, Data Parsing, Automated Status, Notifications
This major release will parse and validate submitted data and store accepted data in a database. This workflow will include additional automated email notifications and user-friendly in-app error messages to help users better understand their data errors and submission history. This release will also include Django admin enhancements and onboard all users as it will meet parity with the legacy TANF Data Reporting System.

| Outcome |
| -------- | 
| TDP can parse all data sections and types through to the Elasticsearch database. |
| TDP runs validation checks on all submitted files. |
| Users receive easy to understand error messages. |
| Users can view their submission history. |
| All users will submit all of their data through TDP . |
| Users will receive email notifications on the state of their submitted data. |
| TDP enhancements for System administrator users. |
| A research oriented TDP environment is created. |


## Release 4 and Beyond
In Release 4, we will begin to deliver features beyond parity with TDRS to address user needs, including (but not limited to) additional user access management tools, user interface enhancements based on usability testing, and reports and analytics. 

## Backlog
For the most up-to-date status please see the roadmap or backlog at [raft-tech fork of the TANF-app GitHub public repository](https://github.com/raft-tech/TANF-app/issues).
