This is a place to document questions for future research.

## Source of data

- What are TANF recipients told about how their data may be used?
- In practice, what does it look like for a STT to collect data on TANF recipients and their work activities? What are common ways this information gets collected? (logs that case workers enter manually vs self reported from recipients vs automatic systems)

## Data transmission

- What is the data transmission experience like for STTs who do not prepare their data reports in-house? Meaning, their system handles data transmission or they've hired a third party vendor to manage data transmission.
- Understand the experience of STTs submitting universal data, as opposed to sample data. What systems and processes do they use?
- Do STT send TANF and SSP-MOE reports at the same time?
- What causes STT to resubmit data?
  - Are there common reasons why a STT may resubmit more frequently?
  - Which STT resubmit, and why? How often do they resubmit?
  - What does the process look like when they need to resubmit data? Are they starting over from the beginning or from an existing report?
  - How do STT and OFA designate a file as "final"?
- How do STT or OFA learn that a file has not been processed by the current system?

## Tribal TANF

- What does the data transmission experience for tribes with a 477 plan look like?

  - Is it different from other tribal data preppers?
  - How do 477 tribes navigate quarterly TANF reporting?

- Do all tribes submit a flat file? Or do they ever send in other data formats?

> from conversation with OFA, this is always a flat file.

- We have a theory that some tribes relied on fTANF to store case management data. Is that true and, if so, how did they use this tool to manage that data?

## Reports and feedback

- What information is most important to STTs when submitting a report and tracking data? What information do STT use from [the different reports currently produced by OFA](<https://teams.microsoft.com/l/file/480F7EF9-C6B1-40C2-8EC8-FDDB919356B1?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=docx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared Documents%2FGeneral%2FLegacy System%2FTANF and SSP Feedback Reports.docx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287>)🔒? What is missing?

## Data validation

- What validation checks should the new system include? [The current validation rules](https://github.com/HHS/TANF-app/wiki/Technical-considerations#known-data-validation-constraints) still let errors into the system, so we'll need to define what validation logic is needed.
- How do OFA analysts check data files for errors? Are they manually reviewing or do they have scripts they use?

> From OFA research, there are a mix of scripts and manual queries that are run to check data files and submission status
