"""Elasticsearch document mappings for TANF submission models."""

from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from ..models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7
from .document_base import DocumentBase

@registry.register_document
class TANF_T1DataSubmissionDocument(DocumentBase, Document):
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
class TANF_T2DataSubmissionDocument(DocumentBase, Document):
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
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'FAMILY_AFFILIATION',
            'NONCUSTODIAL_PARENT',
            'DATE_OF_BIRTH',
            'SSN',
            'RACE_HISPANIC',
            'RACE_AMER_INDIAN',
            'RACE_ASIAN',
            'RACE_BLACK',
            'RACE_HAWAIIAN',
            'RACE_WHITE',
            'GENDER',
            'FED_OASDI_PROGRAM',
            'FED_DISABILITY_STATUS',
            'DISABLED_TITLE_XIVAPDT',
            'AID_AGED_BLIND',
            'RECEIVE_SSI',
            'MARITAL_STATUS',
            'RELATIONSHIP_HOH',
            'PARENT_MINOR_CHILD',
            'NEEDS_PREGNANT_WOMAN',
            'EDUCATION_LEVEL',
            'CITIZENSHIP_STATUS',
            'COOPERATION_CHILD_SUPPORT',
            'MONTHS_FED_TIME_LIMIT',
            'MONTHS_STATE_TIME_LIMIT',
            'CURRENT_MONTH_STATE_EXEMPT',
            'EMPLOYMENT_STATUS',
            'WORK_ELIGIBLE_INDICATOR',
            'WORK_PART_STATUS',
            'UNSUB_EMPLOYMENT',
            'SUB_PRIVATE_EMPLOYMENT',
            'SUB_PUBLIC_EMPLOYMENT',
            'WORK_EXPERIENCE_HOP',
            'WORK_EXPERIENCE_EA',
            'WORK_EXPERIENCE_HOL',
            'OJT',
            'JOB_SEARCH_HOP',
            'JOB_SEARCH_EA',
            'JOB_SEARCH_HOL',
            'COMM_SERVICES_HOP',
            'COMM_SERVICES_EA',
            'COMM_SERVICES_HOL',
            'VOCATIONAL_ED_TRAINING_HOP',
            'VOCATIONAL_ED_TRAINING_EA',
            'VOCATIONAL_ED_TRAINING_HOL',
            'JOB_SKILLS_TRAINING_HOP',
            'JOB_SKILLS_TRAINING_EA',
            'JOB_SKILLS_TRAINING_HOL',
            'ED_NO_HIGH_SCHOOL_DIPL_HOP',
            'ED_NO_HIGH_SCHOOL_DIPL_EA',
            'ED_NO_HIGH_SCHOOL_DIPL_HOL',
            'SCHOOL_ATTENDENCE_HOP',
            'SCHOOL_ATTENDENCE_EA',
            'SCHOOL_ATTENDENCE_HOL',
            'PROVIDE_CC_HOP',
            'PROVIDE_CC_EA',
            'PROVIDE_CC_HOL',
            'OTHER_WORK_ACTIVITIES',
            'DEEMED_HOURS_FOR_OVERALL',
            'DEEMED_HOURS_FOR_TWO_PARENT',
            'EARNED_INCOME',
            'UNEARNED_INCOME_TAX_CREDIT',
            'UNEARNED_SOCIAL_SECURITY',
            'UNEARNED_SSI',
            'UNEARNED_WORKERS_COMP',
            'OTHER_UNEARNED_INCOME',
        ]


@registry.register_document
class TANF_T3DataSubmissionDocument(DocumentBase, Document):
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
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'FAMILY_AFFILIATION',
            'DATE_OF_BIRTH',
            'SSN',
            'RACE_HISPANIC',
            'RACE_AMER_INDIAN',
            'RACE_ASIAN',
            'RACE_BLACK',
            'RACE_HAWAIIAN',
            'RACE_WHITE',
            'GENDER',
            'RECEIVE_NONSSA_BENEFITS',
            'RECEIVE_SSI',
            'RELATIONSHIP_HOH',
            'PARENT_MINOR_CHILD',
            'EDUCATION_LEVEL',
            'CITIZENSHIP_STATUS',
            'UNEARNED_SSI',
            'OTHER_UNEARNED_INCOME',
        ]


@registry.register_document
class TANF_T4DataSubmissionDocument(DocumentBase, Document):
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
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'COUNTY_FIPS_CODE',
            'STRATUM',
            'ZIP_CODE',
            'DISPOSITION',
            'CLOSURE_REASON',
            'REC_SUB_HOUSING',
            'REC_MED_ASSIST',
            'REC_FOOD_STAMPS',
            'REC_SUB_CC',
        ]


@registry.register_document
class TANF_T5DataSubmissionDocument(DocumentBase, Document):
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
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'FAMILY_AFFILIATION',
            'DATE_OF_BIRTH',
            'SSN',
            'RACE_HISPANIC',
            'RACE_AMER_INDIAN',
            'RACE_ASIAN',
            'RACE_BLACK',
            'RACE_HAWAIIAN',
            'RACE_WHITE',
            'GENDER',
            'REC_OASDI_INSURANCE',
            'REC_FEDERAL_DISABILITY',
            'REC_AID_TOTALLY_DISABLED',
            'REC_AID_AGED_BLIND',
            'REC_SSI',
            'MARITAL_STATUS',
            'RELATIONSHIP_HOH',
            'PARENT_MINOR_CHILD',
            'NEEDS_OF_PREGNANT_WOMAN',
            'EDUCATION_LEVEL',
            'CITIZENSHIP_STATUS',
            'COUNTABLE_MONTH_FED_TIME',
            'COUNTABLE_MONTHS_STATE_TRIBE',
            'EMPLOYMENT_STATUS',
            'AMOUNT_EARNED_INCOME',
            'AMOUNT_UNEARNED_INCOME'
        ]


@registry.register_document
class TANF_T6DataSubmissionDocument(DocumentBase, Document):
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
            'RecordType',
            'CALENDAR_QUARTER',
            'RPT_MONTH_YEAR',
            'NUM_APPLICATIONS',
            'NUM_APPROVED',
            'NUM_DENIED',
            'ASSISTANCE',
            'NUM_FAMILIES',
            'NUM_2_PARENTS',
            'NUM_1_PARENTS',
            'NUM_NO_PARENTS',
            'NUM_RECIPIENTS',
            'NUM_ADULT_RECIPIENTS',
            'NUM_CHILD_RECIPIENTS',
            'NUM_NONCUSTODIALS',
            'NUM_BIRTHS',
            'NUM_OUTWEDLOCK_BIRTHS',
            'NUM_CLOSED_CASES'
        ]


@registry.register_document
class TANF_T7DataSubmissionDocument(DocumentBase, Document):
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
            "RecordType",
            "CALENDAR_QUARTER",
            "RPT_MONTH_YEAR",
            "TDRS_SECTION_IND",
            "STRATUM",
            "FAMILIES_MONTH",
        ]
