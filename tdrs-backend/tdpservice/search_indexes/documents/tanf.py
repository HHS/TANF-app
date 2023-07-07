"""Elasticsearch document mappings for TANF submission models."""

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from ..models.tanf import TANF_T1, TANF_T2, TANF_T3, TANF_T4, TANF_T5, TANF_T6, TANF_T7
from tdpservice.data_files.models import DataFile

@registry.register_document
class TANF_T1DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T1 data file."""

    datafile = fields.ObjectField(properties={
                      'pk': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField()
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance

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

    datafile = fields.ObjectField(properties={
                      'pk': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField()
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance

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
            'PARENT_WITH_MINOR_CHILD',
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
class TANF_T3DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T3 data file."""

    datafile = fields.ObjectField(properties={
                      'pk': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField()
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance

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
class TANF_T4DataSubmissionDocument(Document):
    """Elastic search model mapping for a parsed TANF T4 data file."""

    datafile = fields.ObjectField(properties={
                      'pk': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField()
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance

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

    datafile = fields.ObjectField(properties={
                      'pk': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField()
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance

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

    datafile = fields.ObjectField(properties={
                      'pk': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField()
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance

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

    datafile = fields.ObjectField(properties={
                      'pk': fields.IntegerField(),
                      'created_at': fields.DateField(),
                      'version': fields.IntegerField(),
                      'quarter': fields.TextField()
                  })

    def get_instances_from_related(self, related_instance):
        """Return correct instance."""
        if isinstance(related_instance, DataFile):
            return related_instance

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
