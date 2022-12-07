"""Elasticsearch document mappings for Django models."""

from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import T1, T2, T3, T4, T5, T6, T7


@registry.register_document
class T1DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T1 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't1_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = T1
        fields = [
            'record',
            'rpt_month_year',
            'case_number',
            'disposition',
            'fips_code',

            'county_fips_code',
            'stratum',
            'zip_code',
            'funding_stream',
            'new_applicant',
            'nbr_of_family_members',
            'family_type',
            'receives_sub_housing',
            'receives_medical_assistance',
            'receives_food_stamps',
            'amt_food_stamp_assistance',
            'receives_sub_cc',
            'amt_sub_cc',
            'child_support_amount',
            'family_cash_recources',
            'cash_amount',
            'nbr_months',
            'cc_amount',
            'children_covered',
            'cc_nbr_of_months',
            'transp_amount',
            'transp_nbr_months',
            'transition_services_amount',
            'transition_nbr_months',
            'other_amount',
            'other_nbr_of_months',
            'sanc_reduction_amount',
            'work_req_sanction',
            'family_sanct_adult',
            'sanct_teen_parent',
            'non_cooperation_cse',
            'failure_to_comply',
            'other_sanction',
            'recoupment_prior_ovrpmt',
            'other_total_reductions',
            'family_cap',
            'reductions_on_receipts',
            'other_non_sanction',
            'waiver_evalu_control_grps',
            'family_exempt_time_limits',
            'family_new_child',
            'blank',
        ]


@registry.register_document
class T2DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T2 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't2_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = T2
        fields = [
            'record',
            'rpt_month_year',
            'case_number',
            'fips_code',

            'family_affiliation',
            'noncustodial_parent',
            'date_of_birth',
            'ssn',
            'race_hispanic',
            'race_amer_indian',
            'race_asian',
            'race_black',
            'race_hawaiian',
            'race_white',
            'gender',
            'fed_oasdi_program',
            'fed_disability_status',
            'disabled_title_xivapdt',
            'aid_aged_blind',
            'receive_ssi',
            'marital_status',
            'relationship_hoh',
            'parent_minor_child',
            'needs_pregnant_woman',
            'education_level',
            'citizenship_status',
            'cooperation_child_support',
            'months_fed_time_limit',
            'months_state_time_limit',
            'current_month_state_exempt',
            'employment_status',
            'work_eligible_indicator',
            'work_part_status',
            'unsub_employment',
            'sub_private_employment',
            'sub_public_employment',
            'work_experience_hop',
            'work_experience_ea',
            'work_experience_hol',
            'ojt',
            'job_search_hop',
            'job_search_ea',
            'job_search_hol',
            'comm_services_hop',
            'comm_services_ea',
            'comm_services_hol',
            'vocational_ed_training_hop',
            'vocational_ed_training_ea',
            'vocational_ed_training_hol',
            'job_skills_training_hop',
            'job_skills_training_ea',
            'job_skills_training_hol',
            'ed_no_high_school_dipl_hop',
            'ed_no_high_school_dipl_ea',
            'ed_no_high_school_dipl_hol',
            'school_attendence_hop',
            'school_attendence_ea',
            'school_attendence_hol',
            'provide_cc_hop',
            'provide_cc_ea',
            'provide_cc_hol',
            'other_work_activities',
            'deemed_hours_for_overall',
            'deemed_hours_for_two_parent',
            'earned_income',
            'unearned_income_tax_credit',
            'unearned_social_security',
            'unearned_ssi',
            'unearned_workers_comp',
            'other_unearned_income',
        ]


@registry.register_document
class T3DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T3 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't3_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = T3
        fields = [
            'record',
            'rpt_month_year',
            'case_number',
            'fips_code',

            'family_affiliation',
            'date_of_birth',
            'ssn',
            'race_hispanic',
            'race_amer_indian',
            'race_asian',
            'race_black',
            'race_hawaiian',
            'race_white',
            'gender',
            'receive_nonssa_benefits',
            'receive_ssi',
            'relationship_hoh',
            'parent_minor_child',
            'education_level',
            'citizenship_status',
            'unearned_ssi',
            'other_unearned_income',
        ]


@registry.register_document
class T4DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T4 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't4_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = T4
        fields = [
            'record',
            'rpt_month_year',
            'case_number',
            'disposition',
            'fips_code',

            'county_fips_code',
            'stratum',
            'zip_code',
            'closure_reason',
            'rec_sub_housing',
            'rec_med_assist',
            'rec_food_stamps',
            'rec_sub_cc',
            'blank',
        ]


@registry.register_document
class T5DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T5 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't5_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = T5
        fields = [
            'record',
            'rpt_month_year',
            'case_number',
            'fips_code',

            'family_affiliation',
            'date_of_birth',
            'ssn',
            'race_hispanic',
            'race_amer_indian',
            'race_asian',
            'race_black',
            'race_hawaiian',
            'race_white',
            'gender',
            'rec_oasdi_insurance',
            'rec_federal_disability',
            'rec_aid_totally_disabled',
            'rec_aid_aged_blind',
            'rec_ssi',
            'marital_status',
            'relationship_hoh',
            'parent_minor_child',
            'needs_of_pregnant_woman',
            'education_level',
            'citizenship_status',
            'countable_month_fed_time',
            'countable_months_state_tribe',
            'employment_status',
            'amount_earned_income',
            'amount_unearned_income',
        ]


@registry.register_document
class T6DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T6 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't6_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = T6
        fields = [
            'record',
            'rpt_month_year',
            'fips_code',

            'calendar_quarter',
            'applications',
            'approved',
            'denied',
            'assistance',
            'families',
            'num_2_parents',
            'num_1_parents',
            'num_no_parents',
            'recipients',
            'adult_recipients',
            'child_recipients',
            'noncustodials',
            'births',
            'outwedlock_births',
            'closed_cases',
        ]


@registry.register_document
class T7DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed T7 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 't7_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = T7
        fields = [
            'record',
            'rpt_month_year',
            'fips_code',

            'calendar_quarter',
            'tdrs_section_ind',
            'stratum',
            'families',
        ]
