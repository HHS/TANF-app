## Data Extracts

The following datasets may be used for testing

- `TANF_T1_DataSurge_2025-09-10-084149.csv.xz` contains a de-identified version of FY24 TANF Active Family-level records (Record Count=2360870). These data are needed for the WPR and TL calculations. Case numbers within state/terr have been replaced with anonymized versions. This is needed for the WPR and TL calculations.

- `TANF_T2_DataSurge_2025-09-10-084149.csv` contains a de-identified version of FY24 TANF Active adult-level records (Record Count=2458920). These data are needed for the WPR and TL calculations. Case numbers within state/terr have been replaced with anonymized versions. SSNs have also been replaced with anonymized versions that are also technically invalid. `SSN_Invalid` indicates if the real SSN was invalid before anonymization. DOBs have been converted to age as of the first of the reporting month (`AGE_FIRST`). `invalid_DOB` indicates if the real DOB was invalid before age conversion. `is_duplicate` indicates if there is more than one record with the same values for the following columns (before anonymization): `['STT', 'FIPS_CODE','RPT_MONTH_YEAR', 'CASE_NUMBER','SSN','DATE_OF_BIRTH' 'RELATIONSHIP_HOH','FAMILY_AFFILIATION']`.

- `TANF_T3_DataSurge_2025-09-10-084149.csv` contains a de-identified version of FY24 TANF Active child-level records (Record Count=4369546). These data are needed for determining the age of the youngest child on the family's case. Case numbers within state/terr have been replaced with anonymized versions. SSNs have also been replaced with anonymized versions that are also technically invalid. `SSN_Invalid` indicates if the real SSN was invalid before anonymization. DOBs have been converted to age as of the first of the reporting month (`AGE_FIRST`). `invalid_DOB` indicates if the real DOB was invalid before age conversion. `is_duplicate` indicates if there is more than one record with the same values for the following columns (before anonymization): `['STT', 'FIPS_CODE','RPT_MONTH_YEAR', 'CASE_NUMBER','SSN','DATE_OF_BIRTH','RELATIONSHIP_HOH','FAMILY_AFFILIATION']`.

- `TANF_T6_DataSurge_2025-09-10-084149.csv.xz` - contains TANF Aggregate data covering the FY24 period. This is needed for weighting. (Record Count=648)

- `TANF_T7_DataSurge_2025-09-10-084149.csv.xz` - contains TANF Stratum data covering the FY24 period. This is needed for the weighting. (Record Count=936)

- `expected_outputs/sorted_weights_2024.csv.xz` contains the expected FY24
  statistical weights output generated from the T1, T6, and T7 fixture inputs.

- Notes:
  - the family-level and person-level records can be linked by STT, FIPS_CODE,RPT_MONTH_YEAR, and CASE_NUMBER.
  - the disaggregated records (i.e. family-, adult-, and child-level records) can be linked to aggregate records by STT, FIPS_CODE, and RPT_MONTH_YEAR
  - the stratum records and family-level records can be linked by STT, FIPS_CODE,  RPT_MONTH_YEAR, and STRATUM, where TDRS_SECTION_IND = 1 (for Section 1: Active)
  - SSP datasets can be provided upon request.

## Loading the statistical weights test data

The statistical weights ETL reads parsed TANF T1, T6, and T7 records through
accepted `DataFile` rows. These compressed CSV extracts are not raw fixed-width
submission files, so they should not be sent through the parser. Load the
weights fixture data directly with:

```bash
python manage.py load_statistical_weights_test_data \
  --data-dir tdpservice/etl/test/data \
  --fiscal-year 2024 \
  --replace
```

The command loads only `TANF_T1_*`, `TANF_T6_*`, and `TANF_T7_*` files ending in
`.csv.xz`, `.csv.gz`, or `.csv`, preferring `.csv.xz` when multiple forms are
present. It creates synthetic TANF `DataFile` rows with `state=parse_completed`,
`year=2024`, and a high fixture version, then attaches parsed rows to those
files by `FIPS_CODE + RPT_MONTH_YEAR`. Federal quarters are derived from
`RPT_MONTH_YEAR`: October through December map to `Q1`, January through March to
`Q2`, April through June to `Q3`, and July through September to `Q4`.

The fixture inputs are stored as per-file `.csv.xz` archives so individual
large extracts can be updated independently. Expected ETL outputs live under
`expected_outputs/` and use the same per-file `.csv.xz` compression convention.

To regenerate the compressed fixture files from local raw CSV copies, run:

```bash
xz -k -9 -f tdpservice/etl/test/data/TANF_T1_DataSurge_2025-09-10-084149.csv
xz -k -9 -f tdpservice/etl/test/data/TANF_T6_DataSurge_2025-09-10-084149.csv
xz -k -9 -f tdpservice/etl/test/data/TANF_T7_DataSurge_2025-09-10-084149.csv
xz -k -9 -f tdpservice/etl/test/data/expected_outputs/sorted_weights_2024.csv
```

Run `python manage.py populate_stts` first if the local database does not have
STT reference data, or pass `--populate-stts` to the loader. After loading, run
the `statistical_weights` pipeline for
`{"fiscal_year": 2024, "program": "TAN"}`.
