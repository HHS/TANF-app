# 2020, Fall - Understanding STT Roles, Source of Truth, and Metadata

[![Raft Logo](https://goraft.tech/assets/logo.png "Raft LLC Logo" =180x75)](https://goraft.tech/)

<img src="https://goraft.tech/assets/logo.png" width="15%" height="auto" alt="Raft LLC Logo" style="vertical-align:left;">

[Issue #350](https://github.com/raft-tech/TANF-app/issues/350)

---


# What we wanted to learn

**Our goals for this research were to:**

1. Evaluate how grantees react to concept prototypes simulating TANF report creation (e.g. capturing metadata) and the uploading of associated flat files. 
— [Jump to Section](#About-error-validation--correction)

2. Identify how grantees track the status (e.g., drafted, edited, submitted, resubmitted) of their data reports and maintain transparency of that status across their teams. 
— [Jump to Section](#About-the-data-transmission-process)
   - Document how grantees confirm that a report has any given status. 
   - Identify if/how grantees maintain a log of what reports they submitted to OFA. 
   - Identify if/how grantees maintain a version history of resubmitted TANF reports (e.g. what was added, updated or deleted) as if/how they save older versions. 
3. Document the makeup of grantee teams involved with data preparation and data submission. 
— [Jump to Section](#About-grantee-teams)
   - Identify if/how grantees maintain a version history of resubmitted TANF reports (e.g. what was added, updated or deleted) as if/how they save older versions. 
     - The spring research gave us an understanding of what data-preppers do but we hope to dig deeper into how teams of data preppers (when they exist) divide responsibilities and interact with each other.
   - Identify any common roles aligned to admin tasks (e.g. User Management or onboarding new users to data-prep or case management tools) and document how these tasks are managed.
   - Identify team grantees turnover rates and any associated pain points.
4. Deepen our understanding of how grantees create flat files and what causes metadata issues (including title, header, and trailer) 
— [Jump to Section](#About-case-management-systems-and-other-tools)
   - Document how grantees manage their data (e.g. any case management systems, excel files, etc.) and compare TANF reports to how grantees structure and store their data.  
     - The spring research helped us understand how grantees code data from a variety of local or regional resources but we hope to uncover the pain points that might be outside the flow of submitting to OFA but still have an impact on data quality and data management practices relevant to resubmission. 
   - Document the process of coding information from grantee case management systems into TANF report metadata.
     - While the spring research documented coding fixes (and the difficulty of making those fixes), we want to deepen our understanding the circumstances that lead to the need for these coding fixes.



**Related Documentation:**

[Full research plan](<https://hhsgov.sharepoint.com/:w:/r/sites/TANFDataPortalOFA-UserResearch/Shared%20Documents/User%20Research/STT%20Research%20September%202020/%2363%20User%20Research%20Plan%20STTs.docx?d=w2e300237f6454446b191a9ee509026ef&csf=1&web=1&e=pAteXb>) 🔒


---

# Who we talked to

Given the largely generative focus of this research we wanted to talk to 5-9 participants involved in TANF data preparation from a variety of grantee types. We targeted criteria such as: 

- At least one state that submits universal case data
- At least one state that submits sample data
- At least one tribe
- At least one territory
- Preferance toward participants who have no been interviewed in past research

We ended up talking to a total of six participants who fulfilled all of the above criteria. Those participants represented one tribe, one territory, and four states. Sessions ranged from 1 hour to 1 hour and 25 minutes and was equally divided into one half focused on generative interview questions regarding research goals 2-4 and one half moving through the conceptual prototypes.



**Related Documentation:**

[Recruiting Criteria and Selection](<https://hhsgov.sharepoint.com/:w:/r/sites/TANFDataPortalOFA-UserResearch/_layouts/15/WopiFrame2.aspx?sourcedoc=%7B1a533a84-0000-423d-8274-c0767d9f471d%7D&action=view&cid=ad0b98e3-1d2b-46ad-a6f3-50eb0c019c01>) 🔒

[Grantee Attributes](<https://hhsgov.sharepoint.com/:x:/r/sites/TANFDataPortalOFA-UserResearch/_layouts/15/WopiFrame2.aspx?sourcedoc=%7Be83f84f1-71a0-459f-80a4-0d39bc250be9%7D&action=view&cid=f2e656cb-9245-4f02-af6d-2d7e1db6573d>) 🔒

---


# What we tested

Concept testing was focused around a flow depicting the process of report creation. It started from a screen collecting report metadata (e.g. Reporting Year/Quarter, whether the report is TANF or SSP-MOE, etc...), went through flat file upload, metadata validation, and a summary of successfully validated files. Concepts and areas that we wanted to investigate included:

- Participant familiary with data points that make up the Header of a flat file, particularly around encryption of Social Security Numbers.
- Whether participants could correctly identify the names of TANF report sections despite the known variation in what different grantees call them.
- Whether validation error copy was understood by participants and successful in suggesting an actionable next step.
- Contextualizing questions around whether participants currently maintain a revision history of their TANF reporting. 



**Related Documentation:**

[Conversation Guide](<https://hhsgov.sharepoint.com/:w:/r/sites/TANFDataPortalOFA-UserResearch/_layouts/15/WopiFrame2.aspx?sourcedoc=%7B0333313b-0f88-406b-b894-07687d32921b%7D&action=view>) 🔒

[Figma Prototype 1](<https://www.figma.com/proto/y15co5xc7MIZXBnWBOF6hJ/Conceptual-Mockups-for-STT-Feedback?node-id=9%3A332&viewport=187%2C385%2C0.11285778135061264&scaling=min-zoom>)

[Figma Prototype 2](<https://www.figma.com/proto/y15co5xc7MIZXBnWBOF6hJ/Conceptual-Mockups-for-STT-Feedback?node-id=1%3A1070&viewport=530%2C320%2C0.1293068528175354&scaling=min-zoom>)

[PDF Prototype 1 & 2](<https://github.com/HHS/TANF-app/tree/main/docs/User%20Research/2020%2C%20Fall%20-%20Concept%20Prototypes>)

---


# What we learned

Raw notes from interviews were synthesized in Mural with the OFA data division. Then we distilled our learning further into the insights below.



**About error validation & correction**
> Primarily related to Goal 1

- [Grantees have different processes to correct errors in a flat file, which may have implications for the long-term quality of the data.](#Grantees-have-different-processes-to-correct-errors-in-a-flat-file,-which-may-have-implications-for-the-long-term-quality-of-the-data)
- [Grantees want more efficient and more actionable ways to understand the errors (validation, transmission, etc.) and how to fix them.](#Grantees-want-more-efficient-and-more-actionable-ways-to-understand-the-errors-validation-transmission-etc-and-how-to-fix-them)
- [There is confusion about fiscal year and calendar year reporting.](#There-is-confusion-about-fiscal-year-and-calendar-year-reporting) 


**About the data transmission process**
> Primarily related to Goal 2

- [Different grantees treat version & transmission history in different ways](#Different-grantees-treat-version-amp-transmission-history-in-different-ways)
- [Grantees want to submit quality data even if deadlines have passed](#Grantees-want-to-submit-quality-data-even-if-deadlines-have-passed)
- [Grantees sometimes have to communicate with ACF to determine transmission status](#Grantees-sometimes-have-to-communicate-with-ACF-to-determine-transmission-status)
- [Grantees have different ways of transmitting files](#Grantees-have-different-ways-of-transmitting-files)
- [Grantees understood the term 'encryption' differently.](#Grantees-understand-the-term-‘encryption’-differently)
- [ACF TANF file naming conventions aren't familiar to all those involved in prepping data](#ACF-TANF-file-naming-conventions-aren’t-familiar-to-all-those-involved-in-prepping-data)


**About grantee teams**
> Primarily related to Goal 3


- [Responsibility over parts of the prep/submission process fall entirely on one or two people in some grantee teams](#Responsibility-over-parts-of-the-prepsubmission-process-fall-entirely-on-one-or-two-people-in-some-grantee-teams)
- [A variety people and teams own different parts of the TANF report creation and submission process.](#A-variety-of-people-and-teams-own-different-parts-of-the-TANF-report-creation-and-submission-process)


**About case management systems and other tools**
> Primarily related to Goal 4

- [Some case management systems are multipurpose with some degree of customization for TANF.](#Some-case-management-systems-are-multipurpose-with-some-degree-of-customization-for-TANF)
- [TANF staff are navigating multiple software products from data collection through report submission.](#TANF-staff-are-navigating-multiple-software-products-from-data-collection-through-report-submission)
- [Editing often happens in case management tools, but a few tasks are completed directly in the flat file (in a text editor).](#Editing-often-happens-in-case-management-tools-but-a-few-tasks-are-completed-directly-in-the-flat-file-in-a-text-editor)


**Related Documentation**

[Synthesis Workshop  Mural](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1605279076254/8ba4f36f5bc1b2d724fd8c61daf6dc18da096e97) 🔒






---




## About error validation & correction

> Primarily related to [Goal 1:](#What-we-wanted-to-learn) 
> Evaluate how grantees react to concept prototypes simulating TANF report creation (e.g. capturing metadata) and the uploading of associated flat files. 

### Grantees have different processes to correct errors in a flat file, which may have implications for the long-term quality of the data.

Processes for correcting errors varied widely from grantee to grantee. These included splitting up error corrections among multiple people, identifying errors based on memory and experience, and decoding errors from physical reference material.

- "What can be a little challenging is  it's going to give you the element number. It's going to say parents with minor child and the family. Then it says if item 14 equals one to two item 22 must equal one to two. So what I have to do is on our ACF instructional guide, look for what is item 14. So I have to go to my book. "
- "STT data analyst sends us a file with all the errors. We assimilate them to each worker, there are three people under me and myself. So it's four of us. We can't do each other's work. We have our own ID. So she (STT data analyst) sends us the information. We separate to who it (the erros) goes to (other data preppers), make the corrections, retransmit it back to her (STT data analyst). And then she sends it off, back off to the feds (ACF/OFA)"
- "I'm able to review these documents that have all the numbers for our federal statistics and say something looks unusual"8
- [Review and report by month can take 2-3 weeks to make sure we didn't forget anything.]

**Project Impacts**
- Explore how STT teams can assign and task out errors to different types of roles.
- The "Data Prepper" role should be updated so as to better accomodate the breadth of those involved with data at the grantee level.

### Grantees want more efficient and more actionable ways to understand the errors (validation, transmission, etc.) and how to fix them 

Most of the grantees we spoke to had relatively low rates of fatal errors when submitting their data, but all dealt on some level with either reviewing files for data quality issues, or navigating corrections of files when issuess ocurred. One participant gave us a great view into the sheer scale of possible errors & edits by pulling out their "book", a large binder containing printed versions of ACF error codes, they told us:

- "So after [ACF has the data] this is how the feedback comes up to us. The cases are here and here [folder of a variety of PDF reports], it says error flag. So it tells me this case has an error and what the error flag is. So again, I kind of go, you know, try the little book."
- "...it'd be good if instead of looking through a book, you know, something will pop up and say, this is what's what's missing, or this is what you need to correct. Because if not, then I have to kind of go through my little binder and I go to the federal edits guide"

They expanded with an example of how this process isn't always as simple as looking up a single code, but rather crossreferencing multiple data points against multiple error codes and/or data coding instructions:

- "What can be a little challenging is it's going to give you the element number. It's going to say parents with minor child and the family. Then it says if item 14 equals one to two item 22 must equal one to two. So what I have to do is on our ACF instructional guide, look for what is item 14. So I have to go to my book."



**Project Impacts**
- Consider how we might lean *more* into making errors highly understandable and highly actionable—Participants we tested the concept prototype were able to rephrase what was being conveyed by our error copy in their own words, but it was a pretty simplistic error. We should think about how we'll scale writing easy-to-interperet error copy for the broader picture of errors possible for any given report. 
- The "in your own words" explainations from participants of what our error copy meant could be helpful for our iteration on it. 
- Further understand how case data relates to errors and how we might combine like errors for easier case lookup.

### There is confusion about fiscal year and calendar year reporting.

Some grantees talked about how the quarters they submit do not line up with the calendar year but rather the fiscal year.

- "... first quarter of calendar year, [which] I guess, belief, Q1, which would be October through December of 2020"
- "The year and then one digit months can be confusing, I almost wish that it was 2020, 03 or 03, 2020, just because on those months, the last couple of months that have two digits... I know for me, if I had 03 that way, they'd be the same digit length for all of the different things that we do with the data."

**Project Impacts**
- Consider how TDP copy can be further refined to ensure clarity around some of these particularly confusing data points.






---





## About the data transmission process

> Primarily related to [Goal 2:](#What-we-wanted-to-learn) 
> Identify how grantees track the status (e.g., drafted, edited, submitted, resubmitted) of their data reports and maintain transparency of that status across their teams. 

### Different grantees treat version & transmission history in different ways

Some maintain copies of the files they transmit to OFA, others primarily care about the most recent (and presumably most complete) version that's been produced. 

- I would still save it. I would still have it actually. I wouldn't get rid of it and I would to submit a new file and even label it, maybe update or something like that.
- "when the new submission is processed successfully, I delete the previous submission in our archive"

**Project Impacts**
- Consider whether the reuse of flat files for building future reports from has an impact on data quality. 
- Update the process map to encompass report & file management after transmissions to OFA.

### Grantees want to submit quality data even if deadlines have passed

We heard from several grantees that achieving "final" data quality/completeness can be a very extended process that happens over the course of whole years, not just quarters.

- "That's how we basically fix the errors. So, so ACF will sort of give us a timeline, they'll say, okay, we're going to close out 2020 files on March, 2021. So you have to make sure you kind of clean up all your data because after that we can't retransmit "
- "...we're trying to clean stuff up over the year. [As] the end of the fiscal year approaches... we do like an overwrite to ACF for a particular quarter"
- "The data may have been inputted or the correction we have done after the report was sent, which sometimes happens because it does depend on the client submits to us, their attendance, you know or their hours"

Whether data is coming in near the beginning of a quarter or closer to its end can impact the completeness of the report. e.g., for a Quarter 1 TANF report, data for January is more likely to be complete and high quality than data for March. 

- "in January 2020. If somebody did […] a college activity, our workers would have all of February and March to track [that] and then for it to count towards the federal file. But some months, like, for example, March, they only have the month of April to track it. And once April has expired, they can enter it, but it's not going to count towards the [first version of the] federal file" 


**Project Impacts**
- Evaluate whether communication around final reporting deadlines could be delivered automatically by the TANF Data Portal.
- Update the current process map to include steps for resubmitting TANF reports after deadlines have past. 
- Explore if data submission extensions are always in affect or if it is given with an as needed basis.
- Explore whether there's value in automating some predictable communications from OFA to grantees that concern data submission deadlines. Could these be conveyed directly in the conext of a drafted report? In some sort of calendar functionality?

### Grantees sometimes have to communicate with ACF to determine transmission status

The norm among grantees that we have data for indicates that most expect and receive ACF transmission reports after a TANF report has been submitted. However, some have encountered problems receiving the emails containing those. 

- "...they had somebody at ACF that would send those to [us] on a regular basis. Now we have to actually call up and have [OFA statisticians], go ahead and, and send that to us."

Some types of flat file issues may result in transmission reports not being sent to grantees:
- "I submitted a blank report once and I didn’t hear back for a couple of months saying that the report needs resubmission"

Grantees look for clear, timely confirmation that a file was received: 
-  "I [currently] get a delayed response in regard to any errors that it found, I would I would get an immediate response saying that that my one hundred and fifty five thousand was successfully submitted....And that's that's gratifying. That's a cookie. I like that"

**Project Impacts**
- The new TANF Data Portal will have its own notification system indepenedent of the existing OCIO system that sends transmission reports to grantees. An open question that may be important to consider is whether all grantee staffers who currently receive OFA transmission reports will be users of TDP, or whether functionality to notify non-users of various statuses and actions is called for. 





### Grantees have different ways of transmitting files

Some grantees transmit TANF reports in a piecemeal approach, sending sections in one at a time as they're completed rather than in a batch: 

- "...I would do four different transmissions, you know, put this one up, send it and then do the active, and then closed and then the aggregate"
- re. upload/. conceptual prototype : "Cause it might just be two [quarters] that we're doing now"

Some grantees submit monthly reports instead of quarterly 

- "... we've been trying to do now is do [TANF report] each month separately as we finish it, instead of doing the whole quarter at once"

**Project Impacts**
- Consider how we can make the upload function flexible and generally accomodate differing flows relating to assembling TANF reports.
- Include notifications to alert a user of an incomplete report if the upload sections at different times.





### Grantees understand the term 'encryption' differently. 

Some grantees seemed to understood encryption as being something roughly equivalent to 'non human-readable'. Others did connect our question about encryption with the TANF header data point regarding social security numbers (SSN). However not all grantees encrypt those, instead relying on security inherent to the SFTP transfer processes (this includes managed SFTP vendor services like Cyberfusion):

- "We count on the TIBCO [Cyberfusion] process to make the data secure...We don't bother encrypting the SSNs"

Other grantees spoke to quirks of their software tools related to SSN encryption, saying that metadata sometimes has to be changed to get report file imports to work properly:

- "...when we do [import] the first time we have to put “no”. Yeah. For some reason we have to, re-import it. We have to put "yes" in order to see it" 

**Project Impacts**
- Confirm whether we're able to automatically decode encrypted SSNs, or whether users will need to be asked an encryption-related question about their uploads.
- Explore how we might give users confidence in the security of the new TANF Data Portal.
- Consider what permissions should exist around viewing social security numbers in a future version of TDP that presents human-readable data. 




### ACF TANF file naming conventions aren’t familiar to all those involved in prepping data

One part of concept testing involved exposure to TANF report file naming conventions. Ex. 'ADS.E2J.FTP1.TS21.txt'. Some participants recognized the format of the name, but others spoke to or showed us examples of alternate naming. 

- "I'm not familiar with the file name itself...I use a very simple file name instead."

Examples of grantee naming practices we encountered include:

- TANF21_EA_1 (1-3)
- T1 (1-4)
- TAN_1 (1-4)

**Project Impacts**
- We validated our assumption that lifting flat file naming requirements might be an easy way to reduce complexity around submission without causing disruption. That assumption was largely based on the fact that the file names themselves don't contain a great deal of data regarding the overall report and the technical need for them is eliminated by moving to the new TANF Data Portal infrastructure from the current ACF server. Running into so many unique grantee-level naming conventions gave more weight to the idea that requiring them to rename their files is an extra and unnecessary step in the current process.





---



## About grantee teams

> Primarily related to [Goal 3:](#What-we-wanted-to-learn)
> Document the makeup of grantee teams involved with data preparation and data submission.

### Responsibility over parts of the prep/submission process fall entirely on one or two people in some grantee teams

Our participants had held their positions for anywhere from five to twenty years:

- "I'm a Social Service Supervisor. I started off as a social worker [for a jobs program], and I got promoted to the supervisor position [in 2006]"
- "[My] service classification is a State Program administrator coordinator, I consider myself the 'Data Geek' for [grantee], I started working on this stuff thanks to Y2K in the Fall of 99'"
- "I've been working on this for about 20 years now and I'm looking to retire in the next couple of years"
- "My actual title is Public Assistance Program Specialist, but my area is TANF [...] I compile the data, write the report, submit the report"

We heard a variety of team-related concerns ranging from how hard it would be for somebody new to TANF to take over when longtime employees retired to the disruption and delay that can be caused by staff turnover or even the temporary absence of a team member with a monopoly on specific operation critical parts of TANF data work:

- "I'm kind of the go to person for all things TANF, I'm kind of like a jack of all trades source of a lot of questions from a lot of different sources and have to be aware of all the data that we collect"
- "...my goal is to try and get it where more than one person knows what's going on."
- "One person [a consultant] knows how to do something and we're just giving that to that one person [it's a] bad thing if something happens"
- "When something rather complicated comes into our agency, whether it be from the feds or within the agency or public requests, I'm the person that's responsible for researching and sometimes making decisions based on precedent"

**Project Impacts**
- Many current systems require extensive training and/or institutional knowledge to successfully navigate. Consider how we can create as low a barrier to onboarding as possible in the new system. 
- Explore whether there are opportunities to distribute roles and permissions so as to make the absence of individual team members less disruptive to the reporting process.

### A variety of people and teams own different parts of the TANF report creation and submission process.

A number of participants spoke of technology workers or offices of technology that manage certain parts of the TANF Report preparation process. 

- "[Office of Technology workers] are the ones that actually compile and physically submit [the ACF-199] to ACF".
- "[Technical team] actually compile the ACF-199 and send it, but [case managers like myself] rely heavily on [doing things by hand]" .
- Overall team size ranged from a single person (not counting case managers who sat on other teams) to "a couple dozen".

Some TANF teams are a mix of government employees and vendors.

- "Some of the people, like the business analysts on the team, might be contractors who have signed confidentiality agreements and stuff."
- "... [Consultants] put all of that together into a file."
- "Deloitte is our primary contractor for the computer side of our programs. OK, so we do have merit staff that are primarily responsible at their jobs for handling the data... They do employ contractors to help with the staffing issues... And so I don't want to speak out of turn because I don't know what their structure is. Everybody in my department is state merit, but over at Oats (Deloitte) they have a combination of state merit and contractors.

Report generation is often a manual process, both for quarterly TANF reports and for a variety of other reports generated at the grantee level.

- "There's a lot of things I have to hand compile" and "there's a lot of steps before it gets to ACF [...] It's like we're in the 90s".
- "I seriously have some reports that are printed in PDF format that I have to manually look at and enter the reports into an Excel document".


**Project Impacts**
- Consider that “Data Prepper” may be a more variable role than our current definition does justice to. A lot of folks seem to play roles in getting TANF data over the line of being "submittable". They range from contractors working closely with government teams to case managers to program directors. 
- Update current process map to include vendor-STT team relationships to understand how STTs work with vendors to create and submit reports. This can help us determine how the new TANF program can be best used within their current process and where the new TANF program can eliminate pain points from the view of the vendor persona.






---





## About case management systems and other tools

> Primarily related to [Goal 4:](#What-we-wanted-to-learn)
> Deepen our understanding of how grantees create flat files and what causes metadata issues (including title, header, and trailer)


### Some case management systems are multipurpose with some degree of customization for TANF.

Multiple grantees spoke to how one or more of the software tools they use served some degree of double-duty for other offices or departments in their governments. 

- "And then we had a new vendor [shows terminal interface with menus for multiple STT programs including SNAP, Medicaid, and TANF"] 
- "We call it [single source of truth vendor system] the green screen, the green letterings, we call it the green screen. That's actually the platform which is used government wide"
- "We use the public health version [of vendor system] with our specific menus and that was built with a local vendor"

**Project Impacts**
- Consider how TDP can work *with* vendor systems and identify knowledge gaps for future research digging deeper into the TANF Grantee vendor space. It's clear now that (at least some) grantees have a far greater investment in these systems than just as a resource to help facilitate TANF.
- Identify proto-personas and scenarios which could help focus vendor research.
- Update current process map to include "the green screen" and products like it to house "the source of truth" for case data.

### TANF staff are navigating multiple software products from data collection through report submission.

Some grantees explained how they use internal software and vendor software to create, validate and upload their flat files.

- "...we decided to create a data mart on the data warehouse"
- "...using software on the mainframe that hits the data warehouse and create disk files on the mainframe and then submit those to ACF"
- "I don't want to have to use multiple software packages to groom the data to get just the way you guys want it"

**Project Impacts**
- Further exploration of the vendor persona and their journey can help us determine how our product can alleviate unnecessary touch points for both STTs and vendors.

### Editing often happens in case management tools, but a few tasks are completed directly in the flat file (in a text editor).

Grantees talked about how their first instinct would be to validate and manage their flat files prior to using our system. Grantees viewed our system's purpose as a submission tool rather than validation.

- Re: Concept Prototype: "since I've already looked at the data I've already corrected the data, everything should be good to go. I'm pulling the file over here to submit it. I mean, to me the next step should be just to end it"
- Re: Concept Prototype "I would investigate the source of the problem, whether it was a goofy entry by a county worker entering data access or some other thing. And that I would probably make the change, do the fix within my datamart"

One participant we spoke to carries out the responsibility of submitting the final year-end data to ACF leading up to the reporting deadline. This involved assembling a single flat file by copying and pasting the entirety of flat files into a blank text file to combine them into a single one.

- Re: year end revisions: "if I'm submitting multiple quarters, then I basically merge the files. And what I mean by merge is on the note pad [copy/paste of multiple flat files (in their entirety) into a txt],"

**Project Impacts**
- Consider how we could iterate on how we set up tasks and scenarios for future concept or usability testing so as to place the prototype being tested in an approachable context for the participant.
- Update current process map to incorporate editing of files via case management tools.