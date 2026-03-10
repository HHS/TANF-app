# sprint-111-summary

## sprint-111-summary

&#x20;10/22/2024 - 11/5/2024

**Dev:**

**Dev:**

_**Prioritized Errors, Application Health Monitoring, DevSecOps focus**_

* \#3075 — spike - latency on DAC (if 3137 cannot be solved)
* 3155 - spike - prioritized errors
* See below for some options:
  * 1337 - Sys Admin permissions assigned notification
  * 3222 - PLG Production Migration (to track work)
  * 3224 - audit logging ("hide" PII from logs)

**DevOps:**

_**Successful deployments across environments and pipeline stability investments**_

* \#3141/#3194 test-deployment-e2e is failing integration test&#x20;
* 2435 - HHS missing/wrong env vars
* 1786 - linters pre-commit hook

**Design:**

_**Support reviews, continue research planning, support release notes**_

* \#3225 \[Research Planning] FRA MVP
* \#3265: \[Research Facilitation Prep] Finalize Prototypes for FRA research sessions
* \#3230 OFA Service Blueprint
* Release Notes Knowledge Center Updates and Email
* \#3100 \[Design Deliverable] Update stakeholders & personas document

**PM:**

* Sprint Summary (including backlog summaries)

### Tickets

#### Completed/Merged

* \#3210 [Doc/3199 monitoring adr](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3210)
* \#3201 [Spike - testing CSV exports in production](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3201)
* \#3046 [PLG deployed in Cloud.gov](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3046)
* \#3247 [Fixes doc formatting issue](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3247)
* \#3075 [\[Spike\] Investigate latency when clicking into the parsing errors column on DAC data files page](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3075)
* \#3171 [CircleCI pipeline utilizes internal Nexus infrastructure](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3171)
* \#3199 [Performance Monitoring ADR](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3199)
* \#3149 [Sprint 110 Release Notes/Knowledge Center](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3149)
* \#3192 [PLG Cloud.gov](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3192)
* \#3200 [Feat/3171 nexus integration](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3200)
* \#3214 [Update personas document for issue #3100](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3214)
* \#3221 [sprint-109-summary](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3221)
* \#3236 [3075-latency-parsing-errors](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3236)
* \#3239 [Release notes 3.7.0](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3239)

#### Submitted (QASP Review, OCIO Review)

* \#2435 [As tech lead, I need HHS/TANF-app/CircleCI to supply environment variables for staging and prod environments](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2435)
* \#3225 [\[Research Planning\] FRA Research](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3225)
* \#3242 [Local Alertmanager](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3242)

#### Ready to Merge

* N/A

#### Closed (Not Merged)

* \#3100 [\[Design Deliverable\] Update stakeholders & personas document](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3100)

#### Moved to Next Sprint

**In Progress**

* \#1786 [As a developer, I want linters to run automatically before git push](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1786)
* \#2562 [Spike: parsing log per file upload](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2562)
* \#3014 [Outdated info banner for submission history results with data processed before 5/31/24](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3014)
* \#3220 [\[Design Deliverable\] Service Blueprint](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3230)

**Blocked**

* N/A

**Raft Review**

* \#1337 [As a sys owner, I want to be emailed when sys admin permissions have been assigned.](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1337)
* \#3141 [test-deployment-e2e is failing integration test](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3141)
* \#3155 [Spike - Prioritized Errors](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3155)
* \#3224 [Audit Logger](https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3224)

