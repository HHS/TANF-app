"""Factories for generating test data for parsers."""
import factory
from faker import Faker
from tdpservice.data_files.test.factories import DataFileFactory

fake = Faker()

class ParserErrorFactory(factory.django.DjangoModelFactory):
    """Generate test data for parser errors."""

    class Meta:
        """Hardcoded meta data for parser errors."""

        model = "parsers.ParserError"

    file = factory.SubFactory(DataFileFactory)
    row_number = 1
    column_number = "1"
    item_number = "1"
    field_name = "test field name"
    case_number = '1'
    rpt_month_year = 202001
    error_message = "test error message"
    error_type = "out of range"

    created_at = factory.Faker("date_time")
    fields_json = {"test": "test"}

    object_id = 1
    content_type_id = 1

class TanfT1Factory(factory.django.DjangoModelFactory):
    """Generate TANF T1 record for testing."""

    class Meta:
        """Hardcoded meta data for TANF_T1."""

        model = "search_indexes.TANF_T1"

    RecordType = fake.uuid4()
    RPT_MONTH_YEAR = 1
    CASE_NUMBER = "1"
    COUNTY_FIPS_CODE = 1
    STRATUM = "1"
    ZIP_CODE = "00001"
    FUNDING_STREAM = 1
    DISPOSITION = 1
    NEW_APPLICANT = 1
    NBR_FAMILY_MEMBERS = 1
    FAMILY_TYPE = 1
    RECEIVES_SUB_HOUSING = 1
    RECEIVES_MED_ASSISTANCE = 1
    RECEIVES_FOOD_STAMPS = 1
    AMT_FOOD_STAMP_ASSISTANCE = 1
    RECEIVES_SUB_CC = 1
    AMT_SUB_CC = 1
    CHILD_SUPPORT_AMT = 1
    FAMILY_CASH_RESOURCES = 1
    CASH_AMOUNT = 1
    NBR_MONTHS = 1
    CC_AMOUNT = 1
    CHILDREN_COVERED = 1
    CC_NBR_MONTHS = 1
    TRANSP_AMOUNT = 1
    TRANSP_NBR_MONTHS = 1
    TRANSITION_SERVICES_AMOUNT = 1
    TRANSITION_NBR_MONTHS = 1
    OTHER_AMOUNT = 1
    OTHER_NBR_MONTHS = 1
    SANC_REDUCTION_AMT = 1
    WORK_REQ_SANCTION = 1
    FAMILY_SANC_ADULT = 1
    SANC_TEEN_PARENT = 1
    NON_COOPERATION_CSE = 1
    FAILURE_TO_COMPLY = 1
    OTHER_SANCTION = 1
    RECOUPMENT_PRIOR_OVRPMT = 1
    OTHER_TOTAL_REDUCTIONS = 1
    FAMILY_CAP = 1
    REDUCTIONS_ON_RECEIPTS = 1
    OTHER_NON_SANCTION = 1
    WAIVER_EVAL_CONTROL_GRPS = 1
    FAMILY_EXEMPT_TIME_LIMITS = 1
    FAMILY_NEW_CHILD = 1


class TanfT2Factory(factory.django.DjangoModelFactory):
    """Generate TANF T2 record for testing."""

    class Meta:
        """Hardcoded meta data for TANF_T2."""

        model = "search_indexes.TANF_T2"

    RecordType = fake.uuid4()
    RPT_MONTH_YEAR = 1
    CASE_NUMBER = '1'
    FAMILY_AFFILIATION = 1
    NONCUSTODIAL_PARENT = 1
    DATE_OF_BIRTH = 1
    SSN = '1'
    RACE_HISPANIC = 1
    RACE_AMER_INDIAN = 1
    RACE_ASIAN = 1
    RACE_BLACK = 1
    RACE_HAWAIIAN = 1
    RACE_WHITE = 1
    GENDER = 1
    FED_OASDI_PROGRAM = 1
    FED_DISABILITY_STATUS = 1
    DISABLED_TITLE_XIVAPDT = 1
    AID_AGED_BLIND = 1
    RECEIVE_SSI = 1
    MARITAL_STATUS = 1
    RELATIONSHIP_HOH = "01"
    PARENT_WITH_MINOR_CHILD = 1
    NEEDS_PREGNANT_WOMAN = 1
    EDUCATION_LEVEL = "01"
    CITIZENSHIP_STATUS = 1
    COOPERATION_CHILD_SUPPORT = "1"
    MONTHS_FED_TIME_LIMIT = "002"
    MONTHS_STATE_TIME_LIMIT = "02"
    CURRENT_MONTH_STATE_EXEMPT = 1
    EMPLOYMENT_STATUS = 1
    WORK_ELIGIBLE_INDICATOR = "01"
    WORK_PART_STATUS = "01"
    UNSUB_EMPLOYMENT = 1
    SUB_PRIVATE_EMPLOYMENT = 1
    SUB_PUBLIC_EMPLOYMENT = 1
    WORK_EXPERIENCE_HOP = 1
    WORK_EXPERIENCE_EA = 1
    WORK_EXPERIENCE_HOL = 1
    OJT = 1
    JOB_SEARCH_HOP = 1
    JOB_SEARCH_EA = 1
    JOB_SEARCH_HOL = 1
    COMM_SERVICES_HOP = 1
    COMM_SERVICES_EA = 1
    COMM_SERVICES_HOL = 1
    VOCATIONAL_ED_TRAINING_HOP = 1
    VOCATIONAL_ED_TRAINING_EA = 1
    VOCATIONAL_ED_TRAINING_HOL = 1
    JOB_SKILLS_TRAINING_HOP = 1
    JOB_SKILLS_TRAINING_EA = 1
    JOB_SKILLS_TRAINING_HOL = 1
    ED_NO_HIGH_SCHOOL_DIPL_HOP = 1
    ED_NO_HIGH_SCHOOL_DIPL_EA = 1
    ED_NO_HIGH_SCHOOL_DIPL_HOL = 1
    SCHOOL_ATTENDENCE_HOP = 1
    SCHOOL_ATTENDENCE_EA = 1
    SCHOOL_ATTENDENCE_HOL = 1
    PROVIDE_CC_HOP = 1
    PROVIDE_CC_EA = 1
    PROVIDE_CC_HOL = 1
    OTHER_WORK_ACTIVITIES = 1
    DEEMED_HOURS_FOR_OVERALL = 1
    DEEMED_HOURS_FOR_TWO_PARENT = 1
    EARNED_INCOME = 1
    UNEARNED_INCOME_TAX_CREDIT = 1
    UNEARNED_SOCIAL_SECURITY = 1
    UNEARNED_SSI = 1
    UNEARNED_WORKERS_COMP = 1
    OTHER_UNEARNED_INCOME = 1


class TanfT3Factory(factory.django.DjangoModelFactory):
    """Generate TANF T3 record for testing."""

    class Meta:
        """Hardcoded meta data for TANF_T3."""

        model = "search_indexes.TANF_T3"

    RecordType = fake.uuid4()
    RPT_MONTH_YEAR = 1
    CASE_NUMBER = '1'

    FAMILY_AFFILIATION = 1
    DATE_OF_BIRTH = 1
    SSN = '1'
    RACE_HISPANIC = 1
    RACE_AMER_INDIAN = 1
    RACE_ASIAN = 1
    RACE_BLACK = 1
    RACE_HAWAIIAN = 1
    RACE_WHITE = 1
    GENDER = 1
    RECEIVE_NONSSA_BENEFITS = 1
    RECEIVE_SSI = 1
    RELATIONSHIP_HOH = "01"
    PARENT_MINOR_CHILD = 1
    EDUCATION_LEVEL = 1
    CITIZENSHIP_STATUS = 1
    UNEARNED_SSI = 1
    OTHER_UNEARNED_INCOME = 1
