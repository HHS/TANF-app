CREATE OR REPLACE VIEW public.latest_tanf_exiters_view_prod AS
WITH latest_files AS (
    SELECT
        DISTINCT ON (df.stt_id, df.section_id, df.year, df.quarter) df.id,
        df.stt_id,
        section.name AS section,
        df.year,
        df.quarter,
        df.version,
        df.created_at
    FROM data_files_datafile df
    JOIN data_files_section section ON section.id = df.section_id
    JOIN data_files_program program ON program.id = section.program_id
    WHERE ((df.year >= 2025) AND ((section.name)::text = 'Work Outcomes of TANF Exiters'::text) AND ((program.code)::text = 'FRA'::text))
    ORDER BY
        df.stt_id,
        df.section_id,
        df.year,
        df.quarter,
        df.version DESC
),
base_data AS (
    SELECT
        stt.region_id AS "REGION",
        stt.name AS "STT",
        stt.stt_code AS "STT_CODE",
        df.section,
        df.year AS "FISCAL_YR",
        df.quarter AS "FISCAL_QTR",
        df.id AS datafile_id,
        to_char ((df.created_at AT TIME ZONE 'UTC'::text), 'YYYY-MM-DD HH24:MI:SS'::text) AS submission_datetime,
        te."EXIT_DATE",
        te."SSN"
    FROM ((latest_files df JOIN search_indexes_tanf_exiter1 te ON ((te.datafile_id = df.id))) JOIN stts_stt stt ON ((df.stt_id = stt.id)))
),
flagged AS MATERIALIZED (
    SELECT
        b."REGION",
        b."STT",
        b."STT_CODE",
        b.section,
        b."FISCAL_YR",
        b."FISCAL_QTR",
        b.datafile_id,
        b.submission_datetime,
        b."EXIT_DATE",
        b."SSN",
        CASE
        WHEN (((b."SSN")::text = ANY ((ARRAY ['000000000'::character varying, '111111111'::character varying, '222222222'::character varying, '333333333'::character varying, '444444444'::character varying, '555555555'::character varying, '666666666'::character varying, '777777777'::character varying, '888888888'::character varying, '999999999'::character varying])::text [])) OR ("left" ((b."SSN")::text, 3) = '666'::text) OR ("left" ((b."SSN")::text, 1) = '9'::text)) THEN 1
        ELSE 0 END AS is_invalid_ssn
    FROM base_data b
),
ssn_stt_counts AS MATERIALIZED (
    SELECT
        f_1."SSN",
        f_1."STT",
        count (*) AS row_count
    FROM flagged f_1
    WHERE (f_1.is_invalid_ssn = 0)
    GROUP BY
        f_1."SSN",
        f_1."STT"
),
cross_dupes AS (
    SELECT
        s."SSN"
    FROM ssn_stt_counts s
    GROUP BY
        s."SSN"
    HAVING (count (*) > 1)
),
within_dupes AS (
    SELECT
        s."SSN",
        s."STT"
    FROM ssn_stt_counts s
    WHERE (s.row_count > 1)
),
distinct_exit_dates AS MATERIALIZED (
    SELECT
        DISTINCT f_1."SSN",
        f_1."STT",
        f_1."EXIT_DATE"
    FROM flagged f_1
    WHERE (f_1.is_invalid_ssn = 0)
),
ordered_exit_dates AS (
    SELECT
        d."SSN",
        d."STT",
        d."EXIT_DATE",
        LAG (d."EXIT_DATE") OVER (PARTITION BY d."SSN", d."STT" ORDER BY d."EXIT_DATE") AS previous_exit_date,
        LEAD (d."EXIT_DATE") OVER (PARTITION BY d."SSN", d."STT" ORDER BY d."EXIT_DATE") AS next_exit_date
    FROM distinct_exit_dates d
),
adjacent_dupes AS (
    SELECT
        o."SSN",
        o."STT",
        o."EXIT_DATE"
    FROM ordered_exit_dates o
    WHERE (((o."EXIT_DATE" - o.previous_exit_date) = 1) OR ((o.next_exit_date - o."EXIT_DATE") = 1))
    )
    SELECT
        f."REGION",
        f."STT",
        f."STT_CODE",
        f.section,
        f."FISCAL_YR",
        f."FISCAL_QTR",
        f.datafile_id,
        f.submission_datetime,
        f."EXIT_DATE",
        f."SSN",
        f.is_invalid_ssn,
        CASE
        WHEN (c."SSN" IS NOT NULL) THEN 1
        ELSE 0 END AS is_duplicate_ssn_xj,
        CASE
        WHEN (w."SSN" IS NOT NULL) THEN 1
        ELSE 0 END AS is_duplicate_ssn,
        CASE
        WHEN (a."SSN" IS NOT NULL) THEN 1
        ELSE 0 END AS is_duplicate_adjacent
    FROM (((flagged f LEFT JOIN cross_dupes c ON (((f."SSN")::text = (c."SSN")::text))) LEFT JOIN within_dupes w ON ((((f."SSN")::text = (w."SSN")::text) AND ((f."STT")::text = (w."STT")::text)))) LEFT JOIN adjacent_dupes a ON ((((f."SSN")::text = (a."SSN")::text) AND ((f."STT")::text = (a."STT")::text) AND (f."EXIT_DATE" = a."EXIT_DATE"))));
