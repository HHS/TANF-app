"""Schema for TRAILER row of all submission types."""


from ..fields import Field
from ..row_schema import RowSchema
from .. import validators


trailer = RowSchema(
    document=None,
    preparsing_validators=[
        validators.hasLength(
            23,
            lambda value, length: f"Trailer length is {len(value)} but must be {length} characters.",
        ),
        validators.startsWith("TRAILER",
                              lambda value: f"Your file does not end with a {value} record"),
    ],
    postparsing_validators=[],
    fields=[
        Field(
            item="1",
            name='title',
            friendly_name='title',
            type='string',
            startIndex=0,
            endIndex=7,
            required=True,
            validators=[
                validators.matches('TRAILER')
            ]
        ),
        Field(
            item="2",
            name='record_count',
            friendly_name='record count',
            type='number',
            startIndex=7,
            endIndex=14,
            required=True,
            validators=[
                validators.between(0, 9999999)
            ]
        ),
        Field(
            item="-1",
            name='blank',
            friendly_name='blank',
            type='string',
            startIndex=14,
            endIndex=23,
            required=False,
            validators=[
                validators.matches('         ')
            ]
        ),
    ],
)
