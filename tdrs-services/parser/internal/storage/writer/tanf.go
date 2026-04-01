package writer

import (
	"go-parser/internal/parser"
)

// TANF T1 Converter - Case-level data for active TANF cases
// Builds row directly with raw Go types for minimal allocations.

func convertTanfT1(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("CASE_NUMBER"),
		record.Get("COUNTY_FIPS_CODE"),
		record.Get("STRATUM"),
		record.Get("ZIP_CODE"),
		record.Get("FUNDING_STREAM"),
		record.Get("DISPOSITION"),
		record.Get("NEW_APPLICANT"),
		record.Get("NBR_FAMILY_MEMBERS"),
		record.Get("FAMILY_TYPE"),
		record.Get("RECEIVES_SUB_HOUSING"),
		record.Get("RECEIVES_MED_ASSISTANCE"),
		record.Get("RECEIVES_FOOD_STAMPS"),
		record.Get("AMT_FOOD_STAMP_ASSISTANCE"),
		record.Get("RECEIVES_SUB_CC"),
		record.Get("AMT_SUB_CC"),
		record.Get("CHILD_SUPPORT_AMT"),
		record.Get("FAMILY_CASH_RESOURCES"),
		record.Get("CASH_AMOUNT"),
		record.Get("NBR_MONTHS"),
		record.Get("CC_AMOUNT"),
		record.Get("CHILDREN_COVERED"),
		record.Get("CC_NBR_MONTHS"),
		record.Get("TRANSP_AMOUNT"),
		record.Get("TRANSP_NBR_MONTHS"),
		record.Get("TRANSITION_SERVICES_AMOUNT"),
		record.Get("TRANSITION_NBR_MONTHS"),
		record.Get("OTHER_AMOUNT"),
		record.Get("OTHER_NBR_MONTHS"),
		record.Get("SANC_REDUCTION_AMT"),
		record.Get("WORK_REQ_SANCTION"),
		record.Get("FAMILY_SANC_ADULT"),
		record.Get("SANC_TEEN_PARENT"),
		record.Get("NON_COOPERATION_CSE"),
		record.Get("FAILURE_TO_COMPLY"),
		record.Get("OTHER_SANCTION"),
		record.Get("RECOUPMENT_PRIOR_OVRPMT"),
		record.Get("OTHER_TOTAL_REDUCTIONS"),
		record.Get("FAMILY_CAP"),
		record.Get("REDUCTIONS_ON_RECEIPTS"),
		record.Get("OTHER_NON_SANCTION"),
		record.Get("WAIVER_EVAL_CONTROL_GRPS"),
		record.Get("FAMILY_EXEMPT_TIME_LIMITS"),
		record.Get("FAMILY_NEW_CHILD"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// TANF T2 Converter - Adult-level data for active TANF cases
// This is the largest record type with ~69 fields.

func convertTanfT2(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("CASE_NUMBER"),
		record.Get("FAMILY_AFFILIATION"),
		record.Get("NONCUSTODIAL_PARENT"),
		record.Get("DATE_OF_BIRTH"),
		record.Get("SSN"),
		record.Get("RACE_HISPANIC"),
		record.Get("RACE_AMER_INDIAN"),
		record.Get("RACE_ASIAN"),
		record.Get("RACE_BLACK"),
		record.Get("RACE_HAWAIIAN"),
		record.Get("RACE_WHITE"),
		record.Get("SEX"),
		record.Get("FED_OASDI_PROGRAM"),
		record.Get("FED_DISABILITY_STATUS"),
		record.Get("DISABLED_TITLE_XIVAPDT"),
		record.Get("AID_AGED_BLIND"),
		record.Get("RECEIVE_SSI"),
		record.Get("MARITAL_STATUS"),
		record.Get("RELATIONSHIP_HOH"),
		record.Get("PARENT_MINOR_CHILD"),
		record.Get("NEEDS_PREGNANT_WOMAN"),
		record.Get("EDUCATION_LEVEL"),
		record.Get("CITIZENSHIP_STATUS"),
		record.Get("COOPERATION_CHILD_SUPPORT"),
		record.Get("MONTHS_FED_TIME_LIMIT"),
		record.Get("MONTHS_STATE_TIME_LIMIT"),
		record.Get("CURRENT_MONTH_STATE_EXEMPT"),
		record.Get("EMPLOYMENT_STATUS"),
		record.Get("WORK_ELIGIBLE_INDICATOR"),
		record.Get("WORK_PART_STATUS"),
		record.Get("UNSUB_EMPLOYMENT"),
		record.Get("SUB_PRIVATE_EMPLOYMENT"),
		record.Get("SUB_PUBLIC_EMPLOYMENT"),
		record.Get("WORK_EXPERIENCE_HOP"),
		record.Get("WORK_EXPERIENCE_EA"),
		record.Get("WORK_EXPERIENCE_HOL"),
		record.Get("OJT"),
		record.Get("JOB_SEARCH_HOP"),
		record.Get("JOB_SEARCH_EA"),
		record.Get("JOB_SEARCH_HOL"),
		record.Get("COMM_SERVICES_HOP"),
		record.Get("COMM_SERVICES_EA"),
		record.Get("COMM_SERVICES_HOL"),
		record.Get("VOCATIONAL_ED_TRAINING_HOP"),
		record.Get("VOCATIONAL_ED_TRAINING_EA"),
		record.Get("VOCATIONAL_ED_TRAINING_HOL"),
		record.Get("JOB_SKILLS_TRAINING_HOP"),
		record.Get("JOB_SKILLS_TRAINING_EA"),
		record.Get("JOB_SKILLS_TRAINING_HOL"),
		record.Get("ED_NO_HIGH_SCHOOL_DIPL_HOP"),
		record.Get("ED_NO_HIGH_SCHOOL_DIPL_EA"),
		record.Get("ED_NO_HIGH_SCHOOL_DIPL_HOL"),
		record.Get("SCHOOL_ATTENDENCE_HOP"),
		record.Get("SCHOOL_ATTENDENCE_EA"),
		record.Get("SCHOOL_ATTENDENCE_HOL"),
		record.Get("PROVIDE_CC_HOP"),
		record.Get("PROVIDE_CC_EA"),
		record.Get("PROVIDE_CC_HOL"),
		record.Get("OTHER_WORK_ACTIVITIES"),
		record.Get("DEEMED_HOURS_FOR_OVERALL"),
		record.Get("DEEMED_HOURS_FOR_TWO_PARENT"),
		record.Get("EARNED_INCOME"),
		record.Get("UNEARNED_INCOME_TAX_CREDIT"),
		record.Get("UNEARNED_SOCIAL_SECURITY"),
		record.Get("UNEARNED_SSI"),
		record.Get("UNEARNED_WORKERS_COMP"),
		record.Get("OTHER_UNEARNED_INCOME"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// TANF T3 Converter - Child-level data for active TANF cases

func convertTanfT3(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("CASE_NUMBER"),
		record.Get("FAMILY_AFFILIATION"),
		record.Get("DATE_OF_BIRTH"),
		record.Get("SSN"),
		record.Get("RACE_HISPANIC"),
		record.Get("RACE_AMER_INDIAN"),
		record.Get("RACE_ASIAN"),
		record.Get("RACE_BLACK"),
		record.Get("RACE_HAWAIIAN"),
		record.Get("RACE_WHITE"),
		record.Get("SEX"),
		record.Get("RECEIVE_NONSSA_BENEFITS"),
		record.Get("RECEIVE_SSI"),
		record.Get("RELATIONSHIP_HOH"),
		record.Get("PARENT_MINOR_CHILD"),
		record.Get("EDUCATION_LEVEL"),
		record.Get("CITIZENSHIP_STATUS"),
		record.Get("UNEARNED_SSI"),
		record.Get("OTHER_UNEARNED_INCOME"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// TANF T4 Converter - Case-level data for closed TANF cases

func convertTanfT4(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("CASE_NUMBER"),
		record.Get("COUNTY_FIPS_CODE"),
		record.Get("STRATUM"),
		record.Get("ZIP_CODE"),
		record.Get("DISPOSITION"),
		record.Get("CLOSURE_REASON"),
		record.Get("REC_SUB_HOUSING"),
		record.Get("REC_MED_ASSIST"),
		record.Get("REC_FOOD_STAMPS"),
		record.Get("REC_SUB_CC"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// TANF T5 Converter - Adult-level data for closed TANF cases

func convertTanfT5(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("CASE_NUMBER"),
		record.Get("FAMILY_AFFILIATION"),
		record.Get("DATE_OF_BIRTH"),
		record.Get("SSN"),
		record.Get("RACE_HISPANIC"),
		record.Get("RACE_AMER_INDIAN"),
		record.Get("RACE_ASIAN"),
		record.Get("RACE_BLACK"),
		record.Get("RACE_HAWAIIAN"),
		record.Get("RACE_WHITE"),
		record.Get("SEX"),
		record.Get("REC_OASDI_INSURANCE"),
		record.Get("REC_FEDERAL_DISABILITY"),
		record.Get("REC_AID_TOTALLY_DISABLED"),
		record.Get("REC_AID_AGED_BLIND"),
		record.Get("REC_SSI"),
		record.Get("MARITAL_STATUS"),
		record.Get("RELATIONSHIP_HOH"),
		record.Get("PARENT_MINOR_CHILD"),
		record.Get("NEEDS_OF_PREGNANT_WOMAN"),
		record.Get("EDUCATION_LEVEL"),
		record.Get("CITIZENSHIP_STATUS"),
		record.Get("COUNTABLE_MONTH_FED_TIME"),
		record.Get("COUNTABLE_MONTHS_STATE_TRIBE"),
		record.Get("EMPLOYMENT_STATUS"),
		record.Get("AMOUNT_EARNED_INCOME"),
		record.Get("AMOUNT_UNEARNED_INCOME"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// TANF T6 Converter - Aggregate data

func convertTanfT6(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("CALENDAR_QUARTER"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("NUM_APPLICATIONS"),
		record.Get("NUM_APPROVED"),
		record.Get("NUM_DENIED"),
		record.Get("ASSISTANCE"),
		record.Get("NUM_FAMILIES"),
		record.Get("NUM_2_PARENTS"),
		record.Get("NUM_1_PARENTS"),
		record.Get("NUM_NO_PARENTS"),
		record.Get("NUM_RECIPIENTS"),
		record.Get("NUM_ADULT_RECIPIENTS"),
		record.Get("NUM_CHILD_RECIPIENTS"),
		record.Get("NUM_NONCUSTODIALS"),
		record.Get("NUM_BIRTHS"),
		record.Get("NUM_OUTWEDLOCK_BIRTHS"),
		record.Get("NUM_CLOSED_CASES"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// TANF T7 Converter - Stratum data

func convertTanfT7(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("CALENDAR_QUARTER"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("TDRS_SECTION_IND"),
		record.Get("STRATUM"),
		record.Get("FAMILIES_MONTH"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}
