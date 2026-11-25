CREATE OR REPLACE VIEW public.mr_record_counts_by_tableview AS
WITH ssp_counts AS (
    SELECT
        'SSP'::text AS program_type,
        'Active Case Data'::text AS section,
        'm1'::text AS record_type,
        'ssp_m1'::text AS source_table,
        m1."RPT_MONTH_YEAR",
        m1."STT",
        m1."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT m1."CASE_NUMBER") AS unique_case_count
    FROM ssp_m1 m1
    GROUP BY
        m1."RPT_MONTH_YEAR",
        m1."STT",
        m1."STT_CODE"
    UNION ALL
    SELECT
        'SSP'::text AS program_type,
        'Active Case Data'::text AS section,
        'm2'::text AS record_type,
        'ssp_m2'::text AS source_table,
        m2."RPT_MONTH_YEAR",
        m2."STT",
        m2."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT m2."CASE_NUMBER") AS unique_case_count
    FROM ssp_m2 m2
    GROUP BY
        m2."RPT_MONTH_YEAR",
        m2."STT",
        m2."STT_CODE"
    UNION ALL
    SELECT
        'SSP'::text AS program_type,
        'Active Case Data'::text AS section,
        'm3'::text AS record_type,
        'ssp_m3'::text AS source_table,
        m3."RPT_MONTH_YEAR",
        m3."STT",
        m3."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT m3."CASE_NUMBER") AS unique_case_count
    FROM ssp_m3 m3
    WHERE ((m3."FAMILY_AFFILIATION" IS NOT NULL) AND (m3."SEX" IS NOT NULL))
    GROUP BY
        m3."RPT_MONTH_YEAR",
        m3."STT",
        m3."STT_CODE"
    UNION ALL
    SELECT
        'SSP'::text AS program_type,
        'Closed Case Data'::text AS section,
        'm4'::text AS record_type,
        'ssp_m4'::text AS source_table,
        m4."RPT_MONTH_YEAR",
        m4."STT",
        m4."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT m4."CASE_NUMBER") AS unique_case_count
    FROM ssp_m4 m4
    GROUP BY
        m4."RPT_MONTH_YEAR",
        m4."STT",
        m4."STT_CODE"
    UNION ALL
    SELECT
        'SSP'::text AS program_type,
        'Closed Case Data'::text AS section,
        'm5'::text AS record_type,
        'ssp_m5'::text AS source_table,
        m5."RPT_MONTH_YEAR",
        m5."STT",
        m5."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT m5."CASE_NUMBER") AS unique_case_count
    FROM ssp_m5 m5
    GROUP BY
        m5."RPT_MONTH_YEAR",
        m5."STT",
        m5."STT_CODE"
    UNION ALL
    SELECT
        'SSP'::text AS program_type,
        'Aggregate Data'::text AS section,
        'm6'::text AS record_type,
        'ssp_m6'::text AS source_table,
        m6."RPT_MONTH_YEAR",
        m6."STT",
        m6."STT_CODE",
        count (*) AS total_record_count,
        NULL::bigint AS unique_case_count
    FROM ssp_m6 m6
    GROUP BY
        m6."RPT_MONTH_YEAR",
        m6."STT",
        m6."STT_CODE"
    UNION ALL
    SELECT
        'SSP'::text AS program_type,
        'Stratum Data'::text AS section,
        'm7'::text AS record_type,
        'ssp_m7'::text AS source_table,
        m7."RPT_MONTH_YEAR",
        m7."STT",
        m7."STT_CODE",
        count (*) AS total_record_count,
        NULL::bigint AS unique_case_count
    FROM ssp_m7 m7
    WHERE ((m7."TDRS_SECTION_IND" IS NOT NULL) AND (m7."STRATUM" IS NOT NULL))
    GROUP BY
        m7."RPT_MONTH_YEAR",
        m7."STT",
        m7."STT_CODE"
),
tanf_counts AS (
    SELECT
        'TAN'::text AS program_type,
        'Active Case Data'::text AS section,
        't1'::text AS record_type,
        'tanf_t1'::text AS source_table,
        t1."RPT_MONTH_YEAR",
        t1."STT",
        t1."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT t1."CASE_NUMBER") AS unique_case_count
    FROM tanf_t1 t1
    GROUP BY
        t1."RPT_MONTH_YEAR",
        t1."STT",
        t1."STT_CODE"
    UNION ALL
    SELECT
        'TAN'::text AS program_type,
        'Active Case Data'::text AS section,
        't2'::text AS record_type,
        'tanf_t2'::text AS source_table,
        t2."RPT_MONTH_YEAR",
        t2."STT",
        t2."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT t2."CASE_NUMBER") AS unique_case_count
    FROM tanf_t2 t2
    GROUP BY
        t2."RPT_MONTH_YEAR",
        t2."STT",
        t2."STT_CODE"
    UNION ALL
    SELECT
        'TAN'::text AS program_type,
        'Active Case Data'::text AS section,
        't3'::text AS record_type,
        'tanf_t3'::text AS source_table,
        t3."RPT_MONTH_YEAR",
        t3."STT",
        t3."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT t3."CASE_NUMBER") AS unique_case_count
    FROM tanf_t3 t3
    WHERE ((t3."FAMILY_AFFILIATION" IS NOT NULL) AND (t3."SEX" IS NOT NULL))
    GROUP BY
        t3."RPT_MONTH_YEAR",
        t3."STT",
        t3."STT_CODE"
    UNION ALL
    SELECT
        'TAN'::text AS program_type,
        'Closed Case Data'::text AS section,
        't4'::text AS record_type,
        'tanf_t4'::text AS source_table,
        t4."RPT_MONTH_YEAR",
        t4."STT",
        t4."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT t4."CASE_NUMBER") AS unique_case_count
    FROM tanf_t4 t4
    GROUP BY
        t4."RPT_MONTH_YEAR",
        t4."STT",
        t4."STT_CODE"
    UNION ALL
    SELECT
        'TAN'::text AS program_type,
        'Closed Case Data'::text AS section,
        't5'::text AS record_type,
        'tanf_t5'::text AS source_table,
        t5."RPT_MONTH_YEAR",
        t5."STT",
        t5."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT t5."CASE_NUMBER") AS unique_case_count
    FROM tanf_t5 t5
    GROUP BY
        t5."RPT_MONTH_YEAR",
        t5."STT",
        t5."STT_CODE"
    UNION ALL
    SELECT
        'TAN'::text AS program_type,
        'Aggregate Data'::text AS section,
        't6'::text AS record_type,
        'tanf_t6'::text AS source_table,
        t6."RPT_MONTH_YEAR",
        t6."STT",
        t6."STT_CODE",
        count (*) AS total_record_count,
        NULL::bigint AS unique_case_count
    FROM tanf_t6 t6
    GROUP BY
        t6."RPT_MONTH_YEAR",
        t6."STT",
        t6."STT_CODE"
    UNION ALL
    SELECT
        'TAN'::text AS program_type,
        'Stratum Data'::text AS section,
        't7'::text AS record_type,
        'tanf_t7'::text AS source_table,
        t7."RPT_MONTH_YEAR",
        t7."STT",
        t7."STT_CODE",
        count (*) AS total_record_count,
        NULL::bigint AS unique_case_count
    FROM tanf_t7 t7
    WHERE ((t7."TDRS_SECTION_IND" IS NOT NULL) AND (t7."STRATUM" IS NOT NULL))
    GROUP BY
        t7."RPT_MONTH_YEAR",
        t7."STT",
        t7."STT_CODE"
),
tribal_tanf_counts AS (
    SELECT
        'TRIBAL'::text AS program_type,
        'Active Case Data'::text AS section,
        't1'::text AS record_type,
        'tribal_tanf_t1'::text AS source_table,
        tt1."RPT_MONTH_YEAR",
        tt1."STT",
        tt1."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT tt1."CASE_NUMBER") AS unique_case_count
    FROM tribal_tanf_t1 tt1
    GROUP BY
        tt1."RPT_MONTH_YEAR",
        tt1."STT",
        tt1."STT_CODE"
    UNION ALL
    SELECT
        'TRIBAL'::text AS program_type,
        'Active Case Data'::text AS section,
        't2'::text AS record_type,
        'tribal_tanf_t2'::text AS source_table,
        tt2."RPT_MONTH_YEAR",
        tt2."STT",
        tt2."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT tt2."CASE_NUMBER") AS unique_case_count
    FROM tribal_tanf_t2 tt2
    GROUP BY
        tt2."RPT_MONTH_YEAR",
        tt2."STT",
        tt2."STT_CODE"
    UNION ALL
    SELECT
        'TRIBAL'::text AS program_type,
        'Active Case Data'::text AS section,
        't3'::text AS record_type,
        'tribal_tanf_t3'::text AS source_table,
        tt3."RPT_MONTH_YEAR",
        tt3."STT",
        tt3."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT tt3."CASE_NUMBER") AS unique_case_count
    FROM tribal_tanf_t3 tt3
    WHERE ((tt3."FAMILY_AFFILIATION" IS NOT NULL) AND (tt3."SEX" IS NOT NULL))
    GROUP BY
        tt3."RPT_MONTH_YEAR",
        tt3."STT",
        tt3."STT_CODE"
    UNION ALL
    SELECT
        'TRIBAL'::text AS program_type,
        'Closed Case Data'::text AS section,
        't4'::text AS record_type,
        'tribal_tanf_t4'::text AS source_table,
        tt4."RPT_MONTH_YEAR",
        tt4."STT",
        tt4."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT tt4."CASE_NUMBER") AS unique_case_count
    FROM tribal_tanf_t4 tt4
    GROUP BY
        tt4."RPT_MONTH_YEAR",
        tt4."STT",
        tt4."STT_CODE"
    UNION ALL
    SELECT
        'TRIBAL'::text AS program_type,
        'Closed Case Data'::text AS section,
        't5'::text AS record_type,
        'tribal_tanf_t5'::text AS source_table,
        tt5."RPT_MONTH_YEAR",
        tt5."STT",
        tt5."STT_CODE",
        count (*) AS total_record_count,
        count (DISTINCT tt5."CASE_NUMBER") AS unique_case_count
    FROM tribal_tanf_t5 tt5
    GROUP BY
        tt5."RPT_MONTH_YEAR",
        tt5."STT",
        tt5."STT_CODE"
    UNION ALL
    SELECT
        'TRIBAL'::text AS program_type,
        'Aggregate Data'::text AS section,
        't6'::text AS record_type,
        'tribal_tanf_t6'::text AS source_table,
        tt6."RPT_MONTH_YEAR",
        tt6."STT",
        tt6."STT_CODE",
        count (*) AS total_record_count,
        NULL::bigint AS unique_case_count
    FROM tribal_tanf_t6 tt6
    GROUP BY
        tt6."RPT_MONTH_YEAR",
        tt6."STT",
        tt6."STT_CODE"
    UNION ALL
    SELECT
        'TRIBAL'::text AS program_type,
        'Stratum Data'::text AS section,
        't7'::text AS record_type,
        'tribal_tanf_t7'::text AS source_table,
        tt7."RPT_MONTH_YEAR",
        tt7."STT",
        tt7."STT_CODE",
        count (*) AS total_record_count,
        NULL::bigint AS unique_case_count
    FROM tribal_tanf_t7 tt7
    WHERE ((tt7."TDRS_SECTION_IND" IS NOT NULL) AND (tt7."STRATUM" IS NOT NULL))
    GROUP BY
        tt7."RPT_MONTH_YEAR",
        tt7."STT",
        tt7."STT_CODE"
),
exiters_counts AS (
    SELECT
        'FRA'::text AS program_type,
        'Work Outcomes of TANF Exiters'::text AS section,
        'te1'::text AS record_type,
        'latest_tanf_exiters_view_prod'::text AS source_table,
        e."EXIT_DATE" AS "RPT_MONTH_YEAR",
        e."STT",
        e."STT_CODE",
        count (*) AS total_record_count,
        NULL::bigint AS unique_case_count
    FROM latest_tanf_exiters_view_prod e
    GROUP BY
        e."EXIT_DATE",
        e."STT",
        e."STT_CODE"
        )
    SELECT
        ssp_counts.program_type,
        ssp_counts.section,
        ssp_counts.record_type,
        ssp_counts.source_table,
        ssp_counts."RPT_MONTH_YEAR",
        ssp_counts."STT",
        ssp_counts."STT_CODE",
        ssp_counts.total_record_count,
        ssp_counts.unique_case_count
    FROM ssp_counts
    UNION ALL
    SELECT
        tanf_counts.program_type,
        tanf_counts.section,
        tanf_counts.record_type,
        tanf_counts.source_table,
        tanf_counts."RPT_MONTH_YEAR",
        tanf_counts."STT",
        tanf_counts."STT_CODE",
        tanf_counts.total_record_count,
        tanf_counts.unique_case_count
    FROM tanf_counts
    UNION ALL
    SELECT
        tribal_tanf_counts.program_type,
        tribal_tanf_counts.section,
        tribal_tanf_counts.record_type,
        tribal_tanf_counts.source_table,
        tribal_tanf_counts."RPT_MONTH_YEAR",
        tribal_tanf_counts."STT",
        tribal_tanf_counts."STT_CODE",
        tribal_tanf_counts.total_record_count,
        tribal_tanf_counts.unique_case_count
    FROM tribal_tanf_counts
    UNION ALL
    SELECT
        exiters_counts.program_type,
        exiters_counts.section,
        exiters_counts.record_type,
        exiters_counts.source_table,
        exiters_counts."RPT_MONTH_YEAR",
        exiters_counts."STT",
        exiters_counts."STT_CODE",
        exiters_counts.total_record_count,
        exiters_counts.unique_case_count
    FROM exiters_counts;
