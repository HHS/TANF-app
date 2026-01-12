package parser

type ProgramType string
type Section string

const (
	TANF ProgramType = "TANF"
	TRIBAL ProgramType = "TRIBAL"
	SSP ProgramType = "SSP"
	FRA ProgramType = "FRA"
)

const (
	ACTIVE_CASE_DATA = "Active Case Data"
	CLOSED_CASE_DATA = "Closed Case Data"
	AGGREGATE_DATA = "Aggregate Data"
	STRATUM_DATA = "Stratum Data"

	FRA_WORK_OUTCOME_TANF_EXITERS = "Work Outcomes of TANF Exiters"
	FRA_SECONDRY_SCHOOL_ATTAINMENT = "Secondary School Attainment"
	FRA_SUPPLEMENT_WORK_OUTCOMES = "Supplemental Work Outcomes"
)
