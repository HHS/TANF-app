"""Tests for elasticsearch model mapping."""

import pytest
from faker import Faker
from django.db.utils import IntegrityError
from tdpservice.search_indexes import models
from tdpservice.search_indexes import documents
from tdpservice.parsers.util import create_test_datafile


fake = Faker()


@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return create_test_datafile('small_correct_file', stt_user, stt)


@pytest.mark.django_db
def test_can_create_and_index_tanf_t1_submission(test_datafile):
    """TANF T1 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T1()
    submission.datafile = test_datafile
    submission.RecordType = record_num
    submission.RPT_MONTH_YEAR = 1
    submission.CASE_NUMBER = "1"
    submission.COUNTY_FIPS_CODE = 1
    submission.STRATUM = "1"
    submission.ZIP_CODE = "01"
    submission.FUNDING_STREAM = 1
    submission.DISPOSITION = 1
    submission.NEW_APPLICANT = 1
    submission.NBR_FAMILY_MEMBERS = 1
    submission.FAMILY_TYPE = 1
    submission.RECEIVES_SUB_HOUSING = 1
    submission.RECEIVES_MED_ASSISTANCE = 1
    submission.RECEIVES_FOOD_STAMPS = 1
    submission.AMT_FOOD_STAMP_ASSISTANCE = 1
    submission.RECEIVES_SUB_CC = 1
    submission.AMT_SUB_CC = 1
    submission.CHILD_SUPPORT_AMT = 1
    submission.FAMILY_CASH_RESOURCES = 1
    submission.CASH_AMOUNT = 1
    submission.NBR_MONTHS = 1
    submission.CC_AMOUNT = 1
    submission.CHILDREN_COVERED = 1
    submission.CC_NBR_MONTHS = 1
    submission.TRANSP_AMOUNT = 1
    submission.TRANSP_NBR_MONTHS = 1
    submission.TRANSITION_SERVICES_AMOUNT = 1
    submission.TRANSITION_NBR_MONTHS = 1
    submission.OTHER_AMOUNT = 1
    submission.OTHER_NBR_MONTHS = 1
    submission.SANC_REDUCTION_AMT = 1
    submission.WORK_REQ_SANCTION = 1
    submission.FAMILY_SANC_ADULT = 1
    submission.SANC_TEEN_PARENT = 1
    submission.NON_COOPERATION_CSE = 1
    submission.FAILURE_TO_COMPLY = 1
    submission.OTHER_SANCTION = 1
    submission.RECOUPMENT_PRIOR_OVRPMT = 1
    submission.OTHER_TOTAL_REDUCTIONS = 1
    submission.FAMILY_CAP = 1
    submission.REDUCTIONS_ON_RECEIPTS = 1
    submission.OTHER_NON_SANCTION = 1
    submission.WAIVER_EVAL_CONTROL_GRPS = 1
    submission.FAMILY_EXEMPT_TIME_LIMITS = 1
    submission.FAMILY_NEW_CHILD = 1

    submission.save()

    # submission.full_clean()

    assert submission.id is not None

    search = documents.tanf.TANF_T1DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t2_submission(test_datafile):
    """TANF T2 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T2()
    submission.datafile = test_datafile
    submission.RecordType = record_num
    submission.RPT_MONTH_YEAR = 1
    submission.CASE_NUMBER = '1'
    submission.FAMILY_AFFILIATION = 1
    submission.NONCUSTODIAL_PARENT = 1
    submission.DATE_OF_BIRTH = 1
    submission.SSN = '1'
    submission.RACE_HISPANIC = 1
    submission.RACE_AMER_INDIAN = 1
    submission.RACE_ASIAN = 1
    submission.RACE_BLACK = 1
    submission.RACE_HAWAIIAN = 1
    submission.RACE_WHITE = 1
    submission.GENDER = 1
    submission.FED_OASDI_PROGRAM = 1
    submission.FED_DISABILITY_STATUS = 1
    submission.DISABLED_TITLE_XIVAPDT = 1
    submission.AID_AGED_BLIND = 1
    submission.RECEIVE_SSI = 1
    submission.MARITAL_STATUS = 1
    submission.RELATIONSHIP_HOH = "01"
    submission.PARENT_WITH_MINOR_CHILD = 1
    submission.NEEDS_PREGNANT_WOMAN = 1
    submission.EDUCATION_LEVEL = 1
    submission.CITIZENSHIP_STATUS = 1
    submission.COOPERATION_CHILD_SUPPORT = 1
    submission.MONTHS_FED_TIME_LIMIT = 1
    submission.MONTHS_STATE_TIME_LIMIT = 1
    submission.CURRENT_MONTH_STATE_EXEMPT = 1
    submission.EMPLOYMENT_STATUS = 1
    submission.WORK_ELIGIBLE_INDICATOR = 1
    submission.WORK_PART_STATUS = 1
    submission.UNSUB_EMPLOYMENT = 1
    submission.SUB_PRIVATE_EMPLOYMENT = 1
    submission.SUB_PUBLIC_EMPLOYMENT = 1
    submission.WORK_EXPERIENCE_HOP = 1
    submission.WORK_EXPERIENCE_EA = 1
    submission.WORK_EXPERIENCE_HOL = 1
    submission.OJT = 1
    submission.JOB_SEARCH_HOP = 1
    submission.JOB_SEARCH_EA = 1
    submission.JOB_SEARCH_HOL = 1
    submission.COMM_SERVICES_HOP = 1
    submission.COMM_SERVICES_EA = 1
    submission.COMM_SERVICES_HOL = 1
    submission.VOCATIONAL_ED_TRAINING_HOP = 1
    submission.VOCATIONAL_ED_TRAINING_EA = 1
    submission.VOCATIONAL_ED_TRAINING_HOL = 1
    submission.JOB_SKILLS_TRAINING_HOP = 1
    submission.JOB_SKILLS_TRAINING_EA = 1
    submission.JOB_SKILLS_TRAINING_HOL = 1
    submission.ED_NO_HIGH_SCHOOL_DIPL_HOP = 1
    submission.ED_NO_HIGH_SCHOOL_DIPL_EA = 1
    submission.ED_NO_HIGH_SCHOOL_DIPL_HOL = 1
    submission.SCHOOL_ATTENDENCE_HOP = 1
    submission.SCHOOL_ATTENDENCE_EA = 1
    submission.SCHOOL_ATTENDENCE_HOL = 1
    submission.PROVIDE_CC_HOP = 1
    submission.PROVIDE_CC_EA = 1
    submission.PROVIDE_CC_HOL = 1
    submission.OTHER_WORK_ACTIVITIES = 1
    submission.DEEMED_HOURS_FOR_OVERALL = 1
    submission.DEEMED_HOURS_FOR_TWO_PARENT = 1
    submission.EARNED_INCOME = 1
    submission.UNEARNED_INCOME_TAX_CREDIT = 1
    submission.UNEARNED_SOCIAL_SECURITY = 1
    submission.UNEARNED_SSI = 1
    submission.UNEARNED_WORKERS_COMP = 1
    submission.OTHER_UNEARNED_INCOME = 1

    submission.save()

    assert submission.id is not None

    search = documents.tanf.TANF_T2DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t3_submission(test_datafile):
    """TANF T3 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T3()
    submission.datafile = test_datafile
    submission.RecordType = record_num
    submission.RPT_MONTH_YEAR = 1
    submission.CASE_NUMBER = '1'
    submission.FAMILY_AFFILIATION = 1
    submission.DATE_OF_BIRTH = 1
    submission.SSN = '1'
    submission.RACE_HISPANIC = 1
    submission.RACE_AMER_INDIAN = 1
    submission.RACE_ASIAN = 1
    submission.RACE_BLACK = 1
    submission.RACE_HAWAIIAN = 1
    submission.RACE_WHITE = 1
    submission.GENDER = 1
    submission.RECEIVE_NONSSA_BENEFITS = 1
    submission.RECEIVE_SSI = 1
    submission.RELATIONSHIP_HOH = "01"
    submission.PARENT_MINOR_CHILD = 1
    submission.EDUCATION_LEVEL = 1
    submission.CITIZENSHIP_STATUS = 1
    submission.UNEARNED_SSI = 1
    submission.OTHER_UNEARNED_INCOME = 1

    submission.save()

    assert submission.id is not None

    search = documents.tanf.TANF_T3DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t4_submission(test_datafile):
    """TANF T4 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T4()
    submission.datafile = test_datafile
    submission.RecordType = record_num
    submission.RPT_MONTH_YEAR = 1
    submission.CASE_NUMBER = '1'
    submission.COUNTY_FIPS_CODE = '1'
    submission.STRATUM = "1"
    submission.ZIP_CODE = '01'
    submission.DISPOSITION = 1
    submission.CLOSURE_REASON = "1"
    submission.REC_SUB_HOUSING = 1
    submission.REC_MED_ASSIST = 1
    submission.REC_FOOD_STAMPS = 1
    submission.REC_SUB_CC = 1

    submission.save()

    assert submission.id is not None

    search = documents.tanf.TANF_T4DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t5_submission(test_datafile):
    """TANF T5 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T5()
    submission.datafile = test_datafile
    submission.RecordType = record_num
    submission.RPT_MONTH_YEAR = 1
    submission.CASE_NUMBER = '1'
    submission.FAMILY_AFFILIATION = 1
    submission.DATE_OF_BIRTH = '1'
    submission.SSN = '1'
    submission.RACE_HISPANIC = 1
    submission.RACE_AMER_INDIAN = 1
    submission.RACE_ASIAN = 1
    submission.RACE_BLACK = 1
    submission.RACE_HAWAIIAN = 1
    submission.RACE_WHITE = 1
    submission.GENDER = 1
    submission.REC_OASDI_INSURANCE = 1
    submission.REC_FEDERAL_DISABILITY = 1
    submission.REC_AID_TOTALLY_DISABLED = 1
    submission.REC_AID_AGED_BLIND = 1
    submission.RECEIVE_SSI = 1
    submission.MARITAL_STATUS = 1
    submission.RELATIONSHIP_HOH = "01"
    submission.PARENT_WITH_MINOR_CHILD = 1
    submission.NEEDS_PREGNANT_WOMAN = 1
    submission.EDUCATION_LEVEL = "1"
    submission.CITIZENSHIP_STATUS = 1
    submission.COUNTABLE_MONTH_FED_TIME = "1"
    submission.COUNTABLE_MONTHS_STATE_TRIBE = "1"
    submission.EMPLOYMENT_STATUS = 1
    submission.AMOUNT_EARNED_INCOME = "1"
    submission.AMOUNT_UNEARNED_INCOME = "1"

    submission.save()

    assert submission.id is not None

    search = documents.tanf.TANF_T5DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t6_submission(test_datafile):
    """TANF T6 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T6()
    submission.datafile = test_datafile
    submission.RecordType = record_num
    submission.CALENDAR_QUARTER = 1
    submission.RPT_MONTH_YEAR = 1
    submission.NUM_APPLICATIONS = 1
    submission.NUM_APPROVED = 1
    submission.NUM_DENIED = 1
    submission.ASSISTANCE = 1
    submission.NUM_FAMILIES = 1
    submission.NUM_2_PARENTS = 1
    submission.NUM_1_PARENTS = 1
    submission.NUM_NO_PARENTS = 1
    submission.NUM_RECIPIENTS = 1
    submission.NUM_ADULT_RECIPIENTS = 1
    submission.NUM_CHILD_RECIPIENTS = 1
    submission.NUM_NONCUSTODIALS = 1
    submission.NUM_BIRTHS = 1
    submission.NUM_OUTWEDLOCK_BIRTHS = 1
    submission.NUM_CLOSED_CASES = 1

    submission.save()

    assert submission.id is not None

    search = documents.tanf.TANF_T6DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t7_submission(test_datafile):
    """TANF T7 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T7()
    submission.datafile = test_datafile
    submission.record = record_num
    submission.rpt_month_year = 1
    submission.fips_code = '2'
    submission.calendar_quarter = 1
    submission.tdrs_section_ind = '1'
    submission.stratum = '1'
    submission.families = 1

    submission.save()

    # No checks her because t7 records can't be parsed currently.
    # assert submission.id is not None

    # search = documents.tanf.TANF_T7DataSubmissionDocument.search().query(
    #     'match',
    #     record=record_num
    # )
    # response = search.execute()

    # assert response.hits.total.value == 1


@pytest.mark.django_db
def test_does_not_create_index_if_model_creation_fails():
    """Index creation shouldn't happen if saving a model errors."""
    record_num = fake.uuid4()

    with pytest.raises(IntegrityError):
        submission = models.tanf.TANF_T7.objects.create(
            record=record_num
            # leave out a bunch of required fields
        )

        assert submission.id is None

    search = documents.tanf.TANF_T7DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )

    response = search.execute()

    assert response.hits.total.value == 0


@pytest.mark.django_db
def test_can_create_and_map_ssp_m1_submission():
    """SSP M1 Submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.ssp.SSP_M1.objects.create(
        RecordType=record_num,
        RPT_MONTH_YEAR=1,
        CASE_NUMBER="1",
        COUNTY_FIPS_CODE=1,
        STRATUM="1",
        ZIP_CODE="01",
        # FUNDING_STREAM=1,
        DISPOSITION=1,
        # NEW_APPLICANT=1,
        NBR_FAMILY_MEMBERS=1,
        FAMILY_TYPE=1,
        TANF_ASST_IN_6MONTHS=1,
        RECEIVES_SUB_HOUSING=1,
        RECEIVES_MED_ASSISTANCE=1,
        RECEIVES_FOOD_STAMPS=1,
        AMT_FOOD_STAMP_ASSISTANCE=1,
        RECEIVES_SUB_CC=1,
        AMT_SUB_CC=1,
        CHILD_SUPPORT_AMT=1,
        FAMILY_CASH_RESOURCES=1,
        CASH_AMOUNT=1,
        NBR_MONTHS=1,
        CC_AMOUNT=1,
        CHILDREN_COVERED=1,
        CC_NBR_MONTHS=1,
        TRANSP_AMOUNT=1,
        TRANSP_NBR_MONTHS=1,
        TRANSITION_SERVICES_AMOUNT=1,
        TRANSITION_NBR_MONTHS=1,
        OTHER_AMOUNT=1,
        OTHER_NBR_MONTHS=1,
        SANC_REDUCTION_AMT=1,
        WORK_REQ_SANCTION=1,
        FAMILY_SANC_ADULT=1,
        SANC_TEEN_PARENT=1,
        NON_COOPERATION_CSE=1,
        FAILURE_TO_COMPLY=1,
        OTHER_SANCTION=1,
        RECOUPMENT_PRIOR_OVRPMT=1,
        OTHER_TOTAL_REDUCTIONS=1,
        FAMILY_CAP=1,
        REDUCTIONS_ON_RECEIPTS=1,
        OTHER_NON_SANCTION=1,
        WAIVER_EVAL_CONTROL_GRPS=1,
        # FAMILY_EXEMPT_TIME_LIMITS=1,
        # FAMILY_NEW_CHILD=1,
    )

    assert submission.id is not None

    search = documents.ssp.SSP_M1DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_ssp_m2_submission():
    """SSP M2 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.ssp.SSP_M2.objects.create(
        RecordType=record_num,
        RPT_MONTH_YEAR=1,
        CASE_NUMBER='1',
        FIPS_CODE='1',

        FAMILY_AFFILIATION=1,
        NONCUSTODIAL_PARENT=1,
        DATE_OF_BIRTH='1',
        SSN='1',
        RACE_HISPANIC=1,
        RACE_AMER_INDIAN=1,
        RACE_ASIAN=1,
        RACE_BLACK=1,
        RACE_HAWAIIAN=1,
        RACE_WHITE=1,
        GENDER=1,
        FED_OASDI_PROGRAM=1,
        FED_DISABILITY_STATUS=1,
        DISABLED_TITLE_XIVAPDT=1,
        AID_AGED_BLIND=1,
        RECEIVE_SSI=1,
        MARITAL_STATUS=1,
        RELATIONSHIP_HOH="01",
        PARENT_MINOR_CHILD=1,
        NEEDS_PREGNANT_WOMAN=1,
        EDUCATION_LEVEL=1,
        CITIZENSHIP_STATUS=1,
        COOPERATION_CHILD_SUPPORT=1,
        # MONTHS_FED_TIME_LIMIT=1,
        # MONTHS_STATE_TIME_LIMIT=1,
        # CURRENT_MONTH_STATE_EXEMPT=1,
        EMPLOYMENT_STATUS=1,
        WORK_ELIGIBLE_INDICATOR=1,
        WORK_PART_STATUS=1,
        UNSUB_EMPLOYMENT=1,
        SUB_PRIVATE_EMPLOYMENT=1,
        SUB_PUBLIC_EMPLOYMENT=1,
        WORK_EXPERIENCE_HOP=1,
        WORK_EXPERIENCE_EA=1,
        WORK_EXPERIENCE_HOL=1,
        OJT=1,
        JOB_SEARCH_HOP=1,
        JOB_SEARCH_EA=1,
        JOB_SEARCH_HOL=1,
        COMM_SERVICES_HOP=1,
        COMM_SERVICES_EA=1,
        COMM_SERVICES_HOL=1,
        VOCATIONAL_ED_TRAINING_HOP=1,
        VOCATIONAL_ED_TRAINING_EA=1,
        VOCATIONAL_ED_TRAINING_HOL=1,
        JOB_SKILLS_TRAINING_HOP=1,
        JOB_SKILLS_TRAINING_EA=1,
        JOB_SKILLS_TRAINING_HOL=1,
        ED_NO_HIGH_SCHOOL_DIPL_HOP=1,
        ED_NO_HIGH_SCHOOL_DIPL_EA=1,
        ED_NO_HIGH_SCHOOL_DIPL_HOL=1,
        SCHOOL_ATTENDENCE_HOP=1,
        SCHOOL_ATTENDENCE_EA=1,
        SCHOOL_ATTENDENCE_HOL=1,
        PROVIDE_CC_HOP=1,
        PROVIDE_CC_EA=1,
        PROVIDE_CC_HOL=1,
        OTHER_WORK_ACTIVITIES=1,
        DEEMED_HOURS_FOR_OVERALL=1,
        DEEMED_HOURS_FOR_TWO_PARENT=1,
        EARNED_INCOME=1,
        UNEARNED_INCOME_TAX_CREDIT=1,
        UNEARNED_SOCIAL_SECURITY=1,
        UNEARNED_SSI=1,
        UNEARNED_WORKERS_COMP=1,
        OTHER_UNEARNED_INCOME=1
    )

    assert submission.id is not None

    search = documents.ssp.SSP_M2DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_ssp_m3_submission():
    """SSP M3 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.ssp.SSP_M3.objects.create(
        RecordType=record_num,
        RPT_MONTH_YEAR=1,
        CASE_NUMBER='1',
        FIPS_CODE='1',

        FAMILY_AFFILIATION=1,
        DATE_OF_BIRTH=1,
        SSN='1',
        RACE_HISPANIC=1,
        RACE_AMER_INDIAN=1,
        RACE_ASIAN=1,
        RACE_BLACK=1,
        RACE_HAWAIIAN=1,
        RACE_WHITE=1,
        GENDER=1,
        RECEIVE_NONSSI_BENEFITS=1,
        RECEIVE_SSI=1,
        RELATIONSHIP_HOH="01",
        PARENT_MINOR_CHILD=1,
        EDUCATION_LEVEL=1,
        CITIZENSHIP_STATUS=1,
        UNEARNED_SSI=1,
        OTHER_UNEARNED_INCOME=1,
    )

    assert submission.id is not None

    search = documents.ssp.SSP_M3DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1
