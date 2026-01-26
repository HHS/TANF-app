package convert

import (
	"go-parser/internal/parser"
)

// SSP M1 Converter - Case-level data for active SSP cases

func convertSspM1(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("CASE_NUMBER")),
		toText(record.Get("FIPS_CODE")),
		toText(record.Get("COUNTY_FIPS_CODE")),
		toText(record.Get("STRATUM")),
		toText(record.Get("ZIP_CODE")),
		toInt4(record.Get("DISPOSITION")),
		toInt4(record.Get("NBR_FAMILY_MEMBERS")),
		toInt4(record.Get("FAMILY_TYPE")),
		toInt4(record.Get("TANF_ASST_IN_6MONTHS")),
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
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// SSP M2 Converter - Adult-level data for active SSP cases

func convertSspM2(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("CASE_NUMBER")),
		toText(record.Get("FIPS_CODE")),
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
		toInt4(record.Get("RELATIONSHIP_HOH")),
		toInt4(record.Get("PARENT_MINOR_CHILD")),
		toInt4(record.Get("NEEDS_PREGNANT_WOMAN")),
		toText(record.Get("EDUCATION_LEVEL")),
		toInt4(record.Get("CITIZENSHIP_STATUS")),
		toInt4(record.Get("COOPERATION_CHILD_SUPPORT")),
		toInt4(record.Get("EMPLOYMENT_STATUS")),
		toInt4(record.Get("WORK_ELIGIBLE_INDICATOR")),
		toInt4(record.Get("WORK_PART_STATUS")),
		toInt4(record.Get("UNSUB_EMPLOYMENT")),
		toInt4(record.Get("SUB_PRIVATE_EMPLOYMENT")),
		toInt4(record.Get("SUB_PUBLIC_EMPLOYMENT")),
		toInt4(record.Get("WORK_EXPERIENCE_HOP")),
		toInt4(record.Get("WORK_EXPERIENCE_EA")),
		toInt4(record.Get("WORK_EXPERIENCE_HOL")),
		toInt4(record.Get("OJT")),
		toInt4(record.Get("JOB_SEARCH_HOP")),
		toInt4(record.Get("JOB_SEARCH_EA")),
		toInt4(record.Get("JOB_SEARCH_HOL")),
		toInt4(record.Get("COMM_SERVICES_HOP")),
		toInt4(record.Get("COMM_SERVICES_EA")),
		toInt4(record.Get("COMM_SERVICES_HOL")),
		toInt4(record.Get("VOCATIONAL_ED_TRAINING_HOP")),
		toInt4(record.Get("VOCATIONAL_ED_TRAINING_EA")),
		toInt4(record.Get("VOCATIONAL_ED_TRAINING_HOL")),
		toInt4(record.Get("JOB_SKILLS_TRAINING_HOP")),
		toInt4(record.Get("JOB_SKILLS_TRAINING_EA")),
		toInt4(record.Get("JOB_SKILLS_TRAINING_HOL")),
		toInt4(record.Get("ED_NO_HIGH_SCHOOL_DIPL_HOP")),
		toInt4(record.Get("ED_NO_HIGH_SCHOOL_DIPL_EA")),
		toInt4(record.Get("ED_NO_HIGH_SCHOOL_DIPL_HOL")),
		toInt4(record.Get("SCHOOL_ATTENDENCE_HOP")),
		toInt4(record.Get("SCHOOL_ATTENDENCE_EA")),
		toInt4(record.Get("SCHOOL_ATTENDENCE_HOL")),
		toInt4(record.Get("PROVIDE_CC_HOP")),
		toInt4(record.Get("PROVIDE_CC_EA")),
		toInt4(record.Get("PROVIDE_CC_HOL")),
		toInt4(record.Get("OTHER_WORK_ACTIVITIES")),
		toInt4(record.Get("DEEMED_HOURS_FOR_OVERALL")),
		toInt4(record.Get("DEEMED_HOURS_FOR_TWO_PARENT")),
		toInt4(record.Get("EARNED_INCOME")),
		toInt4(record.Get("UNEARNED_INCOME_TAX_CREDIT")),
		toInt4(record.Get("UNEARNED_SOCIAL_SECURITY")),
		toInt4(record.Get("UNEARNED_SSI")),
		toInt4(record.Get("UNEARNED_WORKERS_COMP")),
		toInt4(record.Get("OTHER_UNEARNED_INCOME")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// SSP M3 Converter - Child-level data for active SSP cases

func convertSspM3(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toText(record.Get("CASE_NUMBER")),
		toText(record.Get("FIPS_CODE")),
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
		toInt4(record.Get("RECEIVE_NONSSI_BENEFITS")),
		toInt4(record.Get("RECEIVE_SSI")),
		toInt4(record.Get("RELATIONSHIP_HOH")),
		toInt4(record.Get("PARENT_MINOR_CHILD")),
		toText(record.Get("EDUCATION_LEVEL")),
		toInt4(record.Get("CITIZENSHIP_STATUS")),
		toInt4(record.Get("UNEARNED_SSI")),
		toInt4(record.Get("OTHER_UNEARNED_INCOME")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// SSP M4 Converter - Case-level data for closed SSP cases

func convertSspM4(record *parser.ParsedRecord, datafileID int32) [][]any {
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

// SSP M5 Converter - Adult-level data for closed SSP cases

func convertSspM5(record *parser.ParsedRecord, datafileID int32) [][]any {
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
		toInt4(record.Get("EMPLOYMENT_STATUS")),
		toText(record.Get("AMOUNT_EARNED_INCOME")),
		toText(record.Get("AMOUNT_UNEARNED_INCOME")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// SSP M6 Converter - Aggregate data

func convertSspM6(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		toText(record.Get("RecordType")),
		toInt4(record.Get("CALENDAR_QUARTER")),
		toInt4(record.Get("RPT_MONTH_YEAR")),
		toInt4(record.Get("SSP_MOE_FAMILIES")),
		toInt4(record.Get("NUM_2_PARENTS")),
		toInt4(record.Get("NUM_1_PARENTS")),
		toInt4(record.Get("NUM_NO_PARENTS")),
		toInt4(record.Get("NUM_RECIPIENTS")),
		toInt4(record.Get("ADULT_RECIPIENTS")),
		toInt4(record.Get("CHILD_RECIPIENTS")),
		toInt4(record.Get("NONCUSTODIALS")),
		toInt4(record.Get("AMT_ASSISTANCE")),
		toInt4(record.Get("CLOSED_CASES")),
		newUUID(),
		toDatafileID(datafileID),
		toLineNumber(record.LineNumber),
	})
}

// SSP M7 Converter - Stratum data

func convertSspM7(record *parser.ParsedRecord, datafileID int32) [][]any {
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
