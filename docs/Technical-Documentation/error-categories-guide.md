# Error Categories Guide

TDP checks submitted data files (and data therein) for errors by _first_ checking if the data file being uploaded is the correct [file type](https://tdp-project-updates.app.cloud.gov/knowledge-center/file-extension-guide) [(see PR for technical detail)](https://github.com/raft-tech/TANF-app/pull/2725), _then_ proceeding with a sequence of checks designed to determine if the data in the file can be parsed, and if so, find any issues with the data values reported. 

This guide provides a high-level overview of these types of errors. For more specific details, see [TDP's parsing directory](https://github.com/raft-tech/TANF-app/tree/develop/tdrs-backend/tdpservice/parsers) for current pre- and post-parsing validation logic.

## Category Definitions

Parity with the legacy system includes categories 1-4

1. **Pre-parsing errors** — These types of errors are considered to be violations of the expected record layout, so the records are not "eligible" to be parsed or validated. 

- [Header and Trailer record layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/transmission_file_header_trailer_record.pdf)
- [TANF and SSP record layouts](https://www.acf.hhs.gov/sites/default/files/documents/ofa/ACF-199-%26amp%3B-209-TANF-SSP-data-report-layouts-thru-2026-10.xlsx)
- [Tribal TANF Section 1 record layout](https://www.acf.hhs.gov/sites/default/files/documents/ofa/tribal_layout_for_section1.pdf)
  - Note: Tribal TANF Sections 2 through 4 are the same as TANF Sections 2 - 4 (referenced above). 


   Ex:

   ```Your file does not begin with a header record```,

   ```Header length is 2 characters but must be 23```

2. **Out-of-range value errors –** These are based on [TANF, SSP](https://www.acf.hhs.gov/ofa/policy-guidance/acf-ofa-pi-23-04), and [Tribal TANF](https://www.acf.hhs.gov/ofa/policy-guidance/tribal-tanf-data-coding-instructions) coding instructions.

   Ex:

   ```Item 76 (Citizenship/Alienage) must be in set of values [0, 1, 2, 9]```,

   ```Item 2 (County FIPS Code) must be 3 digits```

3. **Errors re: inconsistent values across data elements within a record –** These are based on [TANF, SSP](https://www.acf.hhs.gov/ofa/policy-guidance/acf-ofa-pi-23-04), and [Tribal TANF](https://www.acf.hhs.gov/ofa/policy-guidance/tribal-tanf-data-coding-instructions) coding instructions. (e.g. If SSI recipient = yes, then SSI amount received > $0).

   Ex:

   ```If Item 30 (Family Affiliation) is 1 then Item 34F (Marital Status) must be in set of values [1, 2]```,

   ```If Item 32 (Date of Birth) is blank or 99999999 then Item 30 (Family Affiliation) must be in set of values [2, 3, 5] ```

   

4. **Errors re: inconsistent values across related records within a section file –** These errors are also based on the abovementioned instructions (e.g. For every family (T1) record for a given month, there is no evidence that at least one adult (T2) or child (T3) associated with the family's case (T1) is a TANF recipient)

    Ex:
```If Item 9 (Reason for Closure) is 3 then at least one T5 (Closed Person) on the case should have Item 21 (Relationship to Head-of-Household) as 1-2 and Item 26 (Number of Months Countable toward Federal Time Limit) of 60 or greater.```



5. **Errors re: inconsistent values across related sections of data –** These errors are based on DIGIT-generated checks, and some reference material included in abovementioned feedback rpts. Because sections of data can be submitted at different points in time, current thinking around these checks suggest that these errors would need to be checked against data from the dB (e.g. total #of families reported in Section 1 > total # families reported in Section 3)

6. **Errors re: inconsistent values across related records and/or sections over time** — Also based on DIGIT-generated checks and would benefit from checks against data from the dB (e.g. state did not submit enough case records to meet annual sample size requirements)

## Plain language category names

| Category # | Internal name                                                | Plain language name      |
| ---------- | ------------------------------------------------------------ | ------------------------ |
| 1          | Pre-parsing errors                                           | File pre-check           |
| 2          | Out-of-range value errors                                    | Record value invalid     |
| 3          | Inconsistent values across data elements within a record     | Record value consistency |
| 4          | Inconsistent values across related records within a section file | Case consistency         |
| 5          | Inconsistent values across related sections of data          | Section consistency      |
| 6          | Inconsistent values across related records and/or sections over time | Historical consistency   |

## Other categorizations of TANF data

### Program types

1. TANF (associated with T`x` record types)
2. SSP-MOE (associated with M`x` record types)
3. Tribal TANF ((associated with Tribal T`x` record types))

### Sections

1. Active Case Data
2. Closed Case Data
3. Aggregate Data
4. Stratum (or Sample) Data

### Record Types

| Record Type Indicator | Record Type Name            |
| --------------------- | --------------------------- |
| T1/M1/Tribal T1                    | Family Case Characteristics |
| T2/M2/Tribal T2                    | Adult                       |
| T3/M3/Tribal T3                    | Child                       |
| T4/M4/Tribal T4                    | Closed Family Case          |
| T5/M5/Tribal T5                    | Closed Person               |
| T6/M6/Tribal T6                    | Aggregate Count             |
| T7/M7/Tribal T7                    | Count by Stratum            |

