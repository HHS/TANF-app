"""Schema for HEADER row of all submission types."""


from ..util import RowSchema, Field
from .. import validators


header = RowSchema(
    model=dict,
    preparsing_validators=[
        validators.hasLength(23),
        validators.startsWith('HEADER'),
    ],
    postparsing_validators=[],
    fields=[
        Field(name='title', type='string', startIndex=0, endIndex=6, required=True, validators=[
            validators.matches('HEADER'),
        ]),
        Field(name='year', type='number', startIndex=6, endIndex=10, required=True, validators=[
            validators.between(2000, 2099)
        ]),
        Field(name='quarter', type='string', startIndex=10, endIndex=11, required=True, validators=[
            validators.oneOf(['1', '2', '3', '4'])
        ]),
        Field(name='type', type='string', startIndex=11, endIndex=12, required=True, validators=[
            validators.oneOf(['A', 'C', 'G', 'S'])
        ]),
        Field(name='state_fips', type='string', startIndex=12, endIndex=14, required=True, validators=[
            validators.between(0, 99)
        ]),
        Field(name='tribe_code', type='string', startIndex=14, endIndex=17, required=False, validators=[
            validators.between(0, 999)
        ]),
        Field(name='program_type', type='string', startIndex=17, endIndex=20, required=True, validators=[
            validators.oneOf(['TAN', 'SSP'])
        ]),
        Field(name='edit', type='string', startIndex=20, endIndex=21, required=True, validators=[
            validators.oneOf(['1', '2'])
        ]),
        Field(name='encryption', type='string', startIndex=21, endIndex=22, required=False, validators=[
            validators.matches('E')
        ]),
        Field(name='update', type='string', startIndex=22, endIndex=23, required=True, validators=[
            validators.oneOf(['N', 'D', 'U'])
        ]),
    ],
)
