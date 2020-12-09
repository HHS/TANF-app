## [TANF APP prototype](https://github.com/HHS/TANF-app-archive)
* How was it created?
  * 18F developed this to test and validate assumptions about if the TANF data file format could be parsed and put into a modern, open source system.

* Current state of development
  * Allows uploading and viewing of txt files.
  * No data validation exists, but it includes the data model of TANF reports for all sections.
  * Includes configuration to be deployed to cloud.gov.
  * Includes configuration for authorization through login.gov.
  * Does not include code linting or tests.
  * This new TDRS prototype was built to test assumptions about the primary goal of this project. At the time of the release of this RFQ, the prototype allows users to upload data in the TANF data reporting format and view the resulting data. It conducts limited data validation of the submissions.

  * It is a Python/Django app with Login.gov integration, and running in Cloud.gov. The OFA team uses SQL with their existing analysis tools, so 18F developed the prototype with a Postgres SQL database. The contractor may extend, extract useful parts, or replace the prototype application entirely.

  * The prototype provided an opportunity to develop an application environment. 18F and OFA have been working together to get core technical infrastructure approved and set up so when the contractor joins the team they can immediately begin to contribute code and have it automatically roll out to their development environment.



## [CSV FTANF prototype](https://github.com/HHS/TANF-app/blob/master/ftanf.py)
* How was it created?
  * Created by OFA and 18F to explore how CSV data could be converted to the flat txt file format.
* Current state of development
  * Initial Excel template and converter script built for [Section 3](https://teams.microsoft.com/l/file/972DF490-7C3B-49F1-B086-890C4F8B0E6C?tenantId=d58addea-5053-4a80-8499-ba4d944910df&fileType=xlsx&objectUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2FGeneral%2FUser%20research%2F2020%20Spring%20local%20experience%20research%2FExcel%20templates%20to%20test%2FFTANF%20Section%203.xlsx&baseUrl=https%3A%2F%2Fhhsgov.sharepoint.com%2Fsites%2FTANFDataPortalOFA&serviceName=teams&threadId=19:f769bbcb029f4f02b55ae7fad90e310d@thread.skype&groupId=41f194a6-c1d3-4680-933e-c8ee7d17e287)🔒 and Section 4.
  * Usability tested the Excel template with grantees in Spring 2020.
  * Paused for now


## [Error page mock ups](https://gsa.invisionapp.com/share/Y5WTQ1XK947#/screens/413210493_tdrs2--section-1-w-errors)
* How was it created
  * Design concept in Invision to guide user research conversations about how grantees troubleshoot data errors
* Current state of development
  * Exists in Invision
