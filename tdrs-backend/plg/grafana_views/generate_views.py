"""
Script to generate SQL query files for each schema in schema_fields.json with specific field transformations.

This script will create a separate SQL file for each schema, replacing:
- DATE_OF_BIRTH with AGE_FIRST and AGE_LAST for non-admin users
- SSN with md5("SSN"::text) as SSN_HASH for non-admin users
"""

import argparse
import datetime
import json
import logging
import os

CWD = os.path.dirname(os.path.abspath(__file__))

query_template = """
SELECT {fields}
    data_files.program_type,
    data_files.section,
    data_files.version,
    data_files.year,
    data_files.quarter,
    stt.name AS "STT",                                                     -- Select stt_name from the stts table
    stt.stt_code AS "STT_CODE",                                            -- Select stt_code from the stts table
    stt.region_id AS "REGION"                                              -- Select region from the stts table
FROM {table} {record_type}
INNER JOIN
        data_files_datafile data_files                                     -- Join with data_files_datafile
        ON {record_type}.datafile_id = data_files.id                       -- Join condition
    INNER JOIN (
        SELECT
            stt_id,                                                        -- Select stt_id
            section,                                                       -- Select section
            year,                                                          -- Select fiscal_year
            quarter,                                                       -- Select fiscal_quarter
            MAX(version) AS version                                        -- Get the maximum version for each group
        FROM
            data_files_datafile                                            -- Subquery table
        GROUP BY
            stt_id, section, year, quarter                                 -- Group by columns
    ) most_recent
        ON data_files.stt_id = most_recent.stt_id
        AND data_files.program_type = most_recent.program_type,
        AND data_files.section = most_recent.section
        AND data_files.version = most_recent.version
        AND data_files.year = most_recent.year
        AND data_files.quarter = most_recent.quarter
    INNER JOIN
        stts_stt stt                                                       -- Join with the stts table (aliased as stt)
        ON data_files.stt_id = stt.id                                      -- Join condition to match stt_id
    WHERE
        data_files.year > 2020 AND                                         -- Filter for fiscal year
        data_files.quarter in ('Q1', 'Q2', 'Q3', 'Q4')                     -- Filter for fiscal quarters
        {custom_where_clause}
;
"""

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def handle_field(field, formatted_fields, is_admin):
    """Mutate or add field to fields array."""
    if field == "SSN":
        # Add SSN to the formatted fields list if generating admin views and SSN_HASH if not admin
        if not is_admin:
            formatted_fields.append(f'md5("{field}"::text) as "SSN_HASH"')
        else:
            formatted_fields.append(f'"{field}"')

        formatted_fields.append(
            f''' --
        -- Calculate if SSN is valid
        CASE
            WHEN "{field}" !~ '^(0{{9}}|1{{9}}|2{{9}}|3{{9}}|4{{9}}|5{{9}}|6{{9}}|7{{9}}|8{{9}}|9{{9}})$' THEN 1
            ELSE 0
        END AS "SSN_VALID"'''.strip()
        )
    elif field == "DATE_OF_BIRTH":
        # Add DATE_OF_BIRTH to the formatted fields list if generating admin views
        if is_admin:
            formatted_fields.append(f'"{field}"')

        formatted_fields.append(
            f''' --
        CASE -- Calculate AGE_FIRST: Age as of the first day of the reporting month
            WHEN "{field}" ~ '^[0-9]{{8}}$' AND
                    -- Validate year (reasonable range)
                    CAST(SUBSTRING("{field}" FROM 1 FOR 4) AS INTEGER) BETWEEN 1900 AND
                    EXTRACT(YEAR FROM CURRENT_DATE) AND
                    -- Validate month (01-12)
                    CAST(SUBSTRING("{field}" FROM 5 FOR 2) AS INTEGER) BETWEEN 1 AND 12 AND
                    -- Validate day (01-31)
                    CAST(SUBSTRING("{field}" FROM 7 FOR 2) AS INTEGER) BETWEEN 1 AND 31 AND
                    -- Validate RPT_MONTH_YEAR format (YYYYMM)
                    "RPT_MONTH_YEAR"::TEXT ~ '^[0-9]{{6}}$'
            THEN
                -- Simple calculation: (end_date - start_date) / 365.25
                ROUND(
                    EXTRACT(EPOCH FROM (
                        -- Calculate the difference in days between last day of reporting month and birth date
                        (DATE_TRUNC('MONTH', TO_DATE(
                            SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 1 FOR 4) || '-' ||
                            SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 5 FOR 2) || '-01',
                            'YYYY-MM-DD'
                        ))) -
                        TO_DATE(
                            SUBSTRING("{field}" FROM 1 FOR 4) || '-' ||
                            SUBSTRING("{field}" FROM 5 FOR 2) || '-' ||
                            SUBSTRING("{field}" FROM 7 FOR 2),
                            'YYYY-MM-DD'
                        )
                    )) / (365.25 * 86400), -- Convert seconds to years (86400 seconds per day)
                    1  -- Round to 1 decimal place
                )
            ELSE NULL
        END AS "AGE_FIRST"'''.strip()
        )

        formatted_fields.append(
            f''' --
        CASE -- Calculate AGE_LAST: Age as of the last day of the reporting month
            WHEN "{field}" ~ '^[0-9]{{8}}$' AND
                    -- Validate year (reasonable range)
                    CAST(SUBSTRING("{field}" FROM 1 FOR 4) AS INTEGER) BETWEEN 1900 AND
                    EXTRACT(YEAR FROM CURRENT_DATE) AND
                    -- Validate month (01-12)
                    CAST(SUBSTRING("{field}" FROM 5 FOR 2) AS INTEGER) BETWEEN 1 AND 12 AND
                    -- Validate day (01-31)
                    CAST(SUBSTRING("{field}" FROM 7 FOR 2) AS INTEGER) BETWEEN 1 AND 31 AND
                    -- Validate RPT_MONTH_YEAR format (YYYYMM)
                    "RPT_MONTH_YEAR"::TEXT ~ '^[0-9]{{6}}$'
            THEN
                -- Simple calculation: (end_date - start_date) / 365.25
                ROUND(
                    EXTRACT(EPOCH FROM (
                        -- Calculate the difference in days between last day of reporting month and birth date
                        (DATE_TRUNC('MONTH', TO_DATE(
                            SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 1 FOR 4) || '-' ||
                            SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 5 FOR 2) || '-01',
                            'YYYY-MM-DD'
                        )) + INTERVAL '1 MONTH - 1 day') -
                        TO_DATE(
                            SUBSTRING("{field}" FROM 1 FOR 4) || '-' ||
                            SUBSTRING("{field}" FROM 5 FOR 2) || '-' ||
                            SUBSTRING("{field}" FROM 7 FOR 2),
                            'YYYY-MM-DD'
                        )
                    )) / (365.25 * 86400), -- Convert seconds to years (86400 seconds per day)
                    1  -- Round to 1 decimal place
                )
            ELSE NULL
        END AS "AGE_LAST"'''.strip()
        )

        formatted_fields.append(
            f''' --
        -- Determine AGE_VALID
        CASE
            WHEN "{field}" !~ '^[0-9]{{8}}$' OR
                    -- Perform null check
                    "{field}" IS NULL OR "{field}" = '' OR
                    -- Validate year (reasonable range)
                    CAST(SUBSTRING("{field}" FROM 1 FOR 4) AS INTEGER) NOT BETWEEN 1900 AND
                    EXTRACT(YEAR FROM CURRENT_DATE) OR
                    -- Validate month (01-12)
                    CAST(SUBSTRING("{field}" FROM 5 FOR 2) AS INTEGER) NOT BETWEEN 1 AND 12 OR
                    -- Validate day (01-31)
                    CAST(SUBSTRING("{field}" FROM 7 FOR 2) AS INTEGER) NOT BETWEEN 1 AND 31
            THEN 0
            ELSE 1
        END AS "AGE_VALID"'''.strip()
        )
    else:
        formatted_fields.append(f'"{field}"')


def handle_table_name(schema_type, schema_name):
    """Determine appropriate table and record type."""
    table_name = ""
    record_type = ""
    if schema_type == "tanf":
        table_name = f"search_indexes_TANF_{schema_name.upper()}"
        record_type = schema_name.upper()
    elif schema_type == "tribal_tanf":
        table_name = f"search_indexes_TRIBAL_TANF_{schema_name.upper()}"
        record_type = schema_name.upper()
    elif schema_type == "ssp":
        table_name = f"search_indexes_SSP_{schema_name.upper()}"
        record_type = schema_name.upper()
    elif schema_type == "fra":
        table_name = f"search_indexes_FRA_{schema_name.upper()}"
        record_type = schema_name.upper()

    return table_name, record_type


def handle_where_clause(record_type):
    """Add custom where clause based on record type."""
    if "3" in record_type:
        return 'AND "FAMILY_AFFILIATION" != 0 AND "FAMILY_AFFILIATION" IS NOT NULL AND "SEX" != 0 AND "SEX" IS NOT NULL'
    elif "7" in record_type:
        return 'AND "FAMILIES_MONTH" != 0 AND "FAMILIES_MONTH" IS NOT NULL AND "TDRS_SECTION_IND" != \'\' AND "TDRS_SECTION_IND" IS NOT NULL'
    else:
        return ""


def main(is_admin):
    """Generate views."""
    # Log start of script execution
    logger.info(f"Starting {'admin' if is_admin else 'user'} view generation")

    # Load the schema fields from the JSON file
    with open(os.path.join(CWD, "schema_fields.json"), "r") as f:
        json_data = json.load(f)

    # Extract the schema data from the 'schemas' key
    schema_data = json_data.get("schemas", {})

    # Log information about the loaded schema data
    logger.info(f"Loaded schema data with {len(schema_data)} schema types")

    # Create the output directory if it doesn't exist
    output_dir_name = "admin_views" if is_admin else "user_views"
    output_dir = os.path.join(CWD, output_dir_name)
    os.makedirs(output_dir, exist_ok=True)

    # Process each schema type and its schemas
    for schema_type, schemas in schema_data.items():
        for schema_name, fields in schemas.items():
            # Skip if no fields
            if not fields:
                continue

            # Format the field list with transformations for DATE_OF_BIRTH and SSN
            formatted_fields = []
            for field in fields:
                handle_field(field, formatted_fields, is_admin)

            formatted_fields_str = ",".join(formatted_fields) + ","

            # Determine the appropriate table name based on schema type and name
            table_name, record_type = handle_table_name(schema_type, schema_name)

            # Handle custom where clause
            custom_where_clause = handle_where_clause(record_type)

            # Construct query
            query = query_template.format(
                fields=formatted_fields_str,
                table=table_name,
                record_type=record_type,
                custom_where_clause=custom_where_clause,
            )

            # Create the header comment with warning, timestamp, and transformation details
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create the header comment as a single string
            header_comment = f"-- AUTOMATICALLY GENERATED FILE ON {timestamp}\n"
            header_comment += "-- DO NOT EDIT - Your changes will be overwritten\n"
            header_comment += "-- Generated by generate_views.py\n\n"
            header_comment += f"-- SQL view for {schema_type}_{schema_name} schema\n"
            header_comment += "-- Transformations applied:\n"

            # Add specific transformation details
            if "DATE_OF_BIRTH" in fields:
                header_comment += (
                    "--   * DATE_OF_BIRTH transformed to AGE calculation (as integer)\n"
                )
            if "SSN" in fields and not is_admin:
                header_comment += "--   * SSN transformed to md5 hash for privacy\n"

            # Add a blank line at the end
            header_comment += "\n\n"

            # Modify the query to create a view
            view_name = f'{"admin_" if is_admin else ""}{schema_type}_{schema_name}'
            view_query = f"""CREATE OR REPLACE VIEW "{view_name}" AS {query}"""

            # Write to a file
            output_file = os.path.join(output_dir, f"{view_name}.sql")
            with open(output_file, "w") as f:
                f.write(header_comment + view_query)

            logger.info(f"Created query for {schema_type}_{schema_name}")

    logger.info(
        f"All query files have been generated in the {output_dir_name} directory."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate PostgreSQL views for Grafana."
    )
    parser.add_argument(
        "--admin_only",
        help="Only generate admin version of views.",
        action="store_true",
    )
    parser.add_argument(
        "--user_only", help="Only generate user version of views.", action="store_true"
    )
    parser.add_argument("--all", help="Generate all views.", action="store_true")

    args = parser.parse_args()
    if args.all:
        main(True)
        main(False)
    elif args.admin_only and not (args.user_only or args.all):
        main(True)
    elif args.user_only and not (args.admin_only or args.all):
        main(False)
