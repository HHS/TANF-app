---
description: December 18, 2024 - December 31, 2024
---

# Sprint 115 Summary

## Summary

### Highlights

In this sprint, our team successfully completed several initiatives aimed at improving system security, user experience, and operational efficiency, while also advancing design efforts to better meet stakeholder needs. Key highlights included:

* Regional Staff Access to TDP:
  * Developed designs to provide regional staff with improved access to submission statuses and error reports, streamlining their workflows.
* Operations & Maintenance:
  * Upgraded critical dependencies, enhancing platform performance and security.
  * Updated release notes and Knowledge Center content for better user guidance and documentation.
* Application Health Monitoring:
  * Enhanced logging capabilities through Promtail pipelines for better troubleshooting.

## Roadmap Progress&#x20;

\[OMITTED] This will be included in future sprint summaries.

## Tasks

### Improved Developer Tooling

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3205">#3205</a> - Reparse command refactor</td><td>Streamlines and simplifies the reparse logic by creating a shared utility function, improving maintainability and enabling more customizable parsing behavior for both the admin and management commands.</td><td><mark style="color:orange;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3223">#3223</a> - Automate buildpack states via Terraform</td><td>Enhances the team's ability to manage and track CloudFoundry deployments more effectively, improving state visibility, reducing unnecessary redeployments, and ensuring better control over infrastructure, while maintaining seamless integration with CircleCI and updating relevant documentation.</td><td><mark style="color:blue;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### FRA Reporting Requirements MVP

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3297">#3297 </a>- FRA Research Synthesis</td><td>Provides valuable user insights through finalized research synthesis and findings, guiding the development of the FRA MVP while ensuring stakeholder alignment, accessibility, and actionable outcomes for future development.</td><td><mark style="color:blue;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Application Health Monitoring

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3243">#3243</a> - Promtail Pipelines</td><td>Enhanced the Grafana logging dashboard by implementing Promtail pipelines to extract and enrich log metadata (such as log level, message, and app name), enabling more powerful and flexible querying of logs in Grafana.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/2346">#2346</a> - As tech lead, I want to load test our application</td><td>Ensures that the backend infrastructure is adequately stress-tested for scalability, identify any performance bottlenecks under heavy concurrent load, and provide actionable insights for optimizing system capacity to handle large file uploads.</td><td><mark style="color:orange;"><strong>RAFT REVIEW</strong></mark></td></tr></tbody></table>

### Operations & Maintenance

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3316">#3316</a> - v 3.7.5 Release Notes and Knowledge Center Updates</td><td>Ensured STTs receive timely and accurate release notes via both the TDP portal and email, improving communication, transparency, and user understanding of recent updates and changes.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/1577">#1577</a> - Upgrade react-scripts to 5.0</td><td>Ensures that the project is using the latest stable versions of <code>react-scripts</code> and <code>file-type</code>, addressing potential breaking changes and improving overall stability and functionality while maintaining compatibility and compliance with modern standards.</td><td><mark style="color:yellow;"><strong>QASP REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3341">#3341</a> - Move Cat 2 and Cat 3 errors from aggregate and stratum to critical worksheet</td><td>Improves the accuracy and relevance of error reporting by ensuring critical data integrity errors are correctly elevated to the Critical worksheet, while also excluding specific non-critical errors, thereby enhancing data oversight and decision-making.</td><td><mark style="color:orange;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3342">#3342</a> - Deprecate Cat 4 validation checks for case closure</td><td>Streamlines the data validation process by deprecating unnecessary checks, improving the accuracy of case file feedback for OFA, and ensuring that records can be properly stored and analyzed in the database.</td><td><mark style="color:orange;"><strong>RAFT REVIEW</strong></mark></td></tr><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3328">#3328</a> - Resolve vulnerabilities in frontend dependencies after React upgrade</td><td>Resolves critical and high-severity vulnerabilities identified in the project, ensuring improved security and stability while documenting and addressing any unresolved issues for future resolution.</td><td><mark style="color:blue;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>

### Regional Staff Access to TDP

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3249">#3249</a> - As regional staff, I want to be able to see the status of my STTs submissions and view their error reports.</td><td>Empowered regional staff with the ability to directly access submission statuses and error reports for their regions, reducing delays and the central office's workload, while improving overall transparency and efficiency in managing STT data submissions.</td><td><mark style="color:green;"><strong>COMPLETE</strong></mark></td></tr></tbody></table>

### OFA Regional Staff UI MVP

<table><thead><tr><th width="176">Task</th><th width="445">Value Proposition</th><th>Status</th></tr></thead><tbody><tr><td><a href="https://app.zenhub.com/workspaces/sprint-board-5f18ab06dfd91c000f7e682e/issues/gh/raft-tech/tanf-app/3262">#3262</a> - [Design Ideation] Regional Staff UI: Submission Status and Missing Submissions</td><td>Delivers testable UI concepts for regional staff, ensuring that the design meets user needs for monitoring submission statuses while adhering to accessibility standards, providing a foundation for future development and user validation.</td><td><mark style="color:blue;"><strong>IN PROGRESS &#x26; MOVED TO NEXT SPRINT</strong></mark></td></tr></tbody></table>
