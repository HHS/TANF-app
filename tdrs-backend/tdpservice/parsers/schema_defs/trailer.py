"""Schema for TRAILER row of all submission types."""


from ..util import RowSchema, Field
from .. import validators


trailer = RowSchema(
    model=dict,
    preparsing_validators=[
        validators.hasLength(23),
        validators.contains('TRAILER')
    ],
    postparsing_validators=[],
    fields=[
        Field(name='title', type='string', startIndex=0, endIndex=7, required=True, validators=[
            validators.matches('TRAILER')
        ]),
        Field(name='record_cound', type='number', startIndex=7, endIndex=14, required=True, validators=[
            validators.between(0, 9999999)
        ]),
        Field(name='blank', type='string', startIndex=14, endIndex=23, required=True, validators=[
            validators.matches('         ')
        ]),
    ],
)
