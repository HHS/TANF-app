# 2024, Summer - OFA Admin Experience

**Jump To:**

* [Background](#background)
* [What we did & who we talked to](#what-we-did--who-we-talked-to)
* [What we learned](#what-we-learned)
* [Next steps](#next-steps)

***

## Background

The Django Admin Console (DAC) is an internal tool tailored for our OFA System Admin and DIGIT Team users. It allows for access to the Postgres database & system logs, managing user permissions, and has been increasingly adopted to provide the DIGIT team with quick insights into data file errors and STT submissions.&#x20;

***

## What we did & who we talked to

We ran two workshops with the DIGIT team; which overlaps with our two OFA System Admins. While those teams overlap, note that the permissions for each user group differ. OFA System Admins have privileged access to DAC while DIGIT team users have non-privileged access. Our product manager and two developers were also in attendance for alignment and work estimation purposes. These workshops facilitated conversation around DAC enhancement requests & pain points provided by OFA in tickets [#2930](https://github.com/raft-tech/TANF-app/issues/2930), [#1662](https://github.com/raft-tech/TANF-app/issues/1662), [#960](https://github.com/raft-tech/TANF-app/issues/960), and [#2910](https://github.com/raft-tech/TANF-app/issues/2910) in order to achieve:

* A clear understanding of current enhancement requests and described pain points
* Initial estimation of the work required to deliver each change to the DAC
* Alignment on the scope of potential work to support prioritizing all issues within our product roadmap and upcoming sprints

***

## What we learned

We identified and refined our understanding of Django Admin Console enhancements in the following categories:

### Filtering & readability

<table><thead><tr><th>Enhancement</th><th>Description</th><th>DAC Page</th><th>Ticket</th><th>Recommended Priority</th></tr></thead><tbody><tr><td>Filter data files by relative date</td><td>Adds filter to the DAC Data Files page that filters by submission date and includes options for submissions yesterday, today, the past 7 days, the current month, and the current year. #3077 captures a higher lift enhancement to this use case.</td><td>Data Files</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3076">#3076</a></td><td>4.0 / P3</td></tr><tr><td>Default filter on DAC Data Files page to show only the most recent submissions per STT, fiscal period, and section. </td><td>Currently DAC Search Indexes pages default to filtering results to "Newest". This ticket updates the language of that filter to "Most recent version" and adds that behavior to the Data Files page.</td><td>Search Indexes, Data Files</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3087">#3087</a></td><td>4.0 / P4</td></tr><tr><td>Add multiselect control to Search Indexes Fiscal Period Filter</td><td>Currently the filter control on DAC Search Indexes pages is a single option dropdown. This ticket replaces it with the multiselect control that we use when filtering by STT. This replicates the SQL union queries used in the legacy system.</td><td>Search Indexes</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3102">#3102</a></td><td>4.0 / P4</td></tr><tr><td>Add filters from DAC Data Files page to Data File Summaries pages</td><td>Currently Data File Summaries pages lack filtering capability. This ticket delivers filter options matching those on the Data Files page.</td><td>Data File Summaries</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3093">#3093</a></td><td>4.0 / P2</td></tr><tr><td>[Spike] Investigate adding Change Message types</td><td>This spike investigates whether we can supplement the current Change Message column on log entries with a change type to allow for filtering capability. </td><td>Log Entries</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3092">#3092</a></td><td>4.0 / P2</td></tr><tr><td>[Spike] Investigates how we can provide a tabular view of data file summaries</td><td>Currently data file summaries are served up in a raw JSON format. To make them easier to read we should investigate how we might map these data to a table view.</td><td>Data File Summaries (Specific Summary view)</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3095">#3095</a></td><td>4.0 / P2</td></tr><tr><td>Rearrange Data Files filters and implement multiselect fiscal period filter</td><td>Adds the multiselect control for fiscal period filtering (as seen on current Search Index pages on the Data Files page and rearanges filters into a more intuitive order.</td><td>Data Files</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3097">#3097</a></td><td>4.0 / P2</td></tr><tr><td>[Spike] Investigate YYYYMMDD value filtering for data files</td><td>Higher lift ideal solution following on from #3076. Investigates how we might add the ability to filter the DAC Data Files page to those submitted on a specific date or within a specific date range. </td><td>Data Files</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3077">#3077</a></td><td>Beyond 4.0 / P2</td></tr><tr><td>List of Cat 1,4 rejected case numbers</td><td>Provides a method of filtering current django outputs to produce a list of case numbers and months which are associated with category 1 and 4 errors. This provides DIGIT with a new analogue to the transmission reports of the legacy system.</td><td>Data File Summaries (Specific Summary view)</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3096">#3096</a></td><td>Beyond 4.0 / P2</td></tr></tbody></table>

### DAC actions & behavior

<table><thead><tr><th>Enhancement</th><th>Description</th><th>DAC Page</th><th>Ticket</th><th>Recommended Priority</th></tr></thead><tbody><tr><td>Read-only data file summaries </td><td>Modifies the DAC Data File Summaries view to make it read-only to better correspond to how it's used by the DIGIT team.</td><td>Data File Summaries (Specific summary view)</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3094">#3094</a></td><td>4.0 / P2</td></tr><tr><td>User deletion</td><td>Currently user deletion is not supported via the DAC. This ticket delivers that capability while retaining all objects associated to deleted users.</td><td>Users</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3089">#3089</a></td><td>Beyond 4.0 / P2</td></tr><tr><td>Mass actions on Users table</td><td>Currently System Admins cannot select and deactivate multiple users at a time. This ticket also delivers a filter to restrict the Users table to only those who have been inactive for 180+ days.</td><td>Users</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3090">#3090</a></td><td>Beyond 4.0 / P2</td></tr><tr><td>Add mailto: functionality to user email addresses in metadata</td><td>Currently in views of date file metadata, clicking on the user's email address links to that users entry in the DAC Users page. This ticket delivers an update that changes it to a mailto: that will open in the device's default email application.</td><td>Users (Specific user view)</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3120">#3120</a></td><td>Beyond 4.0 / P2</td></tr></tbody></table>

### Bugs & system performance

<table><thead><tr><th>Enhancement</th><th>Description</th><th>DAC Page</th><th>Ticket</th><th>Recommended Priority</th></tr></thead><tbody><tr><td>[Bug] Misleading file status column on DAC data files page</td><td>The file status column can return incorrect status values when viewed from the data files table rather than an individual data file's metadata page.</td><td>Data Files</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3068">#3068</a></td><td>4.0 / P2</td></tr><tr><td>[Spike] Investigate handling of custom filters </td><td>During implementation of the first <a href="https://github.com/raft-tech/TANF-app/pull/3083">DAC multiselect filter</a> we discovered problems with the handling of query strings which will pose scalability problems as we introduce new filters. </td><td>N/A</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3110">#3110</a></td><td>4.0 / P3</td></tr><tr><td>[Spike] Investigate latency when clicking into the parsing errors column on DAC data files page</td><td>Currently when clicking into "Parser Errors" for a given row of the DAC Data Files page there is significant latency before the system returns results. </td><td>Data Files</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3075">#3075</a></td><td>4.0 / P3</td></tr></tbody></table>

### Parsing

<table><thead><tr><th>Enhancement</th><th>Description</th><th>Ticket</th><th>Recommended Priority</th></tr></thead><tbody><tr><td>Update Section 3, 4 validation to screen for ≥ 1 families rather than ≥ 0 </td><td>Sections 3 and 4 of TANF data concern aggregate values that are highly unlikely to be 0. This ticket delivers a parsing logic fix to reflect that.</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3088">#3088</a></td><td>4.0 / P3</td></tr></tbody></table>

### User permissions

<table><thead><tr><th>Enhancement</th><th>Description</th><th>Ticket</th><th>Recommended Priority</th></tr></thead><tbody><tr><td>TDP Data Files page permissions for DIGIT &#x26; Sys Admin user groups</td><td>Currently users assigned to the DIGIT or System Admin user groups cannot reach and browse TDP's Data Files page. This ticket adds those permissions for both groups.</td><td><a href="https://github.com/raft-tech/TANF-app/issues/3074">#3074</a></td><td>4.0 / P4</td></tr></tbody></table>

### Security Controls

<table><thead><tr><th>Enhancement</th><th>Description</th><th>Ticket</th><th>Recommended Priority</th></tr></thead><tbody><tr><td>Auto-deactivation of users</td><td>User deactivation is currently a manual process for system admins. This ticket delivers automation that will automatically deactivate users who have been inactive for 180 days.</td><td><a href="https://github.com/raft-tech/TANF-app/issues/2561">#2561</a></td><td>4.0 / P3</td></tr><tr><td>System owner notification upon assigned admin permissions</td><td>Since very few people should be granted System Admin permissions in production, the system owner should be notified  whenever the role is assigned/unassigned.</td><td><a href="https://github.com/raft-tech/TANF-app/issues/1337">#1337</a></td><td>4.0 / P2</td></tr></tbody></table>

***

## Next Steps

Following this research, the design team will fully refine all the tickets referenced above and coordinate time with development and the DIGIT team to determine which enhancements will be tackled in release 4.0 and which will be deprioritized for a subsequent release.&#x20;

Additionally, the design team will prioritize [#3121](https://github.com/raft-tech/TANF-app/issues/3121) which delivers the email template that will be implemented by development in [#1337.](https://github.com/raft-tech/TANF-app/issues/1337)
