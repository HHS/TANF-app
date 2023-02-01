"""Houses definitions for TANF datafile schemas."""

from ..util import RowSchema

def t1_schema():
    """Return a RowSchema for T1 records.

                    FAMILY CASE CHARACTERISTIC DATA

    DESCRIPTION         LENGTH  FROM    TO  COMMENTS
    RECORD TYPE         2       1       2   "T1" - SECTION 1
    REPORTING MONTH     6       3       8   Numeric
    CASE NUMBER         11      9       19  Alphanumeric
    COUNTY FIPS CODE    3       20      22  Numeric
    STRATUM             2       23      24  Numeric
    ZIP CODE            5       25      29  Alphanumeric
    FUNDING STREAM      1       30      30  Numeric
    DISPOSITION         1       31      31  Numeric
    NEW APPLICANT       1       32      32  Numeric
    FAMILY MEMBERS      2       33      34  Numeric
    TYPE OF FAMILY      1       35      35  Numeric
    SUBSIDIZED HOUSING  1       36      36  Numeric
    MEDICAL ASSISTANCE  1       37      37  Numeric
    FOOD STAMPS         1       38      38  Numeric
    FOOD STAMP AMOUNT   4       39      42  Numeric
    SUB CHILD CARE      1       43      43  Numeric
    AMT CHILD CARE      4       44      47  Numeric
    AMT CHIILD SUPPORT  4       48      51  Numeric
    FAMILY'S CASH       4       52      55  Numeric
    CASH
    AMOUNT              4       56      59  Numeric
    NBR_MONTH           3       60      62  Numeric
    TANF CHILD CARE
    AMOUNT              4       63      66  Numeric
    CHILDREN_COVERED    2       67      68  Numeric
    NBR_MONTHS          3       69      71  Numeric
    TRANSPORTATION
    AMOUNT              4       72      75  Numeric
    NBR_MONTHS          3       76      78  Numeric
    TRANSITIONAL SERVICES
    AMOUNT              4       79      82  Numeric
    NBR_MONTHS          3       83      85  Numeric
    OTHER
    AMOUNT              4       86      89  Numeric
    NBR_MONTHS          3       90      92  Numeric
    REASON FOR & AMOUNT OF ASSISTANCE
    REDUCTION
    SANCTIONS AMT       4       93      96  Numeric
    WORK REQ            1       97      97  Alphanumeric
    NO DIPLOMA          1       98      98  Alphanumeric
    NOT IN SCHOOL       1       99      99  Alphanumeric
    NOT CHILD SUPPORT   1       100     100 Alphanumeric
    IRP FAILURE         1       101     101 Alphanumeric
    OTHER SANCTION      1       102     102 Alphanumeric
    PRIOR OVERPAYMENT   4       103     106 Alphanumeric
    TOTAL REDUC AMOUNT  4       107     110 Alphanumeric
    FAMILY CAP          1       111     111 Alphanumeric
    LENGTH OF ASSIST    1       112     112 Alphanumeric
    OTHER, NON-SANCTION 1       113     113 Alphanumeric
    WAIVER_CONTROL_GRPS 1       114     114 Alphanumeric
    TANF FAMILY
    EXEMPT TIME_LIMITS  2       115     116 Numeric
    CHILD ONLY FAMILY   1       117     117 Numeric
    BLANK               39      118     156 Spaces
    """
    family_case_schema = RowSchema()
    family_case_schema.add_fields(
        [  # does it make sense to try to include regex (e.g., =r'^T1$')
            ('RecordType', 2, 1, 2, "Alphanumeric"),
            ('RPT_MONTH_YEAR', 6, 3, 8, "Numeric"),
            ('CASE_NUMBER', 11, 9, 19, "Alphanumeric"),
            ('COUNTY_FIPS_CODE', 3, 20, 22, "Numeric"),
            ('STRATUM', 2, 23, 24, "Numeric"),
            ('ZIP_CODE', 5, 25, 29, "Alphanumeric"),
            ('FUNDING_STREAM', 1, 30, 30, "Numeric"),
            ('DISPOSITION', 1, 31, 31, "Numeric"),
            ('NEW_APPLICANT', 1, 32, 32, "Numeric"),
            ('NBR_FAMILY_MEMBERS', 2, 33, 34, "Numeric"),
            ('FAMILY_TYPE', 1, 35, 35, "Numeric"),
            ('RECEIVES_SUB_HOUSING', 1, 36, 36, "Numeric"),
            ('RECEIVES_MED_ASSISTANCE', 1, 37, 37, "Numeric"),
            ('RECEIVES_FOOD_STAMPS', 1, 38, 38, "Numeric"),
            ('AMT_FOOD_STAMP_ASSISTANCE', 4, 39, 42, "Numeric"),
            ('RECEIVES_SUB_CC', 1, 43, 43, "Numeric"),
            ('AMT_SUB_CC', 4, 44, 47, "Numeric"),
            ('CHILD_SUPPORT_AMT', 4, 48, 51, "Numeric"),
            ('FAMILY_CASH_RESOURCES', 4, 52, 55, "Numeric"),
            ('CASH_AMOUNT', 4, 56, 59, "Numeric"),
            ('NBR_MONTHS', 3, 60, 62, "Numeric"),
            ('CC_AMOUNT', 4, 63, 66, "Numeric"),
            ('CHILDREN_COVERED', 2, 67, 68, "Numeric"),
            ('CC_NBR_MONTHS', 3, 69, 71, "Numeric"),
            ('TRANSP_AMOUNT', 4, 72, 75, "Numeric"),
            ('TRANSP_NBR_MONTHS', 3, 76, 78, "Numeric"),
            ('TRANSITION_SERVICES_AMOUNT', 4, 79, 82, "Numeric"),
            ('TRANSITION_NBR_MONTHS', 3, 83, 85, "Numeric"),
            ('OTHER_AMOUNT', 4, 86, 89, "Numeric"),
            ('OTHER_NBR_MONTHS', 3, 90, 92, "Numeric"),
            ('SANC_REDUCTION_AMT', 4, 93, 96, "Numeric"),
            ('WORK_REQ_SANCTION', 1, 97, 97, "Numeric"),
            ('FAMILY_SANC_ADULT', 1, 98, 98, "Numeric"),
            ('SANC_TEEN_PARENT', 1, 99, 99, "Numeric"),
            ('NON_COOPERATION_CSE', 1, 100, 100, "Numeric"),
            ('FAILURE_TO_COMPLY', 1, 101, 101, "Numeric"),
            ('OTHER_SANCTION', 1, 102, 102, "Numeric"),
            ('RECOUPMENT_PRIOR_OVRPMT', 4, 103, 106, "Numeric"),
            ('OTHER_TOTAL_REDUCTIONS', 4, 107, 110, "Numeric"),
            ('FAMILY_CAP', 1, 111, 111, "Numeric"),
            ('REDUCTIONS_ON_RECEIPTS', 1, 112, 112, "Numeric"),
            ('OTHER_NON_SANCTION', 1, 113, 113, "Numeric"),
            ('WAIVER_EVAL_CONTROL_GRPS', 1, 114, 114, "Numeric"),
            ('FAMILY_EXEMPT_TIME_LIMITS', 2, 115, 116, "Numeric"),
            ('FAMILY_NEW_CHILD', 1, 117, 117, "Numeric"),
            ('BLANK', 39, 118, 156, "Spaces"),
        ]
    )
    return family_case_schema
