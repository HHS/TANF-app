# 2022, Summer - TDP 2.0 Pilot Program

Last updated for [#2058](https://github.com/raft-tech/TANF-app/issues/2058)

---

**Table of Contents:**

- [Who we talked to](#Who-we-talked-to)
- [What we did](#What-we-did)
- [What we tested](#What-we-tested)
- [What we learned](#What-we-learned)
- [What's next](#What’s-next)

---

## Who we talked to

We recruited grantees based primarily on the following criteria:
- Interest in participating in the pilot
- Current reliance on email transmission (Tribes)
- Recent submission of partial data
- Not submitting SSP data

Aligned to those criteria our pilot participants represented:

- 5 Tribes (3 of whom participated in moderated sessions)
- 6 States (3 of whom participated in moderated sessions)

---

## What we did

The pilot program was conducted in order to:

- **Evaluate** the success rate from Grantees (STTs) on their experience with the TANF Data Portal based on existing features with data submission Q3 2022 that is due on August 15, 2022
- **Identify** and document pain points, if any, that Grantees have with secure login, upload/download data files
- **Observe** and document accessibility, browser and general IT compatibility concerns/issues
- **Allocate** and conduct high level research to help inform decisions with Release v3.0
- **Build** a rapport with grantees for future expansion and utilization of the TANF Data Portal

**Supporting Documentation** 
- [Pilot Workshop](https://hackmd.io/ucJ0B3lPQDuhKFFkX9du9Q?view) :lock: 

---

## What we tested

Each participant was tasked with the following:
- **opening** TDP in a compatible browser (i.e. not choosing Internet Explorer) 
- **viewing** the home page
- **signing-in** using Login.gov
- **requesting** access to the TANF Data Portal
- **uploading** data files for FYQ3 2022 (April - June)
- **submitting** data files for FYQ3 2022 (April - June)
- **viewing** the submission notification (or submission error)


*Overall, the pilot program was a success: data was succesfully transmitted  for each grantee that participated.*  

We also measured the extent to which each task could be completed with ease. See chart below, which summarizes how participants in the **moderated group** fared. Tasks denoted in yellow show where some participants experienced some difficulty or delay in completing the task:

[![](https://i.imgur.com/dOlhriE.png)](https://i.imgur.com/dOlhriE.png)

<u>Note</u>: Un-moderated group participants are not captured in the chart because we were unable to observe their tasks. 


In addition to data captured from grantee participants, the pilot also afforded us an opportunity to test TDP's system admin functions in action. Reflections and learnings from OFA staff administrating TDP during the pilot are accordingly captured below.

---

## What we learned

**Jump to:** 
- [What went well](#what-went-well)
- [Some parts of the login and authentication experience may introduce friction for some grantees](#areas-of-the-login-and-authentication-experience-may-introduce-friction-for-some-grantees)
- [Tribal programs listed in the STT selection combobox may pose a discoverability issue](#tribal-programs-listed-in-the-stt-selection-combobox-may-pose-a-discoverability-issue)
- [Terminology used to identify sections and certain UI elements lead to friction among some participants](#terminology-used-to-identify-sections-and-certain-ui-elements-lead-to-friction-among-some-participants)
- [The stratum data file picker being available to all grantees was confusing for those who submit universe data](#the-stratum-data-file-picker-being-available-to-all-grantees-was-confusing-for-those-who-submit-universe-data)
- [Most participants used TDP at resolutions that obscured submission status from view](#most-participants-used-TDP-at-resolutions-that-obscured-submission-status-from-view)
- [Enhancements and bugfixes to django admin could streamline elements of the user approval process](#enhancements-and-bugfixes-to-django-admin-could-streamline-elements-of-the-user-approval-process)
- [We documented some minor bugs during moderated sessions](#we-documented-some-minor-bugs-during-moderated-sessions)
- [Miscellaneous feedback from grantees](#miscellaneous-feedback-from-grantees)




---

### What went well
By all our measures the pilot was a success. Participants were able to access TDP and navigate the process of submitting their data—not to mention able to provide us with insights and feedback that will be instrumental in enhancing this and all future versions of TDP. While our top level findings focus on areas where we can improve TDP it's also well worth mentioning that we received enthusiastically positive feedback from participating grantees as well. 

### Areas of the login and authentication experience may introduce friction for some grantees

The TANF Data Portal utilizes Login.gov for account access. While our ability to change how it functions is limited, it does represent an important part of the TDP experience and should be considered as we expand access to TDP and continue to enhance the [Knowledge Center](https://tdp-project-updates.app.cloud.gov/knowledge-center/).

#### Login.gov emails can end up in junk mail. 
Grantees utilize a variety of email clients and email screening services which categorize Login.gov emails in a variety of ways. For example, one grantee email client we observed set sent emails to a non-inbox “Unread” folder, while another sent the login.gov confirmation email directly to the “Junk Mail” section. 

> “I’m not receiving the email”

**Suggested Actions:**

- Update Knowledge Center to reflect that if Login.gov emails are not received then to refresh and check other in other folders / inbox categories. 
- Prioritize continued consideration of how this issue might impact the emails that TDP will begin sending in v2.1. Will we be able to detect whether TDP emails are being caught in junk email? If not how might we test the success rate in another way? 

#### Authenticating via text message was the most popular 2FA option among moderated participants

- Five of our participants selected “Setup with Text or Voice Message” and one selected the Authentication App option
- The security code did not come through on the 1st try and the participant selected “resend code” which did send a text code right away
- Microsoft Authenticator App settings might need to be adjusted for notifications to surface outside of the app itself in the way certain participants may expect based on other systems they use 2FA for
- Backup Codes setup as a secondary authentication type
> “Oh, I have to add another one?“

**Suggested Actions**
- Ensure that we understand what the authentication experience is like for each method available in login.gov 


___

### Tribal programs listed in the STT selection combobox may pose a discoverability issue
Among our moderated participants from Tribes, all selected and submitted the State their Tribe is located within rather than the name of their Tribe itself. In one case this seemed to be the result of browser autofill feature populating the request access fields like it would for a shipping address form. Another participant told us that the presence of Tribe names in the list wasn't immediately evident.

> "I didn't really see the tribe names before I got to [State] so that's why I selected it. I thought you were looking for an area instead of the tribe name."

If left unaddressed this discoverability/data entry issue could lead to a variety of problems including:
- downstream data integrity issues
- inappropriate access to the data of another grantee
- misaligned attribution of funding 
- inconsistent generation of data files over time
- increased work for OFA Admins when screening access requests

**Suggested Action(s)**
- We plan to evaluate a number of solutions/improvements here ranging from ensuring that OFA Admins take a step to ensure that the email address of a new TDP user matches the STT they're requesting access to improvements to the access request form itself to either eliminate the need for the user to provide STT or to make the presence of Tribes in the list clearer
- Django enhancement to make it easier to identify which STT selection a user has made


___

### Terminology used to identify sections and certain UI elements lead to friction among some participants.

Moderated testing re-emphasized past findings that certain terms have different meanings to different grantees informed both by past experiences with the TANF program and software tools used to prepare TANF data. These differing meanings proved a surmountable obstacle during the pilot but was associated with some degree of friction or decreased confidence in what TDP was asking of them.

#### Section 2 Data: Closed vs. Negative
All of the Tribal participants recognized the “Closed” TANF data section as “Negative”
> “[Our vendor system] creates the files as 'Negative' which is where the term is coming from” 

![](https://i.imgur.com/jTLQhNu.png)

If unaddressed there is potential that Tribal grantees may miss submission of Section 2 data due to unfamiliarity with the term, or may result in additional communication from grantees asking for clarification of the term.

**Suggested Action(s):** 

-  Continued discussion/collaboration with DIGIT on strategy relating to official terminology changes in the pipeline for existing TANF instruction documents.
- Consideration of in-app methods of communicating the fact that Closed == Negative (while not encouraging continued use of the Negative term)
- Update Knowledge Center to include this distinction for future reference 


#### One participant wasn't clear on where to go next after successfully submitting their data.
On the Data Files page, after clicking “Search” the data file upload components appear alongside buttons for “Submit Data Files” and “Cancel”. The latter term is an element of design debt from past versions of the upload flow that included more potential states of the upload which might need to be cancelled out of by the user. However given the ways the flow has been simplified since, "Close" rather than "Cancel" is likely to be the clearer way to indicate the button's purpose to users.

> “I don’t know how to close”

![](https://i.imgur.com/KLCFS1E.png)

**Suggested Action(s)**
- Change the button text from “Cancel” to “Close” to better communicate the intended action


---

### The stratum data file picker being available to all grantees was confusing for those who submit universe data

- **Section 4 Stratum**
    - 100% of the Tribe participants did not submit Section 4 Stratum and did not know what it was
        > "I’m not familiar with Stratum Data—we usually don’t have to submit it"

![](https://i.imgur.com/fjSqKAG.png)

- Usability Impacts: 
        - Section 4 Stratum is not required to be submitted by every State, Tribe and Territory which may cause confusion on whether they need to prepare and submit them or not. 
    - Suggested Action(s): 
        - Is the Stratum data set based on STTs who submit sample vs. universe data sets and could this be used to drive whether Section 4 Stratum data displays? 
        - Appending information listed in Section 4 within Data Files whether it is a hover-on tooltip or on page descriptor

---

### Most participants used TDP at resolutions that obscured submission status from view. 

The majority of moderated participants weren't immediately able to see the status of their submission appear after submitting their files. Their reaction to not seeing that message mapped either to:
- scrolling up/down the page
- continuing to click on “Submit Data Files” 

If left unaddressed this could lead to:
- duplicate data file submissions
- lack of awareness of potential errors that require attention
- lack of awareness of successful submissions

Note: Interestingly, the current state here (on lower screen resolutions) is less communicative than the experience for screen-reader users where the success/error banner is always announced and read as an alert (regardless of where the page is scrolled to).

**Suggested Action(s):**
- New Ticket: After clicking “Submit Data Files” anchor back to where the notification is located


---

### Enhancements and bugfixes to django admin could streamline elements of the user approval process

In addition to evaluating TDP's usability for grantee users the pilot also represented our first real-world opportunity to test drive the system admin functions currently managed in Django. Our system admins reflected on the process of using those and passed on comments and suggestions for streamlining it for future userbase expansions.

#### Confirming that a user is requesting access to the correct STT is overly cumbersome currently due to Django not presenting the right form of data

TDP admins rely upon STT names and/or FIPS/Tribe codes (e.g. Louisiana / FIPS code 22) to identify specific STTs. The pertinent parts of Django admin currently use a separate internal location ID rather than name or FIPS/Tribe code which introduces an extra step to look up which STT a location ID maps to. This issue is documented in [#1641](https://github.com/raft-tech/TANF-app/issues/1641). This process could also be further improved with the addition of more filters in Django admin some of which are currently captured in [#960](https://github.com/raft-tech/TANF-app/issues/960).

#### A bug currently complicates the process of granting permissions to new users.

The intended behavior in Django admin is that a System admin should be able to navigate to a user's profile, pick a role, and save the change to grant them permissions in TDP. However the location type being set to STT blocks this, resulting in an additional step to remove the location type, save, and then return to grant the role and restore the location type. 

**Suggested Action(s):**
- New ticket documenting the above bug and relating it to the change that originally introduced it in [#1387](https://github.com/raft-tech/TANF-app/issues/1387)



---

### We documented some minor bugs during moderated sessions

- **502 Gateway Error** - Participant clicked on the “Login for Grantee” button and received a “502 Bad Gateway Error”. The participant manually refreshed his screen and the error corrected itself. 


**Missing File Type Validation** - Participant was able to upload and submit a non-text file (PRN file) and the validation error appeared but did not provide any action. The error stated “Request failed with status code 400”. 
![](https://i.imgur.com/iYr2dLm.png)


**Disappearing Download Button** - Participant clicked “Download Section 4” and after the data files have been downloaded the button disappears. Previously documented in [#1107](https://github.com/raft-tech/TANF-app/issues/1107).
![](https://i.imgur.com/ifkivzq.png)


**Suggested Action(s)**
- Bug tickets to be created as needed, discussed in backlog refinement, and prioritized based on severity.

---

### Miscellaneous feedback from grantees

As the participants navigated throughout the TANF Data Portal experience, we encouraged them to share their open and honest thoughts and observations. Below is a list of recommendations to be reviewed and considered by the product team. 

- **Home Page (Unauthenticated)**
    - Virtual walkthrough of the site to understand what capabilities are available
    - The Knowledge Center opens in a new tab so people can easily toggle back and forth
- **Home Page (Authenticated)**
    - Dashboard with links to Data Files, outstanding, upcoming deadlines, information that pertains to my STT or region, letting me know about the last upload and a timeline to let you know where it is in the process
    - When data files are due
- **Data Files**
    - Chatbot - being able to message questions
    - Error validation
    - Helpful for auditors to see when files have been submitted and resubmitted
- **Reports**
    > Reporting would be nice!
    - Being able to compare their STT to the broader TANF programs across the country. 
    > "Where do we fall in comparison?"
- **Email Notifications**
    > That goes to everyone, right not just me since I was the one who submitted the files? Referring to the email "Data Files have been submitted" email distribution

___

## What's next
- Prepare and present these findings to the larger product team and stakeholders
- Where applicable, new tickets will be created to document suggested actions based on the feedback and prioritized accordingly into the development backlog
- Extract certain key aspects of the pilot workshop to help facilitate the expansion in November 2022
