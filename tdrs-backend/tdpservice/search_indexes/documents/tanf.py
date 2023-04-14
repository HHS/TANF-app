"""Elasticsearch document mappings for TANF submission models."""

from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from ..models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7


@registry.register_document
class TANF_T1DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T1 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t1_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T1
        fields = [
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'COUNTY_FIPS_CODE',
            'STRATUM',
            'ZIP_CODE',
            'FUNDING_STREAM',
            'DISPOSITION',
            'NEW_APPLICANT',
            'NBR_FAMILY_MEMBERS',
            'FAMILY_TYPE',
            'RECEIVES_SUB_HOUSING',
            'RECEIVES_MED_ASSISTANCE',
            'RECEIVES_FOOD_STAMPS',
            'AMT_FOOD_STAMP_ASSISTANCE',
            'RECEIVES_SUB_CC',
            'AMT_SUB_CC',
            'CHILD_SUPPORT_AMT',
            'FAMILY_CASH_RESOURCES',
            'CASH_AMOUNT',
            'NBR_MONTHS',
            'CC_AMOUNT',
            'CHILDREN_COVERED',
            'CC_NBR_MONTHS',
            'TRANSP_AMOUNT',
            'TRANSP_NBR_MONTHS',
            'TRANSITION_SERVICES_AMOUNT',
            'TRANSITION_NBR_MONTHS',
            'OTHER_AMOUNT',
            'OTHER_NBR_MONTHS',
            'SANC_REDUCTION_AMT',
            'WORK_REQ_SANCTION',
            'FAMILY_SANC_ADULT',
            'SANC_TEEN_PARENT',
            'NON_COOPERATION_CSE',
            'FAILURE_TO_COMPLY',
            'OTHER_SANCTION',
            'RECOUPMENT_PRIOR_OVRPMT',
            'OTHER_TOTAL_REDUCTIONS',
            'FAMILY_CAP',
            'REDUCTIONS_ON_RECEIPTS',
            'OTHER_NON_SANCTION',
            'WAIVER_EVAL_CONTROL_GRPS',
            'FAMILY_EXEMPT_TIME_LIMITS',
            'FAMILY_NEW_CHILD'
        ]


@registry.register_document
class TANF_T2DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T2 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t2_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T2
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
class TANF_T3DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T3 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t3_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T3
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
class TANF_T4DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T4 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t4_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T4
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
        ]


@registry.register_document
class TANF_T5DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T5 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t5_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T5
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
class TANF_T6DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T6 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t6_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T6
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
class TANF_T7DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T7 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'tanf_t7_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = TANF_T7
        fields = [
            'record',
            'rpt_month_year',
            'fips_code',

            'calendar_quarter',
            'tdrs_section_ind',
            'stratum',
            'families',
        ]
