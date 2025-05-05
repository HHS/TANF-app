"""
Script to generate SQL query files for each schema in schema_fields.json.

This script will create a separate SQL file for each schema, replacing the field list
in the first SELECT statement with the fields from that schema.
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
        END AS "AGE_LAST"'''.strip())


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
logger.info("Starting admin schema query generation")

# Load the schema fields from the JSON file
with open('schema_fields.json', 'r') as f:
    json_data = json.load(f)

# Extract the schema data from the 'schemas' key
schema_data = json_data.get('schemas', {})

# Log information about the loaded schema data
logger.info(f"Loaded schema data with {len(schema_data)} schema types")

# Read the template query from the file
with open('view_template.txt', 'r') as f:
    query_template = f.read()

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
output_dir = 'admin_views'
os.makedirs(output_dir, exist_ok=True)

# Process each schema type and its schemas
for schema_type, schemas in schema_data.items():
    for schema_name, fields in schemas.items():
        # Skip if no fields
        if not fields:
            continue

        # Format the field list with double quotes around each field
        formatted_fields = []
        for field in fields:
            formatted_fields.append(f'"{field}"')
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

        # Create the view name based on schema type and name
        view_name = f'admin_{schema_type}_{schema_name}'

        # Create the header comment
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Use a list of lines and join them with os.linesep to avoid string formatting issues
        header_lines = []
        header_lines.append(f'-- AUTOMATICALLY GENERATED FILE ON {timestamp}')
        header_lines.append('-- DO NOT EDIT - Your changes will be overwritten')
        header_lines.append('-- Generated by generate_admin_views.py')
        header_lines.append('')  # Empty line
        header_lines.append(f'-- SQL view for {view_name} schema')
        header_lines.append('-- Transformations applied:')

        # Add specific transformation details
        if "DATE_OF_BIRTH" in fields:
            header_lines.append('--   * DATE_OF_BIRTH transformed to AGE calculation (as integer)')

        # Add a blank line at the end of the header
        header_lines.append('')

        # Join all lines with the system's line separator
        header_text = os.linesep.join(header_lines) + os.linesep

        # Create the view query
        view_query = f'CREATE OR REPLACE VIEW "{view_name}" AS {new_query}'

        # Write to a file
        output_file = os.path.join(output_dir, f'{view_name}.sql')
        with open(output_file, 'w') as f:
            f.write(header_text + view_query)

        logger.info(f'Created query for {schema_type}_{schema_name}')

logger.info('All query files have been generated in the admin_views directory.')
