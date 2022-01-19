# STT Attributes Guide

[Issue #449](https://github.com/raft-tech/TANF-app/issues/449)

---

# Overview
We created this guide to provide context to the [STT Attributes Spreadsheet](<https://hhsgov.sharepoint.com/:x:/r/sites/TANFDataPortalOFA-UserResearch/_layouts/15/doc2.aspx?sourcedoc=%7BF34F9CF0-70F3-46B4-A708-1764C5B3F4BC%7D&file=STTs%20Attributes%20(Current%20Version).xlsx&action=default&mobileredirect=true>):lock: and to describe how we plan to use the data in the spreadsheet to inform qualitative research. This is a living document and will expand and evolve as we gather more data and move along the product roadmap. 

We collaborated with OFA analysts to gather reports that contained information related to data submission errors for all of the grantees from Quarter 3 2018 to Quarter 2 2020. We are starting our analysis with two data sets focused on data quality and common errors given the critical role of data quality in the success of TDRS:

- [Error count across submissions and resubmissions](https://hackmd.io/_PV7z3UAQmOPKbuFQ2BuOQ#Number-of-errors-discovered-from-TANF-reports-for-all-STTs)
- [Error types across submissions and resubmissions](https://hackmd.io/_PV7z3UAQmOPKbuFQ2BuOQ#Most-frequent-errors-from-TANF-reports-for-all-STTs)

---

## Error count across submissions and resubmissions
OFA report categorized errors for submissions and resubmissions as total number of fatal errors, warning errors, and other errors. We differentiated errors in the first submission from errors that occurred in subsequent resubmissions and updated the STT Attributes document accordingly.


**Relevant Documentation:** 
- [Non-parsed data: STTs_First and All Submission Errors_Q3 2018 - Q2 2020](<https://hhsgov.sharepoint.com/:x:/r/sites/TANFDataPortalOFA-UserResearch/_layouts/15/Doc.aspx?sourcedoc=%7B4A62EF0A-65D5-47D9-AF88-E4495C33E9E7%7D&file=STTs_First%20and%20All%20Submission%20Errors_Q3%202018%20-%20Q2%202020.xlsx&action=default&mobileredirect=true>) :lock: 

## Error types across submissions and resubmissions

From the error report provided by OFA, we chose a selection of the data to generate the following subsets:

- most frequent errors across all STTs
- errors that affected the most states and territories
- errors that affected the most tribes

From there, we integrated the following data into the STT Attributes document:

- Top 25 errors that impact the highest number of STTs
- Top 25 errors by frequency across all STTs


**Relevant Documentation:** 
- [Non-parsed data: STTs_Most Frequent Errors from the First Submission_Q3 2018 - Q2 2020](<https://hhsgov.sharepoint.com/:x:/r/sites/TANFDataPortalOFA-UserResearch/_layouts/15/Doc.aspx?sourcedoc=%7BE6487C87-E85B-47CA-9E37-50E68BA4BA99%7D&file=STTs_Most%20Frequent%20Errors%20from%20the%20First%20Submission_Q3%202018%20-%20Q2%202020.xlsx&action=default&mobileredirect=true>) :lock: 

## How we plan to use the data

**Error communication research.**
Updating the STT Attributes guide with error data will allow us to develop more targeted recruitment criteria for future rounds of research.

**Product KPIs**
We will use current error rates to develop key performance indicators to measure data quality over time and measure product performance in reducing errors and streamlining error management.

**Prioritization**
Error frequency will help scope research and prioritize feature development.


## Definition of Terms
- *Fatal Errors* : Errors that can not be processed into the OCIO database
- *Warning Errors* : Errors that can be processed into the OCIO database but represent data quality issues
- *Total Errors* : Sum of fatal, warning, and other errors
- *N/A*: No fatal, warning, or other errors detected by TDRS validation checks (note: OFA data team does additional QC and may detect issues)
- *Other Errors*: TDRS detected an issue but did not specify it. Often related to length of header, trailer, or T1, T2, etc. records. 
- *Error_Code* : Code used for error lookup within the [OFA TANF Error Edits Index](<https://www.acf.hhs.gov/ofa/resource/tanfedit/index>)
- *Error_Freq*: Aggregated number of error instances found for each type of error from all states or tribes








 







