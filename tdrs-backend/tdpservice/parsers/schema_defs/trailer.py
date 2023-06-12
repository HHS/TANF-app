"""Schema for TRAILER row of all submission types."""


from ..util import RowSchema, Field
from .. import validators


trailer = RowSchema(
    model=dict,
    preparsing_validators=[
        # validators.hasLength(23),
        validators.hasLength(
            23,
            lambda value, length: f'Trailer length is {len(value)} but must be {length} characters.'
        ),
        validators.startsWith('TRAILER')
    ],
    postparsing_validators=[],
    fields=[
        Field(item=1, name='title', type='string', startIndex=0, endIndex=7, required=True, validators=[
            validators.matches('TRAILER')
        ]),
        Field(item=2, name='record_count', type='number', startIndex=7, endIndex=14, required=True, validators=[
            validators.between(0, 9999999)
        ]),
        Field(item=3, name='blank', type='string', startIndex=14, endIndex=23, required=False, validators=[
            validators.matches('         ')
        ]),
    ],
)
