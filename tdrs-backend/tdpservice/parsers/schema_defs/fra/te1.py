"""Schema for FRA Work Outcome TANF Exiters records."""

from tdpservice.parsers.constants import (
    HEADER_POSITION,
    INVALID_SSN_AREA_NUMBERS,
    INVALID_SSN_GROUP_NUMBERS,
    INVALID_SSN_SERIAL_NUMBERS,
    SSN_AREA_NUMBER_POSITION,
    SSN_GROUP_NUMBER_POSITION,
    SSN_SERIAL_NUMBER_POSITION,
    TRAILER_POSITION,
)
from tdpservice.parsers.dataclasses import FieldType, Position
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import FRASchema
from tdpservice.parsers.validators import category1, category2
from tdpservice.search_indexes.models.fra import TANF_Exiter1

te1 = [
    FRASchema(
        record_type="TE1",
        model=TANF_Exiter1,
        preparsing_validators=[
            category1.validate_exit_date_against_fiscal_period(),
        ],
        fields=[
            Field(
                item="A",
                name="EXIT_DATE",
                friendly_name="Exit Date",
                type=FieldType.NUMERIC,
                position=Position(start=0),
                required=True,
                validators=[],
                is_encrypted=False,
            ),
            Field(
                item="B",
                name="SSN",
                friendly_name="Social Security Number",
                type=FieldType.ALPHA_NUMERIC,
                position=Position(start=1),
                required=True,
                validators=[
                    category2.fraSSNAllOf(
                        category2.isNumber(),
                        category2.intHasLength(9),
                        *[
                            category2.valueNotAt(slice(0, 3), area_num)
                            for area_num in INVALID_SSN_AREA_NUMBERS
                        ],
                        *[
                            category2.valueNotAt(slice(3, 5), group_num)
                            for group_num in INVALID_SSN_GROUP_NUMBERS
                        ],
                        *[
                            category2.valueNotAt(slice(5, 9), serial_num)
                            for serial_num in INVALID_SSN_SERIAL_NUMBERS
                        ],
                    ),
                ],
                is_encrypted=False,
            ),
        ],
    )
]
