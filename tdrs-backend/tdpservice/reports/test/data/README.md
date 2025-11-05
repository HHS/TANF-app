# Test Zip Files for Reports Workflow

This directory contains test zip files for manually testing the master report ingestion workflow.

## File Structure

All valid files follow the structure: `{YYYY}/{Region_ID}/{STT_CODE}/files`

## Valid Test Files (Should PASS)

### 1. `valid_single_stt.zip`
**Structure:**
```
2025/
  └── 4/
      └── 01/
          ├── alabama_report.pdf
          └── alabama_summary.pdf
```
**Expected Result:** Success
- Creates 1 ReportFile for Alabama (STT_CODE: 01, Region 4)
- Quarter determined by upload date
- Files bundled into `stt_01_reports.zip`

### 2. `valid_multiple_stts_same_region.zip`
**Structure:**
```
2025/
  └── 4/
      ├── 01/
      │   └── alabama_report.pdf
      └── 12/
          └── florida_report.pdf
```
**Expected Result:** Success
- Creates 2 ReportFiles (Alabama and Florida, both Region 4)
- Each STT gets its own bundled zip

### 3. `valid_multiple_regions.zip`
**Structure:**
```
2025/
  ├── 1/
  │   └── 09/
  │       └── connecticut_report.pdf
  ├── 2/
  │   └── 34/
  │       └── new_jersey_report.pdf
  └── 3/
      └── 42/
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
202a/
  └── 4/
      └── 01/
          └── report.pdf
```
**Expected Error:** `"Fiscal year folder '202a' is invalid. Expected 4-digit year (e.g., '2025')."`

### 5. `invalid_flat_structure.zip`
**Structure:**
```
report.pdf  (no folders)
```
**Expected Error:** `"No top-level folder found in zip file. Expected structure: {YYYY}/Region/STT/files"`

### 6. `invalid_stt_code_999.zip`
**Structure:**
```
2025/
  └── 4/
      └── 999/
          └── report.pdf
```
**Expected Error:** `"STT code '999' not found in system."`

### 7. `invalid_empty_stt_folder.zip`
**Structure:**
```
2025/
  └── 4/
      └── 01/  (empty folder)
```
**Expected Error:** `"No STT folders found in structure 2025/Region/STT/."` or `"STT folder '01' is empty."`

### 8. `invalid_multiple_fiscal_years.zip`
**Structure:**
```
2025/
  └── 4/
      └── 01/
          └── report_2025.pdf
2024/
  └── 4/
      └── 01/
          └── report_2024.pdf
```
**Expected Error:** `"Multiple top-level folders found: ['2024', '2025']. Expected single fiscal year folder (e.g., '2025')."`

---

## How to Test

1. **Upload via API** (requires authentication):
   ```bash
   curl -X POST http://localhost:8080/v1/reports/master/ \
     -H "Authorization: Token YOUR_TOKEN" \
     -F "file=@valid_single_stt.zip"
   ```

2. **Check ReportIngest status**:
   - Visit Django admin: `http://localhost:8080/admin/reports/reportingest/`
   - Check status field: PENDING → PROCESSING → SUCCEEDED/FAILED
   - Check `error_message` for failure details
   - Check `num_reports_created` for success count

3. **Verify ReportFiles created**:
   - Visit: `http://localhost:8080/admin/reports/reportfile/`
   - Verify correct STT, year, quarter, version
   - Download bundled zip to verify contents

## Quarter Calculation

Quarter is calculated from `created_at` date. Each quarter window starts the day after the previous quarter's deadline:

- **Q1**: Oct 15 - Feb 14 (for previous year Oct-Dec)
- **Q2**: Feb 15 - May 15 (for current year Jan-Mar)
- **Q3**: May 16 - Aug 14 (for current year Apr-Jun)
- **Q4**: Aug 15 - Oct 14 (for current year Jul-Sep)

**All dates throughout the year are valid** - there are no gaps between quarters.

