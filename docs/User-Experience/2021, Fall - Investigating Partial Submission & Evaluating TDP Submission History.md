# 2021, Fall - Investigating Partial Submission & Evaluating TDP Submission History

Research Round 8 - [Issue #1269](https://github.com/raft-tech/TANF-app/issues/1269)

---

**Table of Contents:**

- [Who we talked to](#who-we-talked-to)
- [What we did](#what-we-did)
- [What we tested](#what-we-tested)
- [What we learned](#what-we-learned)
- [What's next](#whats-next)

---

## Who we talked to

Round 8 research included participants representing: 

- Seven OFA Data Analysts/Regional Staff
- Ten grantee participants across three states—who had either submitted partial data in the past year or ranked in the top 25 for submission volume per quarter—and two Tribes. These participants included:
  - 6 grantee data analysts.
  - 2 grantee program directors.
  - 2 grantee staffers who interact with TANF data from other policy/data analysis-oriented roles.

---

## What we did

### OFA Workshops

**Objectives / Insight Areas**

- Generate attributes which could summarize a particular submission of any given section of TANF data (e.g. Submission status, number of rejected records, number of errors, etc...).
- Prioritize and sort which attributes should be displayed at the top level of submission history pages in TDP. 
- Capture the minimum viable set of attributes needed for Submission History to deliver value and enable user action.
- Assure the quality and realism of example data in Submission History mockups. 

### Grantee Sessions

**Objectives / Insight Areas**

- Split test a version A and B of Submission history pages to determine grantee preferences & the minimum set of attributes needed on the page to deliver value and enable action.
- Seek an informed answer to whether the removal of partial submissions would be disruptive for grantees
- Evaluate whether data statuses (Accepted, Accepted with Errors, and Rejected) are accurately interpreted by grantees.

### Project Impact Workshop

**Objectives / Insight Areas:**

- Align team on newly validated user stories and proposed project impact opportunities. 
- Contextualize project impacts via elaboration on the research findings supporting them.
- Channel project impacts into backlog tickets as appropriate.
- Identify any other actionable next steps and vote on their priority.

**Supporting Documentation:**

- [Research Plan](https://jstrieb.github.io/link-lock/#eyJ2IjoiMC4wLjEiLCJlIjoiUTVwckZFNHljNWc4Mkh2VzJCZDVNalpOamRQQzlYQ016NG1vUTdFSWZqY0pmRTdWcDFRZU10MTVFUXVjSGMvSEM5QXpDU3l0R0RzPSIsImkiOiJJMmY0WVpsYjJrRFNRL0VTIn0=) :lock:
- [Project Impact Workshop Board](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1642104988898/fa7e873790876ee1ac96977fe1e51acc2b7e35b9?sender=laurenfrohlich3146) :lock:
- [Topline Research Synthesis Mural](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1642104940177/3c4ec6a79bda5b6045f43ff4093e78eb5135f332?sender=laurenfrohlich3146) :lock:


---

## What we tested 

The evaluative part of this round of research included two levels of testing

1. Testing two versions of the proposed Submission History page designs 
2. Testing the content for acceptance status messages

**Split testing of design mockups**
We tested two versions of TDP's Submission History page mockups to understand OFA regional staff's and grantees' minimum requirements for file information that they need to see from resubmitted files. 

The data reflected in these mockup versions are displayed in a table format, and were derived after extensive discussion with OFA data analysts who work with TANF data. 

Both versions of the file have basic information which includes:

- Name of file
- Date and time of submission 
- Acceptance Status 
- Error Reports
- Cases accepted, rejected and total

The versions differ in the salient details of the data displayed in the submission history table. While **Version B** provides only case details, **Version A** also displays **rejected records sorted by family, adult and child records**. 

**Content testing of status messages**
Each file that a grantee transmits to the OFA also will be attached to an 'acceptance status' - conveying whether data in a file passed the necessary quality checks and is ready to be accepted.  

**Three Status Messages**

| Status Message       | What it should convey to grantees                            |
| -------------------- | ------------------------------------------------------------ |
| Accepted             | a file has no errors, meets reporting requirements and is accepted into the database |
| Accepted with Errors | a file meets reporting requirements, but has errors that need to be addressed |
| Rejected             | a file did not pass data quality checks and is rejected      |


  We tested the status messaging content with grantees to discover if the right meaning is conveyed 

**Supporting Documentation:**

- [Version A PDF](https://github.com/raft-tech/TANF-app/files/7859592/Submission.History.STT.View.Variation.1.pdf)
- [Version B PDF](https://github.com/raft-tech/TANF-app/files/7859591/Submision.History.STT.View.Variation.2.pdf)



---

## What we learned

**Jump to:**

- [All participants had a good idea of what to expect from the error reports referenced in Version A & B](#all-participants-had-a-good-idea-of-what-to-expect-from-the-error-reports-referenced-in-version-a-b)
- [Seeing who submitted a given file could be an important data point for grantees with multiple data analysts](#seeing-who-submitted-a-given-file-could-be-an-important-data-point-for-grantees-with-multiple-data-analysts)
- [Making minor changes to practical guidance for errors occurring due to external constraints would be helpful in reducing resubmissions](#making-minor-changes-to-practical-guidance-for-errors-occurring-due-to-external-constraints-would-be-helpful-in-reducing-resubmissions)
- [Having access to historical error patterns may help grantees make adjustments to their process that prevent future errors](#having-access-to-historical-error-patterns-may-help-grantees-make-adjustments-to-their-process-that-prevent-future-errors)
- [State participants chose Submission History Version B; Tribal participants chose Version A](#state-participants-chose-submission-history-version-b-tribal-participants-chose-version-a)
- [Grantees who currently submit partial data coded by fTANF may benefit from material detailing how to move to submitting complete data](#grantees-who-currently-submit-partial-data-coded-by-ftanf-may-benefit-from-material-detailing-how-to-move-to-submitting-complete-data)

  

### All participants had a good idea of what to expect from the error reports referenced in Versions A & B

Despite terminology differences from the current state TDRS system, all our participants had accurate ideas of what to expect out of the "Error Report" links surfaced next to each submitted file. Some said they would expect to see the Transmission Report if they clicked one of those links, others predicted something more in the vein of the Questionable Cases report, or similar reports they produce themselves to screen for errors before transmission. Multiple participants also expressed a preference for an Error Report that provided an experience closer to that of Questionable Cases than of Transmission Reports; citing increased detail that requires less effort to act upon. 

> "I hoped that it was THE [questionable cases] error report rather than just the transmission report"

**Project Impacts:**

- The balance of what content exists on Submission History and what will exist on an Error Report is sound and seems to click with grantees. 
  - The importance of error feedback in the current process and our participants in this round successfully identifying what they might find in an Error Report bodes well for the discoverability of that error data.
  - We plan to retain these design elements in dev-ready mockup refinement. 

### Seeing who submitted a given file could be an important data point for grantees with multiple data analysts

One participant noted that they'd like to be able to see which member of their team submitted a given file in addition to the date/time metadata capturing *when* it was submitted. This is likely a larger value add for larger teams where multiple data analysts have hands-on roles on one or multiple section of TANF data. On those teams knowing who submitted a file or who resubmitted one could provide its own level of insight into what level of completeness to expect from it, or what internal checks the file has gone through.

**Project Impacts:**

- We will experiment with the addition of "Submitted by:" data surfaced on Submission History—possibly attached to the date/time stamp. This represents the user story, As a TDP user I want to know who submitted a file. 

### Making minor changes to practical guidance for errors occurring due to external constraints would be helpful in reducing resubmissions

Grantees' gave two examples of error categories that are due to external constraints:

1. Newborn Social Security Number (SSN) - It takes 3 months for newborns to be assigned an SSN, but they are added to TANF families as soon as they are born. This results in child records without SSNs, which in turn gets flagged as errors by OFA. 

> "A lot of times, newborns don't have social security numbers yet. So, we'll get an error report back saying -*here's a list of children without social security numbers*. Well, three months from now, we'll have social security numbers and we'll put them in and we'll resend those cases. We'll have the data, but we won't be able to fix them immediately."   

> "Our rules allow us to grant newborns to become part of the TANF household. And we can do that even without the child, the infant not having a social security number. So we have to use a temporary id. But what happens at the ACF side is that comes back as all zeroes, no values."
2. Declaring Race on a TANF Application - Many TANF recipients prefer not to declare their race on the form when they apply for benefits. Grantees' understand this is not a legal requirement either. However, when there is no race associated with a record, it is flagged as an error.  
> "You have to have a race code or it's a fatal error. We have people applying online, we have people applying by phone. We have people that don't want to tell us that. We can't force them to tell us that. It is not a legal requirement for TANF to tell us that. Are they going to fix that and make it a warning error?" 

### Having access to historical error patterns may help grantees make adjustments to their process that prevent future errors. 

Participants of this round of research session expressed a desire to see historical error data for the data they transmit to OFA. For many participants, insight into error patterns would help them can identify and avoid mistakes that recur over a period of time. For many errors this could help grantees implement measures to prevent those in future submissions. 

**Project Impacts:**

- Like the reporting & analytics use cases referenced by participants who favored Version A, we will plan to follow up on this finding in research concerning Reports and/or Analytics. We hypothesize that having access to data on error trends in addition to data on errors in one particular submission could be a powerful tool toward improving data quality over time and receiving fewer errors submission to submission. 

### State participants chose Submission History Version B; Tribal participants chose Version A

|       | Details                                                      |
| ------------- | ------------------------------------------------------------ |
| **Version A** | Cases (Accepted, Rejected, Total) + Rejected Records by type |
| **Version B** | Cases (Accepted, Rejected, Total)                            |



All state participants of this round of research voted for Version B of the Submission History mockups. Version B included cases information only and provided the total number of accepted, rejected and total cases disaggregated by month. The clear reason for their choice was that it meets parity with the current feedback reports from the OFA, which grantees use to identify and correct errors. 

Both the Tribal participants in this research round, however, voted for Version A for its ability to drill down into rejected records to correct errors. 
It is also noteworthy that one state participant initially opted for Version A , but with further discussion about reasons, changed their preference to Version B for the above-mentioned reason of parity with current feedback reports.  

#### Hypothesis about tribal participants' preference for Version A

We **hypothesize for future research** that tribal participants chose Version A because they depend on third-party vendors for data prepping and error correction. As a result they have fewer errors in their data. Their low error and resubmission rates would make the granular rejected records information easier to manage. 

On the other hand, states with hundreds of rejected records may prefer downloadable error reports. 

**Project Impacts:**



- We'll integrate the research insights around the usefulness of rejected/accepted data by record type into future research epics concerning TDP Reports and Analytics. Associated user stories include:
  - As a grantee user I want to see the number of records that have been accepted by OFA broken down by type. 
  - Aa a grantee user I want to compare accepted and rejected records level data across submissions and across quarters. 
  
- In future research rounds, we will also test our hypothesis about tribal preference for Version A - rejected records by type  so that the page meets tribal grantees' needs.  

- We will proceed with refinement of Version B as being the best baseline experience of Submission History

The described value of record level data seemed to be primarily in the vein of more general reports/analytics use. The grantee respondents also expressed interest in the availability of the same level of insight into accepted cases; this again fits within the scope of being more of a reports/analytics use case than particular instances of Submission History. 

### Grantees who currently submit partial data coded by fTANF may benefit from material detailing how to move to submitting complete data

One of our participants this round codes their data in fTANF and submits revisions to a given quarter that only include modified or added cases/records—using the "U" Update Indicator state—rather than the full set of data. They were able to tie this practice to fTANF's "Edit Status", but told us that they weren't sure how they would go about changing that Edit Status to allow them to export all of their data regardless of whether it had been modified since a prior export. 

We followed up on this session with an internal DIGIT/Design sync to align around the steps users can take in fTANF to set all cases to the correct status; "Passed All Edits" as opposed to "Not Edited" or "Transmitted". The process here is straightforward, involving (for a given section), the following actions: 

1. Click "Reset Transmission Flag"
2. Click "Global Fatal Edits" to run fTANF Fatal Error checks
3. Click "Global Warning Edits" to run fTANF Warning Error checks

Once these steps are complete the Edit Status of all cases should read "Passed all Edits" and all cases will be included in a subsequent export. It is also import to note that having not spoken to all grantees who currently submit partial data we cannot confirm that they all use fTANF. If some use a custom or 3rd party system to code their data there may be a significantly higher barrier to moving away from partial data practices. 

**Project Impacts:**

- We will prioritize the creation of an fTANF specific guide to help grantees move from partial data submissions to full ones as part of Onboarding research/design. 
- Recruiting partial submission grantees for the pilot program could be a prudent way to learn about difficulties in moving to full submissions that may be posed by non fTANF systems earlier rather than later. 





