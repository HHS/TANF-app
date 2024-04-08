"""Schema for Tribal TANF T7 Row."""

from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers.transforms import calendar_quarter_to_rpt_month_year
from tdpservice.parsers import validators
from tdpservice.search_indexes.documents.tribal import Tribal_TANF_T7DataSubmissionDocument

schemas = []

validator_index = 7
section_ind_index = 7
stratum_index = 8
families_index = 10
for i in range(1, 31):
    month_index = (i - 1) % 3
    sub_item_labels = ["A", "B", "C"]
    families_value_item_number = f"6{sub_item_labels[month_index]}"

    schemas.append(
        RowSchema(
            record_type="T7",
            document=Tribal_TANF_T7DataSubmissionDocument(),
            quiet_preparser_errors=i > 1,
            preparsing_validators=[
                validators.recordHasLength(247),
                validators.notEmpty(0, 7),
                validators.notEmpty(validator_index, validator_index + 24),
            ],
            postparsing_validators=[],
            fields=[
                Field(
                    item="0",
                    name="RecordType",
                    friendly_name="Record Type",
                    type="string",
                    startIndex=0,
                    endIndex=2,
                    required=True,
                    validators=[],
                ),
                Field(
                    item="3",
                    name="CALENDAR_QUARTER",
                    friendly_name="Calendar Quarter",
                    type="number",
                    startIndex=2,
                    endIndex=7,
                    required=True,
                    validators=[
                        validators.dateYearIsLargerThan(1998),
                        validators.quarterIsValid(),
                    ],
                ),
                TransformField(
                    transform_func=calendar_quarter_to_rpt_month_year(month_index),
                    item="3A",
                    name="RPT_MONTH_YEAR",
                    friendly_name="Reporting Year and Month",
                    type="number",
                    startIndex=2,
                    endIndex=7,
                    required=True,
                    validators=[
                        validators.dateYearIsLargerThan(1998),
                        validators.dateMonthIsValid(),
                    ],
                ),
                Field(
                    item="4",
                    name="TDRS_SECTION_IND",
                    friendly_name="TDRS Section Indicator",
                    type="string",
                    startIndex=section_ind_index,
                    endIndex=section_ind_index + 1,
                    required=True,
                    validators=[validators.oneOf(["1", "2"])],
                ),
                Field(
                    item="5",
                    name="STRATUM",
                    friendly_name="Stratum",
                    type="string",
                    startIndex=stratum_index,
                    endIndex=stratum_index + 2,
                    required=True,
                    validators=[validators.isInStringRange(0, 99)],
                ),
                Field(
                    item=families_value_item_number,
                    name="FAMILIES_MONTH",
                    friendly_name="Families Month",
                    type="number",
                    startIndex=families_index,
                    endIndex=families_index + 7,
                    required=True,
                    validators=[validators.isInLimits(0, 9999999)],
                ),
            ],
        )
    )

    index_offset = 0 if i % 3 != 0 else 24
    validator_index += index_offset
    section_ind_index += index_offset
    stratum_index += index_offset
    families_index += 7 if i % 3 != 0 else 10

t7 = SchemaManager(schemas=schemas)
