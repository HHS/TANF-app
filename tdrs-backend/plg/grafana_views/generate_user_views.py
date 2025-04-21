"""
Script to generate SQL query files for each schema in schema_fields.json with specific field transformations.

This script will create a separate SQL file for each schema, replacing:
- DATE_OF_BIRTH with AGE_FIRST and AGE_LAST
- SSN with md5("SSN"::text) as SSN_HASH
"""

import os
import json
import re
import logging
import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def handle_field(field, formatted_fields):
    """Mutate or add field to fields array."""
    if field == "DATE_OF_BIRTH":
        # Remove DATE_OF_BIRTH from the formatted fields list since we're adding two new age calculations
        # We'll add the new AGE_FIRST and AGE_LAST calculations instead
        formatted_fields.append(f'''
        -- Calculate AGE_FIRST: Age as of the first day of the reporting month
        CASE
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
                (
                    EXTRACT(YEAR FROM TO_DATE(
                        SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 1 FOR 4) || '-' ||
                        SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 5 FOR 2) || '-01',
                        'YYYY-MM-DD'
                    )) -
                    EXTRACT(YEAR FROM TO_DATE(
                        SUBSTRING("{field}" FROM 1 FOR 4) || '-' ||
                        SUBSTRING("{field}" FROM 5 FOR 2) || '-' ||
                        SUBSTRING("{field}" FROM 7 FOR 2),
                        'YYYY-MM-DD'
                    )) -
                    (CASE
                        WHEN TO_CHAR(TO_DATE(
                            SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 1 FOR 4) || '-' ||
                            SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 5 FOR 2) || '-01',
                            'YYYY-MM-DD'
                        ), 'MMDD') <
                            TO_CHAR(TO_DATE(
                                SUBSTRING("{field}" FROM 1 FOR 4) || '-' ||
                                SUBSTRING("{field}" FROM 5 FOR 2) || '-' ||
                                SUBSTRING("{field}" FROM 7 FOR 2),
                                'YYYY-MM-DD'
                            ), 'MMDD')
                        THEN 1
                        ELSE 0
                    END)
                )
            ELSE NULL
        END AS "AGE_FIRST"'''.strip())

        formatted_fields.append(f'''
        -- Calculate AGE_LAST: Age as of the last day of the reporting month
        CASE
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
                (
                    EXTRACT(YEAR FROM (DATE_TRUNC('MONTH', TO_DATE(
                        SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 1 FOR 4) || '-' ||
                        SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 5 FOR 2) || '-01',
                        'YYYY-MM-DD'
                    )) + INTERVAL '1 MONTH - 1 day')) -
                    EXTRACT(YEAR FROM TO_DATE(
                        SUBSTRING("{field}" FROM 1 FOR 4) || '-' ||
                        SUBSTRING("{field}" FROM 5 FOR 2) || '-' ||
                        SUBSTRING("{field}" FROM 7 FOR 2),
                        'YYYY-MM-DD'
                    )) -
                    (CASE
                        WHEN TO_CHAR((DATE_TRUNC('MONTH', TO_DATE(
                            SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 1 FOR 4) || '-' ||
                            SUBSTRING("RPT_MONTH_YEAR"::TEXT FROM 5 FOR 2) || '-01',
                            'YYYY-MM-DD'
                        )) + INTERVAL '1 MONTH - 1 day'), 'MMDD') <
                            TO_CHAR(TO_DATE(
                                SUBSTRING("{field}" FROM 1 FOR 4) || '-' ||
                                SUBSTRING("{field}" FROM 5 FOR 2) || '-' ||
                                SUBSTRING("{field}" FROM 7 FOR 2),
                                'YYYY-MM-DD'
                            ), 'MMDD')
                        THEN 1
                        ELSE 0
                    END)
                )
            ELSE NULL
        END AS "AGE_LAST"'''.strip())
    elif field == "SSN":
        formatted_fields.append(f'md5("{field}"::text) as "SSN_HASH"')
    else:
        formatted_fields.append(f'"{field}"')


def handle_table_name(schema_type, schema_name):
    """Determine appropriate table name."""
    table_name = ""
    table_alias = ""
    if schema_type == 'tanf':
        table_name = f'search_indexes_TANF_{schema_name.upper()}'
        table_alias = schema_name.upper()
    elif schema_type == 'tribal_tanf':
        table_name = f'search_indexes_TRIBAL_TANF_{schema_name.upper()}'
        table_alias = schema_name.upper()
    elif schema_type == 'ssp':
        table_name = f'search_indexes_SSP_{schema_name.upper()}'
        table_alias = schema_name.upper()
    elif schema_type == 'fra':
        table_name = f'search_indexes_FRA_{schema_name.upper()}'
        table_alias = schema_name.upper()

    return table_name, table_alias


# Log start of script execution
logger.info("Starting user view generation")

# Load the schema fields from the JSON file
with open('schema_fields.json', 'r') as f:
    json_data = json.load(f)

# Extract the schema data from the 'schemas' key
schema_data = json_data.get('schemas', {})

# Log information about the loaded schema data
logger.info(f"Loaded schema data with {len(schema_data)} schema types")

# Read the template query from the file
with open('view_template.txt', 'r') as f:
    query_template = f.read().split(';')[0] + ';'  # Take only the first query

# Extract the SELECT part and the rest of the query
select_pattern = re.compile(r'SELECT\s+([^\n]+),\s*\n')
select_match = select_pattern.search(query_template)

if not select_match:
    logger.error("Could not find SELECT statement in the query template.")
    exit(1)

# Get the part after the field list
query_parts = query_template.split('\n', 1)
after_select = query_parts[1].lstrip()

# Extract the FROM part to identify the table name and alias
from_pattern = re.compile(r'FROM\s+([^\s]+)\s+([^\s\n]+)')
from_match = from_pattern.search(query_template)

if not from_match:
    logger.error("Could not find FROM clause in the query template.")
    exit(1)

template_table = from_match.group(1)  # e.g., search_indexes_TANF_T1
template_alias = from_match.group(2)  # e.g., T1

# Create the output directory if it doesn't exist
output_dir = 'user_views'
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
            handle_field(field, formatted_fields)

        formatted_fields_str = ','.join(formatted_fields)

        # Create the new SELECT statement
        new_select = f'SELECT {formatted_fields_str},'

        # Determine the appropriate table name based on schema type and name
        table_name, table_alias = handle_table_name(schema_type, schema_name)

        # Create a new query by replacing the table name and alias throughout the query
        new_query = query_template

        # Replace the SELECT part
        new_query = select_pattern.sub(f'{new_select} \n', new_query)

        # Replace the table name and alias in the FROM clause
        new_query = new_query.replace(f'FROM {template_table} {template_alias}',
                                      f'FROM {table_name} {table_alias}')

        # Replace all other occurrences of the template alias with the new alias
        # This handles the JOIN conditions and any other references to the table alias
        new_query = re.sub(r'\b' + template_alias + r'\b', table_alias, new_query)

        # Create the header comment with warning, timestamp, and transformation details
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Create the header comment as a single string
        header_comment = f"-- AUTOMATICALLY GENERATED FILE ON {timestamp}\n"
        header_comment += "-- DO NOT EDIT - Your changes will be overwritten\n"
        header_comment += "-- Generated by generate_user_views.py\n\n"
        header_comment += f"-- SQL view for {schema_type}_{schema_name} schema\n"
        header_comment += "-- Transformations applied:\n"

        # Add specific transformation details
        if "DATE_OF_BIRTH" in fields:
            header_comment += "--   * DATE_OF_BIRTH transformed to AGE calculation (as integer)\n"
        if "SSN" in fields:
            header_comment += "--   * SSN transformed to md5 hash for privacy\n"

        # Add a blank line at the end
        header_comment += "\n\n"

        # Modify the query to create a view
        view_name = f'{schema_type}_{schema_name}'
        view_query = f'''CREATE OR REPLACE VIEW "{view_name}" AS {new_query}'''

        # Write to a file
        output_file = os.path.join(output_dir, f'{view_name}.sql')
        with open(output_file, 'w') as f:
            f.write(header_comment + view_query)

        logger.info(f'Created query for {schema_type}_{schema_name}')

logger.info('All query files have been generated in the user_views directory.')
