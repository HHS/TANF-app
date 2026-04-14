//go:build integration

package integration

import (
	"context"
	"path/filepath"
	"testing"
)

// =============================================================================
// TANF Section 1 Tests
// =============================================================================

func TestParseSmallTANFSection1(t *testing.T) {
	ctx := context.Background()

	// Setup
	datafileID, cleanup := createTestDatafile(t, ctx, "TAN", 1)
	defer cleanup()

	// Parse
	filePath := filepath.Join(TestDataDir(), "small_tanf_section1.txt")
	ParseFile(t, ctx, testPool, testRegistry, testValidators, "TANF", 1, filePath, datafileID)

	// Verify record counts
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t1", datafileID, 5)
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t2", datafileID, 5)
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t3", datafileID, 6)

	// Verify T2 field values - Record 0
	t2_0 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t2", datafileID, 0)
	AssertFieldValue(t, t2_0, "RPT_MONTH_YEAR", int32(202010))
	AssertFieldValue(t, t2_0, "CASE_NUMBER", "11111111112")
	AssertFieldValue(t, t2_0, "FAMILY_AFFILIATION", int32(1))
	AssertFieldValue(t, t2_0, "OTHER_UNEARNED_INCOME", "0291")

	// Verify T2 field values - Record 1
	t2_1 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t2", datafileID, 1)
	AssertFieldValue(t, t2_1, "RPT_MONTH_YEAR", int32(202010))
	AssertFieldValue(t, t2_1, "CASE_NUMBER", "11111111115")
	AssertFieldValue(t, t2_1, "FAMILY_AFFILIATION", int32(2))
	AssertFieldValue(t, t2_1, "OTHER_UNEARNED_INCOME", "0000")

	// Verify T3 field values - Record 0
	t3_0 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t3", datafileID, 0)
	AssertFieldValue(t, t3_0, "RPT_MONTH_YEAR", int32(202010))
	AssertFieldValue(t, t3_0, "CASE_NUMBER", "11111111112")
	AssertFieldValue(t, t3_0, "FAMILY_AFFILIATION", int32(1))
	AssertFieldValue(t, t3_0, "SEX", int32(2))
	AssertFieldValue(t, t3_0, "EDUCATION_LEVEL", "98")
}

func TestParseBigTANFSection1(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping big file test in short mode")
	}

	ctx := context.Background()

	// Setup
	datafileID, cleanup := createTestDatafile(t, ctx, "TAN", 1)
	defer cleanup()

	// Parse
	filePath := filepath.Join(TestDataDir(), "ADS.E2J.FTP1.TS06")
	ParseFile(t, ctx, testPool, testRegistry, testValidators, "TANF", 1, filePath, datafileID)

	// Verify record counts (from Python test assertions)
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t1", datafileID, 815)
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t2", datafileID, 882)
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t3", datafileID, 1376)
}

// =============================================================================
// TANF Section 2 Tests
// =============================================================================

func TestParseSmallTANFSection2(t *testing.T) {
	ctx := context.Background()

	// Setup
	datafileID, cleanup := createTestDatafile(t, ctx, "TAN", 2)
	defer cleanup()

	// Parse
	filePath := filepath.Join(TestDataDir(), "small_tanf_section2.txt")
	ParseFile(t, ctx, testPool, testRegistry, testValidators, "TANF", 2, filePath, datafileID)

	// Verify record counts
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t4", datafileID, 1)
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t5", datafileID, 1)

	// Verify T4 field values
	t4_0 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t4", datafileID, 0)
	AssertFieldValue(t, t4_0, "DISPOSITION", int32(1))
	AssertFieldValue(t, t4_0, "REC_SUB_CC", int32(3))

	// Verify T5 field values
	t5_0 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t5", datafileID, 0)
	AssertFieldValue(t, t5_0, "SEX", int32(2))
	AssertFieldValue(t, t5_0, "AMOUNT_UNEARNED_INCOME", "0000")
}

func TestParseBigTANFSection2(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping big file test in short mode")
	}

	ctx := context.Background()

	// Setup
	datafileID, cleanup := createTestDatafile(t, ctx, "TAN", 2)
	defer cleanup()

	// Parse
	filePath := filepath.Join(TestDataDir(), "ADS.E2J.FTP2.TS06")
	ParseFile(t, ctx, testPool, testRegistry, testValidators, "TANF", 2, filePath, datafileID)

	// Verify record counts
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t4", datafileID, 223)
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t5", datafileID, 605)
}

// =============================================================================
// TANF Section 3 Tests
// =============================================================================

func TestParseTANFSection3(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping file test in short mode")
	}

	ctx := context.Background()

	// Setup
	datafileID, cleanup := createTestDatafile(t, ctx, "TAN", 3)
	defer cleanup()

	// Parse
	filePath := filepath.Join(TestDataDir(), "ADS.E2J.FTP3.TS06")
	ParseFile(t, ctx, testPool, testRegistry, testValidators, "TANF", 3, filePath, datafileID)

	// Verify record counts
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t6", datafileID, 3)

	// Verify T6 field values - records ordered by line_number (ascending month order)
	// The file has records in order: Oct (line 2), Nov (line 3), Dec (line 4)
	t6_0 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t6", datafileID, 0)
	AssertFieldValue(t, t6_0, "RPT_MONTH_YEAR", int32(202110))
	AssertFieldValue(t, t6_0, "NUM_APPROVED", int32(4301))
	AssertFieldValue(t, t6_0, "NUM_CLOSED_CASES", int32(5453))

	t6_1 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t6", datafileID, 1)
	AssertFieldValue(t, t6_1, "RPT_MONTH_YEAR", int32(202111))
	AssertFieldValue(t, t6_1, "NUM_APPROVED", int32(3977))

	t6_2 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t6", datafileID, 2)
	AssertFieldValue(t, t6_2, "RPT_MONTH_YEAR", int32(202112))
	AssertFieldValue(t, t6_2, "NUM_APPROVED", int32(3924))
}

// =============================================================================
// TANF Section 4 Tests
// =============================================================================

func TestParseTANFSection4(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping file test in short mode")
	}

	ctx := context.Background()

	// Setup
	datafileID, cleanup := createTestDatafile(t, ctx, "TAN", 4)
	defer cleanup()

	// Parse
	filePath := filepath.Join(TestDataDir(), "ADS.E2J.FTP4.TS06")
	ParseFile(t, ctx, testPool, testRegistry, testValidators, "TANF", 4, filePath, datafileID)

	// Verify record counts - 6 strata populated × 3 months = 18 records
	AssertTableCount(t, ctx, testPool, "search_indexes_tanf_t7", datafileID, 18)

	// Verify T7 field values - all segments from same line so order is arbitrary
	// Just verify first record has valid data from the file (Q4 2021)
	t7_0 := QueryRecord(t, ctx, testPool, "search_indexes_tanf_t7", datafileID, 0)
	AssertFieldValue(t, t7_0, "RPT_MONTH_YEAR", int32(202110)) // October 2021
	AssertFieldValue(t, t7_0, "TDRS_SECTION_IND", "1")
	AssertFieldValue(t, t7_0, "FAMILIES_MONTH", int32(68537))
}
