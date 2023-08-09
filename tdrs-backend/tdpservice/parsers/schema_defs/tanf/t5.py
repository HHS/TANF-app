"""Schema for HEADER row of all submission types."""


from ...util import SchemaManager
from ...fields import EncryptedField, Field, tanf_ssn_decryption_func
from ...row_schema import RowSchema
from ... import validators
from tdpservice.search_indexes.models.tanf import TANF_T5


t5 = SchemaManager(
      schemas=[
        RowSchema(
          model=TANF_T5,
          preparsing_validators=[
              validators.hasLength(71),
          ],
          postparsing_validators=[],
          fields=[
              Field(item="0", name='RecordType', type='string', startIndex=0, endIndex=2,
                    required=True, validators=[]),
              Field(item="4", name='RPT_MONTH_YEAR', type='number', startIndex=2, endIndex=8,
                    required=True, validators=[]),
              Field(item="6", name='CASE_NUMBER', type='string', startIndex=8, endIndex=19,
                    required=True, validators=[]),
              Field(item="14", name='FAMILY_AFFILIATION', type='number', startIndex=19, endIndex=20,
                    required=True, validators=[]),
              Field(item="15", name='DATE_OF_BIRTH', type='number', startIndex=20, endIndex=28,
                    required=True, validators=[]),
              EncryptedField(decryption_func=tanf_ssn_decryption_func, item="16", name='SSN', type='string',
                             startIndex=28, endIndex=37, required=True, validators=[]),
              Field(item="17A", name='RACE_HISPANIC', type='number', startIndex=37, endIndex=38,
                    required=True, validators=[]),
              Field(item="17B", name='RACE_AMER_INDIAN', type='number', startIndex=38, endIndex=39,
                    required=True, validators=[]),
              Field(item="17C", name='RACE_ASIAN', type='number', startIndex=39, endIndex=40,
                    required=True, validators=[]),
              Field(item="17D", name='RACE_BLACK', type='number', startIndex=40, endIndex=41,
                    required=True, validators=[]),
              Field(item="17E", name='RACE_HAWAIIAN', type='number', startIndex=41, endIndex=42,
                    required=True, validators=[]),
              Field(item="17F", name='RACE_WHITE', type='number', startIndex=42, endIndex=43,
                    required=True, validators=[]),
              Field(item="18", name='GENDER', type='number', startIndex=43, endIndex=44,
                    required=True, validators=[]),
              Field(item="19A", name='REC_OASDI_INSURANCE', type='number', startIndex=44, endIndex=45,
                    required=True, validators=[]),
              Field(item="19B", name='REC_FEDERAL_DISABILITY', type='number', startIndex=45, endIndex=46,
                    required=True, validators=[]),
              Field(item="19C", name='REC_AID_TOTALLY_DISABLED', type='number', startIndex=46, endIndex=47,
                    required=True, validators=[]),
              Field(item="19D", name='REC_AID_AGED_BLIND', type='number', startIndex=47, endIndex=48,
                    required=True, validators=[]),
              Field(item="19E", name='REC_SSI', type='number', startIndex=48, endIndex=49,
                    required=True, validators=[]),
              Field(item="20", name='MARITAL_STATUS', type='number', startIndex=49, endIndex=50,
                    required=True, validators=[]),
              Field(item="21", name='RELATIONSHIP_HOH', type='string', startIndex=50, endIndex=52,
                    required=True, validators=[]),
              Field(item="22", name='PARENT_MINOR_CHILD', type='number', startIndex=52, endIndex=53,
                    required=True, validators=[]),
              Field(item="23", name='NEEDS_OF_PREGNANT_WOMAN', type='number', startIndex=53, endIndex=54,
                    required=True, validators=[]),
              Field(item="24", name='EDUCATION_LEVEL', type='string', startIndex=54, endIndex=56,
                    required=True, validators=[]),
              Field(item="25", name='CITIZENSHIP_STATUS', type='number', startIndex=56, endIndex=57,
                    required=True, validators=[]),
              Field(item="26", name='COUNTABLE_MONTH_FED_TIME', type='string', startIndex=57, endIndex=60,
                    required=True, validators=[]),
              Field(item="27", name='COUNTABLE_MONTHS_STATE_TRIBE', type='string', startIndex=60, endIndex=62,
                    required=True, validators=[]),
              Field(item="28", name='EMPLOYMENT_STATUS', type='number', startIndex=62, endIndex=63,
                    required=True, validators=[]),
              Field(item="29", name='AMOUNT_EARNED_INCOME', type='string', startIndex=63, endIndex=67,
                    required=True, validators=[]),
              Field(item="30", name='AMOUNT_UNEARNED_INCOME', type='string', startIndex=67, endIndex=71,
                    required=True, validators=[]),
          ],
        )
      ]
)
