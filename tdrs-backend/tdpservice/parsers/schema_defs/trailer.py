"""Schema for TRAILER row of all submission types."""

from tdpservice.parsers.dataclasses import FieldType
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import TanfDataReportSchema
from tdpservice.parsers.validators import category1, category2

trailer = TanfDataReportSchema(
    record_type="TRAILER",
    model=dict,
    preparsing_validators=[
        category1.recordHasLength(23),
        category1.recordStartsWith(
            "TRAILER", lambda _: "Your file does not end with a TRAILER record."
        ),
    ],
    postparsing_validators=[],
    fields=[
        Field(
            item="1",
            name="title",
            friendly_name="title",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=0,
            endIndex=7,
            required=True,
            validators=[category2.isEqual("TRAILER")],
        ),
        Field(
            item="2",
            name="record_count",
            friendly_name="record count",
            type=FieldType.NUMERIC,
            startIndex=7,
            endIndex=14,
            required=True,
            validators=[category2.isBetween(0, 9999999, inclusive=True)],
        ),
        Field(
            item="-1",
            name="blank",
            friendly_name="blank",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=14,
            endIndex=23,
            required=False,
            validators=[category2.isEqual("         ")],
        ),
    ],
)
