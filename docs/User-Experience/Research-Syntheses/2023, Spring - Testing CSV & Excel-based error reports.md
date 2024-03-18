# Spring 2023 - Testing CSV & Excel-based error reports

## Contents:
* [Key insights](#Key-insights)
* [Who we talked to](#Who-we-talked-to) 
* [What we did](#What-we-did)
* [What we tested](#What-we-tested)
* [What we learned](#What-we-learned)
* [What's next](#Whats-next)
___

### Key insights 
As research conducted in [January 2023 Errors Research](https://hackmd.io/WxtMOPCUQiO-JHjahVMPDQ) focused on error messaging and specific internal workflows occuring after data submission, our research in this cycle explored the end-to-end error report experience and simulated it in the direct context of the file formats that the parsing engine will ultimately produce.



- All participants were able to automatically open all variations of the error report prototypes that we tested in Excel. Participants were also able to expand collapsed columns themselves, but we found that it decreased time and effort on the part of the grantee when we provided versions of the prototype with columns that were pre-expanded to fit their content.

    - **Impact**: As a consequence of this finding and conversations with the development team we shifted from CSV format to XLSX to take advantage of AutoFit column widths to enhance the immediate readability of reports.


- We identified which columns should be included—and in what order—to maximize the actionable : extraneous data ratio of reports. 
    - **Impact**: Case Number, Month, and Error Message columns proved most critical for participants with Item Number and Field Name frequently assessed as a "nice to have". A final prototype reflecting our complete findings in this area will be produced for [#2527](https://github.com/raft-tech/TANF-app/issues/2527) and include the following columns: 

      | Case Number | Month | Error Message | Item Number | Field Name |
      | ----------- | ----- | ------------- | ----------- | ---------- |
    
- Item number and field name represent an area where the language used in TANF documentation has shifted over time. Participants frequently appeared more familiar with the term "Data Element" than "Item" or "Field" but were ultimately all able to make the correct association with the relevant content of the data reporting instructions. 
    - **Impact** After discussions with ACF regarding upcoming revisions to the instructions "Item number" does reflect the preferred terminology going forward. This will be captured in [#2527](https://github.com/raft-tech/TANF-app/issues/2527) and additionally justify future knowledge center content to address any resulting confusion for TDP users. 

**Overall the feedback on the post data file submission was positive and encouraging to continue developing the email communication notice and Error Report.**

> “This [Excel file] is helpful too [...] after further review, I’m able to understand the spreadsheet more. I’m excited for this project!" - Tribe

> "I think this excel sheet is more user friendly than the [legacy system report] table. I think this has more information than compared to what I get now" - State

> "[...]I think this is perfect. Once I knew what I was looking at it’s very easy to follow." - Tribe

> “I’m excited about [having this in] an online portal. One of the things that was an issue prior was they would ask for proof that we submitted and we didn’t have it.” - Tribe

> "I like the words and not just the [item] numbers. This saves me a step." - State
___



### Who we talked to

We recruited based primarily on the following criteria:
* Participants from past error message research sessions
* TANF programs which had previously encountered errors on their Section 1 data files
* Programs and past participants who had expressed specific interest in participating in research sessions

Research sessions were conducted with:
* 5 States
* 4 Tribes
___

### What we did

Our research was conducted in order to:

* Test the usability of an Excel-based error report located in Submission History to evaluate whether participants would be successful in downloading, opening, and ultimately acting on the reports. 
* Explore optimal column structures and data needed to help guide error correction and cut down on the time required to understand the report itself.

___

### What we tested

During these sessions, we wanted to simulate the future experience of the error reports with our participants. We asked participants to:

* Speak about their expectations at each step of the process including the error report email, the submission history page (including acceptance status and the link to the error report), and the downloadable error report prototype itself. 
* Open the error report prototype once they downloaded it. 
* Identify the meaning in their own words of key columns.
* Rank the columns in order of their priority in regard to error correction.
* Use the Error Report as if they were using it to resolve the errors listed and expand on how it might fit into their current workflows.

**Supporting Documentation:**
- [A variation of our HTML/XLSX prototype](https://reitermb.github.io/HTML-Table-example/xlsx-login)
___

### What we learned

Jump to: 
* [Collapsed columns in the Error Report created extra steps for participants when first opening the CSV-based prototype](#Collapsed-columns-in-the-error-report-created-extra-steps-for-participants-when-first-opening-the-csv-based-prototype)
* [We identified which columns should be included—and in what order—to maximize the actionable : extraneous data ratio of reports](#we-identified-which-columns-should-be-includedand-in-what-orderto-maximize-the-actionable--extraneous-data-ratio-of-reports)
* [Participants use the coding instructions in conjunction with the Error Report for error definition, but it can be challenging to know whether all information is available](#Participants-use-the-coding-instructions-in-conjunction-with-the-error-report-for-error-definition-but-it-can-be-challenging-to-know-whether-all-information-is-available)
* [Item number and field name represent an area where the language used in TANF documentation has shifted over time](#Item-number-and-field-name-represent-an-area-where-the-language-used-in-TANF-documentation-has-shifted-over-time)
* [We further validated the utility of submission history and notification emails as ways for TANF programs to show proof of transmission for audit purposes](#We-further-validated-the-utility-of-submission-history-and-notification-emails-as-ways-for-tanf-programs-to-show-proof-of-transmission-for-audit-purposes)

---

#### Collapsed columns in the Error Report created extra steps for participants when first opening the CSV-based prototype

The following observations were made of the first few participants when opening the initial file format of .csv (comma-separated values)

-  Participant expanded the columns one-by-one manually
-  Participant began to expand the first few columns, but then stopped as the screen size hid the final column from view
-  One participant did not expand any of the columns and moved from cell to cell to read the content in the formula bar 
-  The Case Number field was truncated by Excel and could not be easily read (e.g. 1.111+08)

After this initial round of review we determined (via conversations with the product and development teams) that we could move forward with a .xlsx file format which could take advantage of column AutoFit. All further research sessions were conducted with the .xlsx-based prototypes, which eliminated the need for participants to adjust columns and allowed more time to be spent dedicated to the content of the error report.

---

#### We identified which columns should be included—and in what order—to maximize the actionable : extraneous data ratio of reports.

We started the first few research sessions with a version of the column headers and iterated as we went on to further sessions based on early participant feedback. 

Our first version used the following columns/orderings:


| Case Number | Month | Item Number | Field Name | Error Message | Error Type |
| ----------- | ----- | ----------- | ---------- | ------------- | ---------- |



> “I’m not sure about the item number - what does this represent?” - Tribe

> “I don’t know what item number and field name are.” Initial reaction was that the Error Report did not provide the information they needed - State

> “I’d suggest removing item number and field name but leave the rest” - Tribe

> “I would prefer the Error Message come before the Item Number and Field Name” - Tribe

After the first three research sessions we reevaluated our hypothesis that that Item Number and Field Name near the beginning was the most digestible way to present an error report. Those columns coming before the Error Message seemed to be at odds with participant's priorities and expectations.

Our subsequent version—used for the remaining research sessions—had the following columns/orderings:


| Case Number | Month | Error Message | Item Number | Field Name | Error Type |
| ----------- | ----- | ------------- | ----------- | ---------- | ---------- |


> “I like the flow of the columns - Tribe

> “I think the sequence is good for me” - State

> “I am strictly looking at Case Numbers, Month and Error Message here. The rest is noise to me” - State

> “I think these columns are pretty good at showing me where things are at” - Tribe

We received a wide range of feedback around the utility of Item Number and Field Name. Participants who had many years of experience with TANF data tended to feel they were redundant to the Error Message—but might be useful for those new to correcting TANF data. Others seemed to appreciate the degree to which those columns reinforced key parts of the Error Message.

While this research did not directly content test Error Types, some participants were able to correctly interpret their meanings. However, it seemed that the primary way Data Analysts categorize different types of errors among themselves is by classification under their Item/Field names. For example, a Data Analyst receiving the error, "If Item 49 (Work Participation Status) = 99 Or Blank, Item 30 (Family Affiliation - Adult) Must = 2-5" would consider its type to be a "Work Participation Status Error". 


---

#### Participants use the coding instructions in conjunction with the Error Report for error definition, but it can be challenging to know whether all information is available

When we asked participants to use the error report prototype to resolve the errors they consistently understood how to pair it with the coding instructions. 

> “I want to cheat here” (Participant referring to the Tribal Coding Instructions as a cheat sheet while responding to a particular error) - Tribe 

> “I will look at this line and then go to the guide to find more information for Item 7” - State 

> “The way the error report is… it is kind of like a maze where we have to go here and then back” - Tribe

While all had access to at least some of the coding instructions, it wasn't always clear whether the participants had the latest or even complete versions of them. We observed one participant who had printed a few pages to keep in their workspace to help handle common errors.

> “Is there any updated code instructions book so that we have the latest?” - State

> “Can you get to the Instructions from [the excel error report] or no?” - Tribe

Linking to the coding instructions; and particularly linking directly to relevant items may help reduce lookup times and make the whole process easier to navigate for those new to TANF data coding.

> “A link to the coding instructions would not be helpful because it is 97 pages long”. - State

---

#### Item number and field name represent an area where the language used in TANF documentation has shifted over time.

The term “Item Number” originated from the fTANF system where each field is labeled as “Item [x]”. However, in the current coding instructions, it is referred to as a "Data Element". 

> “Are Item Numbers related to Data Elements?” - State

> “What is it called… it’s not item number…” (Participant flips through a printed excerpt of the Coding Instructions) - Tribe

After discussions with OFA regarding upcoming revisions to the coding instructions "Item number" does reflect the preferred terminology going forward. All participants ultimately managed to connect the two terms, but this is still a likely area for future knowledge center content such as an FAQ item to reassure TDP users that they're making the correct connection of terms.

---

#### We further validated the utility of submission history and notification emails as ways for TANF programs to show proof of transmission for audit purposes

The error report email and submission history page would serve to help answer two common questions that Data Analysts—and/or their auditors—have after data file submission. "When did we transmit the data files and has ACF received them?"" 

> “Referenced the transmission file as what they still gets for confirmation on when files are transmitted to ACF.” - State

> “Transmission report is what the auditors get to show that I’ve met the timeline” - State

> “The date and time that I submitted is critical for the auditors” - State

> “Auditors want proof” - State

Participants also spoke to the usefulness of TDP's notification emails for fulfilling elements of these audits. 

A common subsequent question is "Are my files without errors or do they need correction?". While evaluating TDP's acceptance statuses were not a primary goal of this research, multiple participants did respond to its presence in our prototype—commentating on acceptance status and its lack of clarity in TDRS.

> “[After I submit] has it been accepted or is the data okay? Is it acceptable data? Do I need correct anything?” - Tribe

> “[I] wasn’t too clear whether the current transmission report provided [all] errors or files were transmitted successfully” - State



---

### What's next
- We plan to capture final prototype encompassing all changes informed by this research in [#2527](https://github.com/raft-tech/TANF-app/issues/2527). 
- Further errors research with participants from this round who submitted files with errors for the May 15th deadline to repeat many elements of this test but directly in the context of their real data (rather than example data).
