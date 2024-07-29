"""Schema for TRAILER row of all submission types."""


from ..fields import Field
from ..row_schema import RowSchema
from tdpservice.parsers.validators.category1 import PreparsingValidators
from tdpservice.parsers.validators.category2 import FieldValidators
from tdpservice.parsers.validators.category3 import ComposableValidators


trailer = RowSchema(
    record_type="TRAILER",
    document=None,
    preparsing_validators=[
        PreparsingValidators.recordHasLength(23),
        PreparsingValidators.recordStartsWith("TRAILER",
                              lambda value: f"Your file does not end with a {value} record."),
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
                FieldValidators.isEqual('TRAILER')
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
                FieldValidators.isBetween(0, 9999999, inclusive=True, cast=int) # fix
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
                FieldValidators.isEqual('         ')
            ]
        ),
    ],
)
