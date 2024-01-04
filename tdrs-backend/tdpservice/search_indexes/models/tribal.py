"""Models representing parsed TRIBAL data file records submitted to TDP."""

import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import ParserError


class Tribal_TANF_T1(models.Model):
    """
    Parsed record representing a T1 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='tribal_t1_parent'
    )

    error = GenericRelation(ParserError)
    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    COUNTY_FIPS_CODE = models.CharField(
        max_length=3,
        null=True,
        blank=False
    )
    STRATUM = models.CharField(max_length=2, null=True, blank=False)
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


class Tribal_TANF_T2(models.Model):
    """
    Parsed record representing a T2 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='tribal_t2_parent'
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)

    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)
    NONCUSTODIAL_PARENT = models.IntegerField(null=True, blank=False)
    DATE_OF_BIRTH = models.IntegerField(null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    RACE_HISPANIC = models.IntegerField(null=True, blank=False)
    RACE_AMER_INDIAN = models.IntegerField(null=True, blank=False)
    RACE_ASIAN = models.IntegerField(null=True, blank=False)
    RACE_BLACK = models.IntegerField(null=True, blank=False)
    RACE_HAWAIIAN = models.IntegerField(null=True, blank=False)
    RACE_WHITE = models.IntegerField(null=True, blank=False)
    GENDER = models.IntegerField(null=True, blank=False)
    FED_OASDI_PROGRAM = models.IntegerField(null=True, blank=False)
    FED_DISABILITY_STATUS = models.IntegerField(null=True, blank=False)
    DISABLED_TITLE_XIVAPDT = models.IntegerField(null=True, blank=False)
    AID_AGED_BLIND = models.IntegerField(null=True, blank=False)
    RECEIVE_SSI = models.IntegerField(null=True, blank=False)
    MARITAL_STATUS = models.IntegerField(null=True, blank=False)
    RELATIONSHIP_HOH = models.CharField(max_length=2, null=True, blank=False)
    PARENT_MINOR_CHILD = models.IntegerField(null=True, blank=False)
    NEEDS_PREGNANT_WOMAN = models.IntegerField(null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(max_length=2, null=True, blank=False)
    CITIZENSHIP_STATUS = models.IntegerField(null=True, blank=False)
    COOPERATION_CHILD_SUPPORT = models.IntegerField(null=True, blank=False)
    MONTHS_FED_TIME_LIMIT = models.CharField(max_length=3, null=True, blank=False)
    MONTHS_STATE_TIME_LIMIT = models.CharField(max_length=2, null=True, blank=False)
    CURRENT_MONTH_STATE_EXEMPT = models.IntegerField(null=True, blank=False)
    EMPLOYMENT_STATUS = models.IntegerField(null=True, blank=False)
    WORK_PART_STATUS = models.CharField(max_length=2, null=True, blank=False)
    UNSUB_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    SUB_PRIVATE_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    SUB_PUBLIC_EMPLOYMENT = models.CharField(max_length=2, null=True, blank=False)
    WORK_EXPERIENCE = models.CharField(max_length=2, null=True, blank=False)
    OJT = models.CharField(max_length=2, null=True, blank=False)
    JOB_SEARCH = models.CharField(max_length=2, null=True, blank=False)
    COMM_SERVICES = models.CharField(max_length=2, null=True, blank=False)
    VOCATIONAL_ED_TRAINING = models.CharField(max_length=2, null=True, blank=False)
    JOB_SKILLS_TRAINING = models.CharField(max_length=2, null=True, blank=False)
    ED_NO_HIGH_SCHOOL_DIPLOMA = models.CharField(max_length=2, null=True, blank=False)
    SCHOOL_ATTENDENCE = models.CharField(max_length=2, null=True, blank=False)
    PROVIDE_CC = models.CharField(max_length=2, null=True, blank=False)
    ADD_WORK_ACTIVITIES = models.CharField(max_length=2, null=True, blank=False)
    OTHER_WORK_ACTIVITIES = models.CharField(max_length=2, null=True, blank=False)
    REQ_HRS_WAIVER_DEMO = models.CharField(max_length=2, null=True, blank=False)
    EARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_INCOME_TAX_CREDIT = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_SOCIAL_SECURITY = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_SSI = models.CharField(max_length=4, null=True, blank=False)
    UNEARNED_WORKERS_COMP = models.CharField(max_length=4, null=True, blank=False)
    OTHER_UNEARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)


class Tribal_TANF_T3(models.Model):
    """
    Parsed record representing a T3 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='tribal_t3_parent'
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)

    DATE_OF_BIRTH = models.IntegerField(null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    RACE_HISPANIC = models.IntegerField(null=True, blank=False)
    RACE_AMER_INDIAN = models.IntegerField(null=True, blank=False)
    RACE_ASIAN = models.IntegerField(null=True, blank=False)
    RACE_BLACK = models.IntegerField(null=True, blank=False)
    RACE_HAWAIIAN = models.IntegerField(null=True, blank=False)
    RACE_WHITE = models.IntegerField(null=True, blank=False)
    GENDER = models.IntegerField(null=True, blank=False)
    RECEIVE_NONSSA_BENEFITS = models.IntegerField(null=True, blank=False)
    RECEIVE_SSI = models.IntegerField(null=True, blank=False)
    RELATIONSHIP_HOH = models.CharField(max_length=2, null=True, blank=False)
    PARENT_MINOR_CHILD = models.IntegerField(null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(max_length=2, null=True, blank=False)
    CITIZENSHIP_STATUS = models.IntegerField(null=True, blank=False)
    UNEARNED_SSI = models.CharField(max_length=4, null=True, blank=False)
    OTHER_UNEARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)
