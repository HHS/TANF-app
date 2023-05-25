"""Models representing parsed TANF data file records submitted to TDP."""

from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from tdpservice.parsers.models import ParserError


class TANF_T1(models.Model):
    """
    Parsed record representing a T1 data submission.

    Mapped to an elastic search index.
    """

    # def __is_valid__():
    # TODO: might need a correlating validator to check across fields

    error = GenericRelation(ParserError)
    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FIPS_CODE = models.CharField(max_length=2, null=True, blank=False)
    COUNTY_FIPS_CODE = models.CharField(
        max_length=3,
        null=True,
        blank=False
    )
    STRATUM = models.IntegerField(null=True, blank=False)
    ZIP_CODE = models.CharField(max_length=5, null=True, blank=False)
    FUNDING_STREAM = models.IntegerField(null=True, blank=False)
    DISPOSITION = models.IntegerField(null=True, blank=False)
    NEW_APPLICANT = models.IntegerField(null=True, blank=False)
    NBR_FAMILY_MEMBERS = models.IntegerField(null=True, blank=False)
    FAMILY_TYPE = models.IntegerField(null=True, blank=False)
    RECEIVES_SUB_HOUSING = models.IntegerField(null=True, blank=False)
    RECEIVES_MED_ASSISTANCE = models.IntegerField(null=True, blank=False)
    RECEIVES_FOOD_STAMPS = models.IntegerField(null=True, blank=False)
    AMT_FOOD_STAMP_ASSISTANCE = models.IntegerField(null=True, blank=False)
    RECEIVES_SUB_CC = models.IntegerField(null=True, blank=False)
    AMT_SUB_CC = models.IntegerField(null=True, blank=False)
    CHILD_SUPPORT_AMT = models.IntegerField(null=True, blank=False)
    FAMILY_CASH_RESOURCES = models.IntegerField(null=True, blank=False)
    CASH_AMOUNT = models.IntegerField(null=True, blank=False)
    NBR_MONTHS = models.IntegerField(null=True, blank=False)
    CC_AMOUNT = models.IntegerField(null=True, blank=False)
    CHILDREN_COVERED = models.IntegerField(null=True, blank=False)
    CC_NBR_MONTHS = models.IntegerField(null=True, blank=False)
    TRANSP_AMOUNT = models.IntegerField(null=True, blank=False)
    TRANSP_NBR_MONTHS = models.IntegerField(null=True, blank=False)
    TRANSITION_SERVICES_AMOUNT = models.IntegerField(null=True, blank=False)
    TRANSITION_NBR_MONTHS = models.IntegerField(null=True, blank=False)
    OTHER_AMOUNT = models.IntegerField(null=True, blank=False)
    OTHER_NBR_MONTHS = models.IntegerField(null=True, blank=False)
    SANC_REDUCTION_AMT = models.IntegerField(null=True, blank=False)
    WORK_REQ_SANCTION = models.IntegerField(null=True, blank=False)
    FAMILY_SANC_ADULT = models.IntegerField(null=True, blank=False)
    SANC_TEEN_PARENT = models.IntegerField(null=True, blank=False)
    NON_COOPERATION_CSE = models.IntegerField(null=True, blank=False)
    FAILURE_TO_COMPLY = models.IntegerField(null=True, blank=False)
    OTHER_SANCTION = models.IntegerField(null=True, blank=False)
    RECOUPMENT_PRIOR_OVRPMT = models.IntegerField(null=True, blank=False)
    OTHER_TOTAL_REDUCTIONS = models.IntegerField(null=True, blank=False)
    FAMILY_CAP = models.IntegerField(null=True, blank=False)
    REDUCTIONS_ON_RECEIPTS = models.IntegerField(null=True, blank=False)
    OTHER_NON_SANCTION = models.IntegerField(null=True, blank=False)
    WAIVER_EVAL_CONTROL_GRPS = models.IntegerField(null=True, blank=False)
    FAMILY_EXEMPT_TIME_LIMITS = models.IntegerField(null=True, blank=False)
    FAMILY_NEW_CHILD = models.IntegerField(null=True, blank=False)


class TANF_T2(models.Model):
    """
    Parsed record representing a T2 data submission.

    Mapped to an elastic search index.
    """

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)

    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)
    NONCUSTODIAL_PARENT = models.IntegerField(null=True, blank=False)
    DATE_OF_BIRTH = models.IntegerField(null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    RACE_HISPANIC = models.CharField(max_length=1, null=True, blank=False)
    RACE_AMER_INDIAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_ASIAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_BLACK = models.CharField(max_length=1, null=True, blank=False)
    RACE_HAWAIIAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_WHITE = models.CharField(max_length=1, null=True, blank=False)
    GENDER = models.IntegerField(null=True, blank=False)
    FED_OASDI_PROGRAM = models.CharField(max_length=1, null=True, blank=False)
    FED_DISABILITY_STATUS = models.CharField(max_length=1, null=True, blank=False)
    DISABLED_TITLE_XIVAPDT = models.CharField(max_length=1, null=True, blank=False)
    AID_AGED_BLIND = models.CharField(max_length=1, null=True, blank=False)
    RECEIVE_SSI = models.CharField(max_length=1, null=True, blank=False)
    MARITAL_STATUS = models.CharField(max_length=1, null=True, blank=False)
    RELATIONSHIP_HOH = models.IntegerField(null=True, blank=False)
    PARENT_WITH_MINOR_CHILD = models.CharField(max_length=1, null=True, blank=False)
    NEEDS_PREGNANT_WOMAN = models.CharField(max_length=1, null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(max_length=2, null=True, blank=False)
    CITIZENSHIP_STATUS = models.CharField(max_length=1, null=True, blank=False)
    COOPERATION_CHILD_SUPPORT = models.CharField(max_length=1, null=True, blank=False)
    MONTHS_FED_TIME_LIMIT = models.CharField(max_length=3, null=True, blank=False)
    MONTHS_STATE_TIME_LIMIT = models.CharField(max_length=2, null=True, blank=False)
    CURRENT_MONTH_STATE_EXEMPT = models.CharField(max_length=1, null=True, blank=False)
    EMPLOYMENT_STATUS = models.CharField(max_length=1, null=True, blank=False)
    WORK_ELIGIBLE_INDICATOR = models.CharField(max_length=2, null=True, blank=False)
    WORK_PART_STATUS = models.CharField(max_length=2, null=True, blank=False)
    UNSUB_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    SUB_PRIVATE_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    SUB_PUBLIC_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    WORK_EXPERIENCE_HOP = models.CharField(max_length=2, null=True, blank=False)
    WORK_EXPERIENCE_EA = models.CharField(max_length=2, null=True, blank=False)
    WORK_EXPERIENCE_HOL = models.CharField(max_length=2, null=True, blank=False)
    OJT = models.CharField(max_length=2, null=True, blank=False)
    JOB_SEARCH_HOP = models.CharField(max_length=2, null=True, blank=False)
    JOB_SEARCH_EA = models.CharField(max_length=2, null=True, blank=False)
    JOB_SEARCH_HOL = models.CharField(max_length=2, null=True, blank=False)
    COMM_SERVICES_HOP = models.CharField(max_length=2, null=True, blank=False)
    COMM_SERVICES_EA = models.CharField(max_length=2, null=True, blank=False)
    COMM_SERVICES_HOL = models.CharField(max_length=2, null=True, blank=False)
    VOCATIONAL_ED_TRAINING_HOP = models.CharField(max_length=2, null=True, blank=False)
    VOCATIONAL_ED_TRAINING_EA = models.CharField(max_length=2, null=True, blank=False)
    VOCATIONAL_ED_TRAINING_HOL = models.CharField(max_length=2, null=True, blank=False)
    JOB_SKILLS_TRAINING_HOP = models.CharField(max_length=2, null=True, blank=False)
    JOB_SKILLS_TRAINING_EA = models.CharField(max_length=2, null=True, blank=False)
    JOB_SKILLS_TRAINING_HOL = models.CharField(max_length=2, null=True, blank=False)
    ED_NO_HIGH_SCHOOL_DIPL_HOP = models.CharField(max_length=2, null=True, blank=False)
    ED_NO_HIGH_SCHOOL_DIPL_EA = models.CharField(max_length=2, null=True, blank=False)
    ED_NO_HIGH_SCHOOL_DIPL_HOL = models.CharField(max_length=2, null=True, blank=False)
    SCHOOL_ATTENDENCE_HOP = models.CharField(max_length=2, null=True, blank=False)
    SCHOOL_ATTENDENCE_EA = models.CharField(max_length=2, null=True, blank=False)
    SCHOOL_ATTENDENCE_HOL = models.CharField(max_length=2, null=True, blank=False)
    PROVIDE_CC_HOP = models.CharField(max_length=2, null=True, blank=False)
    PROVIDE_CC_EA = models.CharField(max_length=2, null=True, blank=False)
    PROVIDE_CC_HOL = models.CharField(max_length=2, null=True, blank=False)
    OTHER_WORK_ACTIVITIES = models.CharField(max_length=2, null=True, blank=False)
    DEEMED_HOURS_FOR_OVERALL = models.CharField(max_length=2, null=True, blank=False)
    DEEMED_HOURS_FOR_TWO_PARENT = models.CharField(max_length=2, null=True, blank=False)
    EARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_INCOME_TAX_CREDIT = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_SOCIAL_SECURITY = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_SSI = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_WORKERS_COMP = models.CharField(max_length=4, null=True, blank=False)
    OTHER_UNEARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)


class TANF_T3(models.Model):
    """
    Parsed record representing a T3 data submission.

    Mapped to an elastic search index.
    """

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)

    DATE_OF_BIRTH = models.IntegerField(null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    RACE_HISPANIC = models.CharField(max_length=1,  null=True, blank=False)
    RACE_AMER_INDIAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_ASIAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_BLACK = models.CharField(max_length=1, null=True, blank=False)
    RACE_HAWAIIAN = models.CharField(max_length=1, null=True, blank=False)
    RACE_WHITE = models.CharField(max_length=1, null=True, blank=False)
    GENDER = models.IntegerField(null=True, blank=False)
    RECEIVE_NONSSA_BENEFITS = models.CharField(max_length=1, null=True, blank=False)
    RECEIVE_SSI = models.CharField(max_length=1, null=True, blank=False)
    RELATIONSHIP_HOH = models.IntegerField(null=True, blank=False)
    PARENT_MINOR_CHILD = models.CharField(max_length=1, null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(max_length=2, null=True, blank=False)
    CITIZENSHIP_STATUS = models.CharField(max_length=1, null=True, blank=False)
    UNEARNED_SSI = models.CharField(max_length=4, null=True, blank=False)
    OTHER_UNEARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)


class TANF_T4(models.Model):
    """
    Parsed record representing a T4 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    case_number = models.CharField(max_length=11, null=False, blank=False)
    disposition = models.IntegerField(null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    county_fips_code = models.CharField(
        max_length=3,
        null=False,
        blank=False
    )
    stratum = models.IntegerField(null=False, blank=False)
    zip_code = models.CharField(max_length=5, null=False, blank=False)
    closure_reason = models.IntegerField(null=False, blank=False)
    rec_sub_housing = models.IntegerField(null=False, blank=False)
    rec_med_assist = models.IntegerField(null=False, blank=False)
    rec_food_stamps = models.IntegerField(null=False, blank=False)
    rec_sub_cc = models.IntegerField(null=False, blank=False)


class TANF_T5(models.Model):
    """
    Parsed record representing a T5 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    case_number = models.CharField(max_length=11, null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    family_affiliation = models.IntegerField(null=False, blank=False)
    date_of_birth = models.CharField(max_length=8, null=False, blank=False)
    ssn = models.CharField(max_length=9, null=False, blank=False)
    race_hispanic = models.IntegerField(null=False, blank=False)
    race_amer_indian = models.IntegerField(null=False, blank=False)
    race_asian = models.IntegerField(null=False, blank=False)
    race_black = models.IntegerField(null=False, blank=False)
    race_hawaiian = models.IntegerField(null=False, blank=False)
    race_white = models.IntegerField(null=False, blank=False)
    gender = models.IntegerField(null=False, blank=False)
    rec_oasdi_insurance = models.FloatField(null=False, blank=False)
    rec_federal_disability = models.IntegerField(null=False, blank=False)
    rec_aid_totally_disabled = models.FloatField(null=False, blank=False)
    rec_aid_aged_blind = models.FloatField(null=False, blank=False)
    rec_ssi = models.IntegerField(null=False, blank=False)
    marital_status = models.FloatField(null=False, blank=False)
    relationship_hoh = models.IntegerField(null=False, blank=False)
    parent_minor_child = models.IntegerField(null=False, blank=False)
    needs_of_pregnant_woman = models.IntegerField(null=False, blank=False)
    education_level = models.IntegerField(null=False, blank=False)
    citizenship_status = models.IntegerField(null=False, blank=False)
    countable_month_fed_time = models.FloatField(null=False, blank=False)
    countable_months_state_tribe = models.FloatField(null=False, blank=False)
    employment_status = models.FloatField(null=False, blank=False)
    amount_earned_income = models.IntegerField(null=False, blank=False)
    amount_unearned_income = models.IntegerField(null=False, blank=False)


class TANF_T6(models.Model):
    """
    Parsed record representing a T6 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    calendar_quarter = models.IntegerField(null=False, blank=False)
    applications = models.IntegerField(null=False, blank=False)
    approved = models.IntegerField(null=False, blank=False)
    denied = models.IntegerField(null=False, blank=False)
    assistance = models.IntegerField(null=False, blank=False)
    families = models.IntegerField(null=False, blank=False)
    num_2_parents = models.IntegerField(null=False, blank=False)
    num_1_parents = models.IntegerField(null=False, blank=False)
    num_no_parents = models.IntegerField(null=False, blank=False)
    recipients = models.IntegerField(null=False, blank=False)
    adult_recipients = models.IntegerField(null=False, blank=False)
    child_recipients = models.IntegerField(null=False, blank=False)
    noncustodials = models.IntegerField(null=False, blank=False)
    births = models.IntegerField(null=False, blank=False)
    outwedlock_births = models.IntegerField(null=False, blank=False)
    closed_cases = models.IntegerField(null=False, blank=False)


class TANF_T7(models.Model):
    """
    Parsed record representing a T7 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    calendar_quarter = models.IntegerField(null=False, blank=False)
    tdrs_section_ind = models.CharField(
        max_length=1,
        null=False,
        blank=False
    )
    stratum = models.CharField(max_length=2, null=False, blank=False)
    families = models.IntegerField(null=False, blank=False)
