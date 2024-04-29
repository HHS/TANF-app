"""Models representing parsed SSP data file records submitted to TDP."""

import uuid
from django.db import models
from tdpservice.data_files.models import DataFile


class SSP_M1(models.Model):
    """
    Parsed record representing an SSP M1 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='m1_parent'
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FIPS_CODE = models.CharField(max_length=2, null=True, blank=False)
    COUNTY_FIPS_CODE = models.CharField(
        max_length=3,
        null=True,
        blank=False
    )
    STRATUM = models.CharField(max_length=2, null=True, blank=False)
    ZIP_CODE = models.CharField(max_length=5, null=True, blank=False)
    DISPOSITION = models.IntegerField(null=True, blank=False)
    NBR_FAMILY_MEMBERS = models.IntegerField(null=True, blank=False)
    FAMILY_TYPE = models.IntegerField(null=True, blank=False)
    TANF_ASST_IN_6MONTHS = models.IntegerField(null=True, blank=False)
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


class SSP_M2(models.Model):
    """
    Parsed record representing an SSP M2 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='m2_parent'
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FIPS_CODE = models.CharField(max_length=2, null=True, blank=False)

    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)
    NONCUSTODIAL_PARENT = models.IntegerField(null=True, blank=False)
    DATE_OF_BIRTH = models.CharField(max_length=8, null=True, blank=False)
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
    RELATIONSHIP_HOH = models.IntegerField(null=True, blank=False)
    PARENT_MINOR_CHILD = models.IntegerField(null=True, blank=False)
    NEEDS_PREGNANT_WOMAN = models.IntegerField(null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(null=True, blank=False)
    CITIZENSHIP_STATUS = models.IntegerField(null=True, blank=False)
    COOPERATION_CHILD_SUPPORT = models.IntegerField(null=True, blank=False)
    EMPLOYMENT_STATUS = models.IntegerField(null=True, blank=False)
    WORK_ELIGIBLE_INDICATOR = models.IntegerField(null=True, blank=False)
    WORK_PART_STATUS = models.IntegerField(null=True, blank=False)
    UNSUB_EMPLOYMENT = models.IntegerField(null=True, blank=False)
    SUB_PRIVATE_EMPLOYMENT = models.IntegerField(null=True, blank=False)
    SUB_PUBLIC_EMPLOYMENT = models.IntegerField(null=True, blank=False)
    WORK_EXPERIENCE_HOP = models.IntegerField(null=True, blank=False)
    WORK_EXPERIENCE_EA = models.IntegerField(null=True, blank=False)
    WORK_EXPERIENCE_HOL = models.IntegerField(null=True, blank=False)
    OJT = models.IntegerField(null=True, blank=False)
    JOB_SEARCH_HOP = models.IntegerField(null=True, blank=False)
    JOB_SEARCH_EA = models.IntegerField(null=True, blank=False)
    JOB_SEARCH_HOL = models.IntegerField(null=True, blank=False)
    COMM_SERVICES_HOP = models.IntegerField(null=True, blank=False)
    COMM_SERVICES_EA = models.IntegerField(null=True, blank=False)
    COMM_SERVICES_HOL = models.IntegerField(null=True, blank=False)
    VOCATIONAL_ED_TRAINING_HOP = models.IntegerField(null=True, blank=False)
    VOCATIONAL_ED_TRAINING_EA = models.IntegerField(null=True, blank=False)
    VOCATIONAL_ED_TRAINING_HOL = models.IntegerField(null=True, blank=False)
    JOB_SKILLS_TRAINING_HOP = models.IntegerField(null=True, blank=False)
    JOB_SKILLS_TRAINING_EA = models.IntegerField(null=True, blank=False)
    JOB_SKILLS_TRAINING_HOL = models.IntegerField(null=True, blank=False)
    ED_NO_HIGH_SCHOOL_DIPL_HOP = models.IntegerField(null=True, blank=False)
    ED_NO_HIGH_SCHOOL_DIPL_EA = models.IntegerField(null=True, blank=False)
    ED_NO_HIGH_SCHOOL_DIPL_HOL = models.IntegerField(null=True, blank=False)
    SCHOOL_ATTENDENCE_HOP = models.IntegerField(null=True, blank=False)
    SCHOOL_ATTENDENCE_EA = models.IntegerField(null=True, blank=False)
    SCHOOL_ATTENDENCE_HOL = models.IntegerField(null=True, blank=False)
    PROVIDE_CC_HOP = models.IntegerField(null=True, blank=False)
    PROVIDE_CC_EA = models.IntegerField(null=True, blank=False)
    PROVIDE_CC_HOL = models.IntegerField(null=True, blank=False)
    OTHER_WORK_ACTIVITIES = models.IntegerField(null=True, blank=False)
    DEEMED_HOURS_FOR_OVERALL = models.IntegerField(null=True, blank=False)
    DEEMED_HOURS_FOR_TWO_PARENT = models.IntegerField(null=True, blank=False)
    EARNED_INCOME = models.IntegerField(null=True, blank=False)
    UNEARNED_INCOME_TAX_CREDIT = models.IntegerField(null=True, blank=False)
    UNEARNED_SOCIAL_SECURITY = models.IntegerField(null=True, blank=False)
    UNEARNED_SSI = models.IntegerField(null=True, blank=False)
    UNEARNED_WORKERS_COMP = models.IntegerField(null=True, blank=False)
    OTHER_UNEARNED_INCOME = models.IntegerField(null=True, blank=False)


class SSP_M3(models.Model):
    """
    Parsed record representing an SSP M3 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='m3_parent'
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)
    FIPS_CODE = models.CharField(max_length=2, null=True, blank=False)

    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)
    DATE_OF_BIRTH = models.CharField(max_length=8, null=True, blank=False)
    SSN = models.CharField(max_length=100, null=True, blank=False)
    RACE_HISPANIC = models.IntegerField(null=True, blank=False)
    RACE_AMER_INDIAN = models.IntegerField(null=True, blank=False)
    RACE_ASIAN = models.IntegerField(null=True, blank=False)
    RACE_BLACK = models.IntegerField(null=True, blank=False)
    RACE_HAWAIIAN = models.IntegerField(null=True, blank=False)
    RACE_WHITE = models.IntegerField(null=True, blank=False)
    GENDER = models.IntegerField(null=True, blank=False)
    RECEIVE_NONSSI_BENEFITS = models.IntegerField(null=True, blank=False)
    RECEIVE_SSI = models.IntegerField(null=True, blank=False)
    RELATIONSHIP_HOH = models.IntegerField(null=True, blank=False)
    PARENT_MINOR_CHILD = models.IntegerField(null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(null=True, blank=False)
    CITIZENSHIP_STATUS = models.IntegerField(null=True, blank=False)
    UNEARNED_SSI = models.IntegerField(null=True, blank=False)
    OTHER_UNEARNED_INCOME = models.IntegerField(null=True, blank=False)

class SSP_M4(models.Model):
    """
    Parsed record representing an SSP M1 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='m4_parent'
    )

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
    DISPOSITION = models.IntegerField(null=True, blank=False)
    CLOSURE_REASON = models.CharField(max_length=2, null=True, blank=False)
    REC_SUB_HOUSING = models.IntegerField(null=True, blank=False)
    REC_MED_ASSIST = models.IntegerField(null=True, blank=False)
    REC_FOOD_STAMPS = models.IntegerField(null=True, blank=False)
    REC_SUB_CC = models.IntegerField(null=True, blank=False)

class SSP_M5(models.Model):
    """
    Parsed record representing an SSP M1 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='m5_parent'
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=True, blank=False)

    FAMILY_AFFILIATION = models.IntegerField(null=True, blank=False)
    DATE_OF_BIRTH = models.CharField(max_length=8, null=True, blank=False)
    SSN = models.CharField(max_length=9, null=True, blank=False)
    RACE_HISPANIC = models.IntegerField(null=True, blank=False)
    RACE_AMER_INDIAN = models.IntegerField(null=True, blank=False)
    RACE_ASIAN = models.IntegerField(null=True, blank=False)
    RACE_BLACK = models.IntegerField(null=True, blank=False)
    RACE_HAWAIIAN = models.IntegerField(null=True, blank=False)
    RACE_WHITE = models.IntegerField(null=True, blank=False)
    GENDER = models.IntegerField(null=True, blank=False)
    REC_OASDI_INSURANCE = models.IntegerField(null=True, blank=False)
    REC_FEDERAL_DISABILITY = models.IntegerField(null=True, blank=False)
    REC_AID_TOTALLY_DISABLED = models.IntegerField(null=True, blank=False)
    REC_AID_AGED_BLIND = models.IntegerField(null=True, blank=False)
    REC_SSI = models.IntegerField(null=True, blank=False)
    MARITAL_STATUS = models.IntegerField(null=True, blank=False)
    RELATIONSHIP_HOH = models.CharField(max_length=2, null=True, blank=False)
    PARENT_MINOR_CHILD = models.IntegerField(null=True, blank=False)
    NEEDS_OF_PREGNANT_WOMAN = models.IntegerField(null=True, blank=False)
    EDUCATION_LEVEL = models.CharField(max_length=2, null=True, blank=False)
    CITIZENSHIP_STATUS = models.IntegerField(null=True, blank=False)
    EMPLOYMENT_STATUS = models.IntegerField(null=True, blank=False)
    AMOUNT_EARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)
    AMOUNT_UNEARNED_INCOME = models.CharField(max_length=4, null=True, blank=False)

class SSP_M6(models.Model):
    """
    Parsed record representing an M6 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='m6_parent'
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    CALENDAR_QUARTER = models.IntegerField(null=True, blank=True)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)

    SSPMOE_FAMILIES = models.IntegerField(null=True, blank=True)
    NUM_2_PARENTS = models.IntegerField(null=True, blank=True)
    NUM_1_PARENTS = models.IntegerField(null=True, blank=True)
    NUM_NO_PARENTS = models.IntegerField(null=True, blank=True)
    NUM_RECIPIENTS = models.IntegerField(null=True, blank=True)
    ADULT_RECIPIENTS = models.IntegerField(null=True, blank=True)
    CHILD_RECIPIENTS = models.IntegerField(null=True, blank=True)
    NONCUSTODIALS = models.IntegerField(null=True, blank=True)
    AMT_ASSISTANCE = models.IntegerField(null=True, blank=True)
    CLOSED_CASES = models.IntegerField(null=True, blank=True)

class SSP_M7(models.Model):
    """
    Parsed record representing an SSP M3 data submission.

    Mapped to an elastic search index.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    datafile = models.ForeignKey(
        DataFile,
        blank=True,
        help_text='The parent file from which this record was created.',
        null=True,
        on_delete=models.CASCADE,
        related_name='m7_parent'
    )

    RecordType = models.CharField(max_length=156, null=True, blank=False)
    CALENDAR_QUARTER = models.IntegerField(null=True, blank=True)
    RPT_MONTH_YEAR = models.IntegerField(null=True, blank=False)
    TDRS_SECTION_IND = models.CharField(
        max_length=1,
        null=True,
        blank=False
    )
    STRATUM = models.CharField(max_length=2, null=True, blank=False)
    FAMILIES_MONTH = models.IntegerField(null=True, blank=False)
