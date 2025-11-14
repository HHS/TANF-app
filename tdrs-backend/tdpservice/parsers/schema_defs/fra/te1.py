"""Schema for FRA Work Outcome TANF Exiters records."""

from datetime import datetime

from tdpservice.parsers.constants import (
    INVALID_SSN_AREA_NUMBERS,
    INVALID_SSN_GROUP_NUMBERS,
    INVALID_SSN_SERIAL_NUMBERS,
    SSN_AREA_NUMBER_POSITION,
    SSN_GROUP_NUMBER_POSITION,
    SSN_SERIAL_NUMBER_POSITION,
)
from tdpservice.parsers.dataclasses import FieldType, Position
from tdpservice.parsers.fields import Field, TransformField
from tdpservice.parsers.row_schema import FRASchema
from tdpservice.parsers.validators import category1, category2
from tdpservice.search_indexes.models.fra import TANF_Exiter1


def tranform_exit_date(value, **kwargs):
    """transform function to handle datetime to int coercion."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        # Note: No type check here to allow exception to bubble up instead of searching for a fake None type
        return int(value)
    if isinstance(value, datetime):
        return int(value.strftime("%Y%m"))
    return value


te1 = [
    FRASchema(
        record_type="TE1",
        model=TANF_Exiter1,
        preparsing_validators=[
            category1.validate_exit_date_against_fiscal_period(),
        ],
        fields=[
            TransformField(
                item="A",
                name="EXIT_DATE",
                friendly_name="Exit Date",
                type=FieldType.NUMERIC,
                startIndex=0,
                endIndex=1,
                required=True,
                validators=[],
                is_encrypted=False,
                transform_func=tranform_exit_date,
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
                            category2.valueNotAt(SSN_AREA_NUMBER_POSITION, area_num)
                            for area_num in INVALID_SSN_AREA_NUMBERS
                        ],
                        *[
                            category2.valueNotAt(SSN_GROUP_NUMBER_POSITION, group_num)
                            for group_num in INVALID_SSN_GROUP_NUMBERS
                        ],
                        *[
                            category2.valueNotAt(SSN_SERIAL_NUMBER_POSITION, serial_num)
                            for serial_num in INVALID_SSN_SERIAL_NUMBERS
                        ],
                    ),
                ],
                is_encrypted=False,
            ),
        ],
    )
]
