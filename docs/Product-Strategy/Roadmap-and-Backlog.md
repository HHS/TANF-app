_updated June 2021_
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
Value Delivered: ACF employees can use a secure method to log into the system; this would require a PIV/CAC card.

Our first release to production will include the functionality built for ATO (above) and also include secure ways for users to access the system via ACF AMS for ACF users and NextGen XMS/Login.gov for non-ACF users. It is important these measures are put into place before sensitive production data is uploaded to the system.

The team is also investigating options for optimizing permission management and strategy as a part of this release. 
| Outcome | Status | 
| -------- | ------- | 
| Privileged ACF users are required to login with PIV/CAC credentials | In Progress
| Permissions Configuration | Complete
| Secret key leakage prevention | Nearly Complete
| Production Deployment | In Progress


## Release 2: Early Secure Release

Value Delivered: Allow users to securely upload data into our system, replacing a less secure way of doing so while increasing communication with the users and not increasing burden for OFA Admin staff. This replease will include a workflow that 8 Tribes can pilot the use of login, upload and download of files. While this type of workflow isn't our long term workflow, including it at this point delivers value to the users quicker. 

_Risks:_ The users that would be on-boarded to this process, would potentially have to learn and adjust with future releases and changes in functionality and workflow. Increased communication with them should help here.
| Outcome | Status | 
| -------- | ------- | 
| STT user of the system knows their file(s) were successfully uploaded | In progress
| Files successfully transferred to ACF server | Not Started
| Files uploaded by STT user(s) are successfully entered into the existing TDRS system | Not Started

## Release 3 (fka STT MVP)
Value Delivered: Create a database that will parse data, communicate error messages to the user that are easier to read and act upon. The scope of this release is still being defined, but the team agrees that the priority for focusing on processing data is the next right step.

## Potential future work
In addition to the work mentioned above, we are looking forward in our research plans to develop functionality that will serve the rest of our users that includes (but is not limited to) data cleansing and validation, additional user access management tools, and/or user interface enhancements based on usability testing. 
## Backlog
The backlog can be found in the [raft-tech fork of the TANF-app GitHub public repository](https://github.com/raft-tech/TANF-app/issues).
