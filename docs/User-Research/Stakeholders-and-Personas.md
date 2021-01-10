# Stakeholder Types

<img src="https://goraft.tech/assets/logo.png" width="15%" height="auto" alt="Raft LLC Logo">

Last updated for [Issue #371](https://github.com/raft-tech/TANF-app/issues/371)

---

**Table of Contents:**

- [Background](#background)
- [Grantee-level Stakeholders](#grantee-level-stakeholders)
- [ACF Stakeholders](#acf-stakeholders)
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

### Data Preppers

Data Preppers are staffers who collect TANF data and get it ready for submission to OFA. This process can range from manually following OFA data coding instructions to utilizing a software tool to automate some of that work.

A number of factors affect what that process looks like including:

- If TANF is administered by counties or the state/tribe/territory
- If they have an integrated eligibility system, or other software tools that aid in data management / TANF data prepping
- Other details of software tools that impact who can interact with them and what they can be used for. e.g. Some systems allow data preppers to generate flat files themselves directly from a case management system. Others require more assembly or more cross-functional collaboration with technical staff

**In-house Data Preppers**

In-house Data Preppers may be the only person who works on reporting and have competing responsibilities like program management or administrative duties. Or, they could work on a team where there are multiple data preppers to help with reporting.

There are a number of factors that affect the experience of a STT data prepper and the specific actions required of them including:

- If they're a tribal grantee
- If they submit sample or universe data
- Team size and availability of technical resources
- Whether a Managed File Transfer (MFT) solution such as TIBCO (Cyberfusion) is used to transmit data.

**Third-party Data Preppers**

We suspect that some STTs hire third party teams that manage their TANF data transmission for them. Some third party contractors playing a much more hands-on role in coding the data as well as transferring it. More research is needed in this area. 



### Third-party analysts

In Round 3 research we encountered a data prepper working at an STT with a team structure made up of contract workers as well as government employees. The participant told us that these contract workers sat on the team in the role of Business Analysts, but more research is needed to better understand the details of their role. Brief secondary research indicates that Business Analysts exist at several other STTs as well working on or alongside TANF programs.

**Supporting Documentation**

- Example job postings for TANF-related Business Analysts ([Example 1](https://agency.governmentjobs.com/dhsgeorgia/job_bulletin.cfm?jobID=2165694&sharedWindow=0), [Example 2](https://jobs.accaglobal.com/job/7832579/medicaid-business-analyst-snap-tanf-/))



### Program directors

STT program directors manage data preppers and ensure that their STT is staffed and trained to meet federal reporting requirements. We've encountered several directors who are responsible for other programs like SNAP in addition to TANF. They are typically less involved with data collection details and formatting, but want to make sure their teams have the tools they need to get the job done. However, we have spoken to program directors of smaller teams who play a larger role in data prepping responsibilities as well.

It's important to note that "Program Director" might not be the actual title of people in this role. We've encountered a lot of variation in what those with these responsibilities are called including:

- Social Service Supervisor
- State Program administrator coordinator
- Public Assistance Program Specialist



### Technical staff

Some STTs segment data preparation and data transmission into two distinct roles. We've encountered references to (SFTP) transmission being handled by IT workers or by technical offices at the STT level who work with other STT agencies and departments, not just those dealing with TANF. Technical staff can also play a role in generating coded reports 

---

## ACF Stakeholders

### OFA analysts

OFA analysts review, analyze, and report on STT’s TANF data that’s submitted through TDRS. They also help STTs through the transmission process by offering support and guidance around data quality (including fatal/warning edits). 

**Supporting Documentation**

- [Description of the OFA support mailbox](<https://hhsgov.sharepoint.com/:w:/r/sites/TANFDataPortalOFA-UserResearch/Shared%20Documents/User%20Research/OFA%20Resource%20Mailbox%20notes.docx?d=w2542a110040b44c1b82706a54c6ec9f2&csf=1&web=1&e=O5meXQ>) :lock:



### OFA admins

OFA admins are members of the TANF Data Division. They oversee the collection and processing of TANF data and ensure OFA analysts have what they need to do their work.



### Regional program specialists

Regional program specialists are STTs primary OFA point of contact. They track TANF trends in their region and provide troubleshooting and advice to STTs.



### OPRE analysts

OPRE studies ACF programs and the populations they serve through rigorous research and evaluation projects. They use TANF data in their analyses. More research is needed in this area, especially on where duties and responsibilities overlap with OFA analysts.



### OCIO staff

OCIO staff oversees tech projects within ACF. They provide technical and security support to ACF's tech products.



---

## What's Next

An immediate next step will be synthesizing research findings and existing details about stakeholder types & attributes into full-fledged personas—fictional people based on real research findings. These personas will have names, demographic & psychographic details, and offer us a way to channel stakeholder needs, pain points, and behaviors into a format that will help drive detailed user stories as design and development continue. These personas will be living artifacts, always kept up to date with ongoing research efforts. They'll also drive the creation of more focused Journey Maps and other artifacts that help bridge the gap between the current state of TANF reporting and the ideal state we want to move toward.

**Supporting Documentation**

- [Grantee Attributes](<https://hhsgov.sharepoint.com/:x:/r/sites/TANFDataPortalOFA-UserResearch/_layouts/15/WopiFrame2.aspx?sourcedoc=%7Be83f84f1-71a0-459f-80a4-0d39bc250be9%7D&action=view&cid=f2e656cb-9245-4f02-af6d-2d7e1db6573d>) 🔒
- [Proto Journey Maps](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1608238114372/191c53b8ef538838bc8c179daa238dd5c5dcc9e8) :lock:





