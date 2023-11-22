"""Elasticsearch document mappings for SSP submission models."""

from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from ..models.ssp import SSP_M1, SSP_M2, SSP_M3, SSP_M6, SSP_M7
from .document_base import DocumentBase


@registry.register_document
class SSP_M1DataSubmissionDocument(DocumentBase, Document):
    """Elastic search model mapping for a parsed SSP M1 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'ssp_m1_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M1
        fields = [
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'FIPS_CODE',
            'COUNTY_FIPS_CODE',
            'STRATUM',
            'ZIP_CODE',
            'DISPOSITION',
            'NBR_FAMILY_MEMBERS',
            'FAMILY_TYPE',
            'TANF_ASST_IN_6MONTHS',
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
        ]


@registry.register_document
class SSP_M2DataSubmissionDocument(DocumentBase, Document):
    """Elastic search model mapping for a parsed SSP M2 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'ssp_m2_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M2
        fields = [
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'FIPS_CODE',
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
class SSP_M3DataSubmissionDocument(DocumentBase, Document):
    """Elastic search model mapping for a parsed SSP M3 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'ssp_m3_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M3
        fields = [
            'RecordType',
            'RPT_MONTH_YEAR',
            'CASE_NUMBER',
            'FIPS_CODE',
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
            'RECEIVE_NONSSI_BENEFITS',
            'RECEIVE_SSI',
            'RELATIONSHIP_HOH',
            'PARENT_MINOR_CHILD',
            'EDUCATION_LEVEL',
            'CITIZENSHIP_STATUS',
            'UNEARNED_SSI',
            'OTHER_UNEARNED_INCOME',
        ]

@registry.register_document
class SSP_M6DataSubmissionDocument(DocumentBase, Document):
    """Elastic search model mapping for a parsed SSP M6 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'ssp_m6_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M6
        fields = [
            'RecordType',
            'CALENDAR_QUARTER',
            'RPT_MONTH_YEAR',
            'SSPMOE_FAMILIES',
            'NUM_2_PARENTS',
            'NUM_1_PARENTS',
            'NUM_NO_PARENTS',
            'NUM_RECIPIENTS',
            'ADULT_RECIPIENTS',
            'CHILD_RECIPIENTS',
            'NONCUSTODIALS',
            'AMT_ASSISTANCE',
            'CLOSED_CASES',
        ]

@registry.register_document
class SSP_M7DataSubmissionDocument(DocumentBase, Document):
    """Elastic search model mapping for a parsed SSP M7 data file."""

    class Index:
        """ElasticSearch index generation settings."""

        name = 'ssp_m7_submissions'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
        }

    class Django:
        """Django model reference and field mapping."""

        model = SSP_M7
        fields = [
            "RecordType",
            "CALENDAR_QUARTER",
            "RPT_MONTH_YEAR",
            "TDRS_SECTION_IND",
            "STRATUM",
            "FAMILIES_MONTH",
        ]
