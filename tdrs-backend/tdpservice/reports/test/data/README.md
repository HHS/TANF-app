# Test Zip Files for Reports Workflow

This directory contains test zip files for manually testing the report source workflow.

## File Structure

All valid files follow the structure: `FY{YYYY}/R{XX}/F{X}/files`

- **FY{YYYY}**: Fiscal year folder with "FY" prefix (e.g., `FY2025`)
- **R{XX}**: Region folder with "R" prefix (e.g., `R01`, `R04`)
- **F{X}**: STT folder with "F" prefix representing FIPS code (e.g., `F1`, `F12`)

## Valid Test Files (Should PASS)

### 1. `FY2025_valid_single_stt.zip`
**Structure:**
```
FY2025/
  └── R04/
      └── F1/
          ├── alabama_report.pdf
          └── alabama_summary.pdf
```
**Expected Result:** Success
- Creates 1 ReportFile for Alabama (STT_CODE: 1, Region 4)
- Files bundled into `stt_1_reports.zip`

### 2. `FY2025_valid_multiple_stts_same_region.zip`
**Structure:**
```
FY2025/
  └── R04/
      ├── F1/
      │   └── alabama_report.pdf
      └── F12/
          └── florida_report.pdf
```
**Expected Result:** Success
- Creates 2 ReportFiles (Alabama and Florida, both Region 4)
- Each STT gets its own bundled zip

### 3. `FY2025_valid_multiple_regions.zip`
**Structure:**
```
FY2025/
  ├── R01/
  │   └── F9/
  │       └── connecticut_report.pdf
  ├── R02/
  │   └── F34/
  │       └── new_jersey_report.pdf
  └── R03/
      └── F42/
          └── pennsylvania_report.pdf
```
**Expected Result:** Success
- Creates 3 ReportFiles across 3 different regions
- Connecticut (Region 1), New Jersey (Region 2), Pennsylvania (Region 3)

---

## Invalid Test Files (Should FAIL)

### 4. `invalid_fiscal_year_bad_format.zip`
**Structure:**
```
FY202a/
  └── R04/
      └── F1/
          └── report.pdf
```
**Expected Error:** Invalid fiscal year format in folder name.

### 5. `invalid_flat_structure.zip`
**Structure:**
```
report.pdf  (no folders)
```
**Expected Error:** `"No STT folders found. Expected structure: FY{YYYY}/R{XX}/F{X}/files"`

### 6. `FY2025_invalid_stt_code_999.zip`
**Structure:**
```
FY2025/
  └── R04/
      └── F999/
          └── report.pdf
```
**Expected Error:** `"STT code '999' not found in system."`

### 7. `FY2025_invalid_empty_stt_folder.zip`
**Structure:**
```
FY2025/
  └── R04/
      └── F1/  (empty folder)
```
**Expected Error:** `"No STT folders found..."` (empty folders are skipped)

### 8. `invalid_multiple_fiscal_years.zip`
**Structure:**
```
FY2025/
  └── R04/
      └── F1/
          └── report_2025.pdf
FY2024/
  └── R04/
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

