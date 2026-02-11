---
description: September 10, 2025 - September 23, 2025
---

# Sprint 134 Summary

## Summary

This sprint focused on enhancing the system's capabilities and addressing critical issues to ensure compliance and improve user experience. Key achievements include the decoupling of the SSP flag from filenames to retain historical data, the implementation of an admin review workflow for user change requests, and the investigation of missing DataFileSummary records. These efforts not only streamline processes but also enhance data integrity and accessibility, which are crucial for maintaining operational efficiency and compliance with federal reporting requirements.

**Here's a list of the issues the team completed in this Sprint...**

* [Investigate decoupling SSP flag from filenames and retain historical data for NY post-FY24](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3323)  TANF-app #3323
* [Investigate missing DataFileSummary records for submitted files in production](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5264)  TANF-app #5264
* [Implement admin review workflow for user change requests](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/4974)  TANF-app #4974
* [4974 implement admin review workflow user change requests](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5165)  TANF-app #5165
* [3515 bug ofa system admin users get stuck region assigned](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5348)  TANF-app #5348
* [Design MVP interface for centralized feedback reports](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5222)  TANF-app #5222
* [Design MVP for sample STT universe data submission flow](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5349)  TANF-app #5349
* [Universe memory exploration](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/5378)  TANF-app #5378

## Statuses of all issues in this sprint

#### \[BLOCKED] Regional Staff TDP Access & Onboarding (RSAO) (#4395)

| Issue                                                      | Title                                                                                                                        | Status          |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | --------------- |
| [#3461](https://github.com/raft-tech/TANF-app/issues/3461) | Create and facilitate Project Updates meeting for regional staff                                                             | Blocked         |
| [#3462](https://github.com/raft-tech/TANF-app/issues/3462) | Create and facilitate optional training session for regional staff                                                           | Blocked         |
| [#3475](https://github.com/raft-tech/TANF-app/issues/3475) | Update Profile component to display regional user's assigned regions                                                         | Product Backlog |
| [#3523](https://github.com/raft-tech/TANF-app/issues/3523) | Refine research plan for regional staff MVP onboarding experience                                                            | Blocked         |
| [#3995](https://github.com/raft-tech/TANF-app/issues/3995) | Gather and iterate on OFA feedback                                                                                           | Blocked         |
| [#4045](https://github.com/raft-tech/TANF-app/issues/4045) | Gather final OFA feedback and iterate                                                                                        | Blocked         |
| [#4047](https://github.com/raft-tech/TANF-app/issues/4047) | Develop training materials, including slides, written instructions, and screenshots or screen recordings for visual guidance | Blocked         |
| [#4052](https://github.com/raft-tech/TANF-app/issues/4052) | Iterate on training materials internally                                                                                     | In Progress     |

#### Operations & Maintenance (#4445)

| Issue                                                      | Title                                                                                      | Status                 |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ---------------------- |
| [#3323](https://github.com/raft-tech/TANF-app/issues/3323) | Investigate decoupling SSP flag from filenames and retain historical data for NY post-FY24 | In Progress            |
| [#5268](https://github.com/raft-tech/TANF-app/issues/5268) | Implement Login.gov SET Tech Memo                                                          | Raft (Dev) Review      |
| [#5302](https://github.com/raft-tech/TANF-app/issues/5302) | Investigate alignment of application configurations across environments                    | Current Sprint Backlog |
| [#5308](https://github.com/raft-tech/TANF-app/issues/5308) | Improve Cypress E2E reporting and artifacts in CircleCI                                    | UX Review              |
| [#5333](https://github.com/raft-tech/TANF-app/issues/5333) | Implement additional SSN validation for federally-funded TANF recipients                   | Current Sprint Backlog |

#### FRA Post-MVP Enhancements (#4443)

| Issue                                                      | Title                                                        | Status                             |
| ---------------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------- |
| [#3485](https://github.com/raft-tech/TANF-app/issues/3485) | Design FRA successful processing email template              | Ready to merge into staging branch |
| [#3486](https://github.com/raft-tech/TANF-app/issues/3486) | Implement FRA submission email template                      | Current Sprint Backlog             |
| [#4973](https://github.com/raft-tech/TANF-app/issues/4973) | Implement Edit Profile page with shared Request Access logic | In Progress                        |
| [#4974](https://github.com/raft-tech/TANF-app/issues/4974) | Implement admin review workflow for user change requests     | Raft (Dev) Review                  |

#### Program Integrity Audit (#5356)

| Issue                                                      | Title                                                                                           | Status      |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------------------------- | ----------- |
| [#5346](https://github.com/raft-tech/TANF-app/issues/5346) | Backend Program Integrity Audit Schemas, Models, & Parser                                       | In Progress |
| [#5347](https://github.com/raft-tech/TANF-app/issues/5347) | Spike: Identify Memory Overhead of Duplicate Detection WRT Universe/Sample Datafile Submissions | In Progress |
| [#5349](https://github.com/raft-tech/TANF-app/issues/5349) | Design MVP for sample STT universe data submission flow                                         | UX Review   |
| [#5363](https://github.com/raft-tech/TANF-app/issues/5363) | \[Design Deliverable] Email notification for confirming program integrity audit submissions     | UX Review   |

#### Bug Reports (#4441)

| Issue                                                      | Title                                                                         | Status                 |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------- |
| [#3515](https://github.com/raft-tech/TANF-app/issues/3515) | Bug: OFA system admin users get stuck if region is assigned                   | Raft (Dev) Review      |
| [#5264](https://github.com/raft-tech/TANF-app/issues/5264) | Investigate missing DataFileSummary records for submitted files in production | In Progress            |
| [#5368](https://github.com/raft-tech/TANF-app/issues/5368) | \[BUG] User STT and Region assignment validation on user group change         | Current Sprint Backlog |

#### User Experience Enhancements (#4444)

| Issue                                                      | Title                                                                         | Status      |
| ---------------------------------------------------------- | ----------------------------------------------------------------------------- | ----------- |
| [#3251](https://github.com/raft-tech/TANF-app/issues/3251) | Update email templates for STT data submissions re: status and error guidance | QASP Review |
| [#5369](https://github.com/raft-tech/TANF-app/issues/5369) | Create research plan template for UX Playbook                                 | In Progress |

#### In-App Error Reporting - Foundational Design & Concept Validation (#4629)

| Issue                                                      | Title                                              | Status    |
| ---------------------------------------------------------- | -------------------------------------------------- | --------- |
| [#4721](https://github.com/raft-tech/TANF-app/issues/4721) | Plan research for in-app error reporting interface | UX Review |
| [#5300](https://github.com/raft-tech/TANF-app/issues/5300) | Complete In App Error Reports HTML Prototypes      | UX Review |

#### fTANF Replacement - Foundational Research & Concept Validation (#4628)

| Issue                                                      | Title                                                           | Status                 |
| ---------------------------------------------------------- | --------------------------------------------------------------- | ---------------------- |
| [#4989](https://github.com/raft-tech/TANF-app/issues/4989) | Define success metrics and goals for FTANF replacement research | Current Sprint Backlog |

#### Continuous User Feedback & Research Loops (CFL) (#4614)

| Issue                                                      | Title                                                                            | Status            |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------- | ----------------- |
| [#5197](https://github.com/raft-tech/TANF-app/issues/5197) | Add metadata to feedback submissions to support contextual analysis + a11y fixes | Raft (Dev) Review |

#### Centralizing Feedback Reports in TDP - Foundational Discovery (#5276)

| Issue                                                      | Title                                                 | Status    |
| ---------------------------------------------------------- | ----------------------------------------------------- | --------- |
| [#5222](https://github.com/raft-tech/TANF-app/issues/5222) | Design MVP interface for centralized feedback reports | UX Review |

#### Enabling Secure Data Access for DIGIT in Grafana (SDA) (#4339)

| Issue                                                      | Title                                                                    | Status  |
| ---------------------------------------------------------- | ------------------------------------------------------------------------ | ------- |
| [#5269](https://github.com/raft-tech/TANF-app/issues/5269) | Bump Grafana memory in prod by 4GB to support 1.5M record visualizations | Blocked |

#### Application Health Monitoring (AHM) (#3587)

| Issue                                                      | Title            | Status                 |
| ---------------------------------------------------------- | ---------------- | ---------------------- |
| [#5381](https://github.com/raft-tech/TANF-app/issues/5381) | Implement Sentry | Current Sprint Backlog |

