# Winter 2024, Evaluating FRA Submission & Error Reporting

Supports[ #3297](https://github.com/raft-tech/TANF-app/issues/3297)

***

## Background, Motivation and Goals

The Interim Final Rule on TANF Work Outcomes Measures (implementing Section 304 of the Fiscal Responsibility Act or FRA) requires state/territory TANF agencies in to submit three new reports, the first of which (the mandatory quarterly Work Outcomes of TANF Exiters report) will be due for the first time in May of 2025 and is the first requirement for TDP's FRA-relevant functionality.&#x20;

#### Research Goals

* Evaluate key components of TDP's FRA Report #1 (Work Outcomes of TANF Exiters) workflow including:
  * Submission workflow (how to select the fiscal period that the report covers, how to upload/submit the report, and how to access previous submissions)[^1]
  * Error Report presentation and content (A & B variations of how FRA error reports will be presented to users)
* Document how state/territory teams plan to produce the Work Outcomes of TANF Exiters report from data in their own systems.
* Increase our understanding of FRA submitter team makeup.

#### Key Research Questions

* Who will submit FRA reports? Are they the same people who already have TDP accounts for TANF/SSP data?
* What problems might occur in FRA report submission that we would expect users to correct?
* What elements of the FRA reporting experience are most/least confusing for users?
* How might we best illustrate which period of data is due for a given submission deadline? (i.e. FRA equivalent of fiscal : calendar period table)
* How might we best highlight where problems exist in provided FRA reports?&#x20;
* Is FRA submission history similarly useful for internal STT audit purposes as TANF/SSP submission history?&#x20;
* Concept testing prompts (capturing user reactions as they interact with our prototype/mockups) for: Submitting/resubmitting an FRA report, Accessing submission history and Interacting with an FRA report error

***

## Approach and Methodology

Our sessions relied on a combination of user interviews, prototype concept testing, and A/B testing to evaluate the FRA file submission workflow and two variants of FRA error reports.&#x20;

* The interview portion identified participant responsibilities, their current workflows, and their state of planning for FRA readiness.
* Concept testing measured participant reactions to our prototyped FRA workflow; particularly focusing on the unified submission/submission history design and whether participants could successfully identify the correct reporting period for the May 2025 FRA due date.
* A/B testing compared two variants of FRA error reports; particularly focusing on identifying and understanding participant preferences between the two relevant to perceived clarity, and ease of use of their ability to act to correct errors.

While content testing was not the main focus of this research, we did evaluate whether participants understood the errors mocked up in the error report variants; listening to them voice their reactions aloud or prompting them to rephrase the errors in their own words when necessary. To minimize the potential of leading participants toward one A/B variant over another, we alternated which was presented first between each session.

***

### Participants

We recruited a total of 12 participants representing 5 states who had been following emerging OFA guidance on new FRA requirements across a total of 5 research sessions. One participant from one state ultimately chose not to complete the research session as their role was not relevant to the production or submission of TANF or FRA data files to TDP.&#x20;

The remaining 11 participants had varied responsibilities including directing TANF programs, policy advisement closely relevant to data in TANF or FRA reports, case management, data analysis, and file submission to TDP. All four participants who directly drove our prototypes had familiarity with current TANF/SSP submission functionality in TDP.&#x20;

***

## Insights, Findings and Recommendations

### 1. Participants voiced an exclusive preference for Version A of the error report; highlighting the utility of SSN in efficient error correction

Impact: **High**     Participants Affected: **11/12**

> **"**&#x53;o it \[Version A] took me straight to where the error is, I think it's more user friendly and requires less familiarity. " - P2

From this finding, we have a sense of what error reports should look like for STTs. Both versions of the error report were interpretable by participants but Version A was exclusively favored once they had seen both. Participants expressed that it was simpler to quickly identify what errors had been found in the context of their submitted data, that it would save them time switching between multiple documents, and that SSN in particular would be the primary way they would look up the relevant data in their own systems to correct an error. This aligns with insights from past research indicating SSNs are useful search terms when locating an individual in case management systems.

One participant said that while they would prefer Version A, that Version B might be more appropriate (since it doesn't include SSNs) for passing on to their vendor team should changes need to be made to their automations based on error reports. It should be noted that this vendor team would not be direct TDP users. \
\
**Recommendation(s)**

Implement Version A with appropriate redactions/limitations to avoid unnecessary SSN duplication

### 2. Two participants noted that the data disclosure statement would add complexity for them in the report generation process if it were a required part of the template

Impact: **High**     Participants Affected: **2/12**

> "One thing that is annoying to this design is ultimately I'm going to be downloading data first through my SAS program and then through the automated process and it's going to come where columns are true data format. I would prefer this to be a separate table as a read me" - P1

Participants suggested that if the disclosure is required it could be relocated to a readme sheet or a second document. This stems from all participants we spoke to being in the process of building system automations to export the Work Outcomes of TANF Exiters reports. The report itself isn't complex but adding a header cell containing static rather than dynamically populated data adds complexity to their planned automations or a manual step post-generation and pre-submission.\
\
**Recommendation(s)**

Error Report Implementation, we will host disclosures in an entirely separate document or the disclosures statement to a separate tab of the report template/error report.&#x20;

### 3. Participants consistently navigated the submission workflow without issue, but choosing the correct Fiscal Year/Quarter may prove confusing for some users as with TANF/SSP data

> "I think this is what \[other state office] would be doing, not me. I would select 2025, the first Quarter and do a search and this is where I would upload the data. Pretty easy!" – P4

Impact: **Medium**     Participants Affected: **11/12**

The consolidated submission & submission history page tested in the prototype wasn't remarked upon by participants directly but successfully delivered on its intended goal of leading users to immediately read submission history results and open the error report. Because TANF/SSP submission history contains more complex data, some further ideation will be required to align this submission workflow enhancement into TANF/SSP pages, but this research validates the core design as highly functional.

> "It's just helpful when it says identifying the right fiscal year and quarter, the table there has generic names for Fiscal Year it would help me if there were specific numbers" – P2

As we've found with TANF/SSP data, it can be challenging to determine which reporting period should be selected for a given data submission. Multiple participants leveraged the provided table to inform their selections but we observed one instance of selecting Q4 rather than the (in our testing scenario) correct option of Q1. One participant also mentioned that the table could be made clearer by making the listed fiscal years specific (e.g., 2025, 2026, etc.. rather than "FY").&#x20;

**Recommendation(s)**

Related to ticket #3391 Design Spike - Enhancement to Submission Screen to Flag Wrong Fiscal Period&#x20;

### 4. STTs we spoke to were in various stages of planning to support the various FRA reports, with planning for the first due being most developed&#x20;

Impact: **N/A**     Participants Affected: **TBD**

We found that while there is significant overlap in the participants we spoke to and those responsible for TANF/SSP data, STTs have been engaging in a variety of internal conversations that reach outside of TANF-specific roles to prepare for FRA compliance. This includes strategizing reporting process adjustments with data partners and planning investments into technical systems to allow for  export of the new FRA reports themselves.

> "For the new FRA requirements it's just the 45 day deadline. We suggested to ACF 75 day turnaround so we can see the data settle. Because we have a monthly update to our warehouse it gives time to settle." – P5

Alongside ongoing preparations for FRA requirements, one participant was curious about opportunities to adjust submission requirements to better reflect the timelines data processing happens on in their systems before instruction from OFA is fully solidified.&#x20;



<table><thead><tr><th width="371">Key Research Questions</th><th>Summary Insights</th></tr></thead><tbody><tr><td>Who will submit FRA reports? Are they the same people who already have TDP accounts for TANF/SSP data?</td><td>Participant responses indicate significant, but not necessarily universal overlap with those who currently submit TANF data. <br>As with TANF, larger teams contain many surrounding roles consulting/informing on data but not submitting it.</td></tr><tr><td>What problems might occur in FRA report submission that we would expect users to correct?</td><td>SSN/Reporting period validation simulated by our error report prototypes align to internal checks being implemented/planned for by our participants. Participants also don't anticipate errors since they have internal systems, checks, and code in place prior to submission.<br></td></tr><tr><td>What elements of the FRA reporting experience are most/least confusing for users?</td><td>Testing suggests that the unified current submission / submission history interface is simple to understand and highly functional in quickly directing user attention toward submission status and the error report. </td></tr><tr><td>How might we best illustrate which period of data is due for a given submission deadline? (i.e. FRA equivalent of fiscal : calendar period table)</td><td>Most participants appeared to have ignored the table. One session suggested providing specific dates to the months of the Fiscal Year.</td></tr><tr><td>How might we best highlight where problems exist in provided FRA reports? </td><td>All participants preferred Version A for their own internal use and stressed the importance of being able to directly identify and look up relevant SSNs. Version B was suggested by one participant to be useful for their external vendor team. Two participants noted that the data disclosures should be in a separate document or excel sheet.</td></tr><tr><td>How effective are the concept tests when it comes to <br>a. Submitting/resubmitting on FRA reports b. Accessing submission history </td><td>a. All participants had/were building support for systems capable of exporting this first FRA report. Corrections will be made upstream, re-exported, not manually changed in excel<br>b. Participants didn't explicitly note the combined page but did immediately shift into reading submission history / opening the error report<br></td></tr></tbody></table>

## Next Steps and Action Items&#x20;

#### Further Ideation/Designs for Chosen Report Type on FRA Data Submission Page

Not only will the other FRA reports not involve selection of fiscal quarters, they will benefit from their own  guide content (table) to align due dates and fiscal years. To ensure users are able to select the correct report (once all are being submitted) and the correct fiscal period is selected for a given due date we will create design spec / table content for all three of the future report options.&#x20;

## Supporting Documentation

* [TANF Work Outcomes FRA Package](https://www.acf.hhs.gov/media/35532)&#x20;
* [Mural to New Data Requirements (FRA)](https://app.mural.co/t/raft2792/m/raft2792/1727290532610/6aa6777c80afd0eb6cd7b17ec569f2afa991e692?sender=uf443e00cb4626b8bec157528)
* [Figma ideations](https://www.figma.com/design/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=9284-1183\&t=uVBYIX3DmzBG7MKv-1)
* [Version A Prototype ](https://reitermb.github.io/TDPrototype/knowledge-center/index.html)
* [Version B Prototype](https://reitermb.github.io/TDPrototype/knowledge-center/index2.html)
* [FRA Research Sessions Affinity Mapping](https://app.mural.co/t/raft2792/m/raft2792/1732564281598/dcead26cbc0379f5f51aba1b56ca4656d64b9ef5)

[^1]: how to select the fiscal period that the report covers, how to upload/submit the report, and how to access previous submissions of the report? is this correct?&#x20;
