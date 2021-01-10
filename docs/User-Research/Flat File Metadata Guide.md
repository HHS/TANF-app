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

| **Header Field**                     | **Excerpt / Decoding**                                       |
| ------------------------------------ | ------------------------------------------------------------ |
| <br />**Title**<br />                | <br />`HEADER` <br />                                        |
| <br />**Calendar Quarter**<br />     | <br />`20152` (Quarter 2 of 2015)<br />                      |
| <br />**Data Type**<br />            | <br />`G` (Aggregate, i.e, TANF or SSP Report Section 3)<br /> |
| <br />**State Fips Code**<br />      | <br />`02` (Alaska)<br />                                    |
| <br />**Tribe Code**<br />           | <br />`000` (This is equivalent to N/A, in this case the header refers only to Alaska as a state, not a tribe in Alaska)<br /> |
| <br />**Program Type**<br />         | <br />`TAN` (TANF Report, as opposed to SSP-MOE which would be coded as 'SSP')<br /> |
| <br />**Edit Indicator**<br />       | <br />`2` (Legacy data point that seems to refer to fTANF validation. '2' returns only Fatal Edits whereas '1' would return Warning Edits AND Fatal Edits)<br /> |
| <br />**Encryption Indicator**<br /> | <br />`Blank Space` (A blank means that social security numbers are NOT encrypted, 'E' in place of the blank would mean that they were encrypted)<br /> |
| <br />**Update Indicator**<br />     | <br />`N` (New Data, as opposed to Delete and Replace 'D', or Add and Update 'U'. Non 'N' values come into play during resubmission)<br /> |



---

# Trailer structure



---

# Flat file naming conventions



---

# Other notes on file conventions



---

# Metadata validation definitions



---

# MVP metadata validation



---

