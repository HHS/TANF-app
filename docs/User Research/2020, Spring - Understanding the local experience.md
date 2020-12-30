# What we wanted to learn

Our goals for this research were to:

- Evaluate if early design concepts give states, tribes, and territories (STTs) the tools they need to effectively prepare valid data files to submit to OFA.
- Document how STTs currently create “last mile” data files to submit to OFA.
  - Identify which STTs use legacy tools to prepare TDRS submissions, what features were useful, and what caused confusion.
  - Describe how STTs validate and correct their data files before submission.
  - Document what STTs view as the beginning and the end of their data submission process.
- Document how OFA instructions are used by STTs, and how changes to those instructions would affect them and their systems.
- Identify STTs' own data reporting needs and document how they are currently accomplished.

[Full research plan](https://teams.microsoft.com/l/file/A476F16D-98EB-4E62-82C8-1C6200ACE49D?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared Documents%2FGeneral%2FUser research%2F2020 Spring local experience research%2FResearch Plan - Spring 2020.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)🔒

# Who we talked to

We wanted to talk to those who rely most on sunsetting TDRS tools so that we could understand their processes and experiences. We worked with regional program staff to recruit:

- STT staff who are responsible for preparing or submitting TANF data, particularly those who’ve personally use the TDRS extranet or fTANF executable to prepare a Section 3 aggregate data report
- OFA regional program specialists who support STT staff in managing and troubleshooting data submissions.

We interviewed 7 people, with two pairs working in the same office and owning different parts of the data submission process.

By their role and location

- 1 OFA regional program specialist
- 1 grantee from tribal government
- 5 grantees from 3 state governments

By the tools they use

- 4 folks currently using fTANF
- 4 folks familiar with the TDRS extranet

# What we tested

[Research protocol and outreach for testing the xls prototype](https://teams.microsoft.com/l/file/48BE6A88-C680-47E8-A66F-4F7A9CD37005?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared Documents%2FGeneral%2FUser research%2F2020 Spring local experience research%2F2020.03.27 - Interview protocol for xls.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)🔒

[Research protocol for ftanf.exe deep dives](https://teams.microsoft.com/l/file/17A71D28-8DF5-4736-AB53-2F404BA21B21?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared Documents%2FGeneral%2FUser research%2F2020 Spring local experience research%2F2020.04.27 - Interview protocol for executable users.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)🔒

In our interview protocol, we asked about their work, and then walked through two prototypes:

- A [Section 3 Excel spreadsheet prototype](https://teams.microsoft.com/l/file/972DF490-7C3B-49F1-B086-890C4F8B0E6C?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=xlsx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared Documents%2FGeneral%2FUser research%2F2020 Spring local experience research%2FExcel templates to test%2FFTANF Section 3.xlsx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)🔒 for entering and submitting data via excel.
- An [error page mock up based off the current web-based prototype](https://gsa.invisionapp.com/share/Y5WTQ1XK947#/413210493_tdrs2--section-1-w-errors)

One challenge to note is the tools and concepts in this space go by many names, and names often collide. We used [screenshots of past TDRS tools](https://gsa.invisionapp.com/share/Z4WU7KJAGXM#/screens/412744738_Legacy-Screenshots) to help guide conversation. Here’s how we defined certain terms and the other names they can go by:

- **The TANF Data Reporting System (TDRS)** is the system used to collect, store and access TANF data from STTs.
- **The TDRS extranet** was a website where STTs could submit Section 3 aggregate data and Section 4 stratum reports through a web form. The TDRS extranet also allowed STTs and regional program specialists to view the data that had been accepted into the OFA system. The extranet is no longer available.
  - Other names: “TDRS”, “the extranet”
- **The flat file** refers to data formatted according to the special file format currently accepted by TDRS. This is a txt file format that is not human readable, and required data to be in a specific character order. [More detail is available on the ACF website.](https://www.acf.hhs.gov/ofa/resource/tanfedit/index#transmission-file-header)
  - Other names: “fTANF files”, “the fTANF format”, “txt files”, “file layouts”, “transmission files”.
- **fTANF.exe** is a desktop application that STTs could download to prepare flat data files that could then be exported and submitted to OFA. fTANF.exe can prepare all sections of data, and data could be entered by importing a flat file or manually inputting values. The application is no longer supported and doesn’t work on newer versions of Windows, but many STTs still use it on older machines.
  - Other names: “fTANF”, “the executables”, “the grid”
- **Data reports** refer to the type of data STTs submit to OFA. [There are four types of data reports](https://www.acf.hhs.gov/ofa/resource/tanfedit/index#transmission-file-header) that STTs can submit. When sending universal data, STTs submit Section 1, 2, and 3 data reports based on the entire case load. When sending sampled data, states and territories submit Section 1 and 2 data reports based on sampled cases, Section 3 based on the entire case load, and Section 4 to report the stratum counts. About half of states and territories submit sampled data.
  - Other names: OFA staff typically refer to specific data reports by their section number (Section 1, Section 3), while some STTs often use other terms (Disagg, actives, negatives).

# What we learned

Raw notes from interviews were synthesized in Mural with the OFA data division. Then we distilled our learning further into the insights below.

**About the data submission process**

- [There isn’t shared language between OFA and STTs on TANF data concepts and tools](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#there-isnt-shared-language-between-ofa-and-stts-on-tanf-data-concepts-and-tools)
- [Data submitters often have years of TANF reporting experience and manage other mandated reports and data requests](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#data-submitters-often-have-years-of-tanf-reporting-experience-and-manage-other-mandated-reports-and-data-requests)
- [Creating flat files in fTANF is a time-consuming, “moody” process, but there’s also anxiety about changing something established and well-known.](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#creating-flat-files-in-ftanf-is-a-time-consuming-moody-process-but-theres-also-anxiety-about-changing-something-established-and-well-known)
- [It can take multiple data sources to create a complete data submission.](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#it-can-take-multiple-data-sources-to-create-a-complete-data-submission)
- [Getting data to OFA can be a collaborative effort between many people](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#getting-data-to-ofa-can-be-a-collaborative-effort-between-many-people)
- [Creating “a perfect file” is really hard; Data submitters have to resolve downstream data errors, meet TDRS formatting requirements, and wait a long time for feedback.](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#creating-a-perfect-file-is-really-hard-data-submitters-have-to-resolve-downstream-data-errors-meet-tdrs-formatting-requirements-and-wait-a-long-time-for-feedback)
- [It’s hard to confirm when and what data has been transmitted, and data submitters need that information.](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#its-hard-to-confirm-when-and-what-data-has-been-transmitted-and-data-submitters-need-that-information)
- [Covid-19 means adapting to new processes and distractions.](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#covid-19-means-adapting-to-new-processes-and-distractions)
- [Data submitters do a mix of importing and manual entry to build flat files, depending on the section](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#data-submitters-do-a-mix-of-importing-and-manual-entry-to-build-flat-files-depending-on-the-section)
- [The TDRS extranet is really missed, especially how it provided a way to submit data and view past data to confirm status](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#the-tdrs-extranet-is-really-missed-especially-how-it-provided-a-way-to-submit-data-and-view-past-data-to-confirm-status)

**About the prototypes**

- [The XLS template could be a stop-gap for Sections 3 and 4, but submitters are skeptical about Sections 1 and 2.](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#the-xls-template-could-be-a-stop-gap-for-sections-3-and-4-but-submitters-are-skeptical-about-sections-1-and-2)
- [There were unfamiliar fields and layouts in the XLS template](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#there-were-unfamiliar-fields-and-layouts-in-the-xls-template)
- [Seeing why errors happen and getting training on data rules is appreciated, but more detail is needed on where errors are happening](https://github.com/HHS/TANF-app/wiki/2020,-Spring:-Understanding-the-local-experience#seeing-why-errors-happen-and-getting-training-on-data-rules-is-appreciated-but-more-detail-is-needed-on-where-errors-are-happening)

**Resulting artifacts**

- We updated [our stakeholder map](https://github.com/HHS/TANF-app/wiki/Product-Strategy#project-stakeholders) and [user personas](https://github.com/HHS/TANF-app/wiki/User-types).
- We [created an updated process map](https://github.com/HHS/TANF-app/wiki/current-tdrs-system) to show how STTs submit data to OFA.
- Research findings contributed to [our roadmap and initial backlog](https://github.com/HHS/TANF-app/wiki/Roadmap-and-backlog).

## About the data submission process

### There isn’t shared language between OFA and STTs on TANF data concepts and tools

Within OFA, data reports are often referred to by their section number (Section 1 vs Section 3, for example). When talking with STTs, we heard different language being used, such as:

- Active, negative and aggregate.
- Active, new approvals, and cancelled cases
- Participant talks about "disagg" report
- Participant used words Section 1, 2, 3 and 4, which is the same language used by OFA staff.

As noted above, the tools used to submit data are called different things by different people. fTANF.exe was sometimes called fTANF, and also an “executable” or as one participant called it “the grid.” The TDRS extranet was generally referred to as TDRS.

**Project impacts**

- Context for future user research on describing tools
- Context for future name of the system
- Context for how a future system could describe different TANF reports, and the importance of using consistent language across tools and communications.
- Clearly name and label future tools, screens, and reports

------

### Data submitters often have years of TANF reporting experience and manage other mandated reports and data requests.

We spoke to many folks who’ve managed their state, tribe, or territory’s TANF report for years—in a few cases, decades. One participant mentioned they had 25+ years of experience.

Most data submitters also managed other mandated reports and internal data requests.

- “I do federal and annual reports to make sure data is accurate.”
- “I’m mostly responsible for handling sampling estimates for TANF and [the state SNAP program]. Developing estimates to ACF, monitoring the samples, hitting minimum sample requirements. I do the same for [the state SNAP program].”
- “Sometimes I’ll get ad hoc requests for analysis. [For example] Why is there a sudden increase in cases?”
- “Most [of our] work is audit work. Internal and external auditors gathering info, helping, answering questions, findings, corrective actions...we [also] get data requests from all kinds of people, could come from the governor, press, other parts of our agency, colleagues, FOIA requesters—the more of those I can answer internally using my own staff, the better”.

But, some are also balancing non-data responsibilities, like administration and program implementation.

- “I do payroll for the bureau, I [also] work on 2 or 3 contracts with data sharing agreements, and that takes up a lot of time.”
- “I offer training to all of our staff. Even the forms, policies and procedures...I figure out what we need to know and figure out [how it] can be included in the form.”

**Project impacts**

- Not everyone has the same balance of work. This should be considered when developing role-based permissions and user types in a new app.
- Be considerate of what else is competing for their time, and how TDRS compares to their other reporting experiences

------

### Creating flat files in fTANF is a time-consuming, “moody” process, but there’s also anxiety about changing something established and well-known.

Many data submitters described a time-consuming and finicky process to create flat files in fTANF, and expressed frustration with the current state.

- “It’s a very moody process. It's a 6-7 page long instruction [manual].” Participant describing how they move data from their central database through fTANF
- “[We] used to go into the website and enter a password and transfer the numbers. Now we have to create a flat file and it’s taking too much time...If I leave this job it would be too much work for a new person”
- “I wouldn't change much about aggregate or stratum, what I would like to change is the TANF sampling process. [It’s] really complicated, time consuming. My staff enters data on 270 cases. Each month… [It’s] cumbersome to make that whole report more successful and streamlined.”

But, data submitters also own the process for their team, and they know it well. At times there was anxiety about how the system might change in the future, and if they’d be able to use or trust a new system.

- “I tried to put it [ftanf] on my laptop, but I couldn’t find the disk and now I’m just using my tower, and I’m protecting the tower...I can actually do ftanf and I’m not a computer person”
- “I like the way we’re doing it because I can trust the data.”
- When showing them the XLS prototype: “Are you saying you are changing the format again?”

**Project impacts**

- Change should be messaged carefully and be respectful of the work they’ve put into the current system. Training for the new system could consider bridges from the old tools.
- Adds support for a piecemeal, rolling approach, and that supporting parallel systems could help build trust with data submitters.

------

### It can take multiple data sources to create a complete data submission.

For the people we spoke to, TANF data reporting isn’t directly migrating data from one system to OFA. Some data submitters described how they have to augment data from one source with data from another, and often update values manually.

- “They are required to work and income is not included [in the excel sheet provided by the programmer] so they need to have an income sheet..It does not appear since getting our new system...It takes a few days to look at the income and SSI information to help me. Other people help get that information too.”
- The participant describes what they have to update in fTANF after importing their file from the case management system. The participant mentions that education is always wrong because it isn't collected.
- Participant describes the progress of collecting data from counties for the Section 3 aggregate report. They have an Excel workbook with 20-25 sheets where they collect data from 3-4 sources (ex: birth data). Data is provided by research specialists, and takes about two weeks to collect. The participant then imports the data for submission.

**Project impacts**

- Consider how manual data entry and correction will be supported in a new system.
- For future research: can any STTs pull from just one system and get what they need to send to TDRS? Are there lessons that can be learned from those systems that we can incorporate into the new system, or share with other STTs?

------

### Getting data to OFA can be a collaborative effort between many people

The number of people who participate in TANF data reporting varies by locality. In some instances, a single person manages the data migration, preparation and transmission process for all TANF reports.

But, teams can also spread these functions across multiple people. Sometimes, data submission is outsourced to another person or team.

- “We get [the] aggregate report from another section. Sent to me and my colleague. We go into TDRS and input that directly. Now, with executables...we key in info and then export out flat file. A little bit of editing. We send it to our IT department, they transfer via SFTP to somewhere at ACF.”
- “At the end of the quarter, I will send three months worth of cases and send it to [my boss] and [my boss] sends it to you guys.”

We also saw that some teams collaborate in fTANF to create files:

- The participant walks through their process of using fTANF. Mentions that when they go into fTANF... “everything is pre-populated. The programmer does that.”
- Participant describes how they collaborate with teammates in fTANF. “One person working on it at a time [in fTANF]. We’ve got prelim data at the 45 day deadline so if they’re entering their data at 45 day and I’m doing 90 day one, I don’t have their info so I have to create a new screen as opposed to editing the old file.”
- We also observed that different teams could be responsible for different sections of data, even though the data sections rely on one another. For example, one person may be responsible for Section 3 reports, while another for Section 4.

**Project impacts**

- Informs how many users we may need to allow into a new system and the permissioning of those teams
- Users from the same locality may need to see each other’s work.

------

### Creating “a perfect file” is really hard; Data submitters have to resolve downstream data errors, meet TDRS formatting requirements, and wait a long time for feedback.

Data submitters are cleaning their data on many fronts. The raw data they get is sometimes incomplete or includes downstream data quality issues that need correction.

- “[I] always have the education wrong because [it] doesn’t collect. Then change the month. Then change the hours because case managers document it incorrectly.” Participant describing edits after importing file into fTANF
- “I usually find a two digit year which means it was closed 2000 years ago, then I have to do another training. It's happened a lot less since our DB was updated because now they have to open up a calendar.”
- “If it is a cash case or receiving SSI, I have to code that. Sometimes race is not correct, [also check] SSI or SSA, working and how many hours and meeting participation, and fill in the type of employment. Check if the child's race is accurate. That is about it. It takes about 30 seconds to enter each case...Case by case basis. One at a time.”

While fTANF provides some helpful validation checks, as one participant said “mistakes are easy to make”. It can take a long time to learn of issues, and there’s a desire for more immediate feedback:

- “I would like it to catch more things when I enter them. Like if there is no TANF tell me now or if I fail to put in the SS $ amount I would like to know now.”
- When asked what they would change about the process, one participant asked for “real time feedback if I make an error on a case so I can correct it then... knowing what errors I was making so that I could make you a perfect file.”
- One participant described how they may have sent data accidentally coded for FY2021, but that they aren’t sure if that error was in the file that was submitted because it isn’t a readable format.

**Project impacts**

- +1 for manual entry and editing interface.
- Consider what it would look like if a user provides an incomplete data file.
- Consider ways we can provide more real-time feedback in the new system.

------

### It’s hard to confirm when and what data has been transmitted, and data submitters need that information.

Data submitters often need to verify the status of their transmission, but aren’t able to do so.

- “I never received something that I got back that [said] you’ve received your transmission. I need that for my auditor. Otherwise, I'm invisible to my office, until we get a notice that says we're getting a penalty.”
- “[It] would be nice to look to see what info you have for that specific quarter because we’re always sending updates and I don’t always know which updates were sent...Maybe IT put in wrong info and you have something totally wrong in the system. It’s not until [OFA data team member] sends the monthly feedback reports that we can check and see if you have the right info or not. [It would be] good to check at our own leisure”.

OFA regional program specialists also need this information to help their grantees. As one regional program specialist said:

- “I can’t tell what they submit... Before I didn’t have any idea if they submitted unless [OFA data team member] said there was a problem... Now, when they submit data, they have to send a screenshot to me and [OFA data team members] to show they submitted.”

Confirmation emails are (sometimes) sent by the current system, but not consistently. [One participant outlined the information they felt was missing from these emails](https://teams.microsoft.com/l/file/A28971F9-2CD3-4B78-9037-3C4CF6340E2A?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared Documents%2FGeneral%2FUser research%2F2020 Spring local experience research%2FSTT artifacts%2FUltramarine_ Post interview feedback email to research team.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)🔒, including:

- An easy way to know which accepted and for which calendar quarter. This is currently stated in the body of the email, rather than the subject.
- The date the file was transmitted to ACF. Currently the email reports when the file was accepted into ACF’s database.
- A way to see what data was accepted to the system

**Project impacts**

- Consider how data transmission confirmation could be sharable within TDRS (like grantee <> regional program specialist) and outside of TDRS (like grantee <> auditor)
- Consider how grantees can access and view prior data submissions
- Information for a future confirmation message

------

### Covid-19 means adapting to new processes and distractions.

We asked about how Covid-19 had impacted their TANF data submission process. Some of the impacts we heard about included:

- Having to come into the office to complete data submissions: for example one reported they have to go into the office to access network systems, another comes in to access paper records.
- “Everything is just taking longer.”
- Making the transition from paper records to digital records.
- Adjusting to working from home. “People staring at you in your office. With family and kids.”
- The emotional impact. Hearing about the changes within the office and “people who worked for me for years who passed away.”

**Project impacts**

- Context for future user research and usability testing—observation may be tough, and it’s a distracting environment.
- Consider the guidance OFA must give to STTs during epidemic about policy-based changes to submission process and how those messages may get entangled with messages about migration to new system

------

### Data submitters do a mix of importing and manual entry to build flat files, depending on the section

Most of our fTANF users mentioned that they or someone else on their team imported data into fTANF. This was especially common when discussing how they manage sampled case-level data, which at a minimum is ~250 entries for active cases and 67 for closed cases.

- When walking through their process with ftanf: “Everything is pre-populated. The programmer does that.”
- The participant [shared a cheat sheet](https://teams.microsoft.com/l/file/90E9A24D-E510-44A9-8182-D6723D16EBC4?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=pdf&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared Documents%2FGeneral%2FUser research%2F2020 Spring local experience research%2FSTT artifacts%2FCerulean - Steps for Transmission to ACF_20140212.pdf&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)🔒 provided by their vendor on how to move data from their case management system to fTANF. The vendor provides a program that the participant runs to migrate the data from the case management system to fTANF.
- The participant shared a screenshot of the file they export from their case management system and import into fTANF. The file is in the fTANF txt format.
- When submitting simpler data reports, like the Section 3 aggregate report, data submitters may just copy over or key-in the values. Some data submitters shared that they use Excel workbooks to track their Section 3 aggregate data and Section 4 stratum data, and would copy from these files into the TDRS extranet or fTANF.

**Project impacts**

- Many users still rely on importing data into the system, so consider how a new system would support imports of the older txt format.
- +1 to allowing manual data entry in a new system, especially for Section 3 and 4 (which are shorter and mostly aggregate data.)
- Consider how a new system could interact with users’ own internal Excel worksheets and processes.

------

### The TDRS extranet is really missed, especially how it provided a way to submit data and view past data to confirm status

We heard a lot of nostalgia for the TDRS extranet, especially how it would let data submitters manually input data and also see their past submissions.

- When describing their experience using the TDRS extranet: “That aggregate and stratum reports are two of the simplest reporting I do!”
- “If you are moving to a new system, something like TDRS was very useful. A whole lot easier for Sections 3 and 4 since it was very little info. Just high level counts....Obviously [there were] hiccups with the old system...But overall very easy and [I] could pull up old data. With executables feels kind of disjointed, removed from the system...I don’t know if the correct data is getting to you guys.”
- When looking at the TDRS screenshot “That is my favorite, because it gave me the trend. I found that something is not getting reported properly. Easy to catch things that were off. Because have [that] graphic…”

**Project impacts**

- +1 to visibility into what they are submitting and it’s status
- Context for a future design team on what has worked for users in the past.

## About the prototypes

### The XLS template could be a stop-gap for Sections 3 and 4, but submitters are skeptical about Sections 1 and 2.

Some participants felt ok with the idea of using a template like the Section 3 XLS template to submit TANF data:

- “If it's Excel like this, I might be able to figure out internally how to actually upload my data-pull right into this file and avoid typos. I would be all for making a change to this, yeah.”
- When asked if they would use this for Sections 3 and 4 “that would be easy”

However, for participants who handled Sections 1 and 2 data, they expressed concern that it would be more work for them and not compatible with the tools they use now:

- “I’m very concerned about the active cases and don’t want to have to enter that for 275 cases...Depending on how many people in the household, would have to enter a lot of data... I’m just looking how I have to enter less data.”
- “I’d have to have file that I can read because [what they use now] comes as a text file, this would have more errors, it would tell me wrong numbers”
- It’s more work than what I already do. I’d have to write a report and then go in and type it in... could easily do it but the system I have is much less work.
- There were also concerns about sending Sections 1 and 2 via email, as that includes more PII (Personally Identifiable Information). One participant mentioned that they were concerned about keeping the data safe, and that they’re unable to receive zip files in their email.

**Project impacts**

- Consideration for how far we take an XLS stop-gap. Testing Sections 3 and 4 with blocked STTs seems appropriate, but Sections 1 and 2 would be a significant lift for data submitters.

------

### There were unfamiliar fields and layouts in the XLS template

Fields in the header section weren’t familiar to some users, and one suggested that this data may have been prefilled in the past. As one participant with over 25+ years of experience said

- “I don’t know what data type under the header. I don’t know where the header is...I don’t know what FIPP is or what my code is either...I’ve never heard of overlay existing data.”

A number of participants mentioned that layouts similar to the tools they’re already familiar with might be easier to read and follow. Particularly, moving more values to rows rather than columns:

- “It might be easier if it was not columns but rows, this side months and columns, that would be more to how I see in ftanf, but I can change.”
- “Looks like the same data in [the] regular TDRS interface but formatted differently...It looks like I enter in Excel left to right instead of up and down”

And, providing simpler labels and distinction between sections so that it is easier to scan and read.

- “It’s hard to read because it’s all one string. I would recommend boxes/borders around certain sections here.”
- “The text in row 11 needs to be condensed so not so crowded. Don’t need to see the word “item”. Kinda crowded with text.”

**Project impacts**

- Possible layout updates to the XLS template. Note that this would require adjustments to the converter script.
- Design considerations for a future UI.
- Consider what header fields we actually need from the data submitter and which can be filled in by a default value or by OFA. For essential values, consider plain language labels to explain new concepts that are visible to data submitters.

------

### Seeing why errors happen and getting training on data rules is appreciated, but more detail is needed on where errors are happening

Data submitters responded positively to having more descriptive error messages and thought they may be useful for new folks.

- “I wouldn’t need “what it means”...it might be helpful for people just starting, I know when I first started I was kind of in that boat...not sure what it meant”
- “This is good because it’s telling the analyst where it’s gone wrong. That’s an excellent thing.”

In discussing error troubleshooting, we also discussed new staff training. Current OFA resources are often used in data submitters internal training, and additional training from OFA could be useful.

- When discussing how they use OFA instructions when training new staff “That’s what I print them, and that’s their bible.”
- “When all said and done, it would be helpful to have training for grantees and regional staff. Something to refer to and something to walk through. If this comes up, first look at what you put in. Helpful to walk through it! Maybe recorded so when new staff comes on board. Always there and available.”

But, most participants wanted a way to know where the error was occuring—for example what row or case.

- “[It’s] helpful to know what specific value was submitted and what is acceptable. If it’s like a million records that’s obviously a problem.”
- “If comes back that specific, gender incorrect, as long as it tell us which case it was for then they could correct pretty quickly, but doesn’t show what actual case it was on”

**Project impacts**

- Design consideration for a future UI: How do we show where an error is happening in the file, and keep error handling manageable when reviewing very large data sets.
- Consider what sort of data training OFA could offer in the future, and how OFA resources can be integrated into a future TDRS.