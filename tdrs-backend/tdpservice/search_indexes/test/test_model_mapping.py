"""Tests for elasticsearch model mapping."""

import pytest
from faker import Faker
from django.db.utils import IntegrityError
from tdpservice.search_indexes import models
from tdpservice.search_indexes import documents


fake = Faker()


@pytest.mark.django_db
def test_can_create_and_index_tanf_t1_submission():
    """TANF T1 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T1.objects.create(
        RecordType=record_num,
        RPT_MONTH_YEAR=1,
        CASE_NUMBER=1,
        COUNTY_FIPS_CODE=1,
        STRATUM=1,
        ZIP_CODE=1,
        FUNDING_STREAM=1,
        DISPOSITION=1,
        NEW_APPLICANT=1,
        NBR_FAMILY_MEMBERS=1,
        FAMILY_TYPE=1,
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
        FAMILY_EXEMPT_TIME_LIMITS=1,
        FAMILY_NEW_CHILD=1,
    )

    # submission.full_clean()

    assert submission.id is not None

    search = documents.tanf.TANF_T1DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t2_submission():
    """TANF T2 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T2.objects.create(
        RecordType=record_num,
        RPT_MONTH_YEAR=1,
        CASE_NUMBER='1',

        FAMILY_AFFILIATION=1,
        NONCUSTODIAL_PARENT=1,
        DATE_OF_BIRTH=1,
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
        RELATIONSHIP_HOH=1,
        PARENT_WITH_MINOR_CHILD=1,
        NEEDS_PREGNANT_WOMAN=1,
        EDUCATION_LEVEL=1,
        CITIZENSHIP_STATUS=1,
        COOPERATION_CHILD_SUPPORT=1,
        MONTHS_FED_TIME_LIMIT=1,
        MONTHS_STATE_TIME_LIMIT=1,
        CURRENT_MONTH_STATE_EXEMPT=1,
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

    search = documents.tanf.TANF_T2DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t3_submission():
    """TANF T3 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T3.objects.create(
        RecordType=record_num,
        RPT_MONTH_YEAR=1,
        CASE_NUMBER='1',

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
        RECEIVE_NONSSA_BENEFITS=1,
        RECEIVE_SSI=1,
        RELATIONSHIP_HOH=1,
        PARENT_MINOR_CHILD=1,
        EDUCATION_LEVEL=1,
        CITIZENSHIP_STATUS=1,
        UNEARNED_SSI=1,
        OTHER_UNEARNED_INCOME=1,
    )

    assert submission.id is not None

    search = documents.tanf.TANF_T3DataSubmissionDocument.search().query(
        'match',
        RecordType=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t4_submission():
    """TANF T4 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T4.objects.create(
        record=record_num,
        rpt_month_year=1,
        case_number='1',
        disposition=1,
        fips_code='1',

        county_fips_code='1',
        stratum=1,
        zip_code='1',
        closure_reason=1,
        rec_sub_housing=1,
        rec_med_assist=1,
        rec_food_stamps=1,
        rec_sub_cc=1,
    )

    assert submission.id is not None

    search = documents.tanf.TANF_T4DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t5_submission():
    """TANF T5 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T5.objects.create(
        record=record_num,
        rpt_month_year=1,
        case_number='1',
        fips_code='1',

        family_affiliation=1,
        date_of_birth='1',
        ssn='1',
        race_hispanic=1,
        race_amer_indian=1,
        race_asian=1,
        race_black=1,
        race_hawaiian=1,
        race_white=1,
        gender=1,
        rec_oasdi_insurance=1,
        rec_federal_disability=1,
        rec_aid_totally_disabled=1,
        rec_aid_aged_blind=1,
        rec_ssi=1,
        marital_status=1,
        relationship_hoh=1,
        parent_minor_child=1,
        needs_of_pregnant_woman=1,
        education_level=1,
        citizenship_status=1,
        countable_month_fed_time=1,
        countable_months_state_tribe=1,
        employment_status=1,
        amount_earned_income=1,
        amount_unearned_income=1
    )

    assert submission.id is not None

    search = documents.tanf.TANF_T5DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t6_submission():
    """TANF T6 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T6.objects.create(
        record=record_num,
        rpt_month_year=1,
        fips_code='1',

        calendar_quarter=1,
        applications=1,
        approved=1,
        denied=1,
        assistance=1,
        families=1,
        num_2_parents=1,
        num_1_parents=1,
        num_no_parents=1,
        recipients=1,
        adult_recipients=1,
        child_recipients=1,
        noncustodials=1,
        births=1,
        outwedlock_births=1,
        closed_cases=1,
    )

    assert submission.id is not None

    search = documents.tanf.TANF_T6DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


@pytest.mark.django_db
def test_can_create_and_index_tanf_t7_submission():
    """TANF T7 submissions can be created and mapped."""
    record_num = fake.uuid4()

    submission = models.tanf.TANF_T7.objects.create(
        record=record_num,
        rpt_month_year=1,
        fips_code='2',

        calendar_quarter=1,
        tdrs_section_ind='1',
        stratum='1',
        families=1
    )

    assert submission.id is not None

    search = documents.tanf.TANF_T7DataSubmissionDocument.search().query(
        'match',
        record=record_num
    )
    response = search.execute()

    assert response.hits.total.value == 1


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
        CASE_NUMBER=1,
        COUNTY_FIPS_CODE=1,
        STRATUM=1,
        ZIP_CODE=1,
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
        RELATIONSHIP_HOH=1,
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
        RELATIONSHIP_HOH=1,
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
