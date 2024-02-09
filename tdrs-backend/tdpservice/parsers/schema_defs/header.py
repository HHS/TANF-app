"""Schema for HEADER row of all submission types."""


from ..fields import Field
from ..row_schema import RowSchema
from .. import validators


header = RowSchema(
    document=None,
    preparsing_validators=[
        validators.hasLength(
            23,
            lambda value, length: f"Header length is {len(value)} but must be {length} characters.",
        ),
        validators.startsWith("HEADER",
                              lambda value: f"Your file does not begin with a {value} record"),
    ],
    postparsing_validators=[],
    fields=[
        Field(
            item="2",
            name="title",
            friendly_name="title",
            type="string",
            startIndex=0,
            endIndex=6,
            required=True,
            validators=[
                validators.matches("HEADER"),
            ],
        ),
        Field(
            item="4",
            name="year",
            friendly_name="year",
            type="number",
            startIndex=6,
            endIndex=10,
            required=True,
            validators=[validators.isInLimits(2000, 2099)],
        ),
        Field(
            item="5",
            name="quarter",
            friendly_name="quarter",
            type="string",
            startIndex=10,
            endIndex=11,
            required=True,
            validators=[validators.oneOf(["1", "2", "3", "4"])],
        ),
        Field(
            item="6",
            name="type",
            friendly_name="type",
            type="string",
            startIndex=11,
            endIndex=12,
            required=True,
            validators=[validators.oneOf(["A", "C", "G", "S"])],
        ),
        Field(
            item="1",
            name="state_fips",
            friendly_name="state fips",
            type="string",
            startIndex=12,
            endIndex=14,
            required=False,
            validators=[
                validators.or_validators(
                    validators.isInStringRange(0, 2),
                    validators.isInStringRange(4, 6),
                    validators.isInStringRange(8, 13),
                    validators.isInStringRange(15, 42),
                    validators.isInStringRange(44, 51),
                    validators.isInStringRange(53, 56),
                    validators.oneOf(["66", "72", "78"]),
                )
            ],
        ),
        Field(
            item="3",
            name="tribe_code",
            friendly_name="tribe code",
            type="string",
            startIndex=14,
            endIndex=17,
            required=False,
            validators=[validators.isInStringRange(0, 999)],
        ),
        Field(
            item="7",
            name="program_type",
            friendly_name="program type",
            type="string",
            startIndex=17,
            endIndex=20,
            required=True,
            validators=[validators.oneOf(["TAN", "SSP"])],
        ),
        Field(
            item="8",
            name="edit",
            friendly_name="edit",
            type="string",
            startIndex=20,
            endIndex=21,
            required=True,
            validators=[validators.oneOf(["1", "2"])],
        ),
        Field(
            item="9",
            name="encryption",
            friendly_name="encryption",
            type="string",
            startIndex=21,
            endIndex=22,
            required=False,
            validators=[validators.oneOf([" ", "E"])],
        ),
        Field(
            item="10",
            name="update",
            friendly_name="update",
            type="string",
            startIndex=22,
            endIndex=23,
            required=True,
            validators=[validators.oneOf(["N", "D", "U"])],
        ),
    ],
)
