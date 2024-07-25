"""Schema for TANF T7 Row."""

from tdpservice.parsers.transforms import calendar_quarter_to_rpt_month_year
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import RowSchema, SchemaManager
from tdpservice.parsers.validators.category1 import PreparsingValidators
from tdpservice.parsers.validators.category2 import FieldValidators
from tdpservice.parsers.validators.category3 import PostparsingValidators
from tdpservice.search_indexes.documents.ssp import SSP_M7DataSubmissionDocument

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
            record_type="M7",
            document=SSP_M7DataSubmissionDocument(),
            quiet_preparser_errors=i > 1,
            preparsing_validators=[
                PreparsingValidators.recordHasLength(247),
                PreparsingValidators.isNotEmpty(0, 7),
                PreparsingValidators.isNotEmpty(validator_index, validator_index + 24),
                PreparsingValidators.validate_fieldYearMonth_with_headerYearQuarter(),
                PreparsingValidators.calendarQuarterIsValid(2, 7),
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
                    item="2",
                    name="CALENDAR_QUARTER",
                    friendly_name="Calendar Quarter",
                    type="number",
                    startIndex=2,
                    endIndex=7,
                    required=True,
                    validators=[
                        FieldValidators.dateYearIsLargerThan(2020),
                        FieldValidators.quarterIsValid(),
                    ],
                ),
                TransformField(
                    transform_func=calendar_quarter_to_rpt_month_year((i - 1) % 3),
                    item="2A",
                    name="RPT_MONTH_YEAR",
                    friendly_name="Reporting Year and Month",
                    type="number",
                    startIndex=2,
                    endIndex=7,
                    required=True,
                    validators=[
                        FieldValidators.dateYearIsLargerThan(1998),
                        FieldValidators.dateMonthIsValid(),
                    ],
                ),
                Field(
                    item="3",
                    name="TDRS_SECTION_IND",
                    friendly_name="SDR Section Indicator",
                    type="string",
                    startIndex=section_ind_index,
                    endIndex=section_ind_index + 1,
                    required=True,
                    validators=[FieldValidators.isOneOf(["1", "2"])],
                ),
                Field(
                    item="4",
                    name="STRATUM",
                    friendly_name="Stratum",
                    type="string",
                    startIndex=stratum_index,
                    endIndex=stratum_index + 2,
                    required=True,
                    validators=[FieldValidators.isBetween(0, 99, inclusive=True, cast=int)],
                ),
                Field(
                    item=families_item_numbers[i - 1],
                    name="FAMILIES_MONTH",
                    friendly_name="Number of Families",
                    type="number",
                    startIndex=families_index,
                    endIndex=families_index + 7,
                    required=True,
                    validators=[FieldValidators.isBetween(0, 9999999, inclusive=True)],
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
