package convert

import (
	"go-parser/internal/parser"
)

// Tribal TANF T1 Converter - Case-level data for active Tribal TANF cases

func convertTribalT1(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("CASE_NUMBER")),
		toText(record.Get("COUNTY_FIPS_CODE")),
		toText(record.Get("STRATUM")),
		toText(record.Get("ZIP_CODE")),
		toInt4(record.Get("FUNDING_STREAM")),
		toInt4(record.Get("DISPOSITION")),
		toInt4(record.Get("NEW_APPLICANT")),
		toInt4(record.Get("NBR_FAMILY_MEMBERS")),
		toInt4(record.Get("FAMILY_TYPE")),
		toInt4(record.Get("RECEIVES_SUB_HOUSING")),
		toInt4(record.Get("RECEIVES_MED_ASSISTANCE")),
		toInt4(record.Get("RECEIVES_FOOD_STAMPS")),
		toInt4(record.Get("AMT_FOOD_STAMP_ASSISTANCE")),
		toInt4(record.Get("RECEIVES_SUB_CC")),
		toInt4(record.Get("AMT_SUB_CC")),
		toInt4(record.Get("CHILD_SUPPORT_AMT")),
		toInt4(record.Get("FAMILY_CASH_RESOURCES")),
		toInt4(record.Get("CASH_AMOUNT")),
		toInt4(record.Get("NBR_MONTHS")),
		toInt4(record.Get("CC_AMOUNT")),
		toInt4(record.Get("CHILDREN_COVERED")),
		toInt4(record.Get("CC_NBR_MONTHS")),
		toInt4(record.Get("TRANSP_AMOUNT")),
		toInt4(record.Get("TRANSP_NBR_MONTHS")),
		toInt4(record.Get("TRANSITION_SERVICES_AMOUNT")),
		toInt4(record.Get("TRANSITION_NBR_MONTHS")),
		toInt4(record.Get("OTHER_AMOUNT")),
		toInt4(record.Get("OTHER_NBR_MONTHS")),
		toInt4(record.Get("SANC_REDUCTION_AMT")),
		toInt4(record.Get("WORK_REQ_SANCTION")),
		toInt4(record.Get("FAMILY_SANC_ADULT")),
		toInt4(record.Get("SANC_TEEN_PARENT")),
		toInt4(record.Get("NON_COOPERATION_CSE")),
		toInt4(record.Get("FAILURE_TO_COMPLY")),
		toInt4(record.Get("OTHER_SANCTION")),
		toInt4(record.Get("RECOUPMENT_PRIOR_OVRPMT")),
		toInt4(record.Get("OTHER_TOTAL_REDUCTIONS")),
		toInt4(record.Get("FAMILY_CAP")),
		toInt4(record.Get("REDUCTIONS_ON_RECEIPTS")),
		toInt4(record.Get("OTHER_NON_SANCTION")),
		toInt4(record.Get("WAIVER_EVAL_CONTROL_GRPS")),
		toInt4(record.Get("FAMILY_EXEMPT_TIME_LIMITS")),
		toInt4(record.Get("FAMILY_NEW_CHILD")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// Tribal TANF T2 Converter - Adult-level data for active Tribal TANF cases

func convertTribalT2(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("CASE_NUMBER")),
		toInt4(record.Get("FAMILY_AFFILIATION")),
		toInt4(record.Get("NONCUSTODIAL_PARENT")),
		toText(record.Get("DATE_OF_BIRTH")),
		toText(record.Get("SSN")),
		toInt4(record.Get("RACE_HISPANIC")),
		toInt4(record.Get("RACE_AMER_INDIAN")),
		toInt4(record.Get("RACE_ASIAN")),
		toInt4(record.Get("RACE_BLACK")),
		toInt4(record.Get("RACE_HAWAIIAN")),
		toInt4(record.Get("RACE_WHITE")),
		toInt4(record.Get("SEX")),
		toInt4(record.Get("FED_OASDI_PROGRAM")),
		toInt4(record.Get("FED_DISABILITY_STATUS")),
		toInt4(record.Get("DISABLED_TITLE_XIVAPDT")),
		toInt4(record.Get("AID_AGED_BLIND")),
		toInt4(record.Get("RECEIVE_SSI")),
		toInt4(record.Get("MARITAL_STATUS")),
		toText(record.Get("RELATIONSHIP_HOH")),
		toInt4(record.Get("PARENT_MINOR_CHILD")),
		toInt4(record.Get("NEEDS_PREGNANT_WOMAN")),
		toText(record.Get("EDUCATION_LEVEL")),
		toInt4(record.Get("CITIZENSHIP_STATUS")),
		toInt4(record.Get("COOPERATION_CHILD_SUPPORT")),
		toText(record.Get("MONTHS_FED_TIME_LIMIT")),
		toText(record.Get("MONTHS_STATE_TIME_LIMIT")),
		toInt4(record.Get("CURRENT_MONTH_STATE_EXEMPT")),
		toInt4(record.Get("EMPLOYMENT_STATUS")),
		toText(record.Get("WORK_PART_STATUS")),
		toText(record.Get("UNSUB_EMPLOYMENT")),
		toText(record.Get("SUB_PRIVATE_EMPLOYMENT")),
		toText(record.Get("SUB_PUBLIC_EMPLOYMENT")),
		toText(record.Get("WORK_EXPERIENCE")),
		toText(record.Get("OJT")),
		toText(record.Get("JOB_SEARCH")),
		toText(record.Get("COMM_SERVICES")),
		toText(record.Get("VOCATIONAL_ED_TRAINING")),
		toText(record.Get("JOB_SKILLS_TRAINING")),
		toText(record.Get("ED_NO_HIGH_SCHOOL_DIPLOMA")),
		toText(record.Get("SCHOOL_ATTENDENCE")),
		toText(record.Get("PROVIDE_CC")),
		toText(record.Get("ADD_WORK_ACTIVITIES")),
		toText(record.Get("OTHER_WORK_ACTIVITIES")),
		toText(record.Get("REQ_HRS_WAIVER_DEMO")),
		toText(record.Get("EARNED_INCOME")),
		toText(record.Get("UNEARNED_INCOME_TAX_CREDIT")),
		toText(record.Get("UNEARNED_SOCIAL_SECURITY")),
		toText(record.Get("UNEARNED_SSI")),
		toText(record.Get("UNEARNED_WORKERS_COMP")),
		toText(record.Get("OTHER_UNEARNED_INCOME")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// Tribal TANF T3 Converter - Child-level data for active Tribal TANF cases

func convertTribalT3(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("CASE_NUMBER")),
		toInt4(record.Get("FAMILY_AFFILIATION")),
		toText(record.Get("DATE_OF_BIRTH")),
		toText(record.Get("SSN")),
		toInt4(record.Get("RACE_HISPANIC")),
		toInt4(record.Get("RACE_AMER_INDIAN")),
		toInt4(record.Get("RACE_ASIAN")),
		toInt4(record.Get("RACE_BLACK")),
		toInt4(record.Get("RACE_HAWAIIAN")),
		toInt4(record.Get("RACE_WHITE")),
		toInt4(record.Get("SEX")),
		toInt4(record.Get("RECEIVE_NONSSA_BENEFITS")),
		toInt4(record.Get("RECEIVE_SSI")),
		toText(record.Get("RELATIONSHIP_HOH")),
		toInt4(record.Get("PARENT_MINOR_CHILD")),
		toText(record.Get("EDUCATION_LEVEL")),
		toInt4(record.Get("CITIZENSHIP_STATUS")),
		toText(record.Get("UNEARNED_SSI")),
		toText(record.Get("OTHER_UNEARNED_INCOME")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// Tribal TANF T4 Converter - Case-level data for closed Tribal TANF cases

func convertTribalT4(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("CASE_NUMBER")),
		toText(record.Get("COUNTY_FIPS_CODE")),
		toText(record.Get("STRATUM")),
		toText(record.Get("ZIP_CODE")),
		toInt4(record.Get("DISPOSITION")),
		toText(record.Get("CLOSURE_REASON")),
		toInt4(record.Get("REC_SUB_HOUSING")),
		toInt4(record.Get("REC_MED_ASSIST")),
		toInt4(record.Get("REC_FOOD_STAMPS")),
		toInt4(record.Get("REC_SUB_CC")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// Tribal TANF T5 Converter - Adult-level data for closed Tribal TANF cases

func convertTribalT5(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("CASE_NUMBER")),
		toInt4(record.Get("FAMILY_AFFILIATION")),
		toText(record.Get("DATE_OF_BIRTH")),
		toText(record.Get("SSN")),
		toInt4(record.Get("RACE_HISPANIC")),
		toInt4(record.Get("RACE_AMER_INDIAN")),
		toInt4(record.Get("RACE_ASIAN")),
		toInt4(record.Get("RACE_BLACK")),
		toInt4(record.Get("RACE_HAWAIIAN")),
		toInt4(record.Get("RACE_WHITE")),
		toInt4(record.Get("SEX")),
		toInt4(record.Get("REC_OASDI_INSURANCE")),
		toInt4(record.Get("REC_FEDERAL_DISABILITY")),
		toInt4(record.Get("REC_AID_TOTALLY_DISABLED")),
		toInt4(record.Get("REC_AID_AGED_BLIND")),
		toInt4(record.Get("REC_SSI")),
		toInt4(record.Get("MARITAL_STATUS")),
		toText(record.Get("RELATIONSHIP_HOH")),
		toInt4(record.Get("PARENT_MINOR_CHILD")),
		toInt4(record.Get("NEEDS_OF_PREGNANT_WOMAN")),
		toText(record.Get("EDUCATION_LEVEL")),
		toInt4(record.Get("CITIZENSHIP_STATUS")),
		toText(record.Get("COUNTABLE_MONTH_FED_TIME")),
		toText(record.Get("COUNTABLE_MONTHS_STATE_TRIBE")),
		toInt4(record.Get("EMPLOYMENT_STATUS")),
		toText(record.Get("AMOUNT_EARNED_INCOME")),
		toText(record.Get("AMOUNT_UNEARNED_INCOME")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// Tribal TANF T6 Converter - Aggregate data

func convertTribalT6(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("CALENDAR_QUARTER")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toInt4(record.Get("NUM_APPLICATIONS")),
		toInt4(record.Get("NUM_APPROVED")),
		toInt4(record.Get("NUM_DENIED")),
		toInt4(record.Get("ASSISTANCE")),
		toInt4(record.Get("NUM_FAMILIES")),
		toInt4(record.Get("NUM_2_PARENTS")),
		toInt4(record.Get("NUM_1_PARENTS")),
		toInt4(record.Get("NUM_NO_PARENTS")),
		toInt4(record.Get("NUM_RECIPIENTS")),
		toInt4(record.Get("NUM_ADULT_RECIPIENTS")),
		toInt4(record.Get("NUM_CHILD_RECIPIENTS")),
		toInt4(record.Get("NUM_NONCUSTODIALS")),
		toInt4(record.Get("NUM_BIRTHS")),
		toInt4(record.Get("NUM_OUTWEDLOCK_BIRTHS")),
		toInt4(record.Get("NUM_CLOSED_CASES")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// Tribal TANF T7 Converter - Stratum data

func convertTribalT7(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("CALENDAR_QUARTER")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("TDRS_SECTION_IND")),
		toText(record.Get("STRATUM")),
		toInt4(record.Get("FAMILIES_MONTH")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}
