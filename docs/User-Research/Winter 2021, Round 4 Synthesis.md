# Winter 2021, Round 4 Synthesis 

[Issue #669](https://github.com/raft-tech/TANF-app/issues/669)

---

**Table of Contents:**

- [What We Wanted to Learn](#what-we-wanted-to-learn)
- [Whom We Talked To](#whom-we-talked-to)
- [What We Learned (Top Insights)](#what-we-learned-top-insights)
- [What We Learned (Additonal insights, hypotheses, and validations)](#what-we-learned-additional-hypotheses-and-validations)
- [What's Next](#whats-next)
- [Footnotes](#footnotes)

---

## What We Wanted to Learn 

**Our goals for this research were to:**
- Prioritize the pain points we identified from previous rounds for urgency and immediacy 
- Cross-reference interlocking pain points between OFA and STTs
- Narrow our current set of personas to the most comprehensive primary personas so that the journey map and, consequently, our STT MVP is scoped to include the most pressing organizational needs at this time 

**Our research questions were:**
1. Which gaps in knowledge in our current state journey maps are high priority?
2. Which STT pain points take priority for the upcoming STT MVP? What do we want to test?
3. Are there OFA pain points and STT pain points overlapping and therefore more efficient to solve together?
4. Which personas have the most different experiences? How can we be sure we’ve covered the most diversity?
5. Are there behavioral changes implicated in the data process map that we can address in the target state or aspirational state maps?

**We also added two sprint responsive research questions:**

6. What, if any, loose ends exist for OFA MVP which might be revealed by usability testing and design auditing?
7. What insight might regional managers and OFA staff provide to engaging STT Users in on-going user research? 

---

## Whom We Talked To
**This round, we talked to the OFA DIGIT team and Regional Offices, and five participants from States that:**

- Had not participated in past research
- Submit Universe Data
- Submit Sample Data
- Have caseloads either less than 3,500 per month or greater than 9,500

---

## What We Learned (Top Insights)

Included in the learnings of this round is that our participants prefered to be called "Data Analysts" over "Data Preppers", and we will use that convention from here on in.


### Analysts value data cleansing/validation that allows them to predict whether their submission will be accepted
>Related to research questions 3 and 5

One ST data analyst discussed that he has a program from a third party that cleanses and validates the data for him before he submits it, and it “predicts whether or not a submission would be accepted.” Other analysts indicated an interest in having this ability. 

**Project Imapacts**
- We will plan an interview with the vendor of the program and a look at the software application to leverage a competitive analysis with HMDA's data cleansing process in designing our solution.`  
- We validated the hypothesis that STTs cannot receive immediate plain language feedback on how to correct data quality errors.

### A useful distinction between data cleansing and data validating
>Related to research question 5

We clarified for our internal use that there are actually two data quality issues ("cleansing" and "validating"), and the terminologies that our users, stakeholders, and our UX team use varies in talking about it. 

**Project Impacts**
- We conducted secondary research on appropriate data analysis terminology. We determined that we would call the data prep phase the “data cleansing” phase and the submission phase “data validation” phase for our team. [[1]](#footnotes)
- We understand that “data validation” is the process of verifying that raw data has been appropriately “cleansed.”
- We generated the hypothesis that providing support for the data cleansing phase might help reduce the number of fatal errors in the validation phase. We've earmarked this for later testing and validation efforts for STT-MVP. 


### Holidays can impact the ease with which grantees can meet reporting deadlines
>Related to research question 2

Holidays and 45 Day transmissions sometimes don't line up and create confusion. This insight offers another factor at play within a previously uncovered grantee pain point; that due to time constraints, preparing data which comes in for the last month in a quarter is often more difficult than preparing the data for the first two months.

**Project Impacts**
- This should be the subject of a OFA-MVP post-launch user testing session or workshop.


---

## What We Learned (Additional insights, hypotheses, and validations)


### It's important to remember that not all data analysts are responsible for data cleansing.
> Related to research question 4
> See also [[2]](#footnotes)


**Project Impacts**
- This, so far, does not suggest a need for a second persona. Rationale: If we design for data analysts who do data cleansing and data validation, we have coverage across both scenarios.


### Variations in data preparation likely don't require additional personas
> Related to research question 4
> See also [[2]](#footnotes)


We further validated our hypothesis that one persona covers most ST participants' experience in this workshop because the variation in preparation did NOT impact the negative experience of cross-referencing errors as the number one pain point in need of a solution. 

**Project Impacts**
- We will further attempt to falsify this hypothesis in the next Tribal and ST workshop.



### Insights from design audit, usability testing, and Regional Managers & Staff workshop
> Related to research question 6


**INSIGHT 1** 
Our OFA-MVP prototype was missing some components to the user flow.
- This drove our proposed changes with design rationale to the prototype based on the audit outcome. See also [[3] and [4]](#footnotes)



**INSIGHT 2**
In addition to missing components in user-flow, our OFA-MVP prototype needed refinement in human-computer interactions along two axes:
1. Physical interaction (the number of clicks needed to complete a given task)
2. Mental clarity (in this case, we focused on UX language to make sure we used the words used on the prototype in a way that most users could understand).


**INSIGHT 3** 
Based on our meeting with OFA regional and tribal TANF staff, we came up with potential strategies for continuing user engagement in the process of co-creating the TDP solution. [[5]](#footnotes)


R&D team is designing a communication and user workshop and testing plan calendar to be proactive in communicating with STTs for maximal accessibility and engagement to and with this project.

---

## What's Next

**Immediate Next Steps**
- Further validate the number of discrete personas as necessary and explore OFA-specific personas (OFA Admin, OFA Analysts, Regional Staff) and STT program managers
- OFA MVP final testing of prototype focusing on further clarity of UX Language
- Next ST Workshop on the Research Pathway to collaboratively design user flow and validate journey map
- Tribal Workshop (See issues [#667](https://github.com/raft-tech/TANF-app/issues/667) and [#747](https://github.com/raft-tech/TANF-app/issues/747))
- Make sure to include conversations about vendor interactions and vendor-sourced software used for data cleansing.
- Calendar and Plan for Workshops

**Future Validations**
- Grantees prefer to fix errors before submission instead of submitting as-is reports with errors.
- Post-launch validations: possibly points toward cleansing being prioritized over data validation error messaging?
- Investigate variability of data cleansing approaches
- Researching with OFA DIGIT if they track data on when they get most data submissions relative to report submission deadlines.

---

## Footnotes
**[1]** 
We consulted multiple sources, and they were all in agreement, but we used [this open-source one](https://dataresponsibly.github.io/courses/documents/spring19/data-validation-and-data-cleaning.pdf) as authoritative. 
 
**[2]** 
For evidence see [ST Workshop Board](
https://app.mural.co/t/officeoffamilyassistance2744/mural-password/officeoffamilyassistance2744/1613491508274/7cf6d22e727671899d3d1417c2b7e9505eee7f38) :lock:
 
**[3]** 
See [Figma Design Audit](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=4043%3A20688)
 
**[4]** 
See Figma Board [Testing Results](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=3873%3A0) and [Proposed Changes & Current Annotated Mockups](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=3588%3A800)
 
**[5]** 
See [OFA RO & Tribal Workshop Mural](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1614628817099/a7ffd7a8ddaa3baa0581bce2cbf53cc57d1ec4bb) :lock:
