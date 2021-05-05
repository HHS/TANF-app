_updated May 2021_
# Product Roadmap
Our [roadmap](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1617994644349/6047bad9ed365b22986e52f5d9f01aac32286ae9) :lock:represents our latest thinking about the order in which we’ll tackle the various pieces of the overarching problem.

We consider ATO, Release 1 and Release 2 commitments that the team will deliver on at this time. There might be a few shifts in approach, timing or scope, but in general, these outcomes will be worked on by the team. Metrics for success will be added as they are defined for releases.

Beyond that, we're still discovering and planning on what best serves our users. This doc will continue to be updated as we make decisions and scope releases. 

## ATO  
Value Delivered: Get approval for the authority to operate and create a production environment. 

| Outcome | Status | 
| -------- | ------- | 
| User can log in using login.gov | Complete
| Users with appropriate privileges can manage users | Complete
| Users can upload data files by section and quarter | Complete
| Users with appropriate privileges can download files that were previously uploaded     | In Progress
|Create production environment | Will happen after ATO

## Release 1 (fka OFA MVP) Scope
Value Delivered: ACF employees can use a secure method to log into the system; this would require a PIV card.

Our first release to production will include the functionality built for ATO (above) and also include a secure way for ACF employees to access the system, we're currently looking into integrating with HHS AMS/ACF AMS or additional options within login.gov. It is important these measures are put into place before sensitive production data is uploaded to the system.

The team is also investigating options for optimizing permission management and strategy as a part of this release. 
| Outcome | Status | 
| -------- | ------- | 
| Privileged ACF users are required to login with PIV/CAC credentials | Researching
| Permissions Configuration | Researching


## Release 2 (fka Tribal MVP) Scope

Value Delivered: Allow users to securely upload data into our system, replacing a less secure way of doing so while increasing communication with the users and not increasing burden for OFA Admin staff.

_Notes:_ We're investigating a way to automatically update file names once uploaded (based on standard naming convention) and set up a CRON job to pick up files and move them into a place where the existing TDRS application can pick them up. If this solution is selected, it would reduce the amount of time OFA tribal TANF and data staff spend with each file. 

While this type of workflow isn't our long term workflow, including it at this point delivers value to the users quicker. So we are evaluating the ROI before deciding on this path.

_Risks:_ The users that would be on-boarded to this process, would potentially have to learn and adjust with future releases and changes in functionality and workflow. Increased communication with them should help here.
| Outcome | Status | 
| -------- | ------- | 
| STT user of the system knows their file(s) were successfully uploaded | Not Started
| Files successfully transferred to ACF server | Not Started
| Files uploaded by STT user(s) are successfully entered into the existing TDRS system | Not Started

## Potential future work
In addition to the work mentioned above, we are looking forward in our research plans to develop functionality that will serve the rest of our users that includes (but is not limited to) data cleansing and validation, additional user access management tools, and/or user interface enhancements based on usability testing. 
## Backlog
The backlog can be found in the [raft-tech fork of the TANF-app GitHub public repository](https://github.com/raft-tech/TANF-app/issues).
