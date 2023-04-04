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
    RecordType = models.CharField(max_length=156, null=False, blank=False)
    RPT_MONTH_YEAR = models.IntegerField(null=False, blank=False)
    CASE_NUMBER = models.CharField(max_length=11, null=False, blank=False)
    FIPS_CODE = models.CharField(max_length=2, null=False, blank=False)
    COUNTY_FIPS_CODE = models.CharField(
        max_length=3,
        null=False,
        blank=False
    )
    STRATUM = models.IntegerField(null=False, blank=False)
    ZIP_CODE = models.CharField(max_length=5, null=False, blank=False)
    FUNDING_STREAM = models.IntegerField(null=False, blank=False)
    DISPOSITION = models.IntegerField(null=False, blank=False)
    NEW_APPLICANT = models.IntegerField(null=False, blank=False)
    NBR_FAMILY_MEMBERS = models.IntegerField(null=False, blank=False)
    FAMILY_TYPE = models.IntegerField(null=False, blank=False)
    RECEIVES_SUB_HOUSING = models.IntegerField(null=False, blank=False)
    RECEIVES_MED_ASSISTANCE = models.IntegerField(null=False, blank=False)
    RECEIVES_FOOD_STAMPS = models.IntegerField(null=False, blank=False)
    AMT_FOOD_STAMP_ASSISTANCE = models.IntegerField(null=False, blank=False)
    RECEIVES_SUB_CC = models.IntegerField(null=False, blank=False)
    AMT_SUB_CC = models.IntegerField(null=False, blank=False)
    CHILD_SUPPORT_AMT = models.IntegerField(null=False, blank=False)
    FAMILY_CASH_RESOURCES = models.IntegerField(null=False, blank=False)
    CASH_AMOUNT = models.IntegerField(null=False, blank=False)
    NBR_MONTHS = models.IntegerField(null=False, blank=False)
    CC_AMOUNT = models.IntegerField(null=False, blank=False)
    CHILDREN_COVERED = models.IntegerField(null=False, blank=False)
    CC_NBR_MONTHS = models.IntegerField(null=False, blank=False)
    TRANSP_AMOUNT = models.IntegerField(null=False, blank=False)
    TRANSP_NBR_MONTHS = models.IntegerField(null=False, blank=False)
    TRANSITION_SERVICES_AMOUNT = models.IntegerField(null=False, blank=False)
    TRANSITION_NBR_MONTHS = models.IntegerField(null=False, blank=False)
    OTHER_AMOUNT = models.IntegerField(null=False, blank=False)
    OTHER_NBR_MONTHS = models.IntegerField(null=False, blank=False)
    SANC_REDUCTION_AMT = models.IntegerField(null=False, blank=False)
    WORK_REQ_SANCTION = models.IntegerField(null=False, blank=False)
    FAMILY_SANC_ADULT = models.IntegerField(null=False, blank=False)
    SANC_TEEN_PARENT = models.IntegerField(null=False, blank=False)
    NON_COOPERATION_CSE = models.IntegerField(null=False, blank=False)
    FAILURE_TO_COMPLY = models.IntegerField(null=False, blank=False)
    OTHER_SANCTION = models.IntegerField(null=False, blank=False)
    RECOUPMENT_PRIOR_OVRPMT = models.IntegerField(null=False, blank=False)
    OTHER_TOTAL_REDUCTIONS = models.IntegerField(null=False, blank=False)
    FAMILY_CAP = models.IntegerField(null=False, blank=False)
    REDUCTIONS_ON_RECEIPTS = models.IntegerField(null=False, blank=False)
    OTHER_NON_SANCTION = models.IntegerField(null=False, blank=False)
    WAIVER_EVAL_CONTROL_GRPS = models.IntegerField(null=False, blank=False)
    FAMILY_EXEMPT_TIME_LIMITS = models.IntegerField(null=False, blank=False)
    FAMILY_NEW_CHILD = models.IntegerField(null=False, blank=False)


class TANF_T2(models.Model):
    """
    Parsed record representing a T2 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    case_number = models.CharField(max_length=11, null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    family_affiliation = models.IntegerField(null=False, blank=False)
    noncustodial_parent = models.IntegerField(null=False, blank=False)
    date_of_birth = models.CharField(max_length=8, null=False, blank=False)
    ssn = models.CharField(max_length=9, null=False, blank=False)
    race_hispanic = models.IntegerField(null=False, blank=False)
    race_amer_indian = models.IntegerField(null=False, blank=False)
    race_asian = models.IntegerField(null=False, blank=False)
    race_black = models.IntegerField(null=False, blank=False)
    race_hawaiian = models.IntegerField(null=False, blank=False)
    race_white = models.IntegerField(null=False, blank=False)
    gender = models.IntegerField(null=False, blank=False)
    fed_oasdi_program = models.IntegerField(null=False, blank=False)
    fed_disability_status = models.IntegerField(null=False, blank=False)
    disabled_title_xivapdt = models.IntegerField(null=False, blank=False)
    aid_aged_blind = models.IntegerField(null=False, blank=False)
    receive_ssi = models.IntegerField(null=False, blank=False)
    marital_status = models.IntegerField(null=False, blank=False)
    relationship_hoh = models.IntegerField(null=False, blank=False)
    parent_minor_child = models.IntegerField(null=False, blank=False)
    needs_pregnant_woman = models.IntegerField(null=False, blank=False)
    education_level = models.IntegerField(null=False, blank=False)
    citizenship_status = models.IntegerField(null=False, blank=False)
    cooperation_child_support = models.IntegerField(null=False, blank=False)
    months_fed_time_limit = models.FloatField(null=False, blank=False)
    months_state_time_limit = models.FloatField(null=False, blank=False)
    current_month_state_exempt = models.IntegerField(null=False, blank=False)
    employment_status = models.IntegerField(null=False, blank=False)
    work_eligible_indicator = models.IntegerField(null=False, blank=False)
    work_part_status = models.IntegerField(null=False, blank=False)
    unsub_employment = models.IntegerField(null=False, blank=False)
    sub_private_employment = models.IntegerField(null=False, blank=False)
    sub_public_employment = models.IntegerField(null=False, blank=False)
    work_experience_hop = models.IntegerField(null=False, blank=False)
    work_experience_ea = models.IntegerField(null=False, blank=False)
    work_experience_hol = models.IntegerField(null=False, blank=False)
    ojt = models.IntegerField(null=False, blank=False)
    job_search_hop = models.IntegerField(null=False, blank=False)
    job_search_ea = models.IntegerField(null=False, blank=False)
    job_search_hol = models.IntegerField(null=False, blank=False)
    comm_services_hop = models.IntegerField(null=False, blank=False)
    comm_services_ea = models.IntegerField(null=False, blank=False)
    comm_services_hol = models.IntegerField(null=False, blank=False)
    vocational_ed_training_hop = models.IntegerField(null=False, blank=False)
    vocational_ed_training_ea = models.IntegerField(null=False, blank=False)
    vocational_ed_training_hol = models.IntegerField(null=False, blank=False)
    job_skills_training_hop = models.IntegerField(null=False, blank=False)
    job_skills_training_ea = models.IntegerField(null=False, blank=False)
    job_skills_training_hol = models.IntegerField(null=False, blank=False)
    ed_no_high_school_dipl_hop = models.IntegerField(null=False, blank=False)
    ed_no_high_school_dipl_ea = models.IntegerField(null=False, blank=False)
    ed_no_high_school_dipl_hol = models.IntegerField(null=False, blank=False)
    school_attendence_hop = models.IntegerField(null=False, blank=False)
    school_attendence_ea = models.IntegerField(null=False, blank=False)
    school_attendence_hol = models.IntegerField(null=False, blank=False)
    provide_cc_hop = models.IntegerField(null=False, blank=False)
    provide_cc_ea = models.IntegerField(null=False, blank=False)
    provide_cc_hol = models.IntegerField(null=False, blank=False)
    other_work_activities = models.IntegerField(null=False, blank=False)
    deemed_hours_for_overall = models.IntegerField(null=False, blank=False)
    deemed_hours_for_two_parent = models.IntegerField(null=False, blank=False)
    earned_income = models.IntegerField(null=False, blank=False)
    unearned_income_tax_credit = models.IntegerField(null=False, blank=False)
    unearned_social_security = models.IntegerField(null=False, blank=False)
    unearned_ssi = models.IntegerField(null=False, blank=False)
    unearned_workers_comp = models.IntegerField(null=False, blank=False)
    other_unearned_income = models.IntegerField(null=False, blank=False)


class TANF_T3(models.Model):
    """
    Parsed record representing a T3 data submission.

    Mapped to an elastic search index.
    """

    record = models.CharField(max_length=156, null=False, blank=False)
    rpt_month_year = models.IntegerField(null=False, blank=False)
    case_number = models.CharField(max_length=11, null=False, blank=False)
    fips_code = models.CharField(max_length=100, null=False, blank=False)

    family_affiliation = models.IntegerField(null=False, blank=False)
    date_of_birth = models.CharField(max_length=8, null=False, blank=False)
    ssn = models.CharField(max_length=100, null=False, blank=False)
    race_hispanic = models.IntegerField(null=False, blank=False)
    race_amer_indian = models.IntegerField(null=False, blank=False)
    race_asian = models.IntegerField(null=False, blank=False)
    race_black = models.IntegerField(null=False, blank=False)
    race_hawaiian = models.IntegerField(null=False, blank=False)
    race_white = models.IntegerField(null=False, blank=False)
    gender = models.IntegerField(null=False, blank=False)
    receive_nonssa_benefits = models.IntegerField(null=False, blank=False)
    receive_ssi = models.IntegerField(null=False, blank=False)
    relationship_hoh = models.IntegerField(null=False, blank=False)
    parent_minor_child = models.IntegerField(null=False, blank=False)
    education_level = models.IntegerField(null=False, blank=False)
    citizenship_status = models.IntegerField(null=False, blank=False)
    unearned_ssi = models.IntegerField(null=False, blank=False)
    other_unearned_income = models.IntegerField(null=False, blank=False)


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
