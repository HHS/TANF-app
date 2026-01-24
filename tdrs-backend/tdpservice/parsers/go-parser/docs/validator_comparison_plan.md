# Validator Comparison Analysis Plan

## Objective

Analyze the category 3 validators between the Python parser and Go parser to identify any logic differences that could cause the Go parser to report approximately half as many category 3 validation errors as the Python parser for T2 and T3 records.

## Background

- The number of parsed records is equivalent between both parsers
- Category 1 and 4 validators are not causing short-circuiting (no errors in those categories for the test file)
- The discrepancy is specifically in category 3 (cross-field) validators

## Files to Analyze

### Python Parser
- `tdrs-backend/tdpservice/parsers/schema_defs/tanf/t2.py` - T2 schema with postparsing_validators
- `tdrs-backend/tdpservice/parsers/schema_defs/tanf/t3.py` - T3 schema with postparsing_validators
- `tdrs-backend/tdpservice/parsers/validators/category3.py` - Validator implementations
- `tdrs-backend/tdpservice/parsers/validators/base.py` - Base validator functions
- `tdrs-backend/tdpservice/parsers/validators/util.py` - Validator utilities (make_validator, etc.)

### Go Parser
- `tdrs-backend/tdpservice/parsers/go-parser/config/schemas/tanf/t2.yaml` - T2 schema with category3 validators
- `tdrs-backend/tdpservice/parsers/go-parser/config/schemas/tanf/t3.yaml` - T3 schema with category3 validators
- `tdrs-backend/tdpservice/parsers/go-parser/config/validation/validators.yaml` - Predefined validators
- `tdrs-backend/tdpservice/parsers/go-parser/internal/validation/functions.go` - Custom functions
- `tdrs-backend/tdpservice/parsers/go-parser/internal/validation/env.go` - Environment with Get/GetInt/GetString

## Analysis Tasks

### Task 1: Enumerate All Validators

Create a complete list of all category 3 validators for T2 and T3 in both parsers.

**T2 Python Validators (from t2.py postparsing_validators):**
1. Race validators (6): FAMILY_AFFILIATION 1-3 → RACE_* 1-2
2. MARITAL_STATUS: FAMILY_AFFILIATION 1-3 → MARITAL_STATUS 1-5
3. PARENT_MINOR_CHILD: FAMILY_AFFILIATION 1-2 → PARENT_MINOR_CHILD 1-3
4. EDUCATION_LEVEL (affil 2-3): → 0-16 or 98-99
5. EDUCATION_LEVEL (affil 1): → not 0 or 99
6. CITIZENSHIP_STATUS: FAMILY_AFFILIATION 1 → 1,2,3
7. COOPERATION_CHILD_SUPPORT: FAMILY_AFFILIATION 1-3 → 1,2,9
8. EMPLOYMENT_STATUS: FAMILY_AFFILIATION 1-3 → 1-3
9. WORK_ELIGIBLE_INDICATOR: FAMILY_AFFILIATION 1-2 → 1-9 or "11","12"
10. WORK_PART_STATUS (affil): FAMILY_AFFILIATION 1-2 → specific string values
11. WORK_PART_STATUS (work elig): WORK_ELIGIBLE_INDICATOR 1-5 → not "99" (FRA suppressed)
12. SSN: WORK_ELIGIBLE_INDICATOR 1-5 → not repeating digit
13. validate__WORK_ELIGIBLE_INDICATOR__HOH__AGE: complex age-based rule

**T3 Python Validators (from t3.py, applied to both child_one and child_two):**
1. Race validators (6): FAMILY_AFFILIATION 1-2 → RACE_* 1-2
2. RELATIONSHIP_HOH: FAMILY_AFFILIATION 1-2 → 4-9
3. PARENT_MINOR_CHILD: FAMILY_AFFILIATION 1-2 → 2,3
4. EDUCATION_LEVEL: FAMILY_AFFILIATION 1 → not "99"
5. CITIZENSHIP_STATUS (affil 1): → 1,2,3
6. CITIZENSHIP_STATUS (affil 2): → 1,2,3,9

### Task 2: Compare Condition Logic

For each validator, compare the condition check logic:

**Key Questions:**
1. Is `isBetween(1, 3, inclusive=True)` equivalent to `GetInt(...) >= 1 and GetInt(...) <= 3`?
2. Is `isOneOf((1, 2))` equivalent to `GetInt(...) >= 1 and GetInt(...) <= 2`?
3. Is `isEqual(1)` equivalent to `GetInt(...) == 1`?

**Type Handling:**
- Python's `isBetween` with `cast=int` - how does it handle string values?
- Go's `GetInt()` - how does it handle string values like "01" vs "1"?
- Python's `isOneOf((1, 2))` vs `isOneOf(("11", "12"))` - integer vs string comparison

### Task 3: Compare Target Validation Logic

For each validator, compare what happens when the target field is checked:

**Key Questions:**
1. Are the target value ranges identical?
2. Are inclusive/exclusive bounds correct?
3. Are string vs integer comparisons consistent?

### Task 4: Analyze None/Nil Value Handling

Compare how both parsers handle missing or blank field values:

**Python Behavior:**
- In `make_validator`: exceptions are caught and return `Result(valid=False)`
- In `ifThenAlso`: if condition_result.valid is False, returns success (passes)
- Effect: If condition field is None and causes exception, validator passes

**Go Behavior:**
- `GetInt()` returns 0 for nil values
- `GetString()` returns "" for nil values
- Effect: If condition field is nil, GetInt returns 0, condition check (e.g., >= 1) fails, validator passes

**Question:** Are these behaviors equivalent in all cases?

### Task 5: Analyze Specific Validators with Complex Logic

#### EDUCATION_LEVEL (affil 2-3)
- Python: `orValidators([isBetween(0, 16, cast=int), isBetween(98, 99, cast=int)], if_result=True)`
- Go: `(GetInt('EDUCATION_LEVEL') >= 0 and GetInt('EDUCATION_LEVEL') <= 16) or (GetInt('EDUCATION_LEVEL') >= 98 and GetInt('EDUCATION_LEVEL') <= 99)`

#### WORK_ELIGIBLE_INDICATOR
- Python: `orValidators([isBetween(1, 9, cast=int), isOneOf(("11", "12"))], if_result=True)`
- Go: `(GetInt('WORK_ELIGIBLE_INDICATOR') >= 1 and ... <= 9) or GetInt('...') == 11 or GetInt('...') == 12`

**Question:** Does Python's string comparison for "11"/"12" differ from Go's integer comparison for 11/12?

#### WORK_PART_STATUS
- Python: `isOneOf(["01", "02", "05", "07", "09", "15", "17", "18", "19", "99"])` - STRING comparison
- Go: `GetString('WORK_PART_STATUS') in ['01', '02', '05', '07', '09', '15', '17', '18', '19', '99']` - STRING comparison

**Question:** Are the allowed values identical?

### Task 6: Check for FRA Pilot State Suppression

Python has `suppress_for_fra_pilot_state` wrapper for WORK_PART_STATUS validator.
- Does Go implement this suppression?
- If not, this could cause Go to report MORE errors, not fewer.

### Task 7: Verify T3 Multi-Segment Handling

Python defines T3 as two separate schemas (child_one, child_two), each with its own postparsing_validators.
Go defines T3 as one schema with two segments.

**Questions:**
1. Does Go run category 3 validators for EACH segment (each child)?
2. Check the orchestrator: `for _, rec := range group.GetRecords()` - does this include all segments?
3. Verify that both Child 1 and Child 2 ParsedRecords are added to the group

### Task 8: Run Test Comparisons

Using the test file `ADS.E2J.FTP1.TS06`:
1. Count Cat3 errors by validator ID in Python
2. Count Cat3 errors by validator ID in Go
3. Identify which specific validators have the largest discrepancies

## Expected Deliverables

1. A table comparing each validator's logic between Python and Go
2. List of identified discrepancies with severity (likely to cause error count differences)
3. Recommended fixes for any logic differences
4. Test cases to verify fixes

## Priority Areas

Based on "about half" error discrepancy, focus on:
1. Validators that run on every record (race validators, etc.)
2. Type coercion differences (string vs int)
3. Multi-segment handling for T3
