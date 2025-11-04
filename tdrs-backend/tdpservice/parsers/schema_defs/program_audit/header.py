"""Schema for HEADER row of program audit submission types."""

from tdpservice.parsers.dataclasses import FieldType
from tdpservice.parsers.fields import Field
from tdpservice.parsers.row_schema import HeaderSchema
from tdpservice.parsers.validators import category1, category2

header = HeaderSchema(
    record_type="HEADER",
    model=dict,
    preparsing_validators=[
        category1.recordHasLength(23),
        category1.recordStartsWith(
            "HEADER", lambda _: "Your file does not begin with a HEADER record."
        ),
    ],
    postparsing_validators=[],
    fields=[
        Field(
            item="2",
            name="title",
            friendly_name="title",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=0,
            endIndex=6,
            required=True,
            validators=[
                category2.isEqual("HEADER"),
            ],
        ),
        Field(
            item="4",
            name="year",
            friendly_name="year",
            type=FieldType.NUMERIC,
            startIndex=6,
            endIndex=10,
            required=True,
            validators=[category2.isBetween(2000, 2099, inclusive=True)],
        ),
        Field(
            item="5",
            name="quarter",
            friendly_name="quarter",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=10,
            endIndex=11,
            required=True,
            validators=[category2.isOneOf(["1", "2", "3", "4"])],
        ),
        Field(
            item="6",
            name="type",
            friendly_name="type",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=11,
            endIndex=12,
            required=True,
            validators=[category2.isOneOf(["A"])],
        ),
        Field(
            item="1",
            name="state_fips",
            friendly_name="state fips",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=12,
            endIndex=14,
            required=False,
            validators=[
                category2.isNotOneOf(
                    [
                        "00",
                    ]
                ),
            ],
        ),
        Field(
            item="3",
            name="tribe_code",
            friendly_name="tribe code",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=14,
            endIndex=17,
            required=False,
            validators=[category2.isOneOf(["000", "   "])],
        ),
        Field(
            item="7",
            name="program_type",
            friendly_name="program type",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=17,
            endIndex=20,
            required=True,
            validators=[category2.isOneOf(["TAN", "SSP"])],
        ),
        Field(
            item="8",
            name="edit",
            friendly_name="edit",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=20,
            endIndex=21,
            required=True,
            validators=[category2.isOneOf(["1", "2"])],
        ),
        Field(
            item="9",
            name="encryption",
            friendly_name="encryption",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=21,
            endIndex=22,
            required=False,
            validators=[category2.isOneOf([" ", "E"])],
        ),
        Field(
            item="10",
            name="update",
            friendly_name="update indicator",
            type=FieldType.ALPHA_NUMERIC,
            startIndex=22,
            endIndex=23,
            required=True,
            validators=[category2.validateHeaderUpdateIndicator()],
            ignore_errors=True,
        ),
    ],
)
