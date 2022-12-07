"""Models representing parsed data file records submitted to TDP."""

from django.db import models

# Create your models here.


class T1(models.Model):
    """
    Parsed record representing a T1 data submission.

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
    funding_stream = models.IntegerField(null=False, blank=False)
    new_applicant = models.IntegerField(null=False, blank=False)
    nbr_of_family_members = models.IntegerField(null=False, blank=False)
    family_type = models.IntegerField(null=False, blank=False)
    receives_sub_housing = models.IntegerField(null=False, blank=False)
    receives_medical_assistance = models.IntegerField(null=False, blank=False)
    receives_food_stamps = models.IntegerField(null=False, blank=False)
    amt_food_stamp_assistance = models.IntegerField(null=False, blank=False)
    receives_sub_cc = models.IntegerField(null=False, blank=False)
    amt_sub_cc = models.IntegerField(null=False, blank=False)
    child_support_amount = models.IntegerField(null=False, blank=False)
    family_cash_recources = models.IntegerField(null=False, blank=False)
    cash_amount = models.IntegerField(null=False, blank=False)
    nbr_months = models.IntegerField(null=False, blank=False)
    cc_amount = models.IntegerField(null=False, blank=False)
    children_covered = models.IntegerField(null=False, blank=False)
    cc_nbr_of_months = models.IntegerField(null=False, blank=False)
    transp_amount = models.IntegerField(null=False, blank=False)
    transp_nbr_months = models.IntegerField(null=False, blank=False)
    transition_services_amount = models.IntegerField(null=False, blank=False)
    transition_nbr_months = models.IntegerField(null=False, blank=False)
    other_amount = models.IntegerField(null=False, blank=False)
    other_nbr_of_months = models.IntegerField(null=False, blank=False)
    sanc_reduction_amount = models.IntegerField(null=False, blank=False)
    work_req_sanction = models.IntegerField(null=False, blank=False)
    family_sanct_adult = models.IntegerField(null=False, blank=False)
    sanct_teen_parent = models.IntegerField(null=False, blank=False)
    non_cooperation_cse = models.IntegerField(null=False, blank=False)
    failure_to_comply = models.IntegerField(null=False, blank=False)
    other_sanction = models.IntegerField(null=False, blank=False)
    recoupment_prior_ovrpmt = models.IntegerField(null=False, blank=False)
    other_total_reductions = models.IntegerField(null=False, blank=False)
    family_cap = models.IntegerField(null=False, blank=False)
    reductions_on_receipts = models.IntegerField(null=False, blank=False)
    other_non_sanction = models.IntegerField(null=False, blank=False)
    waiver_evalu_control_grps = models.IntegerField(null=False, blank=False)
    family_exempt_time_limits = models.IntegerField(null=False, blank=False)
    family_new_child = models.IntegerField(null=False, blank=False)
    blank = models.CharField(max_length=39, null=False, blank=False)


class T2(models.Model):
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


class T3(models.Model):
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
    blank = models.CharField(max_length=55, null=False, blank=False)


class T4(models.Model):
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
    blank = models.CharField(max_length=100, null=False, blank=False)


class T5(models.Model):
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


class T6(models.Model):
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


class T7(models.Model):
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
