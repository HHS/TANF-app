"""Schema for TANF T7 Row."""

from ...fields import Field, TransformField
from ...row_schema import RowSchema, SchemaManager
from ...transforms import calendar_quarter_to_rpt_month_year
from ... import validators
from tdpservice.search_indexes.documents.ssp import SSP_M7DataSubmissionDocument
import datetime

minYear = datetime.date.today().year - 5

schemas = []

validator_index = 7
section_ind_index = 7
stratum_index = 8
families_index = 10

sub_item_labels = ["5A", "5B", "5C"]
families_item_numbers = [sub_item_labels[i % 3] for i in range(30)]

for i in range(1, 31):
    schemas.append(
        RowSchema(
            document=SSP_M7DataSubmissionDocument(),
            quiet_preparser_errors=i > 1,
            preparsing_validators=[
                validators.hasLength(247),
                validators.notEmpty(0, 7),
                validators.notEmpty(validator_index, validator_index + 24),
                validators.field_year_month_with_header_year_quarter(),
            ],
            postparsing_validators=[],
            fields=[
                Field(
                    item="0",
                    name="RecordType",
                    friendly_name="record type",
                    type="string",
                    startIndex=0,
                    endIndex=2,
                    required=True,
                    validators=[],
                ),
                Field(
                    item="2",
                    name="CALENDAR_QUARTER",
                    friendly_name="calendar quarter",
                    type="number",
                    startIndex=2,
                    endIndex=7,
                    required=True,
                    validators=[
                        validators.dateYearIsLargerThan(minYear),
                        validators.quarterIsValid(),
                    ],
                ),
                TransformField(
                    transform_func=calendar_quarter_to_rpt_month_year((i - 1) % 3),
                    item="2A",
                    name="RPT_MONTH_YEAR",
                    friendly_name="reporting month and year",
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
                    item="3",
                    name="TDRS_SECTION_IND",
                    friendly_name="tdrs section indicator",
                    type="string",
                    startIndex=section_ind_index,
                    endIndex=section_ind_index + 1,
                    required=True,
                    validators=[validators.oneOf(["1", "2"])],
                ),
                Field(
                    item="4",
                    name="STRATUM",
                    friendly_name="stratum",
                    type="string",
                    startIndex=stratum_index,
                    endIndex=stratum_index + 2,
                    required=True,
                    validators=[validators.isInStringRange(0, 99)],
                ),
                Field(
                    item=families_item_numbers[i - 1],
                    name="FAMILIES_MONTH",
                    friendly_name="families month",
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

m7 = SchemaManager(schemas=schemas)
