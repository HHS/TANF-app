# %% [markdown]
#
# # TANF - Generating Weights File
#
# This script the weighted TANF summary reports using data extracts. The weights file  calculates weight (cases divided by count) for each STT and stratum and reporting month. This file is used to apply weights to feedback reports' summary statistics.

# %%
-- =========================================================
-- Declare variables
-- =========================================================

-- current year --
DECLARE OR REPLACE yr INT DEFAULT 2025;

-- current yearmonth --
DECLARE OR REPLACE yrmo INT DEFAULT 202503;

-- weight file name --
DECLARE OR REPLACE year_weight_table_name STRING DEFAULT CONCAT('weight', yr);

# %%
-- =========================================================
-- Clean up prior temp objects from this session
-- =========================================================

DROP TABLE IF EXISTS pg_temp.test_FY26_weights_table;
DROP VIEW IF EXISTS pg_temp.weight1;
DROP VIEW IF EXISTS pg_temp.s4;
DROP VIEW IF EXISTS pg_temp.s3;
DROP VIEW IF EXISTS pg_temp.s1;

# %%
-- =========================================================
-- 1) Number of unique families by STT_CODE / RPT_MONTH_YEAR / STRATUM from TANF T1
-- =========================================================
CREATE OR REPLACE TEMP VIEW s1 AS
SELECT
  "STT_CODE"::int,
  "RPT_MONTH_YEAR"::int,
  "STRATUM"::int,
  COUNT(DISTINCT "CASE_NUMBER")::numeric AS case_count
FROM tanf_t1
WHERE year = yr -- this can be parametrized by fiscal year or by RPT_MONTH_YEAR, since both in the db view.
GROUP BY
  "STT_CODE",
  "RPT_MONTH_YEAR",
  "STRATUM";

-- =========================================================
-- 2) Number of families (cases) by STT_CODE / RPT_MONTH_YEAR from TANF T6
-- it is assumed that aggregate count reflects unique families per month
-- =========================================================
CREATE OR REPLACE TEMP VIEW s3 AS
SELECT
  "STT_CODE"::int,
  "RPT_MONTH_YEAR"::int,
  "NUM_FAMILIES"::numeric as case_count
FROM tanf_t6
WHERE year = yr; -- this can be parametrized by fiscal year or by RPT_MONTH_YEAR, since both in the db view.

-- =========================================================
-- 3) Number of families by STT_CODE / STRATUM / RPT_MONTH_YEAR from TANF T7
-- =========================================================
CREATE OR REPLACE TEMP VIEW s4 AS
SELECT
  "STT_CODE"::int,
  "RPT_MONTH_YEAR"::int,
  "STRATUM"::int,
  "TDRS_SECTION_IND"::int,
  "FAMILIES_MONTH"::numeric AS cases
FROM tanf_t7
WHERE year = yr -- this can be parametrized by fiscal year or by RPT_MONTH_YEAR, since both in the db view.
  AND "TDRS_SECTION_IND" = '1' -- this can be expanded to other sections if needed
  AND "FAMILIES_MONTH" > 0;

-- =========================================================
-- 4) Build weights into a temp table
-- =========================================================
CREATE OR REPLACE TEMP VIEW weight1 AS
SELECT
  s1."STT_CODE",
  s1."RPT_MONTH_YEAR",
  s1."STRATUM",
  s1.case_count,
  S4."TDRS_SECTION_IND",
  CASE
    WHEN s4.cases IS NOT NULL THEN GREATEST(s1.case_count, s4.cases)
    WHEN s3.case_count IS NOT NULL THEN GREATEST(s1.case_count, s3.case_count)
    ELSE NULL
  END as cases
FROM s1
LEFT JOIN s3
  ON s1."STT_CODE" = s3."STT_CODE"
  AND s1."RPT_MONTH_YEAR" = s3."RPT_MONTH_YEAR"
LEFT JOIN s4
  ON s1."STT_CODE" = s4."STT_CODE"
  AND s1."RPT_MONTH_YEAR" = s4."RPT_MONTH_YEAR"
  AND s1."STRATUM" = s4."STRATUM";

-- =========================================================
-- 5) Final output as a temp table
-- =========================================================
CREATE TEMP TABLE year_weight_table_name AS
SELECT
  "STT_CODE",
  "RPT_MONTH_YEAR",
  "STRATUM",
  case_count,
  cases,
  ROUND(cases/case_count, 4) as wght,
  cases::numeric / NULLIF(case_count, 0) as wght
FROM weight1
WHERE cases <> 0;


# %%
-- =========================================================
-- Quality Assurance Check 1) Number of rows per dataset
-- =========================================================
CREATE OR REPLACE TEMP VIEW qa1 AS
SELECT
  's1' AS table_name,
  COUNT(*) as row_count
FROM s1
UNION ALL
SELECT
  's3',
  COUNT(*)
FROM s3
UNION ALL
SELECT
  's4',
  COUNT(*) FROM s4
UNION ALL
SELECT
  'year_weight_table_name',
  COUNT(*)
FROM year_weight_table_name;

-- =========================================================
-- Quality Assurance Check 2) Which datasets are missing STTs
-- =========================================================
CREATE OR REPLACE VIEW qa2 AS
WITH required_values AS (
  SELECT
    unnest(ARRAY[1,2,4,5,6,8,9,10,12,13,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,44,45,46,47,48,49,50,51,53,54,55,56,66,72,78]) AS stt_codes
),
required_values_stratified AS (
  SELECT
    unnest(ARRAY(SELECT stt_code::int FROM stts_stt WHERE sample = 'true')) AS stratified_stt_codes
),
s1_missing AS (
  SELECT
    's1' AS table_name,
    'RPT_MONTH_YEAR',
    rv.stt_codes AS missing_value
  FROM required_values rv
  LEFT JOIN (SELECT * FROM s1 WHERE "RPT_MONTH_YEAR" = yrmo) d
    ON d."STT_CODE" = rv.stt_codes
  WHERE d."STT_CODE" IS NULL
),
s3_missing AS (
  SELECT
    's3' AS table_name,
    'RPT_MONTH_YEAR',
    rv.stt_codes AS missing_value
  FROM required_values rv
  LEFT JOIN (SELECT * FROM s3 WHERE "RPT_MONTH_YEAR" = yrmo) d
    ON d."STT_CODE" = rv.stt_codes
  WHERE d."STT_CODE" IS NULL
),
s4_missing AS (
  SELECT
    's4' AS table_name,
    'RPT_MONTH_YEAR',
    rv.stratified_stt_codes AS missing_value
  FROM required_values_stratified rv
  LEFT JOIN (SELECT * FROM s4 WHERE "RPT_MONTH_YEAR" = yrmo) d
    ON d."STT_CODE" = rv.stratified_stt_codes
  WHERE d."STT_CODE" IS NULL
)
SELECT * FROM s1_missing
UNION ALL
SELECT * FROM s3_missing
UNION ALL
SELECT * FROM s4_missing
ORDER BY table_name, missing_value;

-- =========================================================
-- Quality Assurance Check 3) Which RPT_MONTH_YEAR-STT pairs exist in s1 that do not exist in s3 & vice versa
-- =========================================================
CREATE OR REPLACE TEMP VIEW qa3 AS
SELECT
  "STT_CODE",
  "RPT_MONTH_YEAR",
  SUM(in_s1) as in_s1,
  SUM(in_s3) as in_s3
FROM (SELECT DISTINCT
  "STT_CODE",
  "RPT_MONTH_YEAR",
  1 as in_s1,
  0 as in_s3
FROM s1
UNION ALL
SELECT DISTINCT
  "STT_CODE",
  "RPT_MONTH_YEAR",
  0 as in_s1,
  1 as in_s3
FROM s3) differences
GROUP BY
  "STT_CODE",
  "RPT_MONTH_YEAR"
HAVING
  COUNT(*) <> 2;

-- =========================================================
-- Quality Assurance Check 4) Which sample-state RPT_MONTH_YEAR-STT-STRATUM pairs exist in s1 that do not exist in s4 & vice versa
-- =========================================================
CREATE OR REPLACE TEMP VIEW qa4 AS
SELECT
  "STT_CODE",
  "STRATUM",
  "RPT_MONTH_YEAR",
  SUM(in_s1) as in_s1,
  SUM(in_s4) as in_s4
FROM (SELECT DISTINCT
  "STT_CODE",
  "STRATUM",
  "RPT_MONTH_YEAR",
  1 as in_s1,
  0 as in_s4
FROM s1
UNION ALL
SELECT DISTINCT
  "STT_CODE",
  "STRATUM",
  "RPT_MONTH_YEAR",
  0 as in_s1,
  1 as in_s4
FROM s4) differences
-- filtering to stratified STTs
WHERE "STT_CODE" IN (6,8,9,12,17,20,24,25,26,28,32,35,36,39,42,45,47,48,54,72)
GROUP BY
  "STT_CODE",
  "STRATUM",
  "RPT_MONTH_YEAR"
HAVING
  COUNT(*) <> 2;


# %%
-- =========================================================
-- Optional explicit cleanup at the end
-- =========================================================
-- DROP TABLE IF EXISTS pg_temp.test_FY26_weights_table;
-- DROP TABLE IF EXISTS pg_temp.weight1;
-- DROP VIEW IF EXISTS pg_temp.s4;
-- DROP VIEW IF EXISTS pg_temp.s3;
-- DROP VIEW IF EXISTS pg_temp.s1;
