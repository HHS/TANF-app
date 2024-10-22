![image](https://github.com/user-attachments/assets/97e8fbf1-954b-4f3b-9000-ecb3b0f1d0d9)![image](https://github.com/user-attachments/assets/39a7b775-2771-438f-a270-d09dc263ef3c)# Stakeholders and Personas

Last updated for [Issue #3100](https://github.com/raft-tech/TANF-app/issues/3100)

---

**Table of Contents:**

- [Background](#background)
- [Grantee-level Stakeholders](#grantee-level-stakeholders)
- [ACF Stakeholders](#acf-stakeholders)
- [Personas](#personas)

---

## Background

A number of groups and prospective stakeholder types had been identified as groups impacted by this project. Some of them interact with TDP directly, and some are impacted indirectly. The original TDP personas that were identified can be found in the personas mural linked below.

We expect that there will be a couple hundred users who interact with the TDP system, made up of both STT and OFA staff.

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

OFA analysts review, analyze, and report on STT’s TANF data that’s submitted through TDP. They also help STTs through the transmission process by offering support and guidance around data quality. 

**Supporting Documentation**

- [Description of the OFA support mailbox](<https://hhsgov.sharepoint.com/:w:/r/sites/TANFDataPortalOFA-UserResearch/Shared%20Documents/User%20Research/OFA%20Resource%20Mailbox%20notes.docx?d=w2542a110040b44c1b82706a54c6ec9f2&csf=1&web=1&e=O5meXQ>) :lock:

### OFA system admins

OFA admins are members of the TANF Data Division. They manage access requests for the TANF data portal, help troubleshoot issues with submission, and broadly ensure that OFA analysts have what they need to do their work.

### Regional program specialists

Regional program specialists are STT's primary OFA point of contact. They track TANF trends in their region and provide troubleshooting, advice, and reminders to STTs.

### OPRE analysts

The Office of Planning, Research, and Evaluation (OPRE) studies ACF programs and the populations they serve through rigorous research and evaluation projects. They use TANF data in their analyses. More research is needed in this area, especially on where duties and responsibilities overlap with OFA analysts.

### ACF OCIO Staff

Office of the Chief Information Officer (OCIO) staff oversees technology projects within ACF. They provide technical and security support to ACF's tech products. In 
respect to TDP, OCIO staff will have access to subsets of the Django Admin experience so as to be able to view logs to ensure and audit security.

---

## Personas

Research up to this point has suggested a need for three working personas: an OFA Data Analyst (Grace), an OFA System Admin (Elliott), and an STT data analyst. While these don't reflect the full diversity of  roles, responsibilities, and team makeups on both the grantee and federal levels, the "jobs to be done" for each in the context of TDP have a lot of overlap. A single persona could also have many different combinations of permissions available to them in the data portal. 

### Grace — OFA Data Portal User

| Grace                               |                                                              |
| :---------------------------------- | :----------------------------------------------------------- |
| Role                                | OFA Data Portal User                                         |
| Age                                 | 35                                                           |
| Location                            | Washington DC                                                |
| Work Environment                    | Home and Office|
| Goals<br /><br /><br />             | 1. Identify all states that have or have not transmitted data<br />2. Transform and clean data to generate reports <br />3. Produce reports including: Work participation Rate, Transmission History, Section 1v Section 3, 4 Caseload, Missing Data, Preliminary Quarterly Caseload<br />4. Publish and share reports with STTs, research partners, and colleagues within OFA<br />5. Answer STT questions<br/> 6. Work with the OFA System Admins |
| Pain Points<br /><br /><br /><br /> | 1. "It can currently take a lot of time to sort out data ready to be reported on from data that's not, and to integrate that into my reporting workflows" <br /> 2. "If data that isn't ready for reporting accidentally makes its way into that workflow then that can cause significant rework and make me have to redo the whole process" <br /> 3. "I don't have a quick way to produce certain reports to communicate to STTs" <br /> 4. "It can be difficult to identify where an error is coming from in a file"                            |
| Delights                            | 1. "With TDP, I have a lot [of data] once the State submits the data the data gets processed already so that's really good. Now  I don't need to spend too much time with state if the  data wasn't processed." <br /> 2. "Having direct and up to date access to the data in the database" |
| Tools                               | Django CSV exports, Excel, SAS, email, reporting/analytics software |


### Elliott — OFA System Admin

| Grace                               |                                                              |
| :---------------------------------- | :----------------------------------------------------------- |
| Role                                | OFA Data Portal User, Viewing and Editing Permissions        |
| Age                                 | 46                                                           |
| Location                            | USA, Occasionally In DC Office                              |
| Work Environment                    | Home and Office, Desktop, and Government Furnished Equipment (GFE) |
| Goals<br /><br /><br />             | 1. Ensure availability of features and components of the system <br />2. Work with regional OFA staff to confirm who should and shouldn't be granted access to the system<br />3. Access system logs to troubleshoot problems and remediate scans as needed <br />4. Provide access to OCIO (ACF-Tech) staff for security auditing purposes <br />5. Monitoring emails, notifications and answering STT Questions |
| Pain Points<br /><br /><br /><br /> | 1. "Django doesn't have all the filters I need to efficiently use it for certain admin tasks" <br /> 2. "The system can sometimes log me out with no warning" <br/> 3. Accessing data from cloud.gov-brokered databases is only possible by disconnecting from the HHS network on site and VPN when remote. <br/> 4. The toolstack needed as an administrator can be difficult to use on a Windows GFE <br/> 5. Requesting access to developer tools can take months at a time to get approved                           |
| Delights                            | 1. "Django has become a tool that provides me a lot of insights about data in the system rather than solely being a user administration tool" <br/> 2. "Automated notifications have been convenient [so that I am aware of what is happening]" <br/> 3. "Being able to use an interface and see what [actions] users did" <br/> 4. "A point and click experience to see how the system is performing...I use the front end the most"|
| Tools                               | TDP Portal, Django CSV exports, Excel, SAS, email, reporting/analytics software, Microsoft Suite, Python, Axe Dev Tools |
| Expectations | 1. TDP should help sys admin do things from an interface as much as possible <br /> 2. We need to have multiple ways to troubleshoot and remediate issues |

To view a further in-depth system of the interactions, primary tasks and touchpoints taken by OFA System Admins, please refer to the ecosystem map in the supporting documents below.

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
- [Ecosystem Map OFA System Admin](https://app.mural.co/t/raft2792/m/raft2792/1728311825176/74942929a28857c3ef1c401f0d07ccfe1073e882?sender=uf443e00cb4626b8bec157528) :lock:
