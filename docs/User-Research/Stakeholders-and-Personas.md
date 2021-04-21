# Stakeholder Types

<img src="https://goraft.tech/assets/logo.png" width="15%" height="auto" alt="Raft LLC Logo">

Last updated for [Issue #804](https://github.com/raft-tech/TANF-app/issues/804)

---

**Table of Contents:**

- [Background](#background)
- [Grantee-level Stakeholders](#grantee-level-stakeholders)
- [ACF Stakeholders](#acf-stakeholders)
- [Personas](#personas)
- [What's Next](#whats-next)

---

## Background

As of Summer 2020, a number of groups and prospective stakeholder types had been identified as groups impacted by this project. Some of them interact with TDRS directly, and some are impacted indirectly. The original TDRS personas that were identified can be found in the personas mural linked below.

We expect that there will be a couple hundred users who interact with the TDRS system, made up of both STT and OFA staff.

For the purposes of the OFA MVP, the only users who will have access to the application will be OFA Admin and STT (test) users.  Raft team or OFA will be acting as STT users for the OFA MVP.

**Supporting Documentation**

- [Personas mural](https://app.mural.co/t/officeoffamilyassistance2744/m/gsa6/1592254280716/2ae8293a3233a95941d548cda4f373faab96b40b) :lock:
- [Vision and Stakeholders Doc](https://github.com/HHS/TANF-app/blob/main/docs/Product-Strategy/Vision-and-Stakeholders.md)

---

## Grantee-level Stakeholders

### Data analysts

Data analysts are staffers who collect TANF data and get it ready for submission to OFA. This process can range from manually following OFA data coding instructions to utilizing a software tool to automate some of that work.

A number of factors affect what that process looks like including:

- If TANF is administered by counties or the state/tribe/territory
- If they have an integrated eligibility system, or other software tools that aid in data management / TANF data preparation
- Other details of software tools that impact who can interact with them and what they can be used for. e.g. Some systems allow analysts to generate flat files themselves directly from a case management system. Others require more assembly or more cross-functional collaboration with technical staff

**In-house Data Analysts**

In-house Data Analysts may be the only person who works on reporting and have competing responsibilities like program management or administrative duties. Or, they could work on a team where there are multiple data people to help with reporting.

There are a number of factors that affect the experience of an analyst and the specific actions required of them including:

- If they're a tribal grantee
- If they submit sample or universe data
- Team size and availability of technical resources
- Whether a Managed File Transfer (MFT) solution such as TIBCO (Cyberfusion) is used to transmit data.

**Third-party Data Analysts**

We also suspect that some grantees hire third party teams that manage their TANF data transmission for them. Some third party contractors playing a much more hands-on role in coding the data as well as transferring it. More research is needed in this area. 

### Third-party Business Analysts

In Round 3 research one participant spoke to working as part of a team made up of contract workers in addition to government employees. The participant told us that these contract workers sat on the team in the role of Business Analysts but more research is needed to better understand the details of their role. Brief secondary research indicates that Business Analysts exist at several other grantees as well; working on or alongside TANF programs.

**Supporting Documentation**

- Example job postings for TANF-related Business Analysts ([Example 1](https://agency.governmentjobs.com/dhsgeorgia/job_bulletin.cfm?jobID=2165694&sharedWindow=0), [Example 2](https://jobs.accaglobal.com/job/7832579/medicaid-business-analyst-snap-tanf-/))

### Program directors

Grantee program directors oversee data analysts and ensure that their STT is staffed and trained to meet federal reporting requirements. We've encountered several directors who are responsible for other programs like SNAP in addition to TANF. They are typically less involved with data collection details and formatting, but want to make sure their teams have the tools they need to get the job done. However, we have spoken to program directors of smaller teams who play a larger role in data preparation and transmission as well or step into that role when analysts are out of the office.

It's important to note that "Program Director" might not be the actual title of people in this role. We've encountered a lot of variation in what those with these responsibilities are called including:

- Social Service Supervisor
- State Program administrator coordinator
- Public Assistance Program Specialist
- Compliance Officer

### Technical staff

Some grantees segment data preparation and data transmission into two distinct roles. We've encountered references to (SFTP) transmission being handled by IT workers or by technical offices at the grantee level who work with other agencies and departments, not just those dealing with TANF. Technical staff can also play a role in generating coded reports.

---

## ACF Stakeholders

### OFA analysts

OFA analysts review, analyze, and report on STT’s TANF data that’s submitted through TDRS. They also help STTs through the transmission process by offering support and guidance around data quality (including fatal/warning edits). Analysts in the Tribal TANF Division also play a direct role communicating submission status, resubmission requests, and various reports to Tribes. 

**Supporting Documentation**

- [Description of the OFA support mailbox](<https://hhsgov.sharepoint.com/:w:/r/sites/TANFDataPortalOFA-UserResearch/Shared%20Documents/User%20Research/OFA%20Resource%20Mailbox%20notes.docx?d=w2542a110040b44c1b82706a54c6ec9f2&csf=1&web=1&e=O5meXQ>) :lock:

### OFA admins

OFA admins are members of the TANF Data Division. They oversee the collection and processing of TANF data and ensure OFA analysts have what they need to do their work.

### Regional program specialists

Regional program specialists are grantee's primary OFA point of contact. They track TANF trends in their region and provide troubleshooting, advice, and reminders to STTs.

### OPRE analysts

The Office of Planning, Research, and Evaluation (OPRE) studies ACF programs and the populations they serve through rigorous research and evaluation projects. They use TANF data in their analyses. More research is needed in this area, especially on where duties and responsibilities overlap with OFA analysts.

### OCIO staff

Office of the Chief Information Officer (OCIO) staff oversees technology projects within ACF. They provide technical and security support to ACF's tech products.

---

## Personas

Research up to this point has suggested a need for two working personas; an OFA Data Portal User (Grace) and a grantee-side persona. While there's no shortage of variety in roles, responsibilities, and team makeups on both the grantee and federal levels, the "jobs to be done" for each in the TANF Data Portal are shared. A single persona could also have many different combinations of permissions available to them in the data portal. e.g. While the OFA Persona represents all tasks that an OFA user might want to complete, some may only be assigned to some subset of those tasks. 

### Grace — OFA Data Portal User

| Grace                               |                                                              |
| :---------------------------------- | :----------------------------------------------------------- |
| Role                                | OFA Data Portal User                                         |
| Age                                 | 35                                                           |
| Location                            | Washington DC                                                |
| Work Environment                    | Office                                                       |
| Goals<br /><br /><br />             | 1. I've identified all states that have or have not transmitted data<br />2. I've identified any outstanding errors in submitted data<br />3. I'm able to contact grantees and facilitate corrections and resubmissions<br />4. I've enabled grantees to fix errors without communication from OFA<br />5. The final TANF data is completely submitted and error free |
| Pain Points<br /><br /><br /><br /> | 1. Transmission reports can be confusing and aren't actionable enough<br />2. Current errors aren't easy to understand and act to fix, nor easy to explain to grantees<br />3. It can be difficult to identify where an error is coming from in a file<br />4. I see submitted data differently (in different systems) than the grantee submitting it does—The lack of a shared place to view data complicates communication.<br /><br /> |
| Delights                            | 1. We send out WPR reports far faster than we used to        |
| Tools                               | OCIO database, scripts to interact with or query the database, email, reporting/analytics software, excel, fTANF.exe |

### Awinita — Grantee Data Analyst

| Awinita                 |                                                              |
| :---------------------- | :----------------------------------------------------------- |
| Role                    | STT Data Analyst                                             |
| Age                     | 37                                                           |
| Location                | Window Rock, AZ                                              |
| Work Environment        | Office                                                       |
| Goals<br /><br />       | 1. Cases kept up to date and accurate<br />2. My WPR calculations match those of ACF<br />3. I'm able to submit data in a timely manner<br />4. The data I submit is error free |
| Pain Points<br /><br /> | 1. I have concerns about security when I submit files via email (Tribe pain point)<br />2. Errors can be difficult to understand, track down, and correct<br />3. I don't always hear back about the status of my submission in as timely a way as I'd like to.<br /> |
| Delights<br />          | 1. I appreciate receiving WPR reports from ACF faster than I used to in the past<br />2. Higher data quality let's me make better policy recommendations<br />3. My [software tool] is great at identifying errors before I submit data for a quarter |
| Tools                   | Integrated Eligibility System (IES) or other Case Management Software, email, reporting/analytics software, excel, fTANF.exe |

**Supporting Documentation**

- [Grantee Attributes](<https://hhsgov.sharepoint.com/:x:/r/sites/TANFDataPortalOFA-UserResearch/_layouts/15/WopiFrame2.aspx?sourcedoc=%7Be83f84f1-71a0-459f-80a4-0d39bc250be9%7D&action=view&cid=f2e656cb-9245-4f02-af6d-2d7e1db6573d>) :lock:
- [Working Journey Maps & Personas Mural](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1608238114372/191c53b8ef538838bc8c179daa238dd5c5dcc9e8) :lock:

---

## What's Next

Personas and their associated journey maps will continue to be kept up to date with our most recent research findings. Future research insights or updates to the roadmap may also suggest a need for additional personas. For instance, if we discover that grantee program directors can and want to play a role in administering their own teams within the data portal it may prove useful to divide the grantee persona into two; covering grantee staff with and without administrative duties respectively. 

In the shorter term, we plan to:

- [Issue #841](https://github.com/raft-tech/TANF-app/issues/841) Likely a priority for Round 6 research. Evaluates functionality for regional specialists and identifies any functionality gaps needed to allow them to support the first grantee-facing data portal release. Additional detail regarding the approach to this research will be added as part of the Round 6 planning sprint.
- [Issue #840](https://github.com/raft-tech/TANF-app/issues/840) Validate whether grantee program directors can/will take on admin responsibilities in the data portal in respect to managing their own teams.
