package writer

import (
	"go-parser/internal/parser"
)

// SSP M1 Serializer - Case-level data for active SSP cases

func serializeSspM1(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("CASE_NUMBER"),
		record.Get("COUNTY_FIPS_CODE"),
		record.Get("STRATUM"),
		record.Get("ZIP_CODE"),
		record.Get("DISPOSITION"),
		record.Get("NBR_FAMILY_MEMBERS"),
		record.Get("FAMILY_TYPE"),
		record.Get("TANF_ASST_IN_6MONTHS"),
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
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// SSP M2 Serializer - Adult-level data for active SSP cases

func serializeSspM2(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("CASE_NUMBER"),
		record.Get("FIPS_CODE"),
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

// SSP M3 Serializer - Child-level data for active SSP cases

func serializeSspM3(record *parser.ParsedRecord, datafileID int32) [][]any {
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
		record.Get("RECEIVE_NONSSI_BENEFITS"),
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

// SSP M4 Serializer - Case-level data for closed SSP cases

func serializeSspM4(record *parser.ParsedRecord, datafileID int32) [][]any {
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

// SSP M5 Serializer - Adult-level data for closed SSP cases

func serializeSspM5(record *parser.ParsedRecord, datafileID int32) [][]any {
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
		record.Get("EMPLOYMENT_STATUS"),
		record.Get("AMOUNT_EARNED_INCOME"),
		record.Get("AMOUNT_UNEARNED_INCOME"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// SSP M6 Serializer - Aggregate data

func serializeSspM6(record *parser.ParsedRecord, datafileID int32) [][]any {
	return singleRow([]any{
		record.Get("RecordType"),
		record.Get("CALENDAR_QUARTER"),
		record.Get("RPT_MONTH_YEAR"),
		record.Get("SSPMOE_FAMILIES"),
		record.Get("NUM_2_PARENTS"),
		record.Get("NUM_1_PARENTS"),
		record.Get("NUM_NO_PARENTS"),
		record.Get("NUM_RECIPIENTS"),
		record.Get("ADULT_RECIPIENTS"),
		record.Get("CHILD_RECIPIENTS"),
		record.Get("NONCUSTODIALS"),
		record.Get("AMT_ASSISTANCE"),
		record.Get("CLOSED_CASES"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}

// SSP M7 Serializer - Stratum data

func serializeSspM7(record *parser.ParsedRecord, datafileID int32) [][]any {
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
