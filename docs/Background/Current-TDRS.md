# Background on Legacy System (TDRS)

OFA's TANF grantees in the states, territories, and tribes (STTs) are [legislatively-mandated](https://www.law.cornell.edu/uscode/text/42/611) to to report data via TDRS. OFA then aggregates the data and uses it for descriptive analyses and program performance monitoring, most notably through the [work participation rate calculations (WPR)](https://www.acf.hhs.gov/ofa/resource-library?f%5B0%5D=program%3A270&f%5B1%5D=program_topic%3A633&f%5B2%5D=type%3Aeasychart&keyword=&sort_by=combined_publication_date). The WPR measures how well states engage families receiving assistance in certain work activities during a fiscal year. STTs must meet both an overall (or “all families”) WPR and a two-parent work participation rate or be subject to a financial penalty.

Included herein is an overview of:
- **[the data](#about-the-data)**, 
- **[the legacy TDRS](#About-the-TANF-Data-Reporting-Sysyem-(TDRS))**, and
- **[the process through which data flow through the system](#About-the-data-reporting-process)**.

Additionally, **[FAQs](#FAQs)** related to the data and the system are included. 

## Overview
### About the data 
There are two categories of data reports that STTs submit to OFA--

**TANF data report (ACF-199)** include characteristics about families (and individuals therein) receiving federally-funded TANF assistance.

There is also the **SSP-MOE data report (ACF-209)**. As a condition of receiving federal TANF funds, states are required to spend a certain amount of their own funds (maintenance-of-effort or MOE) on TANF-allowable categories. This report includes characteristics of families (and individuals therein) receiving MOE-funded assistance.

### About the TANF Data Reporting System (TDRS)
TDRS was developed in the late 1990s to collect, validate, and store TANF data reported to HHS. Only minor updates have been made to the system in the past 20 years, so its functionality is limited (e.g. it is a backend-only system).  

### About the data reporting process

The TANF grantees usually **prepare** their data files using (1) a gov-furnished legacy tool (e.g. ftanf.exe) or (2) their own software to export data files in the required format. 

The data is then **transmitted** using a secure file transfer protocol (SFTP) onto an ACF server, which is monitored daily for new files. An ACF OCIO engineer picks up any new files and transfers them to another ACF server for processing/validation and storage into the national TANF database (RDMS). 

OFA data staff have read-only access to the dB and run SQL-like queries on the data to facilitate **data quality feedback** generation and **data publications**. 

See below for a visual of this data flow. 

![dataflow_tdrs](https://i.imgur.com/1bK7HMJ.jpg)
[Figma link to data flow](https://www.figma.com/file/irgQPLTrajxCXNiYBTEnMV/TDP-Mockups-For-Feedback?node-id=5617%3A47733)

We've also outlined what we've observed from [user research](https://github.com/HHS/TANF-app/blob/main/docs/User-Experience/Research/2020%2C%20Fall%20-%20Understanding%20STT%20Roles%2C%20Source%20of%20Truth%2C%20and%20Metadata.md) about how data is prepared, transmitted, and used. This includes details about: 
 * the kinds of data STTs can submit
 * tools STTs use to prepare data files (fTANF, etc.)
 * resources OFA provides to STTs on how to prepare and validate their files
 * the kinds of communications sent between OFA and STTs
 * the types of reports OFA publishes using this data

## FAQs
### Data preparation

**<details><summary>What is FTANF.exe?</summary>**

A desktop application designed by ACF's IT shop that STTs could download and use to prepare data files that could then be exported and transmitted to OFA. fTANF.exe can prepare all sections of data, check these data for the same types of errors that TDRS uses during processing/validation. The data could be entered by importing a previously-generated transmission file or by manual entry.  The application is no longer supported and is incompatible with newer versions of Windows, but many STTs with older versions of Windows still use it.
    
STTs using this tool are tracked [here](https://github.com/raft-tech/TANF-app/tree/raft-tdp-main/tdrs-backend/tdpservice/stts/management/commands/data). These STTs will have an `SSN_Encrypted` value of 1. This may change over time. 
</details>

---
### Data transmission

**<details><summary>When are the data reports due?</summary>**

Data reports are due within 45 days of the end of the fiscal quarter--

| Fiscal Quarter | Calendar Period | Due Date    |
| -------------- | --------------- | ----------- |
| 1              | Oct 1 - Dec 31  | February 14 |
| 2              | Jan 1 – Mar 3   | May 15      |
| 3              | Apr 1 – Jun 30  | August 15   |
| 4              | Jul 1 – Sep 30  | November 14 |

STTs are permitted to make corrections and re-transmit data throughout the fiscal year, but an end-of-fiscal year deadline is enforced after the fiscal quarter 4 data is due. 
</details>

**<details><summary>How do STTs transmit the data reports?</summary>**

Many STTs use SFTP clients like Winscp or IPSwitch. Others (especially STTs that manage their own legacy system) leverage Cyberfusion.     
</details>

**<details><summary>How many data files are included in each report?</summary>**

A minimum of 3 data files are included in each quarterly report--1 file per section (1, 2, and 3) of the TANF data report. Note:
* Section 4 is required *only* for STTs that submit data for a *sample* of its full caseload. 
    
* STTs that submit the SSP-MOE data report or sample data can vary by fiscal year. Their status for the current fiscal year are captured in the `SSP` and `Sample` indicators [here](https://github.com/raft-tech/TANF-app/tree/raft-tdp-main/tdrs-backend/tdpservice/stts/management/commands/data).
</details>

**<details><summary>How are the data organized in each file?</summary>**
    
TANF and SSP-MOE reports each have [4 data layouts](https://www.acf.hhs.gov/ofa/resource/tanfedit/index#transmission-file-header)--one layout per section of the report. The layouts between TANF and SSP-MOE are similar, but not identical.
    
**<details><summary>TANF</summary>**

#### Section 1 - active report
* *Structure*: one fixed width record per: (1) case and month and (2) case, person, and month for families receiving benefits through TANF
* [TANF Transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_data_report_section1_10_2008.pdf)
    * [Example file](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/tanf/ADS.E2J.FTP1.TS06?csf=1&web=1&e=hfI3Um) :lock:
    * [Instructions](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_instr_10_01_2008_tansec1.pdf)
    * [Form](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_form_reports_10_1_2008_tansec1.pdf)
* [Tribal TANF transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tribal_layout_for_section1.pdf)
    * [Example file](https://hhsgov.sharepoint.com/:t:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/tribal_tanf/ADS.E2J.FTP1.TS142.txt?csf=1&web=1&e=7BoNEz) :lock:
    * [Instructions](https://www.acf.hhs.gov/ofa/resource/tribal-tanf-data-coding-instructions)

#### Section 2 - closed report
* *Structure*: one fixed width record per: (1) case and month and (2) case, person, and month for families  who stopped receiving benefits through TANF
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_data_report_section2.pdf)
    * [Example file](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/tanf/ADS.E2J.FTP2.TS06?csf=1&web=1&e=DyDW6R) :lock:
    * [Instructions](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_instr_10_02_2007_tansec2.pdf)
    * [Form](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_form_reports_10_1_2008_tansec2.pdf)

#### Section 3 - aggregate report
* *Structure*: one fixed width record for the quarter that captures monthly counts of families that are applying for, receiving, and no longer receiving TANF benefits 
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_data_report_section3.pdf)
    * [Example file](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/tanf/ADS.E2J.FTP3.TS06?csf=1&web=1&e=txpefp) :lock:
    * [Instructions](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_instr_10_02_2007_tansec3.pdf)
    * [Form](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_form_reports_10_1_2008_tansec3.pdf)

#### Section 4 - stratum report
* *Structure*: one fixed width record for the quarter that captures monthly counts of families within each strata (Note: only relevant for STTs submitting Section 1 and Section 2 data that covers only a *sample* of the caseload)
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tanf_data_report_section4.pdf)
    * [Example file](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/tanf/ADS.E2J.FTP4.TS06?csf=1&web=1&e=HZhbOF) :lock:
    * [Instructions](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_instr_10_02_2008_tansec4.pdf)
    * [Form](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_form_reports_10_1_2008_tansec4.pdf)
</details>

**<details><summary>SSP-MOE</summary>**

#### Section 1 - active report
* *Structure*: one fixed width record per: (1) case and month and (2) case, person, and month for families receiving benefits through SSP-MOE
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/ssp_moe_transmission_format_section_1.pdf)
    * [Example file](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/ssp/ADS.E2J.NDM1.MS24?csf=1&web=1&e=nAxAFw) :lock:
    * [Instructions](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_instr_10_01_2008_sspsec1.pdf)
    * [Form](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_form_reports_10_1_2008_sspsec1.pdf)

#### Section 2 - closed report
* *Structure*: one fixed width record per: (1) case and month and (2) case, person, and month for families no longer receiving benefits through SSP-MOE
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/ssp_moe_transmission_format_section_2.pdf)
     * [Example file](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/ssp/ADS.E2J.NDM2.MS24?csf=1&web=1&e=IcVe3F) :lock:
     * [Instructions](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_instr_10_02_2007_sspsec2.pdf)
     * [Form](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_form_reports_10_1_2008_sspsec2.pdf)

#### Section 3 - aggregate report
* *Structure*: one fixed width record for the quarter that captures monthly counts of families that are applying for, receiving, and no longer receiving SSP-MOE benefits
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/ssp_moe_transmission_format_section_3.pdf)
    * [Example file](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/ssp/ADS.E2J.NDM3.MS24?csf=1&web=1&e=cpj3iQ) :lock:
    * [Instructions](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_instr_10_02_2007_sspsec3.pdf)
    * [Form](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_form_reports_10_1_2008_sspsec3.pdf)

#### Section 4 - stratum report
* *Structure*: one fixed width record for the quarter that captures monthly counts of families within each strata (Note: only relevant for STTs submitting Section 1 and Section 2 data that covers only a sample of the caseload)
* [Transmission file layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/ssp_moe_transmission_format_section_4.pdf)
     * [Example file](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/dev/Parsing/data/ssp/ADS.E2J.NDM4.MS24?csf=1&web=1&e=DY8e7u) :lock:
     * [Instructions](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_instr_10_01_2008_sspsec4.pdf)
     * [Form](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tdrs_form_reports_10_1_2008_sspsec4.pdf)
</details>
    
</details>

**<details><summary>How large are the data files from STTs?</summary>**

Data file sizes vary by section of the TANF/SSP-MOE reports and are as follows:
- Section 1: 123kb - 50,000kb
- Section 2: 14kb - 2,000kb
- Section 3: 1kb - 2kb
- Section 4: 1kb - 2kb
</details>

**<details><summary>How does TDRS decrypt data files from STTs?</summary>**

"Encryption" is an artifact of STTs using executables like FTANF.exe and SSPMOE.exe to prepare their data transmissions files. Encryption in this context means that the values in the SSN position of Section 1 and Section 2 data files are replaced with other alphanumeric characters. 
    
TDRS has a decryption script that runs on transmitted files if (and only if) the files have an "E" as the [encryption indicator in the header record](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/User-Experience/Research/2020%2C%20Fall%20-%20Flat%20File%20Metadata%20Guide.md#header-structure). For future reference: in the absence of checking the header record, if the SSN includes special characters, this is also evidence of encryption.
    
This decryption ensures that SSNs stored in the database can be used to match to other administrative data sources (e.g. matching to wage records to track employment outcomes for individuals receiving TANF). 

STTs using these executables are tracked [here](https://github.com/raft-tech/TANF-app/tree/raft-tdp-main/tdrs-backend/tdpservice/stts/management/commands/data). These STTs will have an `SSN_Encrypted` value of 1. This may change over time. 

The decryption code is included the [parsing notebooks](https://hhsgov.sharepoint.com/sites/TANFDataPortalOFA/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2Fdev%2FParsing&viewid=6ecbc5f1%2Dfa9c%2D4b0a%2Da454%2D35e222e8044e) :lock:
</details>

**<details><summary>How does TDRS determine that the data are acceptable to be stored?</summary>**

TDRS has a hierarchy of checks to determine if the data meet minimum standards for dB storage:
- *Are the file naming conventions valid?* If not, the data file(s) will not be transferred to the ACF server for processing/validation and storage. 
- *Does the file have the appropriate layout?* Here the system will essentially check the file to determine if there is sufficient information in the file to determine how to parse there data therein. These checks are to determine if the record layout is valid and the records are eligible to be parsed (aka _pre-parsing errors_). See **[mural](https://app.mural.co/t/raft2792/m/raft2792/1624455269095/a03c7a41f537ee50530451e7cb2a26fa11d2c9e6?sender=alexandrapennington7597)** and **pre-parsing section of [notebooks](https://hhsgov.sharepoint.com/sites/TANFDataPortalOFA/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2Fdev%2FParsing&viewid=6ecbc5f1%2Dfa9c%2D4b0a%2Da454%2D35e222e8044e)** for more details :lock:. 
- *Do the data have valid values and are the data consistent within and across records?* TDRS checks for out-of-range values (based on coding instructions) as well as for consistency between related data elements within and across records. Examples:
    * *out-of-range value*: Receipt of SNAP assistance (T1 record) can take on only 2 possible values: 1:Yes or 2:No.
    * *consistency within a record*: If SSI recipient = 1:yes then SSI amount received > $0 (T2 record)
    * *consistency across records*:  For every family (T1 record) for a given month, there is no evidence that at least one adult (T2 record) or child (T3 record) associated with the family's case is a TANF recipient.

Current TDRS checks (which are being revised and expanded upon for TDP) are included [here](https://www.acf.hhs.gov/ofa/policy-guidance/final-tanf-ssp-moe-data-reporting-system-transmission-files-layouts-and-edits#tanf-edits) and [here](https://www.acf.hhs.gov/ofa/policy-guidance/final-tanf-ssp-moe-data-reporting-system-transmission-files-layouts-and-edits#ssp-edits). 

**Important Note**: Acceptance and storage does not mean that transmitted data are error-free. OFA data staff conduct additional data quality checks to ensure accuracy, completeness, and consistency of the data within and across records and sections of the report over time. Data quality feedback reports are sent to STTs throughout the data reporting period (See feedback FAQ below for more details).
</details>

**<details><summary>What types of metadata does OFA collect about data transmissions?</summary>**

TDRS tracks data transmissions from the point that data files are *successfully* picked up for processing (i.e. if files are not picked up, no metadata is tracked) to storage into the dB. Metadata collected include: when the data was processed, the reporting period, all information from the [header record](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/User-Experience/Research/2020,%20Fall%20-%20Flat%20File%20Metadata%20Guide.md#header-structure), which tells the system how to process and store the data, and a list of any errors detected by the system. 

See [Transmissions notebook](https://hhsgov.sharepoint.com/sites/TANFDataPortalOFA/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2FDesign%2FTransmissionsDemo%2Ehtml&parent=%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2FDesign) for more details :lock:. 
</details>

**<details><summary>How are the data stored?</summary>**

Once the data are parsed and validated, they are stored in dB tables by record type. There are:
* 7 record types for TANF
* 6 record types for Tribal TANF (_tribal grantees do not currently submit section 4 data_)
* 7 record types for SSP-MOE

See **[parsing notebooks](https://hhsgov.sharepoint.com/sites/TANFDataPortalOFA/Shared%20Documents/Forms/AllItems.aspx?id=%2Fsites%2FTANFDataPortalOFA%2FShared%20Documents%2Fdev%2FParsing&viewid=6ecbc5f1%2Dfa9c%2D4b0a%2Da454%2D35e222e8044e)** :lock: for script to parse data by all of the abovementioned record types.  Most of the tables contain between 700,000 to 1,300,000 rows. 
    
The database currently is around 50GB in size, though most of it is historical data which will not need to be migrated. Access to this data is extremely limited, both because the data is sensitive (contains personally identifiable information or PII) and because managing access to these aging systems is difficult.
</details>

---
### Data quality 

**<details><summary>What languages, tools, and formats do OFA data staff use to work with the data?</summary>**
 - Languages
    - SAS
    - SQL
    - Python
    - R

- Tools
    - SAS Enterprise Guide; Base SAS
    - Jupyter Notebooks
    - VS Code
    - RStudio; Base R
    - Excel
    - Tableau

- Data Formats
    - .txt
    - .xls/.xlsx/.csv
    - .json

</details>

**<details><summary>What types of feedback do STTs receive from OFA about their data reports?</summary>**

![](https://i.imgur.com/cAesptu.png)
Examples of these reports can be found here :lock::
- [transmissions feedback](https://hhsgov.sharepoint.com/:u:/r/sites/TANFDataPortalOFA/Shared%20Documents/Design/TransmissionsDemo.html?csf=1&web=1&e=1navYZ)
- [monthly feedback](https://hhsgov.sharepoint.com/:x:/r/sites/TANFDataPortalOFA-UserResearch/Shared%20Documents/User%20Research/FeedbackRpts/Reference%20TANF%26SSP%20WPR%26TL%20Reports.xlsx?d=wdb175f3b3da54dd7ad49ce2a55e7cc2b&csf=1&web=1&e=ZjFqOv)
- [bi-quarterly feedback](https://hhsgov.sharepoint.com/:b:/r/sites/TANFDataPortalOFA-UserResearch/Shared%20Documents/User%20Research/FeedbackRpts/TANF%20Data%20Report%20(Form%20ACF-199)%20Section%201%20Questionable%20Cases%20Reference%20Guide.pdf?csf=1&web=1&e=50d7It)
</details>

---
### Data publications

**<details><summary>How are the data used by OFA?</summary>**

The table below is a representation of each publication OFA produces, frequency of the publication, and the sections of the data reports used to produce them. 
| Publication                                                                                                                                                                                                    | Frequency | Section 1 | Section  2 | Section 3 | Section 4          |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- | --------- | ---------- | --------- | ------------------ |
|                                                                                                                                                                                                                |           |           |            |           |                    |
| [Caseload Report](https://www.acf.hhs.gov/ofa/resource-library?f%5B0%5D=program%3A270&f%5B1%5D=program_topic%3A634&sort_by=combined_publication_date&sort_order=DESC&items_per_page=10)                        | Quarterly |           |            |:heavy_check_mark: |  |
| [Characteristics Report](https://www.acf.hhs.gov/ofa/resource-library?f%5B0%5D=program%3A270&f%5B1%5D=program_topic%3A584&f%5B2%5D=type%3Aeasychart&keyword=Characteristics&sort_by=combined_publication_date) | Annually          | :heavy_check_mark: |:heavy_check_mark:|:heavy_check_mark:|   :heavy_check_mark:|
|[Work Participation Report](https://www.acf.hhs.gov/ofa/resource-library?f%5B0%5D=program%3A270&f%5B1%5D=program_topic%3A633&f%5B2%5D=type%3Aeasychart&keyword=&sort_by=combined_publication_date)| Annually          |:heavy_check_mark: |            | :heavy_check_mark: | :heavy_check_mark:  |
|[Time Limits Report](https://www.acf.hhs.gov/ofa/data/tanf-federal-five-year-time-limit)| Annually |:heavy_check_mark:|            | :heavy_check_mark: | :heavy_check_mark: |
|[TANF Annual Report to Congress](https://www.acf.hhs.gov/ofa/resource-library?f%5B0%5D=program%3A270&f%5B1%5D=report_type%3A613)| Annually | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark:          |   :heavy_check_mark: |

</details>

## Additional resources:
* [Project Glossary](https://github.com/raft-tech/TANF-app/blob/raft-tdp-main/docs/Background/Project-Glossary.md) 
* [Instructions and form templates for all sections](https://www.acf.hhs.gov/ofa/resource/policy/pi-ofa/2008/200809/tanf-acf-pi-2008-07)








