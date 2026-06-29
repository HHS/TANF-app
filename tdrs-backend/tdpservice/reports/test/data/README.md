# Test Zip Files for Reports Workflow

This directory contains test zip files for manually testing the report source workflow.

## File Structure

All valid files follow the structure: `{ZipName}/FY{YYYY}/RO{X}/F{X}/files`, where files may be at any depth under the STT folder.

- **{ZipName}**: Root folder matching the zip filename (e.g., `FY2025_07312025`)
- **FY{YYYY}**: Fiscal year folder with "FY" prefix (e.g., `FY2025`)
- **RO{X}**: Regional Office folder with "RO" prefix (e.g., `RO1`, `RO4`)
- **F{X}**: STT folder with "F" prefix representing FIPS code (e.g., `F1`, `F12`)
- **files**: Report files directly under the STT folder or in nested subfolders. Generated STT zip files preserve paths relative to the STT folder.

## Valid Test Files (Should PASS)

### 1. `FY2025_valid_single_stt.zip`
**Structure:**
```
FY2025_valid_single_stt/
  └── FY2025/
      └── RO4/
          └── F1/
              ├── alabama_report.pdf
              └── alabama_summary.pdf
```
**Expected Result:** Success
- Creates 1 ReportFile for Alabama (STT_CODE: 1, Region 4)
- Files bundled into `stt_1_reports.zip`

### 2. `FY2025_valid_nested_stt.zip`
**Structure:**
```
FY2025_valid_nested_stt/
  └── FY2025/
      └── RO4/
          └── F12/
              ├── reports/
              │   ├── january/
              │   │   └── summary.pdf
              │   └── february/
              │       └── summary.pdf
              └── readme.txt
```
**Expected bundled `stt_12_reports.zip` contents:**
```
reports/january/summary.pdf
reports/february/summary.pdf
readme.txt
```

### 3. `FY2025_valid_multiple_stts_same_region.zip`
**Structure:**
```
FY2025_valid_multiple_stts_same_region/
  └── FY2025/
      └── RO4/
          ├── F1/
          │   └── alabama_report.pdf
          └── F12/
              └── florida_report.pdf
```
**Expected Result:** Success
- Creates 2 ReportFiles (Alabama and Florida, both Region 4)
- Each STT gets its own bundled zip

### 4. `FY2025_valid_multiple_regions.zip`
**Structure:**
```
FY2025_valid_multiple_regions/
  └── FY2025/
      ├── RO1/
      │   └── F9/
      │       └── connecticut_report.pdf
      ├── RO2/
      │   └── F34/
      │       └── new_jersey_report.pdf
      └── RO3/
          └── F42/
              └── pennsylvania_report.pdf
```
**Expected Result:** Success
- Creates 3 ReportFiles across 3 different regions
- Connecticut (Region 1), New Jersey (Region 2), Pennsylvania (Region 3)

### 5. `FY2025_mixed_valid_and_invalid_dirs.zip`
**Structure:**
```
FY2025_mixed_valid_and_invalid_dirs/
  ├── .DS_Store
  └── FY2025/
      ├── R05/
      │   └── F020/
      │       └── invalid_region_report.pdf
      └── RO5/
          ├── 020/
          │   └── invalid_stt_report.pdf
          └── F020/
              ├── .hidden_report.pdf
              ├── blackfeet_nation_report.pdf
              ├── blackfeet_nation_summary.pdf
              └── nested/
                  └── ignored_nested_report.pdf
__MACOSX/
  └── FY2025_mixed_valid_and_invalid_dirs/
      ├── ._.DS_Store
      └── FY2025/
          └── R05/
              └── ._invalid_region_report.pdf
```
**Expected Result:** Success
- Creates 1 ReportFile for Blackfeet Nation (STT_CODE: 020, Region 5)
- Ignores invalid folders and metadata paths (`R05`, `020`, hidden files, `.DS_Store`, and `__MACOSX`)
- Useful for manual upload testing that invalid paths do not fail the entire upload

---

## Invalid Test Files (Should FAIL)

### 6. `invalid_fiscal_year_bad_format.zip`
**Structure:**
```
invalid_fiscal_year_bad_format/
  └── FY202a/
      └── RO4/
          └── F1/
              └── report.pdf
```
**Expected Error:** Invalid fiscal year format in folder name.

### 7. `invalid_flat_structure.zip`
**Structure:**
```
report.pdf  (no folders)
```
**Expected Error:** `"No STT folders found. Expected structure: {ZipName}/FY{YYYY}/RO{X}/F{X}/files"`

### 8. `FY2025_invalid_stt_code_999.zip`
**Structure:**
```
FY2025_invalid_stt_code_999/
  └── FY2025/
      └── RO4/
          └── F999/
              └── report.pdf
```
**Expected Error:** `"STT code '999' not found in system."`

### 9. `FY2025_invalid_empty_stt_folder.zip`
**Structure:**
```
FY2025_invalid_empty_stt_folder/
  └── FY2025/
      └── RO4/
          └── F1/  (empty folder)
```
**Expected Error:** `"No STT folders found..."` (empty folders are skipped)

### 10. `FY2025_invalid_duplicate_stt_relative_paths.zip`
**Structure:**
```
FY2025_invalid_duplicate_stt_relative_paths/
  └── FY2025/
      ├── RO4/
      │   └── F12/
      │       └── reports/
      │           └── january/
      │               └── summary.pdf
      └── RO5/
          └── F12/
              └── reports/
                  └── january/
                      └── summary.pdf
```
**Expected Error:** `"Duplicate file path in STT folder '12': reports/january/summary.pdf"`

### 11. `invalid_multiple_fiscal_years.zip`
**Structure:**
```
invalid_multiple_fiscal_years/
  ├── FY2025/
  │   └── RO4/
  │       └── F1/
  │           └── report_2025.pdf
  └── FY2024/
      └── RO4/
          └── F1/
              └── report_2024.pdf
```
**Expected Error:** Files from multiple fiscal years will be processed together (all STT codes aggregated).

---

## How to Test

1. **Upload via API** (requires authentication):
   ```bash
   curl -X POST http://localhost:8080/v1/reports/report_source/ \
     -H "Authorization: Token YOUR_TOKEN" \
     -F "file=@FY2025_valid_single_stt.zip" \
     -F "year=2025" \
     -F "date_extracted_on=2025-01-31"
   ```

2. **Check ReportSource status**:
   - Visit Django admin: `http://localhost:8080/admin/reports/reportsource/`
   - Check status field: PENDING → PROCESSING → SUCCEEDED/FAILED
   - Check `error_message` for failure details
   - Check `num_reports_created` for success count

3. **Verify ReportFiles created**:
   - Visit: `http://localhost:8080/admin/reports/reportfile/`
   - Verify correct STT, year, date_extracted_on, version
   - Download bundled zip to verify contents

## Data Extraction Date

The `date_extracted_on` field indicates when the data was extracted from the database. This date is:
- Set by the admin during upload
- Copied from ReportSource to each ReportFile created
- Displayed to STT users in the feedback reports table
- Used in email notifications to indicate the data cutoff date
