# Our Workflow

Included herein is a description of how TDP features are implemented---from the point of **issue creation** to explain the current conditions that justify an issue resolution, implementation considerations, and tasks---to the point of **issue closure**, which should reflect government acceptance of the research, design, and/or development work into the [HHS TDP repo](https://github.com/HHS/TANF-app). 

Issues will be created in the [Raft TDP repo](https://github.com/raft-tech/TANF-app/issues/new/choose) and tracked in Zenhub. See [TDP Workflows in Zenhub](https://app.zenhub.com/workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/workflows) for a visual representation of how issues move across the boards. The diagram below is an abbreviated version. 

![](https://i.imgur.com/UGlqsXv.jpg)

[Figma link to TDP workflow diagram](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=6202%3A49062)

### A new issue is created
- New issues should be primarily focused on the goals for the release work in-progress along the [Product Roadmap](), but can also be created when the team identifies a need for a larger conversation that falls outside the scope of regular sprint ceremonies.
- Use the appropriate [issue template](https://github.com/raft-tech/TANF-app/issues/new/choose). These include standard elements that should be completed **before** the issue can be discussed during backlog refinement: 1. acceptance criteria; (2) list of tasks, (3) any open questions, and (4) helpful links. 
    - The title of the issue should be a user story with a clear goal (e.g., `As a <role>, I want to <action> so that <value>`).
   - An issue should always start with a clear summary of the current condition and an explanation of why it needs to be addressed.
   - For _dev_ issues, implementation options should be included in the issue summary. See [here](https://hackmd.io/@jtwillis92/r1KF0K8tF#Tasks) for more guidance on describing tasks.
- New issues will automatically be placed in the “New issues to be sorted column” in the [Product Backlog](https://app.zenhub.com/workspaces/tdrs-product-backlog-5f2c6cdc7c0bb1001bdc43a5/board?repos=281707402) in Zenhub.

### The issue is refined
- The Product Owner, ACF Tech Lead, Project Manager, Design Lead, and Raft Tech Lead will meet weekly for [backlog refinement](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/team-charter/team-meetings.md#backlog-refinement) to review issues on the Product Backlog. They will flesh out details on the issues, group them into epics if applicable, and prioritize them into the appropriate column/pipeline in Zenhub. 
- _Epics_ are used to group issues by their theme, and often span multiple sprints. The epics appear as issues with the label “epic" will be are organized into milestones and releases in the [Product Roadmap](https://app.mural.co/t/raft2792/m/raft2792/1629476801275/0f2773589c30764b9f53740adbc5706074ac52a6?).


### The issue is pointed, assigned, and accepted into sprint 
- **The PO and ACF Tech Lead will propose a set of refined issues during [sprint planning](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/team-charter/team-meetings.md#sprint-planning) mtg that they would like the team to focus on for the next sprint.**
- Refined issues should be pointed, which will be based on the amount and complexity of work ([Practical Fibonacci: A Beginner's Guide to Relative Sizing](https://www.scrum.org/resources/blog/practical-fibonacci-beginners-guide-relative-sizing)), as well as other details defined in the ticket (e.g. open questions, risks, etc.). Issue points _do not_ directly correlate to hours/time spent on an issue. 
- Pointed issues should be assigned to at least one team member before acceptance into the sprint.
- Once the issue has been accepted into the sprint:
    - the issue should move to the "Current Sprint" column on the Product Backlog Board and "Current Sprint Backlog" on the Sprint Board in Zenhub.
    - the issues should be assigned to the sprint.
    - Sprint goals will be added as a pinned post in the [TDP General Channel](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/team-charter/communication-tools.md#using-github-plugin-for-mattermost) at the start of each sprint. Sprint goals are also documented in each [Sprint Summary](https://github.com/raft-tech/TANF-app/tree/raft-tdp-main/docs/Sprint-Review).

### Work on the issue is started
- When the individual assigned to work on an issue starts work on it, they should move it to the “In Progress” column/pipeline in Zenhub. 
- Progress should be updated in issue daily. Any major decisions or discussions about the issue--especially **scope creep** and **blockers** should be documented within the issue.
- **If the issue grows in scope**:
  - Determine with the PO, ACF Tech Lead, and PM if more refinement is needed and/or new issue(s) should be spun out from parent ticket. 
  - Any new issues should be discussed at the next backlog refinement, unless it is a hot fix or other high priority that requires earlier discussion.
- **If the issue becomes blocked**:
  - Move the issue to the “Blocked” column/pipeline in Zenhub.
  - Document (and include references and visual evidence if applicable) in the issue and indicate if the issue is _not resolvable_ or _dependent on completion of other issues_. Assignee should report on a blocked issue in standup.
  - If dependent on other issues, [document those dependencies within the issue.](https://help.zenhub.com/support/solutions/articles/43000010349-)
- Pairing session(s) with ACF are encouraged throughout the sprint to increase transparency and familiarity with the issue.

### The issue is ready for Raft review
- When the issue is ready for review, the assignee should check that:
  - all ACs are met and tasks complete
  - documentation necessary to review the work is captured
  - A pull request is drafted using the [PR template]() for issues that will result in changes to the documentation/code managed in the TDP repo. **See [ADR 009]() for more details on the PR review process, which may vary depending on the issue type (e.g. frontend, security controls, dependencies)**.
- If all this is in place, the assignee should move the card to “Raft Review” column/pipeline in Zenhub and ping the appropriate reviewer(s).
     - Once _research_ issues are approved in raft review, the assignee should tag the PO for review and move the issue/PR to the "QASP Review" pipeline in Zenhub. 
     - For _design_ issues, the assignee should tag at least one developer for raft review. Upon approval,  the reviewer tags the ACF Tech Lead and moves the issue/PR to the "QASP Review" pipeline in Zenhub.
     - _Dev_ issues must proceed through the **[tabletop process](https://github.com/raft-tech/TANF-app/tree/raft-tdp-main/docs/How-We-Work/Developer-Tabletops.md)** and be approved in raft review before it is moved the "QASP Review" pipeline in Zenhub. 

### The issue is ready for QASP review
- The government reviewers (i.e. PO or ACF Tech Lead) verify that all the acceptance criteria and the relevant [QASP elements](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/.github/pull_request_template.md) have been met.
- The reviewer checks the issue/PR against the QASP checklist and provides feedback if needed. Raft addresses any small feedback (one/two pointer) within the same PR. Larger feedback is added as an issue for backlog refinement and PR is updated with a note on the ‘issue # has been created to address the specific feedback.’
- Government reviewers approve PRs (or request changes) and when relevant qasp elements satisfied, adds the label "Ready to Merge". 

### The issue is ready for demo
- When QASP reviewers have signed off and the team is ready for feedback from OFA stakeholders, then the feature is demonstrated in [Sprint Demo](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/How-We-Work/team-charter/team-meetings.md#sprint-demo).
- PM organizes sprint demo agenda and posts agenda in Mattermost. This will also serve as the basis for the Sprint Summary md. 
- Feedback from stakeholders is discussed and, if necessary, new issues are created to address feedback.

### The issue is considered closed when:
  - Issues in sprint meet the deliverables in the QASP checklist
  - PR is merged in main HHS repo