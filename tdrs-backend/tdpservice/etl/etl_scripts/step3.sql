# %% [markdown]
#
# # PART 3: CREATING UNWEIGHTED SUMMARY REPORTS
#
# The third part of this project is to create the weighted TANF summary reports. Generally, each report is a different set of variables from the current month's TAN reports. Sometimes additional variables are calculated. These reports are then printed out in an Excel file which can be distributed to different entitites.

# %%
-------------------------------
-- Step 1: Declare variables --
-------------------------------

-- this is the variable used to filter the dataframes to the current month --
DECLARE OR REPLACE ym INT DEFAULT 202408;

-- this is the name of the final TAN dataframe for the current month --
DECLARE OR REPLACE tan_table_name STRING DEFAULT CONCAT('ofa_sandbox.legacy_code.tan', ym);

-- this is the name of the final WPR dataframe for the current month --
DECLARE OR REPLACE wpr_table_name STRING DEFAULT CONCAT('ofa_sandbox.legacy_code.WPR', ym);

# %%
---------------------------------------------------------------------
-- Step 2: Combine all TAN datasets for errorflags summary reports --
---------------------------------------------------------------------


CREATE OR REPLACE TEMPORARY VIEW sumrpt_errorflags AS
SELECT
	*
FROM
  ofa_sandbox.legacy_code.tan202408
  --IDENTIFIER(tan_table_name);
WHERE
	(AFERRFG != '  ' AND AFERRFG IS NOT NULL) OR (TPERRFG != '  ' AND TPERRFG IS NOT NULL);

# %%
-----------------------------------------------------------------
-- Step 3: Create "TANF All-family Errorflags Frequency Table" --
-----------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW TANF_allfamily_errorflags_freq AS
SELECT
  RPT_MONTH_YEAR,
	AFERRFG,
  COUNT(*) AS Frequency
FROM
  sumrpt_errorflags
WHERE
  AFERRFG != '  ' AND AFERRFG IS NOT NULL
GROUP BY
  RPT_MONTH_YEAR,
	AFERRFG
ORDER BY
  Frequency DESC;

# %%
------------------------------------------------------------------------
-- Step 4: Create "TANF Two-Parent-family Errorflags Frequency Table" --
------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW TANF_2pfamily_errorflags_freq AS
SELECT
  RPT_MONTH_YEAR,
	TPERRFG,
  COUNT(*) AS Frequency
FROM
  sumrpt_errorflags
WHERE
  TPERRFG != '  ' AND TPERRFG IS NOT NULL
GROUP BY
  RPT_MONTH_YEAR,
	TPERRFG
ORDER BY
  Frequency DESC;

# %%
--------------------------------------------
-- Step 5: Create "TANF Errorflags Table" --
--------------------------------------------

-- not sure what these names mean - should check --
-- commenting out the ones throwing errors --

CREATE OR REPLACE TEMPORARY VIEW TANF_errorflags_table AS
SELECT
	FIPS_CODE,
	RPT_MONTH_YEAR AS MONTH,
	STRATUM,
	CASE_ID,
	FAMILY_TYPE, -- "type_fam"
	N_WEI, -- "#WEI",
	NWORK, -- "Met AF WPR",
	AF_WEI, -- "WEI #48",
	AF_FAMILY_AFFILIATION, -- "Famaff#30",
	AF_AGE AS Age,
	AF_PARENT, -- "Parent?#39",
	AF_WORK_PART_STATUS, -- "WPS#49",
	AF_UNEARNED_SSI, --  "$SSI#66C",
	AF_FED_OASDI_PROGRAM, -- "SSI#36E",
	SANC_REDUCTION_AMT, -- "$#26Ai",
	WORK_REQ_SANCTION, -- "#26Aii",
	AF_NONCUSTODIAL_PARENT, -- "NCP#31",
	AF_CITIZENSHIP_STATUS, -- "Citizen#42",
	YOUNGEST,
	NDVEXEM,
	AFERRFG,
	TPWORK, -- "Met 2p WPR",
	TPERRFG
FROM
  sumrpt_errorflags;

# %%
-----------------------------------------------------------------
-- Step 6: Combine all TAN datasets for review summary reports --
-----------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW sumrpt_review1 AS
SELECT
	*
FROM
  ofa_sandbox.legacy_code.tan202408
  --IDENTIFIER(tan_table_name);
WHERE
	--FIPS in @FIPS AND
	CASH_AMOUNT + TRANSITION_SERVICES_AMOUNT + TRANSP_AMOUNT + CC_AMOUNT + OTHER_AMOUNT = 0;

-- Some reports require calculated values

CREATE OR REPLACE TEMPORARY VIEW sumrpt_review AS
SELECT
	*,
	-- excused absence hours variables for AF, P1, and P2 --
	AF_WORK_EXPERIENCE_EA + AF_JOB_SEARCH_EA + AF_COMM_SERVICES_EA + AF_VOCATIONAL_ED_TRAINING_EA + AF_JOB_SKILLS_TRAINING_EA + AF_ED_NO_HIGH_SCHOOL_DIPL_EA + AF_SCHOOL_ATTENDENCE_EA + AF_PROVIDE_CC_EA AS AFEAHRS,
	P1_WORK_EXPERIENCE_EA + P1_JOB_SEARCH_EA + P1_COMM_SERVICES_EA + P1_VOCATIONAL_ED_TRAINING_EA + P1_JOB_SKILLS_TRAINING_EA + P1_ED_NO_HIGH_SCHOOL_DIPL_EA + P1_SCHOOL_ATTENDENCE_EA + P1_PROVIDE_CC_EA AS P1EAHRS,
	P2_WORK_EXPERIENCE_EA + P2_JOB_SEARCH_EA + P2_COMM_SERVICES_EA + P2_VOCATIONAL_ED_TRAINING_EA + P2_JOB_SKILLS_TRAINING_EA + P2_ED_NO_HIGH_SCHOOL_DIPL_EA + P2_SCHOOL_ATTENDENCE_EA + P2_PROVIDE_CC_EA AS P2EAHRS,
	-- holiday hours variables for AF, P1, and P2 --
	AF_WORK_EXPERIENCE_HOL + AF_JOB_SEARCH_HOL + AF_COMM_SERVICES_HOL + AF_VOCATIONAL_ED_TRAINING_HOL + AF_JOB_SKILLS_TRAINING_HOL + AF_ED_NO_HIGH_SCHOOL_DIPL_HOL + AF_SCHOOL_ATTENDENCE_HOL + AF_PROVIDE_CC_HOL AS AFHLHRS,
	P1_WORK_EXPERIENCE_HOL + P1_JOB_SEARCH_HOL + P1_COMM_SERVICES_HOL + P1_VOCATIONAL_ED_TRAINING_HOL + P1_JOB_SKILLS_TRAINING_HOL + P1_ED_NO_HIGH_SCHOOL_DIPL_HOL + P1_SCHOOL_ATTENDENCE_HOL + P1_PROVIDE_CC_HOL AS P1HLHRS,
	P2_WORK_EXPERIENCE_HOL + P2_JOB_SEARCH_HOL + P2_COMM_SERVICES_HOL + P2_VOCATIONAL_ED_TRAINING_HOL + P2_JOB_SKILLS_TRAINING_HOL + P2_ED_NO_HIGH_SCHOOL_DIPL_HOL + P2_SCHOOL_ATTENDENCE_HOL + P2_PROVIDE_CC_HOL AS P2HLHRS,
	-- work hours variables for AF, P1, and P2 --
	AF_UNSUB_EMPLOYMENT + AF_SUB_PRIVATE_EMPLOYMENT + AF_SUB_PUBLIC_EMPLOYMENT + AF_WORK_EXPERIENCE_HOP + AF_OJT + AF_JOB_SEARCH_HOP + AF_COMM_SERVICES_HOP + AF_VOCATIONAL_ED_TRAINING_HOP + AF_JOB_SKILLS_TRAINING_HOP + AF_ED_NO_HIGH_SCHOOL_DIPL_HOP + AF_SCHOOL_ATTENDENCE_HOP + AF_PROVIDE_CC_HOP + AF_OTHER_WORK_ACTIVITIES AS AFHOURS,
	P1_UNSUB_EMPLOYMENT + P1_SUB_PRIVATE_EMPLOYMENT + P1_SUB_PUBLIC_EMPLOYMENT + P1_WORK_EXPERIENCE_HOP + P1_OJT + P1_JOB_SEARCH_HOP + P1_COMM_SERVICES_HOP + P1_VOCATIONAL_ED_TRAINING_HOP + P1_JOB_SKILLS_TRAINING_HOP + P1_ED_NO_HIGH_SCHOOL_DIPL_HOP + P1_SCHOOL_ATTENDENCE_HOP + P1_PROVIDE_CC_HOP + P1_OTHER_WORK_ACTIVITIES AS P1HOURS,
	P2_UNSUB_EMPLOYMENT + P2_SUB_PRIVATE_EMPLOYMENT + P2_SUB_PUBLIC_EMPLOYMENT + P2_WORK_EXPERIENCE_HOP + P2_OJT + P2_JOB_SEARCH_HOP + P2_COMM_SERVICES_HOP + P2_VOCATIONAL_ED_TRAINING_HOP + P2_JOB_SKILLS_TRAINING_HOP + P2_ED_NO_HIGH_SCHOOL_DIPL_HOP + P2_SCHOOL_ATTENDENCE_HOP + P2_PROVIDE_CC_HOP + P2_OTHER_WORK_ACTIVITIES AS P2HOURS
FROM
	sumrpt_review1;

# %%
------------------------------------------------------------
-- Step 7: Create "TANF Cases Zero Amount of Assistances" --
------------------------------------------------------------

-- commenting out several variables with names that are throwing errors --

CREATE OR REPLACE TEMPORARY VIEW TANF_assistances_table AS
SELECT
	FIPS_CODE,
	RPT_MONTH_YEAR AS MONTH,
	CASE_ID,
	CASH_AMOUNT, -- "Cash Assistance $"
	CC_AMOUNT, -- "TANF child care $"
	TRANSP_AMOUNT -- "Transportation $"
FROM
  sumrpt_review;

# %%
---------------------------------------------------------------------------------
-- Step 8: Create "TANF Cases with 'Excuse Absence' that is more than 4 hours" --
---------------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW sumrpt_excused_absence_4hrs AS
SELECT
	*--,
  -- should be able to pull these variables from a previous step, so should remove these
  --AF_WORK_EXPERIENCE_EA + AF_JOB_SEARCH_EA + AF_COMM_SERVICES_EA + AF_VOCATIONAL_ED_TRAINING_EA + AF_JOB_SKILLS_TRAINING_EA + AF_ED_NO_HIGH_SCHOOL_DIPL_EA + AF_SCHOOL_ATTENDENCE_EA + AF_PROVIDE_CC_EA AS AFEAHRS,
  --P1_WORK_EXPERIENCE_EA + P1_JOB_SEARCH_EA + P1_COMM_SERVICES_EA + P1_VOCATIONAL_ED_TRAINING_EA + P1_JOB_SKILLS_TRAINING_EA + P1_ED_NO_HIGH_SCHOOL_DIPL_EA + P1_SCHOOL_ATTENDENCE_EA + P1_PROVIDE_CC_EA AS P1EAHRS,
  --P2_WORK_EXPERIENCE_EA + P2_JOB_SEARCH_EA + P2_COMM_SERVICES_EA + P2_VOCATIONAL_ED_TRAINING_EA + P2_JOB_SKILLS_TRAINING_EA + P2_ED_NO_HIGH_SCHOOL_DIPL_EA + P2_SCHOOL_ATTENDENCE_EA + P2_PROVIDE_CC_EA AS P2EAHRS
FROM
	sumrpt_review
WHERE
	AFEAHRS > 4 OR
  P1EAHRS > 4 OR
  P2EAHRS > 4;

# %%
---------------------------------------------------------------------------------
-- Step 9: Create "TANF Cases with 'Excuse Absence' that is more than 4 hours" --
---------------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW TANF_excuse_absence_table AS
SELECT
	FIPS_CODE,
	RPT_MONTH_YEAR AS MONTH,
	CASE_ID,
	AF_WORK_EXPERIENCE_EA + P1_WORK_EXPERIENCE_EA + P2_WORK_EXPERIENCE_EA AS work_exp, -- "work exp"
	AF_JOB_SEARCH_EA + P1_JOB_SEARCH_EA + P2_JOB_SEARCH_EA AS job_search, -- "job search"
	AF_COMM_SERVICES_EA + P1_COMM_SERVICES_EA + P2_COMM_SERVICES_EA AS comm_serv, -- "comm serv"
	AF_VOCATIONAL_ED_TRAINING_EA + P1_VOCATIONAL_ED_TRAINING_EA + P2_VOCATIONAL_ED_TRAINING_EA AS voc_ed, -- "voc.ed"
	AF_JOB_SKILLS_TRAINING_EA + P1_JOB_SKILLS_TRAINING_EA + P2_JOB_SKILLS_TRAINING_EA AS job_skills, -- "job skills"
	AF_ED_NO_HIGH_SCHOOL_DIPL_EA + P1_ED_NO_HIGH_SCHOOL_DIPL_EA + P2_ED_NO_HIGH_SCHOOL_DIPL_EA AS ed_no_ns_dipl, -- "ed.no.hs.dipl"
	AF_SCHOOL_ATTENDENCE_EA + P1_SCHOOL_ATTENDENCE_EA + P2_SCHOOL_ATTENDENCE_EA AS school_attend, -- "school attend"
	AF_PROVIDE_CC_EA + P1_PROVIDE_CC_EA + P2_PROVIDE_CC_EA AS provide_cc -- "provide cc"
FROM
  sumrpt_excused_absence_4hrs;

# %%
-------------------------------------------------------------------------------
-- Step 10: Create "TANF CASES WITH 'HOLIDAY HOURS' MORE THAN MAXIMUM HOURS" --
-------------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW sumrpt_holiday_hours1 AS
SELECT
	*,
	CASE
		WHEN FIPS_CODE IN ('08','13','17','19','20','24','26','27','31','33','51') AND MOD(RPT_MONTH_YEAR,100) = 11 THEN 6
		WHEN FIPS_CODE IN ('21', '45', '55') AND MOD(RPT_MONTH_YEAR, 100) = 12 THEN 6
		WHEN FIPS_CODE = 49 AND MOD(RPT_MONTH_YEAR, 100) IN (1, 7) THEN 6
		ELSE 4
	END AS MAXHRS
	-- these were previously defined so should be able to get rid of these --
	--AF_WORK_EXPEREINCE_EA + AF_JOB_SEARCH_EA + AF_COMM_SERVICES_EA + AF_VOCATIONAL_ED_TRAINING_EA + AF_JOB_SKILLS_TRAINING_EA + AF_ED_NO_HIGH_SCHOOL_DIPL_EA + AF_SCHOOL_ATTENDENCE_EA + AF_PROVIDE_CC_EA AS AFEAHRS,
	--P1_WORK_EXPEREINCE_EA + P1_JOB_SEARCH_EA + P1_COMM_SERVICES_EA + P1_VOCATIONAL_ED_TRAINING_EA + P1_JOB_SKILLS_TRAINING_EA + P1_ED_NO_HIGH_SCHOOL_DIPL_EA + P1_SCHOOL_ATTENDENCE_EA + P1_PROVIDE_CC_EA AS P1EAHRS,
	--P2_WORK_EXPEREINCE_EA + P2_JOB_SEARCH_EA + P2_COMM_SERVICES_EA + P2_VOCATIONAL_ED_TRAINING_EA + P2_JOB_SKILLS_TRAINING_EA + P2_ED_NO_HIGH_SCHOOL_DIPL_EA + P2_SCHOOL_ATTENDENCE_EA + P2_PROVIDE_CC_EA AS P2EAHRS
FROM
	sumrpt_review;

CREATE OR REPLACE TEMPORARY VIEW sumrpt_holiday_hours AS
SELECT
	*
FROM
	sumrpt_holiday_hours1
WHERE
	AFHLHRS > MAXHRS OR
	P1HLHRS > MAXHRS OR
	P2HLHRS > MAXHRS;

# %%
------------------------------------------------------------------------------------------
-- Step 11: Create "TANF CASES WITH 'HOLIDAY HOURS' MORE THAN MAXIMUM HOURS" freq table --
------------------------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW TANF_holiday_hours_table AS
SELECT
	FIPS_CODE,
	RPT_MONTH_YEAR AS MONTH,
	CASE_ID,
	AF_WORK_EXPERIENCE_EA + P1_WORK_EXPERIENCE_EA + P2_WORK_EXPERIENCE_EA AS work_exp, -- "work exp"
	AF_JOB_SEARCH_EA + P1_JOB_SEARCH_EA + P2_JOB_SEARCH_EA AS job_search, -- "job search"
	AF_COMM_SERVICES_EA + P1_COMM_SERVICES_EA + P2_COMM_SERVICES_EA AS comm_serv, -- "comm serv"
	AF_VOCATIONAL_ED_TRAINING_EA + P1_VOCATIONAL_ED_TRAINING_EA + P2_VOCATIONAL_ED_TRAINING_EA AS voc_ed, -- "voc.ed"
	AF_JOB_SKILLS_TRAINING_EA + P1_JOB_SKILLS_TRAINING_EA + P2_JOB_SKILLS_TRAINING_EA AS job_skills, -- "job skills"
	AF_ED_NO_HIGH_SCHOOL_DIPL_EA + P1_ED_NO_HIGH_SCHOOL_DIPL_EA + P2_ED_NO_HIGH_SCHOOL_DIPL_EA AS ed_no_hs_dipl, -- "ed.no.hs.dipl"
	AF_SCHOOL_ATTENDENCE_EA + P1_SCHOOL_ATTENDENCE_EA + P2_SCHOOL_ATTENDENCE_EA AS school_attend, -- "school attend"
	AF_PROVIDE_CC_EA + P1_PROVIDE_CC_EA + P2_PROVIDE_CC_EA AS provide_cc -- "provide cc"
FROM
	sumrpt_holiday_hours;

# %%
----------------------------------------------------------------------------------------
-- Step 12: Create "TANF FAMILIES INCLUDING AN ADULT WITH 80+ HOURS OF PARTICIPATION" --
----------------------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW sumrpt_80plus_hrs AS
SELECT
	FIPS_CODE,
	RPT_MONTH_YEAR AS MONTH,
	STRATUM,
	CASE_ID,
	-- all family variables --
	AF_UNSUB_EMPLOYMENT,
	AF_SUB_PRIVATE_EMPLOYMENT,
	AF_SUB_PUBLIC_EMPLOYMENT,
	AF_WORK_EXPERIENCE_HOP,
	AF_OJT,
	AF_JOB_SEARCH_HOP,
	AF_COMM_SERVICES_HOP,
	AF_VOCATIONAL_ED_TRAINING_HOP,
	AF_JOB_SKILLS_TRAINING_HOP,
	AF_ED_NO_HIGH_SCHOOL_DIPL_HOP,
	AF_SCHOOL_ATTENDENCE_HOP,
	AF_PROVIDE_CC_HOP,
	AF_OTHER_WORK_ACTIVITIES,
	AFHOURS,
	-- p1 variables --
	P1_UNSUB_EMPLOYMENT,
	P1_SUB_PRIVATE_EMPLOYMENT,
	P1_SUB_PUBLIC_EMPLOYMENT,
	P1_WORK_EXPERIENCE_HOP,
	P1_OJT,
	P1_JOB_SEARCH_HOP,
	P1_COMM_SERVICES_HOP,
	P1_VOCATIONAL_ED_TRAINING_HOP,
	P1_JOB_SKILLS_TRAINING_HOP,
	P1_ED_NO_HIGH_SCHOOL_DIPL_HOP,
	P1_SCHOOL_ATTENDENCE_HOP,
	P1_PROVIDE_CC_HOP,
	P1_OTHER_WORK_ACTIVITIES,
	P1HOURS,
	-- p2 variables --
	P2_UNSUB_EMPLOYMENT,
	P2_SUB_PRIVATE_EMPLOYMENT,
	P2_SUB_PUBLIC_EMPLOYMENT,
	P2_WORK_EXPERIENCE_HOP,
	P2_OJT,
	P2_JOB_SEARCH_HOP,
	P2_COMM_SERVICES_HOP,
	P2_VOCATIONAL_ED_TRAINING_HOP,
	P2_JOB_SKILLS_TRAINING_HOP,
	P2_ED_NO_HIGH_SCHOOL_DIPL_HOP,
	P2_SCHOOL_ATTENDENCE_HOP,
	P2_PROVIDE_CC_HOP,
	P2_OTHER_WORK_ACTIVITIES,
	P2HOURS
FROM
	sumrpt_review
WHERE
	(AFHOURS >= 80) OR
	(P1HOURS >= 80) OR
	(P2HOURS >= 80);

# %%
---------------------------------------------------------------------------------------------------
-- Step 13: Create "TANF FAMILIES INCLUDING AN ADULT WITH 80+ HOURS OF PARTICIPATION" freq table --
---------------------------------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW TANF_holiday_hours_table AS
SELECT
	FIPS_CODE,
	RPT_MONTH_YEAR AS MONTH,
	CASE_ID,
	AFHOURS, -- "AF hours"
	P1HOURS, -- "P1 hours",
	P2HOURS, -- "P2 hours",
	TPSAMP AS 2_parent_fam, -- "2 parent FAM"
	AF_UNSUB_EMPLOYMENT + P1_UNSUB_EMPLOYMENT + P2_UNSUB_EMPLOYMENT AS unsub_employ, -- "Unsub employ"
	AF_SUB_PRIVATE_EMPLOYMENT + P1_SUB_PRIVATE_EMPLOYMENT + P2_SUB_PRIVATE_EMPLOYMENT AS sub_priv_employ, -- "sub.priv.employ"
	AF_SUB_PUBLIC_EMPLOYMENT + P1_SUB_PUBLIC_EMPLOYMENT + P2_SUB_PUBLIC_EMPLOYMENT AS sub_pub_employ, -- "sub.pub.employ"
	AF_WORK_EXPERIENCE_HOP + P1_WORK_EXPERIENCE_HOP + P2_WORK_EXPERIENCE_HOP AS work_exper, -- "work exper"
	AF_OJT + P1_OJT + P2_OJT AS ojt, -- "ojt"
	AF_JOB_SEARCH_HOP + P1_JOB_SEARCH_HOP + P2_JOB_SEARCH_HOP AS job_search, -- "job search"
	AF_COMM_SERVICES_HOP + P1_COMM_SERVICES_HOP + P2_COMM_SERVICES_HOP AS comm_serv, -- "comm.serv"
	AF_VOCATIONAL_ED_TRAINING_HOP + P1_VOCATIONAL_ED_TRAINING_HOP + P2_VOCATIONAL_ED_TRAINING_HOP AS voc_ed, -- "voc ed"
	AF_JOB_SKILLS_TRAINING_HOP + P1_JOB_SKILLS_TRAINING_HOP + P2_JOB_SKILLS_TRAINING_HOP AS jo_skills, -- "job skills"
	AF_ED_NO_HIGH_SCHOOL_DIPL_HOP + P1_ED_NO_HIGH_SCHOOL_DIPL_HOP + P2_ED_NO_HIGH_SCHOOL_DIPL_HOP AS ed_no_hs, -- "ed.no.hs"
	AF_SCHOOL_ATTENDENCE_HOP + P1_SCHOOL_ATTENDENCE_HOP + P2_SCHOOL_ATTENDENCE_HOP AS school_attend, -- "school attend"
	AF_PROVIDE_CC_HOP + P1_PROVIDE_CC_HOP + P2_PROVIDE_CC_HOP AS provide_cc, -- "provide cc"
	AF_OTHER_WORK_ACTIVITIES + P1_OTHER_WORK_ACTIVITIES + P2_OTHER_WORK_ACTIVITIES AS other_activ -- "other activ"
FROM
	sumrpt_80plus_hrs;

# %%
-----------------------------------------------------------------------------------------------------
-- Step 14: Create "TANF FAMILIES MET WORK REQUIREMENT WITH DISREGARDED WORK PARTICIPATION STATUS" --
-----------------------------------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW sumrpt_work_requirement AS
SELECT
	*
FROM
	sumrpt_review1
WHERE
	FTYPE IN (1,2) AND
	((NDCRD_PART = 1 AND NWORK = 1) OR (TPDCRD_PART = 1 AND TPWORK = 1));

# %%
----------------------------------------------------------------------------------------------------------------
-- Step 15: Create "TANF FAMILIES MET WORK REQUIREMENT WITH DISREGARDED WORK PARTICIPATION STATUS" freq table --
----------------------------------------------------------------------------------------------------------------

CREATE OR REPLACE TEMPORARY VIEW TANF_holiday_hours_table AS
SELECT
	FIPS_CODE,
	RPT_MONTH_YEAR AS MONTH,
	STRATUM,
	CASE_ID,
	FAMILY_TYPE,
	FTYPE,
	N_WEI,
	NWORK,
	AF_WORK_PART_STATUS,
	NDCRD_PART,
	TPWORK,
	P1_WORK_PART_STATUS,
	P2_WORK_PART_STATUS,
	TPDABLE,
	TPDCRD_PART,
	TPERRFG
FROM
	sumrpt_work_requirement;
