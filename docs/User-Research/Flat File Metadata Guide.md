# Flat File Metadata Guide

[Issue #248](https://github.com/raft-tech/TANF-app/issues/248)

---

**Table of Contents:**

- [Background](#background)
- [Header structure](#header-structure)
- [Trailer strcture](#trailer-structure)
- [Flat file naming conventions](#flat-file-naming-conventions)
- [Other notes on file conventions](#other-notes-on-file-conventions)
- [Metadata validation definitions](#metadata-validation-definitions)
- [MVP metadata validation](#mvp-metadata-validation)

---

# Background

During OFA research, we discovered that submitted flat files have header and trailer errors. Further research is needed to understand how the header and trailer are created for flat files, what is the cause of the errors, and what information can be automatically added (by default), and what information needs to be added by STTs. Having this understanding would allow us to standardize header and trailers and gather the correct information from STTs when creating flat files for submission.

---

# Header structure

Example header:

`HEADER20152G02000TAN2 N`

| **Header Field**                           | **Excerpt / Decoding**                                       |
| :----------------------------------------- | :----------------------------------------------------------- |
| <br />**Title**<br /><br />                | <br />`HEADER` <br /><br />                                  |
| <br />**Calendar Quarter**<br /><br />     | <br />`20152` (Quarter 2 of 2015)<br /><br />                |
| <br />**Data Type**<br /><br />            | <br />`G` (Aggregate, i.e, TANF or SSP Report Section 3)<br /><br /> |
| <br />**State Fips Code**<br /><br />      | <br />`02` (Alaska)<br /><br />                              |
| <br />**Tribe Code**<br /><br />           | <br />`000` (This is equivalent to N/A, in this case the header refers only to Alaska as a state, not a tribe in Alaska)<br /><br /> |
| <br />**Program Type**<br /><br />         | <br />`TAN` (TANF Report, as opposed to SSP-MOE which would be coded as 'SSP')<br /><br /> |
| <br />**Edit Indicator**<br /><br />       | <br />`2` (Legacy data point that seems to refer to fTANF validation. '2' returns only Fatal Edits whereas '1' would return Warning Edits AND Fatal Edits)<br /><br /> |
| <br />**Encryption Indicator**<br /><br /> | <br />`Blank Space` (A blank means that social security numbers are NOT encrypted, 'E' in place of the blank would mean that they were encrypted)<br /><br /> |
| <br />**Update Indicator**<br /><br />     | <br />`N` (New Data, as opposed to Delete and Replace 'D', or Add and Update 'U'. Non 'N' values come into play during resubmission)<br /><br /> |



---

# Trailer structure

Example trailer:

`TRAILER0000042[9 blank spaces here]`

| **Trailer Field**                       | **Excerpt / Decoding**                                       |
| :-------------------------------------- | :----------------------------------------------------------- |
| <br />**Title**<br /><br />             | <br />`TRAILER` <br /><br />                                 |
| <br />**Number of Records**<br /><br /> | <br />`0000042` (Number of records in report in a seven-digit format)<br /><br /> |
| <br />**Blank Spaces**<br /><br />      | <br />` ` (9 blank spaces)<br /><br />                       |



---

# Flat file naming conventions

ADS.E2J. Does not change across report types or transmission methods. The third decimal delineated section (FTP# or NDM#) identify transmission method (SFTP vs Cyberfusion) and TANF or SSP-MOE report section in the file. The fourth section Identifies Program Type (TANF vs SSP-MOE as ‘TS’ or ‘MS’ respectively) followed by State Fips Code. In the case of Tribes, only TANF reports (TS) are submitted and a 3 digit Tribal Code follows.

For states and territories, ## represents their 2 digit Fips Code

| **Program** | **Transmission Method** | **Report Section** | **File Naming Convention** |
| :---------- | :---------------------- | :----------------- | :------------------------- |
| TANF        | SFTP                    | 1 (Active)         | `ADS.E2J.FTP1.TS##`        |
| TANF        | SFTP                    | 2 (Closed)         | `ADS.E2J.FTP2.TS##`        |
| TANF        | SFTP                    | 3 (Aggregate)      | `ADS.E2J.FTP3.TS##`        |
| TANF        | SFTP                    | 4 (Stratum)        | `ADS.E2J.FTP4.TS##`        |
| TANF        | CyberFusion             | 1 (Active)         | `ADS.E2J.NDM1.TS##`        |
| TANF        | CyberFusion             | 2 (Closed)         | `ADS.E2J.NDM2.TS##`        |
| TANF        | CyberFusion             | 3 (Aggregate)      | `ADS.E2J.NDM3.TS##`        |
| TANF        | CyberFusion             | 4 (Stratum)        | `ADS.E2J.NDM4.TS##`        |
| SSP         | SFTP                    | 1 (Active)         | `ADS.E2J.FTP1.MS##`        |
| SSP         | SFTP                    | 2 (Closed)         | `ADS.E2J.FTP2.MS##`        |
| SSP         | SFTP                    | 3 (Aggregate)      | `ADS.E2J.FTP3.MS##`        |
| SSP         | SFTP                    | 4 (Stratum)        | `ADS.E2J.FTP4.MS##`        |
| SSP         | CyberFusion             | 1 (Active)         | `ADS.E2J.NDM1.MS##`        |
| SSP         | CyberFusion             | 2 (Closed)         | `ADS.E2J.NDM2.MS##`        |
| SSP         | CyberFusion             | 3 (Aggregate)      | `ADS.E2J.NDM3.MS##`        |
| SSP         | CyberFusion             | 4 (Stratum)        | `ADS.E2J.NDM4.MS##`        |

For tribes, ### represents their 3 digit Tribe Code

| **Report Section** | **File Naming Convention** |
| :----------------- | :------------------------- |
| 1 (Active)         | `ADS.E2J.FTP1.TS###`       |
| 2 (Closed)         | `ADS.E2J.FTP2.TS###`       |
| 3 (Aggregate)      | `ADS.E2J.FTP3.TS###`       |

---

# Other notes on file naming



---

# Metadata validation definitions



---

# MVP metadata validation



---

