--
-- PostgreSQL database dump
--

-- Dumped from database version 15.7 (Debian 15.7-1.pgdg120+1)
-- Dumped by pg_dump version 15.7 (Debian 15.7-1.pgdg120+1)




--
-- Name: data_files_datafile; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.data_files_datafile (
    id integer NOT NULL,
    original_filename character varying(256) NOT NULL,
    slug character varying(256) NOT NULL,
    extension character varying(8) NOT NULL,
    quarter character varying(16) NOT NULL,
    year integer NOT NULL,
    section character varying(32) NOT NULL,
    version integer NOT NULL,
    stt_id integer NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    file character varying(100),
    s3_versioning_id character varying(1024),
    program_type character varying(32) NOT NULL,
    is_program_audit boolean NOT NULL,
    state character varying(32) NOT NULL
);


--
-- Name: search_indexes_ssp_m1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_ssp_m1 (
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FIPS_CODE" character varying(2),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "DISPOSITION" integer,
    "NBR_FAMILY_MEMBERS" integer,
    "FAMILY_TYPE" integer,
    "TANF_ASST_IN_6MONTHS" integer,
    "RECEIVES_SUB_HOUSING" integer,
    "RECEIVES_MED_ASSISTANCE" integer,
    "RECEIVES_FOOD_STAMPS" integer,
    "AMT_FOOD_STAMP_ASSISTANCE" integer,
    "RECEIVES_SUB_CC" integer,
    "AMT_SUB_CC" integer,
    "CHILD_SUPPORT_AMT" integer,
    "FAMILY_CASH_RESOURCES" integer,
    "CASH_AMOUNT" integer,
    "NBR_MONTHS" integer,
    "CC_AMOUNT" integer,
    "CHILDREN_COVERED" integer,
    "CC_NBR_MONTHS" integer,
    "TRANSP_AMOUNT" integer,
    "TRANSP_NBR_MONTHS" integer,
    "TRANSITION_SERVICES_AMOUNT" integer,
    "TRANSITION_NBR_MONTHS" integer,
    "OTHER_AMOUNT" integer,
    "OTHER_NBR_MONTHS" integer,
    "SANC_REDUCTION_AMT" integer,
    "WORK_REQ_SANCTION" integer,
    "FAMILY_SANC_ADULT" integer,
    "SANC_TEEN_PARENT" integer,
    "NON_COOPERATION_CSE" integer,
    "FAILURE_TO_COMPLY" integer,
    "OTHER_SANCTION" integer,
    "RECOUPMENT_PRIOR_OVRPMT" integer,
    "OTHER_TOTAL_REDUCTIONS" integer,
    "FAMILY_CAP" integer,
    "REDUCTIONS_ON_RECEIPTS" integer,
    "OTHER_NON_SANCTION" integer,
    "WAIVER_EVAL_CONTROL_GRPS" integer,
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);


--
-- Name: stts_stt; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stts_stt (
    id integer NOT NULL,
    type character varying(200),
    postal_code character varying(2),
    name character varying(1000) NOT NULL,
    region_id integer,
    state_id integer,
    filenames jsonb,
    stt_code character varying(3),
    ssp boolean,
    sample boolean,
    timezone character varying(63) NOT NULL
);


--
-- Name: search_indexes_ssp_m2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_ssp_m2 (
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FIPS_CODE" character varying(2),
    "FAMILY_AFFILIATION" integer,
    "NONCUSTODIAL_PARENT" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "FED_OASDI_PROGRAM" integer,
    "FED_DISABILITY_STATUS" integer,
    "DISABLED_TITLE_XIVAPDT" integer,
    "AID_AGED_BLIND" integer,
    "RECEIVE_SSI" integer,
    "MARITAL_STATUS" integer,
    "RELATIONSHIP_HOH" integer,
    "PARENT_MINOR_CHILD" integer,
    "NEEDS_PREGNANT_WOMAN" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "COOPERATION_CHILD_SUPPORT" integer,
    "EMPLOYMENT_STATUS" integer,
    "WORK_ELIGIBLE_INDICATOR" integer,
    "WORK_PART_STATUS" integer,
    "UNSUB_EMPLOYMENT" integer,
    "SUB_PRIVATE_EMPLOYMENT" integer,
    "SUB_PUBLIC_EMPLOYMENT" integer,
    "WORK_EXPERIENCE_HOP" integer,
    "WORK_EXPERIENCE_EA" integer,
    "WORK_EXPERIENCE_HOL" integer,
    "OJT" integer,
    "JOB_SEARCH_HOP" integer,
    "JOB_SEARCH_EA" integer,
    "JOB_SEARCH_HOL" integer,
    "COMM_SERVICES_HOP" integer,
    "COMM_SERVICES_EA" integer,
    "COMM_SERVICES_HOL" integer,
    "VOCATIONAL_ED_TRAINING_HOP" integer,
    "VOCATIONAL_ED_TRAINING_EA" integer,
    "VOCATIONAL_ED_TRAINING_HOL" integer,
    "JOB_SKILLS_TRAINING_HOP" integer,
    "JOB_SKILLS_TRAINING_EA" integer,
    "JOB_SKILLS_TRAINING_HOL" integer,
    "ED_NO_HIGH_SCHOOL_DIPL_HOP" integer,
    "ED_NO_HIGH_SCHOOL_DIPL_EA" integer,
    "ED_NO_HIGH_SCHOOL_DIPL_HOL" integer,
    "SCHOOL_ATTENDENCE_HOP" integer,
    "SCHOOL_ATTENDENCE_EA" integer,
    "SCHOOL_ATTENDENCE_HOL" integer,
    "PROVIDE_CC_HOP" integer,
    "PROVIDE_CC_EA" integer,
    "PROVIDE_CC_HOL" integer,
    "OTHER_WORK_ACTIVITIES" integer,
    "DEEMED_HOURS_FOR_OVERALL" integer,
    "DEEMED_HOURS_FOR_TWO_PARENT" integer,
    "EARNED_INCOME" integer,
    "UNEARNED_INCOME_TAX_CREDIT" integer,
    "UNEARNED_SOCIAL_SECURITY" integer,
    "UNEARNED_SSI" integer,
    "UNEARNED_WORKERS_COMP" integer,
    "OTHER_UNEARNED_INCOME" integer,
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_ssp_m3; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_ssp_m3 (
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FIPS_CODE" character varying(2),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(100),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "RECEIVE_NONSSI_BENEFITS" integer,
    "RECEIVE_SSI" integer,
    "RELATIONSHIP_HOH" integer,
    "PARENT_MINOR_CHILD" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "UNEARNED_SSI" integer,
    "OTHER_UNEARNED_INCOME" integer,
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_ssp_m4; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_ssp_m4 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "DISPOSITION" integer,
    "CLOSURE_REASON" character varying(2),
    "REC_SUB_HOUSING" integer,
    "REC_MED_ASSIST" integer,
    "REC_FOOD_STAMPS" integer,
    "REC_SUB_CC" integer,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_ssp_m5; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_ssp_m5 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "REC_OASDI_INSURANCE" integer,
    "REC_FEDERAL_DISABILITY" integer,
    "REC_AID_TOTALLY_DISABLED" integer,
    "REC_AID_AGED_BLIND" integer,
    "REC_SSI" integer,
    "MARITAL_STATUS" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "NEEDS_OF_PREGNANT_WOMAN" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "EMPLOYMENT_STATUS" integer,
    "AMOUNT_EARNED_INCOME" character varying(4),
    "AMOUNT_UNEARNED_INCOME" character varying(4),
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_ssp_m6; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_ssp_m6 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "CALENDAR_QUARTER" integer,
    "RPT_MONTH_YEAR" integer,
    "SSPMOE_FAMILIES" integer,
    "NUM_2_PARENTS" integer,
    "NUM_1_PARENTS" integer,
    "NUM_NO_PARENTS" integer,
    "NUM_RECIPIENTS" integer,
    "ADULT_RECIPIENTS" integer,
    "CHILD_RECIPIENTS" integer,
    "NONCUSTODIALS" integer,
    "AMT_ASSISTANCE" integer,
    "CLOSED_CASES" integer,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_ssp_m7; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_ssp_m7 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "CALENDAR_QUARTER" integer,
    "RPT_MONTH_YEAR" integer,
    "TDRS_SECTION_IND" character varying(1),
    "STRATUM" character varying(2),
    "FAMILIES_MONTH" integer,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tanf_t1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tanf_t1 (
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "DISPOSITION" integer,
    "FIPS_CODE" character varying(2),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "FUNDING_STREAM" integer,
    "NEW_APPLICANT" integer,
    "NBR_FAMILY_MEMBERS" integer,
    "FAMILY_TYPE" integer,
    "RECEIVES_SUB_HOUSING" integer,
    "RECEIVES_MED_ASSISTANCE" integer,
    "RECEIVES_FOOD_STAMPS" integer,
    "AMT_FOOD_STAMP_ASSISTANCE" integer,
    "RECEIVES_SUB_CC" integer,
    "AMT_SUB_CC" integer,
    "CHILD_SUPPORT_AMT" integer,
    "FAMILY_CASH_RESOURCES" integer,
    "CASH_AMOUNT" integer,
    "NBR_MONTHS" integer,
    "CC_AMOUNT" integer,
    "CHILDREN_COVERED" integer,
    "CC_NBR_MONTHS" integer,
    "TRANSP_AMOUNT" integer,
    "TRANSP_NBR_MONTHS" integer,
    "TRANSITION_SERVICES_AMOUNT" integer,
    "TRANSITION_NBR_MONTHS" integer,
    "OTHER_AMOUNT" integer,
    "OTHER_NBR_MONTHS" integer,
    "SANC_REDUCTION_AMT" integer,
    "WORK_REQ_SANCTION" integer,
    "FAMILY_SANC_ADULT" integer,
    "SANC_TEEN_PARENT" integer,
    "NON_COOPERATION_CSE" integer,
    "FAILURE_TO_COMPLY" integer,
    "OTHER_SANCTION" integer,
    "RECOUPMENT_PRIOR_OVRPMT" integer,
    "OTHER_TOTAL_REDUCTIONS" integer,
    "FAMILY_CAP" integer,
    "REDUCTIONS_ON_RECEIPTS" integer,
    "OTHER_NON_SANCTION" integer,
    "WAIVER_EVAL_CONTROL_GRPS" integer,
    "FAMILY_EXEMPT_TIME_LIMITS" integer,
    "FAMILY_NEW_CHILD" integer,
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tanf_t2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tanf_t2 (
    "AID_AGED_BLIND" integer,
    "CASE_NUMBER" character varying(11),
    "CITIZENSHIP_STATUS" integer,
    "COMM_SERVICES_EA" character varying(2),
    "COMM_SERVICES_HOL" character varying(2),
    "COMM_SERVICES_HOP" character varying(2),
    "COOPERATION_CHILD_SUPPORT" integer,
    "CURRENT_MONTH_STATE_EXEMPT" integer,
    "DATE_OF_BIRTH" character varying(8),
    "DEEMED_HOURS_FOR_OVERALL" character varying(2),
    "DEEMED_HOURS_FOR_TWO_PARENT" character varying(2),
    "DISABLED_TITLE_XIVAPDT" integer,
    "EARNED_INCOME" character varying(4),
    "EDUCATION_LEVEL" character varying(2),
    "ED_NO_HIGH_SCHOOL_DIPL_EA" character varying(2),
    "ED_NO_HIGH_SCHOOL_DIPL_HOL" character varying(2),
    "ED_NO_HIGH_SCHOOL_DIPL_HOP" character varying(2),
    "EMPLOYMENT_STATUS" integer,
    "FAMILY_AFFILIATION" integer,
    "FED_DISABILITY_STATUS" integer,
    "FED_OASDI_PROGRAM" integer,
    "SEX" integer,
    "JOB_SEARCH_EA" character varying(2),
    "JOB_SEARCH_HOL" character varying(2),
    "JOB_SEARCH_HOP" character varying(2),
    "JOB_SKILLS_TRAINING_EA" character varying(2),
    "JOB_SKILLS_TRAINING_HOL" character varying(2),
    "JOB_SKILLS_TRAINING_HOP" character varying(2),
    "MARITAL_STATUS" integer,
    "MONTHS_FED_TIME_LIMIT" character varying(3),
    "MONTHS_STATE_TIME_LIMIT" character varying(2),
    "NEEDS_PREGNANT_WOMAN" integer,
    "NONCUSTODIAL_PARENT" integer,
    "OJT" character varying(2),
    "OTHER_UNEARNED_INCOME" character varying(4),
    "OTHER_WORK_ACTIVITIES" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "PROVIDE_CC_EA" character varying(2),
    "PROVIDE_CC_HOL" character varying(2),
    "PROVIDE_CC_HOP" character varying(2),
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_HISPANIC" integer,
    "RACE_WHITE" integer,
    "RECEIVE_SSI" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "SCHOOL_ATTENDENCE_EA" character varying(2),
    "SCHOOL_ATTENDENCE_HOL" character varying(2),
    "SCHOOL_ATTENDENCE_HOP" character varying(2),
    "SSN" character varying(9),
    "SUB_PRIVATE_EMPLOYMENT" character varying(2),
    "SUB_PUBLIC_EMPLOYMENT" character varying(2),
    "UNEARNED_INCOME_TAX_CREDIT" character varying(4),
    "UNEARNED_SOCIAL_SECURITY" character varying(4),
    "UNEARNED_SSI" character varying(4),
    "UNEARNED_WORKERS_COMP" character varying(4),
    "UNSUB_EMPLOYMENT" character varying(2),
    "VOCATIONAL_ED_TRAINING_EA" character varying(2),
    "VOCATIONAL_ED_TRAINING_HOL" character varying(2),
    "VOCATIONAL_ED_TRAINING_HOP" character varying(2),
    "WORK_ELIGIBLE_INDICATOR" character varying(2),
    "WORK_EXPERIENCE_EA" character varying(2),
    "WORK_EXPERIENCE_HOL" character varying(2),
    "WORK_EXPERIENCE_HOP" character varying(2),
    "WORK_PART_STATUS" character varying(2),
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tanf_t3; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tanf_t3 (
    "CASE_NUMBER" character varying(11),
    "CITIZENSHIP_STATUS" integer,
    "DATE_OF_BIRTH" character varying(8),
    "EDUCATION_LEVEL" character varying(2),
    "FAMILY_AFFILIATION" integer,
    "SEX" integer,
    "OTHER_UNEARNED_INCOME" character varying(4),
    "PARENT_MINOR_CHILD" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_HISPANIC" integer,
    "RACE_WHITE" integer,
    "RECEIVE_NONSSA_BENEFITS" integer,
    "RECEIVE_SSI" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "SSN" character varying(9),
    "UNEARNED_SSI" character varying(4),
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tanf_t4; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tanf_t4 (
    id uuid NOT NULL,
    datafile_id integer,
    "CASE_NUMBER" character varying(11),
    "CLOSURE_REASON" character varying(2),
    "COUNTY_FIPS_CODE" character varying(3),
    "DISPOSITION" integer,
    "REC_FOOD_STAMPS" integer,
    "REC_MED_ASSIST" integer,
    "REC_SUB_CC" integer,
    "REC_SUB_HOUSING" integer,
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    line_number integer
);


--
-- Name: search_indexes_tanf_t5; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tanf_t5 (
    id uuid NOT NULL,
    datafile_id integer,
    "AMOUNT_EARNED_INCOME" character varying(4),
    "AMOUNT_UNEARNED_INCOME" character varying(4),
    "CASE_NUMBER" character varying(11),
    "CITIZENSHIP_STATUS" integer,
    "COUNTABLE_MONTHS_STATE_TRIBE" character varying(2),
    "COUNTABLE_MONTH_FED_TIME" character varying(3),
    "DATE_OF_BIRTH" character varying(8),
    "EDUCATION_LEVEL" character varying(2),
    "EMPLOYMENT_STATUS" integer,
    "FAMILY_AFFILIATION" integer,
    "SEX" integer,
    "MARITAL_STATUS" integer,
    "NEEDS_OF_PREGNANT_WOMAN" integer,
    "PARENT_MINOR_CHILD" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_HISPANIC" integer,
    "RACE_WHITE" integer,
    "REC_AID_AGED_BLIND" integer,
    "REC_AID_TOTALLY_DISABLED" integer,
    "REC_FEDERAL_DISABILITY" integer,
    "REC_OASDI_INSURANCE" integer,
    "REC_SSI" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "SSN" character varying(9),
    line_number integer
);


--
-- Name: search_indexes_tanf_t6; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tanf_t6 (
    id uuid NOT NULL,
    datafile_id integer,
    "ASSISTANCE" integer,
    "CALENDAR_QUARTER" integer,
    "NUM_1_PARENTS" integer,
    "NUM_2_PARENTS" integer,
    "NUM_ADULT_RECIPIENTS" integer,
    "NUM_APPLICATIONS" integer,
    "NUM_APPROVED" integer,
    "NUM_BIRTHS" integer,
    "NUM_CHILD_RECIPIENTS" integer,
    "NUM_CLOSED_CASES" integer,
    "NUM_DENIED" integer,
    "NUM_FAMILIES" integer,
    "NUM_NONCUSTODIALS" integer,
    "NUM_NO_PARENTS" integer,
    "NUM_OUTWEDLOCK_BIRTHS" integer,
    "NUM_RECIPIENTS" integer,
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    line_number integer
);


--
-- Name: search_indexes_tanf_t7; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tanf_t7 (
    id uuid NOT NULL,
    datafile_id integer,
    "CALENDAR_QUARTER" integer,
    "FAMILIES_MONTH" integer,
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "STRATUM" character varying(2),
    "TDRS_SECTION_IND" character varying(1),
    line_number integer
);


--
-- Name: search_indexes_tribal_tanf_t1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tribal_tanf_t1 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "FUNDING_STREAM" integer,
    "DISPOSITION" integer,
    "NEW_APPLICANT" integer,
    "NBR_FAMILY_MEMBERS" integer,
    "FAMILY_TYPE" integer,
    "RECEIVES_SUB_HOUSING" integer,
    "RECEIVES_MED_ASSISTANCE" integer,
    "RECEIVES_FOOD_STAMPS" integer,
    "AMT_FOOD_STAMP_ASSISTANCE" integer,
    "RECEIVES_SUB_CC" integer,
    "AMT_SUB_CC" integer,
    "CHILD_SUPPORT_AMT" integer,
    "FAMILY_CASH_RESOURCES" integer,
    "CASH_AMOUNT" integer,
    "NBR_MONTHS" integer,
    "CC_AMOUNT" integer,
    "CHILDREN_COVERED" integer,
    "CC_NBR_MONTHS" integer,
    "TRANSP_AMOUNT" integer,
    "TRANSP_NBR_MONTHS" integer,
    "TRANSITION_SERVICES_AMOUNT" integer,
    "TRANSITION_NBR_MONTHS" integer,
    "OTHER_AMOUNT" integer,
    "OTHER_NBR_MONTHS" integer,
    "SANC_REDUCTION_AMT" integer,
    "WORK_REQ_SANCTION" integer,
    "FAMILY_SANC_ADULT" integer,
    "SANC_TEEN_PARENT" integer,
    "NON_COOPERATION_CSE" integer,
    "FAILURE_TO_COMPLY" integer,
    "OTHER_SANCTION" integer,
    "RECOUPMENT_PRIOR_OVRPMT" integer,
    "OTHER_TOTAL_REDUCTIONS" integer,
    "FAMILY_CAP" integer,
    "REDUCTIONS_ON_RECEIPTS" integer,
    "OTHER_NON_SANCTION" integer,
    "WAIVER_EVAL_CONTROL_GRPS" integer,
    "FAMILY_EXEMPT_TIME_LIMITS" integer,
    "FAMILY_NEW_CHILD" integer,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tribal_tanf_t2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tribal_tanf_t2 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "NONCUSTODIAL_PARENT" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "FED_OASDI_PROGRAM" integer,
    "FED_DISABILITY_STATUS" integer,
    "DISABLED_TITLE_XIVAPDT" integer,
    "AID_AGED_BLIND" integer,
    "RECEIVE_SSI" integer,
    "MARITAL_STATUS" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "NEEDS_PREGNANT_WOMAN" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "COOPERATION_CHILD_SUPPORT" integer,
    "MONTHS_FED_TIME_LIMIT" character varying(3),
    "MONTHS_STATE_TIME_LIMIT" character varying(2),
    "CURRENT_MONTH_STATE_EXEMPT" integer,
    "EMPLOYMENT_STATUS" integer,
    "WORK_PART_STATUS" character varying(2),
    "UNSUB_EMPLOYMENT" character varying(2),
    "SUB_PRIVATE_EMPLOYMENT" character varying(2),
    "SUB_PUBLIC_EMPLOYMENT" character varying(2),
    "WORK_EXPERIENCE" character varying(2),
    "OJT" character varying(2),
    "JOB_SEARCH" character varying(2),
    "COMM_SERVICES" character varying(2),
    "VOCATIONAL_ED_TRAINING" character varying(2),
    "JOB_SKILLS_TRAINING" character varying(2),
    "ED_NO_HIGH_SCHOOL_DIPLOMA" character varying(2),
    "SCHOOL_ATTENDENCE" character varying(2),
    "PROVIDE_CC" character varying(2),
    "ADD_WORK_ACTIVITIES" character varying(2),
    "OTHER_WORK_ACTIVITIES" character varying(2),
    "REQ_HRS_WAIVER_DEMO" character varying(2),
    "EARNED_INCOME" character varying(4),
    "UNEARNED_INCOME_TAX_CREDIT" character varying(4),
    "UNEARNED_SOCIAL_SECURITY" character varying(4),
    "UNEARNED_SSI" character varying(4),
    "UNEARNED_WORKERS_COMP" character varying(4),
    "OTHER_UNEARNED_INCOME" character varying(4),
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tribal_tanf_t3; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tribal_tanf_t3 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "RECEIVE_NONSSA_BENEFITS" integer,
    "RECEIVE_SSI" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "UNEARNED_SSI" character varying(4),
    "OTHER_UNEARNED_INCOME" character varying(4),
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tribal_tanf_t4; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tribal_tanf_t4 (
    id uuid NOT NULL,
    "RecordType" character varying(71),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "DISPOSITION" integer,
    "CLOSURE_REASON" character varying(2),
    "REC_SUB_HOUSING" integer,
    "REC_MED_ASSIST" integer,
    "REC_FOOD_STAMPS" integer,
    "REC_SUB_CC" integer,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tribal_tanf_t5; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tribal_tanf_t5 (
    id uuid NOT NULL,
    "RecordType" character varying(71),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "REC_OASDI_INSURANCE" integer,
    "REC_FEDERAL_DISABILITY" integer,
    "REC_AID_TOTALLY_DISABLED" integer,
    "REC_AID_AGED_BLIND" integer,
    "REC_SSI" integer,
    "MARITAL_STATUS" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "NEEDS_OF_PREGNANT_WOMAN" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "COUNTABLE_MONTH_FED_TIME" character varying(3),
    "COUNTABLE_MONTHS_STATE_TRIBE" character varying(2),
    "EMPLOYMENT_STATUS" integer,
    "AMOUNT_EARNED_INCOME" character varying(4),
    "AMOUNT_UNEARNED_INCOME" character varying(4),
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tribal_tanf_t6; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tribal_tanf_t6 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "CALENDAR_QUARTER" integer,
    "RPT_MONTH_YEAR" integer,
    "NUM_APPLICATIONS" integer,
    "NUM_APPROVED" integer,
    "NUM_DENIED" integer,
    "ASSISTANCE" integer,
    "NUM_FAMILIES" integer,
    "NUM_2_PARENTS" integer,
    "NUM_1_PARENTS" integer,
    "NUM_NO_PARENTS" integer,
    "NUM_RECIPIENTS" integer,
    "NUM_ADULT_RECIPIENTS" integer,
    "NUM_CHILD_RECIPIENTS" integer,
    "NUM_NONCUSTODIALS" integer,
    "NUM_BIRTHS" integer,
    "NUM_OUTWEDLOCK_BIRTHS" integer,
    "NUM_CLOSED_CASES" integer,
    datafile_id integer,
    line_number integer
);


--
-- Name: search_indexes_tribal_tanf_t7; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tribal_tanf_t7 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "CALENDAR_QUARTER" integer,
    "RPT_MONTH_YEAR" integer,
    "TDRS_SECTION_IND" character varying(1),
    "STRATUM" character varying(2),
    "FAMILIES_MONTH" integer,
    datafile_id integer,
    line_number integer
);


--
-- Name: parser_error; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parser_error (
    id integer NOT NULL,
    row_number integer,
    column_number character varying(8),
    item_number character varying(8),
    field_name text,
    case_number text,
    rpt_month_year integer,
    error_message text,
    error_type text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    fields_json jsonb,
    content_type_id integer,
    file_id integer,
    object_id uuid,
    deprecated boolean NOT NULL,
    values_json jsonb
);


--
-- Name: parser_error_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.parser_error ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.parser_error_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: parsers_datafilesummary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parsers_datafilesummary (
    id bigint NOT NULL,
    status character varying(50) NOT NULL,
    case_aggregates jsonb,
    datafile_id integer NOT NULL,
    total_number_of_records_created integer,
    total_number_of_records_in_file integer,
    error_report character varying(500)
);


--
-- Name: parsers_datafilesummary_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.parsers_datafilesummary ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.parsers_datafilesummary_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: reports_reportfile_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.data_files_datafile ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.reports_reportfile_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: search_indexes_programaudit_t1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_programaudit_t1 (
    line_number integer,
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FUNDING_STREAM" integer,
    "CASH_AMOUNT" integer,
    datafile_id integer
);


--
-- Name: search_indexes_programaudit_t2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_programaudit_t2 (
    line_number integer,
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "CITIZENSHIP_STATUS" integer,
    datafile_id integer
);


--
-- Name: search_indexes_programaudit_t3; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_programaudit_t3 (
    line_number integer,
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "CITIZENSHIP_STATUS" integer,
    datafile_id integer
);


--
-- Name: search_indexes_reparsemeta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_reparsemeta (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    timeout_at timestamp with time zone,
    num_records_deleted integer NOT NULL,
    total_num_records_initial bigint NOT NULL,
    total_num_records_post bigint NOT NULL,
    db_backup_location character varying(512) NOT NULL,
    fiscal_quarter character varying(2),
    fiscal_year integer,
    "all" boolean NOT NULL,
    new_indices boolean NOT NULL,
    delete_old_indices boolean NOT NULL,
    CONSTRAINT search_indexes_reparsemeta_fiscal_year_check CHECK ((fiscal_year >= 0)),
    CONSTRAINT search_indexes_reparsemeta_num_records_deleted_check CHECK ((num_records_deleted >= 0)),
    CONSTRAINT search_indexes_reparsemeta_total_num_records_initial_check CHECK ((total_num_records_initial >= 0)),
    CONSTRAINT search_indexes_reparsemeta_total_num_records_post_check CHECK ((total_num_records_post >= 0))
);


--
-- Name: search_indexes_reparsemeta_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.search_indexes_reparsemeta ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.search_indexes_reparsemeta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: search_indexes_tanf_exiter1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.search_indexes_tanf_exiter1 (
    id uuid NOT NULL,
    "RecordType" character varying(25),
    "EXIT_DATE" integer,
    "SSN" character varying(9),
    datafile_id integer,
    line_number integer
);


--
-- Name: stts_stt_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.stts_stt ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.stts_stt_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- PostgreSQL database dump complete
--

--
-- Name: shadow_data_files_datafile; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_data_files_datafile (
    id integer NOT NULL,
    original_filename character varying(256) NOT NULL,
    slug character varying(256) NOT NULL,
    extension character varying(8) NOT NULL,
    quarter character varying(16) NOT NULL,
    year integer NOT NULL,
    section character varying(32) NOT NULL,
    version integer NOT NULL,
    stt_id integer NOT NULL,
    user_id uuid NOT NULL,
    created_at timestamp with time zone NOT NULL,
    file character varying(100),
    s3_versioning_id character varying(1024),
    program_type character varying(32) NOT NULL,
    is_program_audit boolean NOT NULL,
    state character varying(32) NOT NULL
);
--
-- Name: shadow_search_indexes_ssp_m1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_ssp_m1 (
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FIPS_CODE" character varying(2),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "DISPOSITION" integer,
    "NBR_FAMILY_MEMBERS" integer,
    "FAMILY_TYPE" integer,
    "TANF_ASST_IN_6MONTHS" integer,
    "RECEIVES_SUB_HOUSING" integer,
    "RECEIVES_MED_ASSISTANCE" integer,
    "RECEIVES_FOOD_STAMPS" integer,
    "AMT_FOOD_STAMP_ASSISTANCE" integer,
    "RECEIVES_SUB_CC" integer,
    "AMT_SUB_CC" integer,
    "CHILD_SUPPORT_AMT" integer,
    "FAMILY_CASH_RESOURCES" integer,
    "CASH_AMOUNT" integer,
    "NBR_MONTHS" integer,
    "CC_AMOUNT" integer,
    "CHILDREN_COVERED" integer,
    "CC_NBR_MONTHS" integer,
    "TRANSP_AMOUNT" integer,
    "TRANSP_NBR_MONTHS" integer,
    "TRANSITION_SERVICES_AMOUNT" integer,
    "TRANSITION_NBR_MONTHS" integer,
    "OTHER_AMOUNT" integer,
    "OTHER_NBR_MONTHS" integer,
    "SANC_REDUCTION_AMT" integer,
    "WORK_REQ_SANCTION" integer,
    "FAMILY_SANC_ADULT" integer,
    "SANC_TEEN_PARENT" integer,
    "NON_COOPERATION_CSE" integer,
    "FAILURE_TO_COMPLY" integer,
    "OTHER_SANCTION" integer,
    "RECOUPMENT_PRIOR_OVRPMT" integer,
    "OTHER_TOTAL_REDUCTIONS" integer,
    "FAMILY_CAP" integer,
    "REDUCTIONS_ON_RECEIPTS" integer,
    "OTHER_NON_SANCTION" integer,
    "WAIVER_EVAL_CONTROL_GRPS" integer,
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_ssp_m2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_ssp_m2 (
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FIPS_CODE" character varying(2),
    "FAMILY_AFFILIATION" integer,
    "NONCUSTODIAL_PARENT" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "FED_OASDI_PROGRAM" integer,
    "FED_DISABILITY_STATUS" integer,
    "DISABLED_TITLE_XIVAPDT" integer,
    "AID_AGED_BLIND" integer,
    "RECEIVE_SSI" integer,
    "MARITAL_STATUS" integer,
    "RELATIONSHIP_HOH" integer,
    "PARENT_MINOR_CHILD" integer,
    "NEEDS_PREGNANT_WOMAN" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "COOPERATION_CHILD_SUPPORT" integer,
    "EMPLOYMENT_STATUS" integer,
    "WORK_ELIGIBLE_INDICATOR" integer,
    "WORK_PART_STATUS" integer,
    "UNSUB_EMPLOYMENT" integer,
    "SUB_PRIVATE_EMPLOYMENT" integer,
    "SUB_PUBLIC_EMPLOYMENT" integer,
    "WORK_EXPERIENCE_HOP" integer,
    "WORK_EXPERIENCE_EA" integer,
    "WORK_EXPERIENCE_HOL" integer,
    "OJT" integer,
    "JOB_SEARCH_HOP" integer,
    "JOB_SEARCH_EA" integer,
    "JOB_SEARCH_HOL" integer,
    "COMM_SERVICES_HOP" integer,
    "COMM_SERVICES_EA" integer,
    "COMM_SERVICES_HOL" integer,
    "VOCATIONAL_ED_TRAINING_HOP" integer,
    "VOCATIONAL_ED_TRAINING_EA" integer,
    "VOCATIONAL_ED_TRAINING_HOL" integer,
    "JOB_SKILLS_TRAINING_HOP" integer,
    "JOB_SKILLS_TRAINING_EA" integer,
    "JOB_SKILLS_TRAINING_HOL" integer,
    "ED_NO_HIGH_SCHOOL_DIPL_HOP" integer,
    "ED_NO_HIGH_SCHOOL_DIPL_EA" integer,
    "ED_NO_HIGH_SCHOOL_DIPL_HOL" integer,
    "SCHOOL_ATTENDENCE_HOP" integer,
    "SCHOOL_ATTENDENCE_EA" integer,
    "SCHOOL_ATTENDENCE_HOL" integer,
    "PROVIDE_CC_HOP" integer,
    "PROVIDE_CC_EA" integer,
    "PROVIDE_CC_HOL" integer,
    "OTHER_WORK_ACTIVITIES" integer,
    "DEEMED_HOURS_FOR_OVERALL" integer,
    "DEEMED_HOURS_FOR_TWO_PARENT" integer,
    "EARNED_INCOME" integer,
    "UNEARNED_INCOME_TAX_CREDIT" integer,
    "UNEARNED_SOCIAL_SECURITY" integer,
    "UNEARNED_SSI" integer,
    "UNEARNED_WORKERS_COMP" integer,
    "OTHER_UNEARNED_INCOME" integer,
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_ssp_m3; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_ssp_m3 (
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FIPS_CODE" character varying(2),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(100),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "RECEIVE_NONSSI_BENEFITS" integer,
    "RECEIVE_SSI" integer,
    "RELATIONSHIP_HOH" integer,
    "PARENT_MINOR_CHILD" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "UNEARNED_SSI" integer,
    "OTHER_UNEARNED_INCOME" integer,
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_ssp_m4; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_ssp_m4 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "DISPOSITION" integer,
    "CLOSURE_REASON" character varying(2),
    "REC_SUB_HOUSING" integer,
    "REC_MED_ASSIST" integer,
    "REC_FOOD_STAMPS" integer,
    "REC_SUB_CC" integer,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_ssp_m5; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_ssp_m5 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "REC_OASDI_INSURANCE" integer,
    "REC_FEDERAL_DISABILITY" integer,
    "REC_AID_TOTALLY_DISABLED" integer,
    "REC_AID_AGED_BLIND" integer,
    "REC_SSI" integer,
    "MARITAL_STATUS" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "NEEDS_OF_PREGNANT_WOMAN" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "EMPLOYMENT_STATUS" integer,
    "AMOUNT_EARNED_INCOME" character varying(4),
    "AMOUNT_UNEARNED_INCOME" character varying(4),
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_ssp_m6; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_ssp_m6 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "CALENDAR_QUARTER" integer,
    "RPT_MONTH_YEAR" integer,
    "SSPMOE_FAMILIES" integer,
    "NUM_2_PARENTS" integer,
    "NUM_1_PARENTS" integer,
    "NUM_NO_PARENTS" integer,
    "NUM_RECIPIENTS" integer,
    "ADULT_RECIPIENTS" integer,
    "CHILD_RECIPIENTS" integer,
    "NONCUSTODIALS" integer,
    "AMT_ASSISTANCE" integer,
    "CLOSED_CASES" integer,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_ssp_m7; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_ssp_m7 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "CALENDAR_QUARTER" integer,
    "RPT_MONTH_YEAR" integer,
    "TDRS_SECTION_IND" character varying(1),
    "STRATUM" character varying(2),
    "FAMILIES_MONTH" integer,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tanf_t1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tanf_t1 (
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "DISPOSITION" integer,
    "FIPS_CODE" character varying(2),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "FUNDING_STREAM" integer,
    "NEW_APPLICANT" integer,
    "NBR_FAMILY_MEMBERS" integer,
    "FAMILY_TYPE" integer,
    "RECEIVES_SUB_HOUSING" integer,
    "RECEIVES_MED_ASSISTANCE" integer,
    "RECEIVES_FOOD_STAMPS" integer,
    "AMT_FOOD_STAMP_ASSISTANCE" integer,
    "RECEIVES_SUB_CC" integer,
    "AMT_SUB_CC" integer,
    "CHILD_SUPPORT_AMT" integer,
    "FAMILY_CASH_RESOURCES" integer,
    "CASH_AMOUNT" integer,
    "NBR_MONTHS" integer,
    "CC_AMOUNT" integer,
    "CHILDREN_COVERED" integer,
    "CC_NBR_MONTHS" integer,
    "TRANSP_AMOUNT" integer,
    "TRANSP_NBR_MONTHS" integer,
    "TRANSITION_SERVICES_AMOUNT" integer,
    "TRANSITION_NBR_MONTHS" integer,
    "OTHER_AMOUNT" integer,
    "OTHER_NBR_MONTHS" integer,
    "SANC_REDUCTION_AMT" integer,
    "WORK_REQ_SANCTION" integer,
    "FAMILY_SANC_ADULT" integer,
    "SANC_TEEN_PARENT" integer,
    "NON_COOPERATION_CSE" integer,
    "FAILURE_TO_COMPLY" integer,
    "OTHER_SANCTION" integer,
    "RECOUPMENT_PRIOR_OVRPMT" integer,
    "OTHER_TOTAL_REDUCTIONS" integer,
    "FAMILY_CAP" integer,
    "REDUCTIONS_ON_RECEIPTS" integer,
    "OTHER_NON_SANCTION" integer,
    "WAIVER_EVAL_CONTROL_GRPS" integer,
    "FAMILY_EXEMPT_TIME_LIMITS" integer,
    "FAMILY_NEW_CHILD" integer,
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tanf_t2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tanf_t2 (
    "AID_AGED_BLIND" integer,
    "CASE_NUMBER" character varying(11),
    "CITIZENSHIP_STATUS" integer,
    "COMM_SERVICES_EA" character varying(2),
    "COMM_SERVICES_HOL" character varying(2),
    "COMM_SERVICES_HOP" character varying(2),
    "COOPERATION_CHILD_SUPPORT" integer,
    "CURRENT_MONTH_STATE_EXEMPT" integer,
    "DATE_OF_BIRTH" character varying(8),
    "DEEMED_HOURS_FOR_OVERALL" character varying(2),
    "DEEMED_HOURS_FOR_TWO_PARENT" character varying(2),
    "DISABLED_TITLE_XIVAPDT" integer,
    "EARNED_INCOME" character varying(4),
    "EDUCATION_LEVEL" character varying(2),
    "ED_NO_HIGH_SCHOOL_DIPL_EA" character varying(2),
    "ED_NO_HIGH_SCHOOL_DIPL_HOL" character varying(2),
    "ED_NO_HIGH_SCHOOL_DIPL_HOP" character varying(2),
    "EMPLOYMENT_STATUS" integer,
    "FAMILY_AFFILIATION" integer,
    "FED_DISABILITY_STATUS" integer,
    "FED_OASDI_PROGRAM" integer,
    "SEX" integer,
    "JOB_SEARCH_EA" character varying(2),
    "JOB_SEARCH_HOL" character varying(2),
    "JOB_SEARCH_HOP" character varying(2),
    "JOB_SKILLS_TRAINING_EA" character varying(2),
    "JOB_SKILLS_TRAINING_HOL" character varying(2),
    "JOB_SKILLS_TRAINING_HOP" character varying(2),
    "MARITAL_STATUS" integer,
    "MONTHS_FED_TIME_LIMIT" character varying(3),
    "MONTHS_STATE_TIME_LIMIT" character varying(2),
    "NEEDS_PREGNANT_WOMAN" integer,
    "NONCUSTODIAL_PARENT" integer,
    "OJT" character varying(2),
    "OTHER_UNEARNED_INCOME" character varying(4),
    "OTHER_WORK_ACTIVITIES" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "PROVIDE_CC_EA" character varying(2),
    "PROVIDE_CC_HOL" character varying(2),
    "PROVIDE_CC_HOP" character varying(2),
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_HISPANIC" integer,
    "RACE_WHITE" integer,
    "RECEIVE_SSI" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "SCHOOL_ATTENDENCE_EA" character varying(2),
    "SCHOOL_ATTENDENCE_HOL" character varying(2),
    "SCHOOL_ATTENDENCE_HOP" character varying(2),
    "SSN" character varying(9),
    "SUB_PRIVATE_EMPLOYMENT" character varying(2),
    "SUB_PUBLIC_EMPLOYMENT" character varying(2),
    "UNEARNED_INCOME_TAX_CREDIT" character varying(4),
    "UNEARNED_SOCIAL_SECURITY" character varying(4),
    "UNEARNED_SSI" character varying(4),
    "UNEARNED_WORKERS_COMP" character varying(4),
    "UNSUB_EMPLOYMENT" character varying(2),
    "VOCATIONAL_ED_TRAINING_EA" character varying(2),
    "VOCATIONAL_ED_TRAINING_HOL" character varying(2),
    "VOCATIONAL_ED_TRAINING_HOP" character varying(2),
    "WORK_ELIGIBLE_INDICATOR" character varying(2),
    "WORK_EXPERIENCE_EA" character varying(2),
    "WORK_EXPERIENCE_HOL" character varying(2),
    "WORK_EXPERIENCE_HOP" character varying(2),
    "WORK_PART_STATUS" character varying(2),
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tanf_t3; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tanf_t3 (
    "CASE_NUMBER" character varying(11),
    "CITIZENSHIP_STATUS" integer,
    "DATE_OF_BIRTH" character varying(8),
    "EDUCATION_LEVEL" character varying(2),
    "FAMILY_AFFILIATION" integer,
    "SEX" integer,
    "OTHER_UNEARNED_INCOME" character varying(4),
    "PARENT_MINOR_CHILD" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_HISPANIC" integer,
    "RACE_WHITE" integer,
    "RECEIVE_NONSSA_BENEFITS" integer,
    "RECEIVE_SSI" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "SSN" character varying(9),
    "UNEARNED_SSI" character varying(4),
    id uuid NOT NULL,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tanf_t4; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tanf_t4 (
    id uuid NOT NULL,
    datafile_id integer,
    "CASE_NUMBER" character varying(11),
    "CLOSURE_REASON" character varying(2),
    "COUNTY_FIPS_CODE" character varying(3),
    "DISPOSITION" integer,
    "REC_FOOD_STAMPS" integer,
    "REC_MED_ASSIST" integer,
    "REC_SUB_CC" integer,
    "REC_SUB_HOUSING" integer,
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    line_number integer
);
--
-- Name: shadow_search_indexes_tanf_t5; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tanf_t5 (
    id uuid NOT NULL,
    datafile_id integer,
    "AMOUNT_EARNED_INCOME" character varying(4),
    "AMOUNT_UNEARNED_INCOME" character varying(4),
    "CASE_NUMBER" character varying(11),
    "CITIZENSHIP_STATUS" integer,
    "COUNTABLE_MONTHS_STATE_TRIBE" character varying(2),
    "COUNTABLE_MONTH_FED_TIME" character varying(3),
    "DATE_OF_BIRTH" character varying(8),
    "EDUCATION_LEVEL" character varying(2),
    "EMPLOYMENT_STATUS" integer,
    "FAMILY_AFFILIATION" integer,
    "SEX" integer,
    "MARITAL_STATUS" integer,
    "NEEDS_OF_PREGNANT_WOMAN" integer,
    "PARENT_MINOR_CHILD" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_HISPANIC" integer,
    "RACE_WHITE" integer,
    "REC_AID_AGED_BLIND" integer,
    "REC_AID_TOTALLY_DISABLED" integer,
    "REC_FEDERAL_DISABILITY" integer,
    "REC_OASDI_INSURANCE" integer,
    "REC_SSI" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "SSN" character varying(9),
    line_number integer
);
--
-- Name: shadow_search_indexes_tanf_t6; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tanf_t6 (
    id uuid NOT NULL,
    datafile_id integer,
    "ASSISTANCE" integer,
    "CALENDAR_QUARTER" integer,
    "NUM_1_PARENTS" integer,
    "NUM_2_PARENTS" integer,
    "NUM_ADULT_RECIPIENTS" integer,
    "NUM_APPLICATIONS" integer,
    "NUM_APPROVED" integer,
    "NUM_BIRTHS" integer,
    "NUM_CHILD_RECIPIENTS" integer,
    "NUM_CLOSED_CASES" integer,
    "NUM_DENIED" integer,
    "NUM_FAMILIES" integer,
    "NUM_NONCUSTODIALS" integer,
    "NUM_NO_PARENTS" integer,
    "NUM_OUTWEDLOCK_BIRTHS" integer,
    "NUM_RECIPIENTS" integer,
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    line_number integer
);
--
-- Name: shadow_search_indexes_tanf_t7; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tanf_t7 (
    id uuid NOT NULL,
    datafile_id integer,
    "CALENDAR_QUARTER" integer,
    "FAMILIES_MONTH" integer,
    "RPT_MONTH_YEAR" integer,
    "RecordType" character varying(156),
    "STRATUM" character varying(2),
    "TDRS_SECTION_IND" character varying(1),
    line_number integer
);
--
-- Name: shadow_search_indexes_tribal_tanf_t1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tribal_tanf_t1 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "FUNDING_STREAM" integer,
    "DISPOSITION" integer,
    "NEW_APPLICANT" integer,
    "NBR_FAMILY_MEMBERS" integer,
    "FAMILY_TYPE" integer,
    "RECEIVES_SUB_HOUSING" integer,
    "RECEIVES_MED_ASSISTANCE" integer,
    "RECEIVES_FOOD_STAMPS" integer,
    "AMT_FOOD_STAMP_ASSISTANCE" integer,
    "RECEIVES_SUB_CC" integer,
    "AMT_SUB_CC" integer,
    "CHILD_SUPPORT_AMT" integer,
    "FAMILY_CASH_RESOURCES" integer,
    "CASH_AMOUNT" integer,
    "NBR_MONTHS" integer,
    "CC_AMOUNT" integer,
    "CHILDREN_COVERED" integer,
    "CC_NBR_MONTHS" integer,
    "TRANSP_AMOUNT" integer,
    "TRANSP_NBR_MONTHS" integer,
    "TRANSITION_SERVICES_AMOUNT" integer,
    "TRANSITION_NBR_MONTHS" integer,
    "OTHER_AMOUNT" integer,
    "OTHER_NBR_MONTHS" integer,
    "SANC_REDUCTION_AMT" integer,
    "WORK_REQ_SANCTION" integer,
    "FAMILY_SANC_ADULT" integer,
    "SANC_TEEN_PARENT" integer,
    "NON_COOPERATION_CSE" integer,
    "FAILURE_TO_COMPLY" integer,
    "OTHER_SANCTION" integer,
    "RECOUPMENT_PRIOR_OVRPMT" integer,
    "OTHER_TOTAL_REDUCTIONS" integer,
    "FAMILY_CAP" integer,
    "REDUCTIONS_ON_RECEIPTS" integer,
    "OTHER_NON_SANCTION" integer,
    "WAIVER_EVAL_CONTROL_GRPS" integer,
    "FAMILY_EXEMPT_TIME_LIMITS" integer,
    "FAMILY_NEW_CHILD" integer,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tribal_tanf_t2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tribal_tanf_t2 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "NONCUSTODIAL_PARENT" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "FED_OASDI_PROGRAM" integer,
    "FED_DISABILITY_STATUS" integer,
    "DISABLED_TITLE_XIVAPDT" integer,
    "AID_AGED_BLIND" integer,
    "RECEIVE_SSI" integer,
    "MARITAL_STATUS" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "NEEDS_PREGNANT_WOMAN" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "COOPERATION_CHILD_SUPPORT" integer,
    "MONTHS_FED_TIME_LIMIT" character varying(3),
    "MONTHS_STATE_TIME_LIMIT" character varying(2),
    "CURRENT_MONTH_STATE_EXEMPT" integer,
    "EMPLOYMENT_STATUS" integer,
    "WORK_PART_STATUS" character varying(2),
    "UNSUB_EMPLOYMENT" character varying(2),
    "SUB_PRIVATE_EMPLOYMENT" character varying(2),
    "SUB_PUBLIC_EMPLOYMENT" character varying(2),
    "WORK_EXPERIENCE" character varying(2),
    "OJT" character varying(2),
    "JOB_SEARCH" character varying(2),
    "COMM_SERVICES" character varying(2),
    "VOCATIONAL_ED_TRAINING" character varying(2),
    "JOB_SKILLS_TRAINING" character varying(2),
    "ED_NO_HIGH_SCHOOL_DIPLOMA" character varying(2),
    "SCHOOL_ATTENDENCE" character varying(2),
    "PROVIDE_CC" character varying(2),
    "ADD_WORK_ACTIVITIES" character varying(2),
    "OTHER_WORK_ACTIVITIES" character varying(2),
    "REQ_HRS_WAIVER_DEMO" character varying(2),
    "EARNED_INCOME" character varying(4),
    "UNEARNED_INCOME_TAX_CREDIT" character varying(4),
    "UNEARNED_SOCIAL_SECURITY" character varying(4),
    "UNEARNED_SSI" character varying(4),
    "UNEARNED_WORKERS_COMP" character varying(4),
    "OTHER_UNEARNED_INCOME" character varying(4),
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tribal_tanf_t3; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tribal_tanf_t3 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "RECEIVE_NONSSA_BENEFITS" integer,
    "RECEIVE_SSI" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "UNEARNED_SSI" character varying(4),
    "OTHER_UNEARNED_INCOME" character varying(4),
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tribal_tanf_t4; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tribal_tanf_t4 (
    id uuid NOT NULL,
    "RecordType" character varying(71),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "COUNTY_FIPS_CODE" character varying(3),
    "STRATUM" character varying(2),
    "ZIP_CODE" character varying(5),
    "DISPOSITION" integer,
    "CLOSURE_REASON" character varying(2),
    "REC_SUB_HOUSING" integer,
    "REC_MED_ASSIST" integer,
    "REC_FOOD_STAMPS" integer,
    "REC_SUB_CC" integer,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tribal_tanf_t5; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tribal_tanf_t5 (
    id uuid NOT NULL,
    "RecordType" character varying(71),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "RACE_HISPANIC" integer,
    "RACE_AMER_INDIAN" integer,
    "RACE_ASIAN" integer,
    "RACE_BLACK" integer,
    "RACE_HAWAIIAN" integer,
    "RACE_WHITE" integer,
    "SEX" integer,
    "REC_OASDI_INSURANCE" integer,
    "REC_FEDERAL_DISABILITY" integer,
    "REC_AID_TOTALLY_DISABLED" integer,
    "REC_AID_AGED_BLIND" integer,
    "REC_SSI" integer,
    "MARITAL_STATUS" integer,
    "RELATIONSHIP_HOH" character varying(2),
    "PARENT_MINOR_CHILD" integer,
    "NEEDS_OF_PREGNANT_WOMAN" integer,
    "EDUCATION_LEVEL" character varying(2),
    "CITIZENSHIP_STATUS" integer,
    "COUNTABLE_MONTH_FED_TIME" character varying(3),
    "COUNTABLE_MONTHS_STATE_TRIBE" character varying(2),
    "EMPLOYMENT_STATUS" integer,
    "AMOUNT_EARNED_INCOME" character varying(4),
    "AMOUNT_UNEARNED_INCOME" character varying(4),
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tribal_tanf_t6; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tribal_tanf_t6 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "CALENDAR_QUARTER" integer,
    "RPT_MONTH_YEAR" integer,
    "NUM_APPLICATIONS" integer,
    "NUM_APPROVED" integer,
    "NUM_DENIED" integer,
    "ASSISTANCE" integer,
    "NUM_FAMILIES" integer,
    "NUM_2_PARENTS" integer,
    "NUM_1_PARENTS" integer,
    "NUM_NO_PARENTS" integer,
    "NUM_RECIPIENTS" integer,
    "NUM_ADULT_RECIPIENTS" integer,
    "NUM_CHILD_RECIPIENTS" integer,
    "NUM_NONCUSTODIALS" integer,
    "NUM_BIRTHS" integer,
    "NUM_OUTWEDLOCK_BIRTHS" integer,
    "NUM_CLOSED_CASES" integer,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_search_indexes_tribal_tanf_t7; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tribal_tanf_t7 (
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "CALENDAR_QUARTER" integer,
    "RPT_MONTH_YEAR" integer,
    "TDRS_SECTION_IND" character varying(1),
    "STRATUM" character varying(2),
    "FAMILIES_MONTH" integer,
    datafile_id integer,
    line_number integer
);
--
-- Name: shadow_parser_error; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_parser_error (
    id integer NOT NULL,
    row_number integer,
    column_number character varying(8),
    item_number character varying(8),
    field_name text,
    case_number text,
    rpt_month_year integer,
    error_message text,
    error_type text NOT NULL,
    created_at timestamp with time zone NOT NULL,
    fields_json jsonb,
    content_type_id integer,
    file_id integer,
    object_id uuid,
    deprecated boolean NOT NULL,
    values_json jsonb
);
--
-- Name: shadow_parsers_datafilesummary; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_parsers_datafilesummary (
    id bigint NOT NULL,
    status character varying(50) NOT NULL,
    case_aggregates jsonb,
    datafile_id integer NOT NULL,
    total_number_of_records_created integer,
    total_number_of_records_in_file integer,
    error_report character varying(500)
);
--
-- Name: shadow_search_indexes_programaudit_t1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_programaudit_t1 (
    line_number integer,
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FUNDING_STREAM" integer,
    "CASH_AMOUNT" integer,
    datafile_id integer
);
--
-- Name: shadow_search_indexes_programaudit_t2; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_programaudit_t2 (
    line_number integer,
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "CITIZENSHIP_STATUS" integer,
    datafile_id integer
);
--
-- Name: shadow_search_indexes_programaudit_t3; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_programaudit_t3 (
    line_number integer,
    id uuid NOT NULL,
    "RecordType" character varying(156),
    "RPT_MONTH_YEAR" integer,
    "CASE_NUMBER" character varying(11),
    "FAMILY_AFFILIATION" integer,
    "DATE_OF_BIRTH" character varying(8),
    "SSN" character varying(9),
    "CITIZENSHIP_STATUS" integer,
    datafile_id integer
);
--
-- Name: shadow_search_indexes_reparsemeta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_reparsemeta (
    id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL,
    timeout_at timestamp with time zone,
    num_records_deleted integer NOT NULL,
    total_num_records_initial bigint NOT NULL,
    total_num_records_post bigint NOT NULL,
    db_backup_location character varying(512) NOT NULL,
    fiscal_quarter character varying(2),
    fiscal_year integer,
    "all" boolean NOT NULL,
    new_indices boolean NOT NULL,
    delete_old_indices boolean NOT NULL,
    CONSTRAINT shadow_search_indexes_reparsemeta_fiscal_year_check CHECK ((fiscal_year >= 0)),
    CONSTRAINT shadow_search_indexes_reparsemeta_num_records_deleted_check CHECK ((num_records_deleted >= 0)),
    CONSTRAINT shadow_search_indexes_reparsemeta_total_num_records_initial_check CHECK ((total_num_records_initial >= 0)),
    CONSTRAINT shadow_search_indexes_reparsemeta_total_num_records_post_check CHECK ((total_num_records_post >= 0))
);
--
-- Name: shadow_search_indexes_tanf_exiter1; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.shadow_search_indexes_tanf_exiter1 (
    id uuid NOT NULL,
    "RecordType" character varying(25),
    "EXIT_DATE" integer,
    "SSN" character varying(9),
    datafile_id integer,
    line_number integer
);
