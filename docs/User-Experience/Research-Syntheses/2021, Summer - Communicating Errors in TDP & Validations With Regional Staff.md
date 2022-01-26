# 2021, Summer - Communicating Errors in TDP & Validations With Regional Staff

Research Round 7 - [Issue #1017](https://github.com/raft-tech/TANF-app/issues/1017)

---

**Table of Contents:**

- [Who we talked to](#who-we-talked-to)
- [What we did](#what-we-did)
- [What we tested](#what-we-tested)
- [What we learned](#what-we-learned)
- [What's next](#whats-next)

---

## Who we talked to

Round 7 research included participants representing: 

- The OFA DIGIT team (Pre-parsing Error Workshops).
- OFA Regional Staff (Regional Staff Journey Workshop).
- Seven grantee participants across three states who had experienced one or more pre-parsing error in recent submissions (Content Testing workshops):
  - Three grantee data analysts.
  - One grantee program director.
  - Two grantee staffers who interact with TANF data from other policy/data analysis oriented roles.

---

## What we did

### Regional Staff Journey Workshop

**Objectives / Insight Areas**

- Follow up on past research with OFA analysts that had informed prospective journey maps for OFA regional staff.
  - Validate/Correct/Expand regional staff journey maps given input *from* regional staff.
- Capture the current interactions with/view into grantee teams that regional staff have.
- Document information regional staff would need to have to feel comfortable approving a grantee user's access to TDP.

### Pre-parsing Error Workshops (2)

**Objectives / Insight Areas**

- Capture the full set of pre-parsing errors.
- Align around the meaning of those errors and the grantees impacted by them.
- Ideate on new error copy that could accurately convey the meaning of all pre-parsing errors. 
  - Test the new copy with the DIGIT team to capture their input into Do's, Don'ts, and accuracy, and actionability. 

### Grantee Content Testing Workshops

**Objectives / Insight Areas**

- Refine ideations from the Pre-parsing Error Workshops into lo-fi mockups.
  - Evaluate error mockups for clarity, usefulness, and actionability.
- Document the data points that grantee data analysts rely upon to find records or cases that contain errors in their case management software.
- Capture the steps they would take to fix an error and resubmit to determine whether TDP would be disruptive or be able to smoothly take the place of SFTP transmission in current processes.

### Synthesis Workshop

**Objectives / Insight Areas:**

- Share research insights with a broader cross-functional slice of the team.
- Affinity map insights and co-create themes.
- Identify actionable next steps and vote on their priority.

**Supporting Documentation:**

- [Regional Staff Journey Workshop Board](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1629404914670/04e319e4922e14214a1f5b3e12864d12dc8d2975?sender=mreiter1745) :lock:

- [Pre-parsing Error Workshops Board](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1629404865218/d048e5d323fbefbfa2dc3a748d1d6fc923c02f08?sender=mreiter1745) :lock:

- [Grantee Content Test Workshops Board](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1629404959587/ecfc0bfc8be2af4b19a20ab45afe624d8dd4e7ba?sender=mreiter1745) :lock:

- [Synthesis Workshop Board](https://app.mural.co/t/officeoffamilyassistance2744/m/officeoffamilyassistance2744/1629404764806/8081a78f0c82a6632027c8e9a1a7d43a7a457908?sender=mreiter1745) :lock:


---

## What we tested

We refined three pre-parsing errors from our workshops with DIGIT into full lo-fi errors that allowed us to test the impact of several error patterns including:

- Plain language error names
- Legacy error names

- Split errors 

- "See More" links

- Error Instance(s)

We matched our errors were matched with grantee participants accordingly to which errors might be more familiar to them due to past submissions. 

### Error One

> | Case record is missing Adult or Child record                 | T1-502 |
> | ------------------------------------------------------------ | ------ |
> | Case record ##### has no associated Adult or Child records. All Case records should be associated with at least one Adult record **or** one Child Record. |        |
>
> Associated checks: 
>
> - Each Adult record must be associated with one Case record. 
> - Each Child record must be associated with one Case record.
>
> Key:
>
> | Record Type  | Type Indicator |
> | ------------ | -------------- |
> | Case Record  | T1             |
> | Adult Record | T2             |
> | Child Record | T3             |
>
> For more details, refer to the Section 1 (Active Cases) [Transmission Layout]()

### Error Two

> | One or more records contain data from the wrong quarter      | T1-513 |
> | ------------------------------------------------------------ | ------ |
> | You're currently submitting data for Quarter 2 (January - March) of Fiscal Year 2021 but your file contains records for months outside of that range. |        |
>
> | Associated Record | Case Number  | Fiscal Year / Month | Value in file | Line in file |
> | ----------------- | ------------ | ------------------- | ------------- | ------------ |
> | Adult Record      | ############ | 2021 / January      | "`202001`"    | 5            |
> | Child Record      | ############ | 2021 / May          | "`202105`"    | 68           |
>
> Key: 
>
> | Record Type  | Type Indicator |
> | ------------ | -------------- |
> | Adult Record | T2             |
> | Child Record | T3             |
>
> For more details, refer to the Section 1 (Active Cases) [Transmission Layout]()

### Error Three

> | One or more of your records is too short                     | T1-517 |
> | ------------------------------------------------------------ | ------ |
> | One or more of your records is shorter than the expected length of 71 characters. This indicates that is has missing data, or that it wasn't coded correctly. We won't be able to read the following records until they are corrected and reuploaded: |        |
>
> | Associated Record    | Case Number  | Fiscal Year / Month | Line in file |
> | -------------------- | ------------ | ------------------- | ------------ |
> | Closed Person Record | ############ | 2021 / May          | 5            |
> | Closed Person Record | ############ | 2021 / May          | 6            |
> | Closed Person Record | ############ | 2021 / June         | 102          |
>
> Key:
>
> | Record Type          | Type Indicator | Expected Character Length |
> | -------------------- | -------------- | ------------------------- |
> | Closed Case Record   | T4             | 71                        |
> | Closed Person Record | T5             | 71                        |
>
> For more details, refer to the Section 2 (Closed Cases) [Transmission Layout]()

### Content Testing Process

1. We asked participants take their time reading each error and then to write in their own words how they might communicate it to a colleague to help them facilitate correction. 
2. We captured—verbally and/or via annotations—participant perceptions and thoughts about all the granular detail within each error, e.g., "Tell us about 'T1-502', what if any meaning did it convey to you?". 
3. We captured instances of specific terminology or data not being at all familiar to the participant. 
4. We had participants vote on Likert scales (Strongly Disagree - Strongly Agree) to capture a quantitative measure of how they felt about each error. The Likert prompts were the following:
   - I can understand this error message.
   - I have a clear idea of what my next step is.
   - I gained useful information from this error message.
   - This error message is conversational.

---

## What we learned

- [Regional staff have the closest OFA-side view into the makeup of grantee teams, but that view is not always complete](#regional-staff-have-the-closest-ofa-side-view-into-the-makeup-of-grantee-teams-but-that-view-is-not-always-complete)
- [We documented "error patterns"  that may be utilized throughout error guidance in TDP](#we-documented-error-patterns--that-may-be-utilized-throughout-error-guidance-in-tdp)
- [Error Content Testing Results](#error-content-testing-results)
- [Grantees rely on a variety of data and techniques to look up specific cases or records within their case management software](#grantees-rely-on-a-variety-of-data-and-techniques-to-look-up-specific-cases-or-records-within-their-case-management-software)
- [Specificity and putting the *right* data points in front of the right grantee is key to their ability to effectively act on an error](#specificity-and-putting-the-right-data-points-in-front-of-the-right-grantee-is-key-to-their-ability-to-effectively-act-on-an-error)

---

### Regional staff have the closest OFA-side view into the makeup of grantee teams, but that view is not always complete.

Regional staff participants told us that while they're often at the forefront of contact between OFA and Grantees, they don't have comprehensive information into the full makeup of those grantee teams that they work with. Like OFA analysts, their contact tends to be with some subset of grantee staff. However, regional staff shared that they will usually know who the grantee program director is, as well as have frequent contact with whoever is taking the lead on data cleansing/validation. They compared the dynamic to a "social club", where transparency into membership is dependent on referrals from those who are already in it. 

**Project Impact(s):**

As there is no requirement for grantees to submit verifiable data about their teams, it seems likely that this "social club" dynamic will need to continue in regard to requests for TDP access. Ways we can investigate to add security into that include:

- Giving grantee program directors a standardized way to submit a request for access for somebody on their team within TDP.
- Requiring that non-director grantee staff have been authorized by their program director (via the above) to receive the access they're requesting.
- Clearly displaying information about new users requesting access for the regional staff who will be approving them. (e.g email address, associated STT, associated/referring program director, etc...)

---

### We documented "error patterns"  that may be utilized throughout error guidance in TDP.

**Naming Patterns**

Plain Language Error Names

- Affords glanceability (and potentially referenceability) to a user who might not be familiar with legacy error codes, or who might not have them committed to memory.

Legacy Error Names

- Largely for those either playing a role in designing their own grantee level systems or those already highly familiar with existing error codes. Draws a through line showing which legacy errors map to newer, plainer language TDP errors. Can be used alongside the newer error names.

**Scope Patterns**

Split Errors

- There seems to be potential to make certain legacy TDRS errors more actionable by splitting them into several variations. For instance, the "Other" error type could differentiate between a record being too short and too long as opposed to only communicating that a record is the wrong length. 

**Guidance Patterns**

"See More" Links

- Provides additional guidance for errors that are much more involved to fix (e.g. "Other") or any other errors when lengthier guidance is warranted and useful. In the early versions of TDP this is likely less common, unless we prioritize the creation of new guidance content to supplement current error and transmission layout documents.

Side-by-sides

- Errors that compare data submitted against what was expected. Can potentially be blocked by data issues severe enough to block parsing as a whole. In cases where user input can't be predicted, the "Expected" side would be limited to an example or a breakdown of the relevant layout.

Snippets

- Overlaps with side by sides, snippets are simply excerpts or breakdowns of parts of the submitted file or parts of the expected layout. The distinction is simply that a snippet could be used with or without user input depending on the context (e.g. in guidance content that's accessible pre-submission or around submissions, not just specific errors during a specific submission)

**Call to Action Patterns**

Bypass

- In-app ability to actively ignore and dismiss certain errors.

Review

- Guidance that states exactly where to "confirm" / "review" / "check" errors in the source file. Includes markers like case number and record type when possible to allow for referencability in case management systems.

In-app Edit

- Interactivity to allow changes to a file directly from TDP; revisions & resubmissions. Could apply to missing data or existing data.

**Organization Patterns**

Summary

- Answers the question of "Which types of error have I gotten for each of my sections?"

Error Instance(s)

- Answers the question of "For a given error showing up in the summary, how many are there and where are they within the section/file?"

Sort by / Group by

- Toggles the display of errors, e.g. by error type vs by record (when a record has errors)

**Project Impacts(s)**

- These patterns give us an organizational framework for continued error ideation as we continue work relating to the Errors epic on the research roadmap; it will serve as a short-hand for patterns within design spec and evaluative research aimed at delivering templates for all types of errors TDP will parse and check files for.



---



### Error Content Testing Results.

Participants all managed to identify the basic meaning of each error we tested, however many were confused along the way by unnecessary data or data elements they don't rely on to look up errors in their case management software (e.g. Line number was confusing for a participant who simply relied on case numbers and wasn't overly familiar with viewing data in the flat file itself). 

#### Error One (Case record is missing Adult or Child record)

![Missing Adult or Child Record](https://user-images.githubusercontent.com/28515874/131410564-c0b3a6ef-f353-4048-afa6-0ba12ae52bb7.png)

**Quantitative results:** 
Tested with four participants

I can understand this error message: (3 somewhat agree, 1 neither agree nor disagree)
I have a clear idea of what my next step is: (1 somewhat disagree, 3 somewhat agree)
I gained useful information from this error message: (1 somewhat disagree, 1 somewhat agree, 2 strongly agree)
This error message is conversational: (1 strongly disagree, 1 somewhat disagree, 1 neither agree nor disagree, 1 somewhat agree)

**Participant Rephrasings**

> "Basically I would say that an individual, either a child or adult, needs to be added to the record."
>
> "The case record entered has no affiliated individuals.  Please check the case record number for accuracy and try again."
>
> "Individual recipient information is missing or incomplete from the sampled case record. Review data provided and update."

#### Error Two (One or more records contain data from the wrong quarter)

![One or more records contain data from the wrong quarter](https://user-images.githubusercontent.com/28515874/131410856-64cd20e5-faf7-4a6a-b69c-6ac21844e2a0.png)

**Quantitative results:** 
Tested with two participants

I can understand this error message: (1 somewhat agree, 1 strongly agree)
I have a clear idea of what my next step is: (1 somewhat agree, 1 strongly agree)
I gained useful information from this error message: (1 somewhat agree, 1 strongly agree)
This error message is conversational: (1 neither agree nor disagree, 1 strongly agree)

**Participant Rephrasings**

> "You've put the wrong months in the Q2 data"
>
> "The file seems to be pulling data for the incorrect months.  Please review a sample of the cases provided and the months that is pulling for the report."

#### Error Three (One or more of your records is too short)

![One or more records is too short](https://user-images.githubusercontent.com/28515874/131410988-3f1c5320-1390-4e93-986c-54775fdab09a.png)

**Quantitative results:** 
Tested with six participants

I can understand this error message: (1 neither agree nor disagree, 2 somewhat agree, 3 strongly agree)
I have a clear idea of what my next step is: (1 somewhat disagree, 2 somewhat agree, 3 strongly agree)
I gained useful information from this error message: (1 somewhat disagree, 1 somewhat agree, 4 strongly agree)
This error message is conversational: (2 neither agree nor disagree, 1 somewhat agree, 3 strongly agree)

**Participant Rephrasings**

> "The report is failing due to missing data.  Please review data to determine root cause."
>
> "Missing data - probably a leading zero - not very clear where the error is."
>
> "data is incomplete, missing, or individuals are coded incorrectly; review and resubmit 3 records, 3 lines"
>
> "Please note that record submissions must meet the 71 character requirement.  One or more of your files has not met this requirement.  Please review uploads and try again."
>
> "One or more records is missing data or is coded incorrectly"
>
> "One of more of your records has missing data or it is not coded correctly. The expected character length for each record is 71 characters."

---

### Grantees rely on a variety of data and techniques to look up specific cases or records within their case management software.

| Error Lookup Method                 | Additional Details                                           | Participant Comment(s)                                       |
| ----------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| Custom IDs for cases and recipients | We discovered that some grantees have case management systems that introduce metadata external to required federal data, or the data used in tools like fTANF meaning that some grantees have additional tools (like their own ID numbering system) for finding a distinct TANF recipients or other records. | "Client ID that is tied to each person is important to me", "review # is an internal reference [for us]" |
| TANF Item Numbers                   | Some grantees rely on the item numbers inherent to required TANF data and tools like fTANF.  e.g., Item 15 of Section 2 translates to Date of Birth. | "item 28 gives us errors [frequently", "we use Item number"  |
| Line Number                         | Line number refers to the line (numbered from the top of the file) of a record within a flat file. Few grantees make significant corrections in flat files, preferring to work with data in their case management systems, but we have heard from some participants that they have to fix "Other"/T1-517 errors via manual edits to their flat files. We've hypothesized that those who do that will be more familiar with line number than those who don't. | "Line number would be easiest to look up a case, not everyone has a SSN", "Confused as to what 'Line in file' means" |
| Case Numbers                        | Some participants rely on case numbers to find the location of errors, this can involve either searching for them within the flat file itself, or searching their case management system. | "Usually what I do is to ctrl f and enter the case number, sometimes I search with the SSN but it looks like this is probably not associate to a specific person so that would be less useful here." |
| Individual Data                     | Some participants told us that they've frequently used data on individual recipients of TANF to look up specific cases. Using the last four digits of a social security number or birthdates being two examples. Which is used can depend on other factors including whether the individual has a shared birthday with another family member and whether they have a social security number yet. | "Last 4 for SSN or DOB would be good to have to locate the case faster", "A new born might not have a SSN" |

### Specificity and putting the *right* data points in front of the right grantee is key to their ability to effectively act on an error.

We found that in addition to the aforementioned techniques and data points that grantees rely on for data lookup, participants were confused when presented with data connected to the methods they *don't* use. e..g, if one participant relies upon fTANF-like item numbers to break down records and look up the location of an error, they were likely to have been thrown off when they saw data like "Line in file" rather than "Item Number". 

> "I don't know what "Line in file" refers to" - From a grantee who isn't very familiar with the process of looking up data inside the flat file itself
>
> "Line number would be easiest to look up a case, not everyone has a SSN" - From a grantee who told us it's one of the data points they rely on

**Project Impact(s):**

- This finding lead us to the user story, "As a grantee data analyst I only want to see data attributes useful for looking up records in my system.". The idea being investigating a way to allow different grantees to see errors presented in different ways in TDP via grantee-level or user-level customization. 

---

## What's next

Follow-on content testing with grantees

- Evaluate pre-parsing error content with Tribal grantees.

- Test the impact on data analyst's ability to determine how many cases/records are impacted by an error when real case numbers are present in  error mockups rather than placeholders (e.g. ############).
- Internal Design/DIGIT/Development workshop to determine what we can do to "highlight" where the problem is inside of long records within submitted files.
  - Test a version of the Other/T1-517 error that includes highlighting with grantees.

We spoke to one grantee who relies on 3rd party vendors for data *correction* as well as data submission. This was a past finding but we still need to determine whether these situations will be best served by direct access to TDP or by exportable/shareable error reports. The "Vendor Inclusion" epic in the Spikes section of the research roadmap will investigate this further. 

---
