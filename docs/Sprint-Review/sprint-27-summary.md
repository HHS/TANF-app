# Sprint 27 Summary
**08/03/2021 - 08/17/2021 **

### Summary Updates
Continued work on Secret Key mitigation, all but 2 tasks completed, others in progress.
Continued work on parsing errors UX/UI
Started UX UI for Access Request Process
Started TDP Permissions engineering work.


## Sprint 27 Goals

Begin TDP Permissions Epic build items
Work on Production Readiness Tickets for V1
UX:
1. Access Request UX/UI
2. Continue Error UX/UI
### [Next Sprint (28) Goals](https://github.com/raft-tech/TANF-app/milestone/30))
## Closed/Merged/Completed (Done/Demo, Closed)
- [Backend] Change reports to data files [#755](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/755)
- [Backend] Utilize Django settings modules for non-sensitive environment variables that differ between deployed environments [#970](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/970) 


## Submitted (QASP Review, OCIO Review)
- Round 7 PreParsing Errors Live Comms w/ Regional Staff [#1194](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1194)
- Round 7 (Sprint 24-26) UX Research and Design [#1017](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1017)

## Moving to Next Sprint (Raft Review, In Progress, Current Sprint Backlog)
**Raft Review**
- As a dev, I'd like to be able to retain my database contents between restarts [#795](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/795)


**Blocked**
- As a dev, I want Terraform changes to be reflected in label driven deployments (GitHub Action) [#1059](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1059)

**In Progress**
- (Sprint 27) UX Research Support & Comms [#1166](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1166)
- As a dev, I need to know which authentication service we're using (login.gov vs. NextGen XMS) [#638](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/638)
- [Epic]Secret Key Leakage Mitigation [#972](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/972)
- As a TDP user, I want to see a picture that better represents the program on the homepage [#640](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/640) 
- Django Admin a11y Fixes (Sprint 3)  [#1054](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1054)
- Round 7 PreParsing Errors Research Synthesis [#1193](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1193)
- Remove "Super User" attribute, leverage model permissions [#901](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/901)
- System Admin group by default [#1065](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1065)
- Update/Create Target and Aspirational State Journey Maps Based on New Research and Roadmap Discovery [#1196](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1196)
- [DevOps] Add a Circle CI testing step that confirms no secret keys have been committed [#966](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/966)
- As a dev, I want the authentication credentials used for testing to be dynamically generated [#969](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/969)

**Current Sprint Backlog**
Items moved to next Sprint 28  


## Agenda for Sprint 27 Demo 
- [Product Roadmap Updates](https://app.mural.co/t/raft2792/m/raft2792/1621347373680/75cdd996c2ef8cf2a46825705fb7d7b38727f77d?sender=u64c7132cff9878e9eb088109)- Angela 
- UX Roadmap prep [#1147](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1147)- Miles/Angela
- (UX Sprint 26) Test Error Communication for Parsing Blockers [#1020](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1020) - Miles
- I want a Content Security Policy to protect me from XSS and other client side attacks [#907](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/907)
- Set CSP Header for Backend [#1192](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/1192) - Andrew
- As a dev, I'd like to be able to retain my database contents between restarts [#795](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/795) - John
- [Backend] Change reports to data files [#755](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/issues/raft-tech/tanf-app/755)- Aaron

[Link to Sprint 27 Milestone Details](https://github.com/raft-tech/TANF-app/milestone/30)
