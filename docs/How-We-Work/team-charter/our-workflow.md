# Our Boards/Workspaces

We have three project management boards for organizing our work:

- **[Sprint Board](https://github.com/raft-tech/TANF-app#workspaces/tdrs-sprint-board-5f18ab06dfd91c000f7e682e/board?repos=281707402)** This is only for the issues our team committed to for the current sprint. This lives in the Raft GitHub account.
- **[Product Backlog](https://github.com/raft-tech/TANF-app#workspaces/tdrs-product-backlog-5f2c6cdc7c0bb1001bdc43a5/board?repos=281707402)** This is where the PO can stage user stories, adjust prioritization, and prepare issues to bring to Sprint Planning meetings. This also lives in the Raft GitHub account.

# Government Priorities

Based on the September 2020 iron triangle conversations, the product team committed to the following:

1. **Prioritizing quality over time and scope.** Quality is the rigid end of the triangle while time and scope are flexible ends of the triangle.
2. **Raft moves issues to QASP review pipeline if and only if Raft believes issues meet the AC.** [who checks off the AC has not been determined – so far – until Sprint 4 - Lauren/QASP reviewers have been checking off the AC]. If AC cannot be met or has to be updated, then Rafter(s) document the change/update in GitHub.
3. **Issue(s) are submitted for QASP review on a rolling basis.** For each sprint, Raft submits at least one issue for QASP review.


# Workflow

## A new issue is created
- New issues should usually be created on the [Product Backlog](https://github.com/raft-tech/TANF-app#workspaces/tdrs-product-backlog-5f2c6cdc7c0bb1001bdc43a5/board?repos=281707402) and placed in the “New issues to be sorted column.”
- Whenever possible, the title of the issue should be a user story with a clear goal.
- The default issue templates will outline the standard elements for you—a description, a list of tasks, acceptance criteria, and definition of done. An issue may also contain open questions or helpful links.
- If an issue is tightly scoped, the templates for engineering, research, or design may be used for more specialized acceptance criteria and definition of done.
- It’s okay if you can’t define every element of the template right away—we can develop our understanding as the issue is prioritized.
- A new issue should also be created when the team identifies a need for a larger conversation that falls outside the scope of regular sprint ceremonies. This should be prioritize alongside other issues in a sprint.


## The issue is refined and organized into an epic
- The product owner, Design Lead, and Tech lead will meet weekly to review issues on the Product Backlog. They will flesh out details on the issues, prioritize them, and group them.
- Epics are used to group issues by their theme. The Epics appear as issues with the label “Epic.” The “Epic Name” should be simple, high-level user story using the “As a <role>, I want to <action> so that <value> syntax.
- Issues and epics are organized into Product Goals. Most of the columns or “pipelines” on the Product Backlog board are Product Goals. These are a set of epics that we work on in parallel and develop KPIs around. These are laid on the [Product Roadmap](https://app.mural.co/t/officeoffamilyassistance2744/m/gsa6/1592336604317/61159efd030645a74c267130ea19b2083f87dd09).


## The product owner proposes the issue for the next sprint
- The PO will come to Sprint Planning meeting with a set of issues she would like the team to focus on for the next sprint. The team discusses these and may add clarifications to the issue cards, break one issue down into two, or in other ways adjust the definition of the work.
- All elements of the issue template should be defined before the issue is accepted into the sprint

## The issue is assigned points
- We will follow a hybrid approach of tracking product delivery and utilization to point issues that are related to admin and tech debt. When assigning points to OCIO related issues, we are thinking of the Raft’s commitment.  
- At the end of sprint planning, we will acknowledge how many points are for non-product issues (e.g., admin and tech debt) and use them to guide the team towards future planning. 


## The issue is accepted into the sprint
- If the issue is accepted into the sprint, it should move to the Sprint Board and the Sprint Backlog column.
- All issues accepted into the sprint should be assigned the corresponding ZenHub Milestone for the sprint. (Milestones = Sprints).
- Milestones should also be applied to any pull requests during a sprint.
- Milestones may contain issues from different Epics.
- The “Milestone Name” should be formatted as Sprint #: <Start Date> - <End Date>
- The issue should be assigned to at least one team member.
- The acceptance criteria for issues is written as an achievable outcomes of tasks.


## Work on the issue is started
- When the individual assigned to work on an issue starts work on it, they should move it to the “In Progress” column/pipeline.
- Any decisions or discussions about the issue should be documented within the issue
- Ad hoc pairing or scheduled pairing session(s) with 18F are encouraged prior to the Day 13 QASP review so the 18F team does not see progress on the issue for the first time on Day 13.
- For dev issues
  - The branch you create should be prefixed with the issue number
  - Push the branch up as soon as possible and open a Draft PR.


## If a design issue is done and needs to be handed off to Dev team
- Figma links, containing committed designs and notes, are included in dev issue and design issue is referenced
- Design can be viewed in Figma as a story, including only screens that were touched for that particular story. This will be primary source of truth for the design commit.
- Design can be viewed in Figma in the context of the whole site. The reviewable screens are clickable to disclose possible user work flows.
- (Optional) For complex designs, a loom video can be included to walk the viewer through the workflow with a voice over from the designer for more transparency.


## If the issue grows in scope
- If a sprint demo or other activity causes an issue to grow in scope, discuss this with the PO.
- If the scope has grown significantly, a new issue should be spun off as a child of the original issue. Make sure both parent and child issue have the related epic tag.
- If appropriate, tag the new issue in the current Sprint and leave it in Sprint Backlog column/pipeline or move it to the Product Backlog board.


## If the issue becomes blocked
- When an issue can’t be resolved due to other issues or is dependent on completion of other issues document those dependencies within the issue. [See how to utilize dependencies.](https://help.zenhub.com/support/solutions/articles/43000010349-create-github-issue-dependencies)
- If no progress can be made, move the issue to the “Blocked” column/pipeline.
- Assignee should discuss any blocked issue in standup.
- Long-standing blocked issues will also be reviewed as part of Sprint Planning.


## The issue is ready for Raft review
- Once the assignee feels the issue is ready for review, they should check the following:
  - All tasks complete
  - Acceptance criteria is met or a note is added in GitHub if AC is not being to be met and why
  - Issue contains links to documents or environments necessary to review the work
  - If dev issue, create a PR for the issue using the PR template
  - See docs/team-charter/reviewing-work.md
- If all this is in place, the assignee should move the card to “Raft Review” column/pipeline and ping the appropriate reviewer/s.



## The issue is reviewed by Raft
- If changes are needed, reviewer moves the issue back to ‘In Progress’ and notes the comments and pings the assignee for revision.
- For dev issues, if issue meets the acceptance criteria and all tasks are done, the reviewer
  - closes PR to merge it into the Raft dev environment
  - creates a new PR for all the issues to be reviewed during QASP review using the ‘Sprint Summary Report’ template (page 16) with a WIP label/note until it is ready to be reviewed
  - moves the issues to ‘Government Review’ pipeline and assign Laura (gov tech lead) and Lauren to review the PR
  - Once the WIP label is removed from the PR created in the HHS repo, no work is to be done against the branch submitted for review unless changes are requested and/or the branch has been approved and merged.
- For design or research issues, if issue meets the acceptance criteria and all tasks are done, the reviewer
  - moves the issue to ‘Government Review’ pipeline and tags Lauren for review


## The issue is reviewed by government
- Lauren verifies that all the acceptance criteria and the relevant QASP elements have been met.
- If issues meet the acceptance criteria, reviewers move the issue to “Done and ready for demo.” Only issues in “Done and ready for demo” will be demoed. (So keep issues small!)
- If changes are needed, government reviewer/s move the issue back to ‘In Progress,’ notes the comments, and tags the assignee. Small tweaks can be sent back to the assignee on the same issue at this stage, but a new issue should be created if the feedback constitutes an significant expansion of scope.
- When issues are being reviewed by QASP review day (Day 13), Raft team can continue to work on issues that are ‘In progress’ or ‘To Do’ pipeline. If all issues in these columns have been addressed, then Raft team can pull from prioritized product backlog 'Ready to go for Next Sprint'


## The issue is ready for demo
- When QASP reviewers have signed off and the team is ready for feedback from OFA stakeholders, then the feature is demonstrated in Sprint Demo meeting.
- Feedback from stakeholders is discussed and, if necessary, new issues are created to address feedback.


## The issue is complete and ready for final QASP review
- Raft creates a PR and a Sprint Summary Report (see Page 11), which is included in the PR notes.
- Tech lead reviews the PR, the COR comments acceptance, and Lauren merges the PR into main HHS repo
- QASP reviewer reviews the PR against the contract QASP, DoD, and provides feedback by Monday (Day 13). Raft address any small feedback (one/two pointer) prior to 12pm Day 15 deadline. Larger feedback is added as an issue for backlog refinement and PR is updated with a note on the ‘issue # has been created to address the specific feedback.’
- Dev issues: DoD for dev issues is reviewed at the QASP level and is met when the PR: (1) note contains sprint report, (2) meets the QASP, (3) Raft has addressed small feedback (by 12pm on Wednesday, which is Day 15 of the last sprint/Day 1 of next sprint), and (4) has received a signed off from QASP reviewer.
- Design issues: DoD for design issues is stated in the actual issues

The following evaluate AC and DoD to close issues and/or PR:

AC: Lauren or Alex S (Tech lead)

DoD: Alex S (Tech lead) for dev issues; Design and research - Lauren


## The issue is considered ‘sprint done’ when
  - Issue is closed
  - Issues in sprint meet the QASP
  - PR is merged in main HHS repo
