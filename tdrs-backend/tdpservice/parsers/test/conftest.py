"""Fixtures for parsing integration tests."""
import pytest
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.test.factories import DataFileSummaryFactory, ParsingFileFactory
from tdpservice.parsers import util

@pytest.fixture
def small_correct_file(stt_user, stt):
    """Fixture for small_correct_file."""
    return util.create_test_datafile('small_correct_file.txt', stt_user, stt)

@pytest.fixture
def header_datafile(stt_user, stt):
    """Fixture for header test."""
    return util.create_test_datafile('tanf_section1_header_test.txt', stt_user, stt)

@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.build()

@pytest.fixture
def t2_invalid_dob_file():
    """Fixture for T2 file with an invalid DOB."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='t2_invalid_dob_file.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A25   TAN1ED\n'
                    b'T22020101111111111212Q897$9 3WTTTTTY@W222122222222101221211001472201140000000000000000000000000'
                    b'0000000000000000000000000000000000000000000000000000000000291\n'
                    b'TRAILER0000001         ')
    )
    return parsing_file

@pytest.fixture
def t3_cat2_invalid_citizenship_file():
    """Fixture for T3 file with an invalid CITIZENSHIP_STATUS."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='t3_invalid_citizenship_file.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A06   TAN1ED\n'
                    b'T320201011111111112420190127WTTTT90W022212222204398000000000\n'
                    b'T320201011111111112420190127WTTTT90W0222122222043981000000004201001013333333330000000'
                    b'1100000099998888\n'
                    b'TRAILER0000002         ')
    )
    return parsing_file

@pytest.fixture
def big_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP1.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP1.TS06', stt_user, stt)

@pytest.fixture
def bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S2."""
    return util.create_test_datafile('bad_TANF_S2.txt', stt_user, stt)

@pytest.fixture
def bad_file_missing_header(stt_user, stt):
    """Fixture for bad_missing_header."""
    return util.create_test_datafile('bad_missing_header.txt', stt_user, stt)

@pytest.fixture
def bad_file_multiple_headers(stt_user, stt):
    """Fixture for bad_two_headers."""
    return util.create_test_datafile('bad_two_headers.txt', stt_user, stt)

@pytest.fixture
def big_bad_test_file(stt_user, stt):
    """Fixture for bad_TANF_S1."""
    return util.create_test_datafile('bad_TANF_S1.txt', stt_user, stt)

@pytest.fixture
def bad_trailer_file(stt_user, stt):
    """Fixture for bad_trailer_1."""
    return util.create_test_datafile('bad_trailer_1.txt', stt_user, stt)

@pytest.fixture
def bad_trailer_file_2(stt_user, stt):
    """Fixture for bad_trailer_2."""
    return util.create_test_datafile('bad_trailer_2.txt', stt_user, stt)

@pytest.fixture
def empty_file(stt_user, stt):
    """Fixture for empty_file."""
    return util.create_test_datafile('empty_file', stt_user, stt)

@pytest.fixture
def small_ssp_section1_datafile(stt_user, stt):
    """Fixture for small_ssp_section1."""
    return util.create_test_datafile('small_ssp_section1.txt', stt_user, stt, 'SSP Active Case Data')

@pytest.fixture
def ssp_section1_datafile(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return util.create_test_datafile('ssp_section1_datafile.txt', stt_user, stt, 'SSP Active Case Data')

@pytest.fixture
def small_tanf_section1_datafile(stt_user, stt):
    """Fixture for small_tanf_section1."""
    return util.create_test_datafile('small_tanf_section1.txt', stt_user, stt)

@pytest.fixture
def super_big_s1_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM1.TS53_fake."""
    return util.create_test_datafile('ADS.E2J.NDM1.TS53_fake.txt', stt_user, stt)

@pytest.fixture
def big_s1_rollback_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM1.TS53_fake.rollback."""
    return util.create_test_datafile('ADS.E2J.NDM1.TS53_fake.rollback.txt', stt_user, stt)

@pytest.fixture
def bad_tanf_s1__row_missing_required_field(stt_user, stt):
    """Fixture for small_tanf_section1."""
    return util.create_test_datafile('small_bad_tanf_s1.txt', stt_user, stt)

@pytest.fixture
def bad_ssp_s1__row_missing_required_field(stt_user, stt):
    """Fixture for ssp_section1_datafile."""
    return util.create_test_datafile('small_bad_ssp_s1.txt', stt_user, stt, 'SSP Active Case Data')

@pytest.fixture
def small_tanf_section2_file(stt_user, stt):
    """Fixture for tanf section2 datafile."""
    return util.create_test_datafile('small_tanf_section2.txt', stt_user, stt, 'Closed Case Data')

@pytest.fixture
def tanf_section2_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP2.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP2.TS06', stt_user, stt, 'Closed Case Data')

@pytest.fixture
def tanf_section3_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP3.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP3.TS06', stt_user, stt, "Aggregate Data")

@pytest.fixture
def tanf_section1_file_with_blanks(stt_user, stt):
    """Fixture for ADS.E2J.FTP3.TS06."""
    return util.create_test_datafile('tanf_section1_blanks.txt', stt_user, stt)

@pytest.fixture
def tanf_section4_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP4.TS06', stt_user, stt, "Stratum Data")

@pytest.fixture
def bad_tanf_section4_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('bad_tanf_section_4.txt', stt_user, stt, "Stratum Data")

@pytest.fixture
def ssp_section4_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM4.MS24."""
    return util.create_test_datafile('ADS.E2J.NDM4.MS24', stt_user, stt, "SSP Stratum Data")

@pytest.fixture
def ssp_section2_rec_oadsi_file(stt_user, stt):
    """Fixture for sp_section2_rec_oadsi_file."""
    return util.create_test_datafile('ssp_section2_rec_oadsi_file.txt', stt_user, stt, 'SSP Closed Case Data')

@pytest.fixture
def ssp_section2_file(stt_user, stt):
    """Fixture for ADS.E2J.NDM2.MS24."""
    return util.create_test_datafile('ADS.E2J.NDM2.MS24', stt_user, stt, 'SSP Closed Case Data')

@pytest.fixture
def ssp_section3_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP3.TS06."""
    return util.create_test_datafile('ADS.E2J.NDM3.MS24', stt_user, stt, "SSP Aggregate Data")

@pytest.fixture
def tribal_section_1_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP1.TS142', stt_user, stt, "Tribal Active Case Data")

@pytest.fixture
def tribal_section_1_inconsistency_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('tribal_section_1_inconsistency.txt', stt_user, stt, "Tribal Active Case Data")

@pytest.fixture
def tribal_section_2_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP4.TS06."""
    return util.create_test_datafile('ADS.E2J.FTP2.TS142.txt', stt_user, stt, "Tribal Closed Case Data")

@pytest.fixture
def tribal_section_3_file(stt_user, stt):
    """Fixture for ADS.E2J.FTP3.TS142."""
    return util.create_test_datafile('ADS.E2J.FTP3.TS142', stt_user, stt, "Tribal Aggregate Data")

@pytest.fixture
def tribal_section_4_file(stt_user, stt):
    """Fixture for tribal_section_4_fake.txt."""
    return util.create_test_datafile('tribal_section_4_fake.txt', stt_user, stt, "Tribal Stratum Data")

@pytest.fixture
def tanf_section_4_file_with_errors(stt_user, stt):
    """Fixture for tanf_section4_with_errors."""
    return util.create_test_datafile('tanf_section4_with_errors.txt', stt_user, stt, "Stratum Data")

@pytest.fixture
def aggregates_rejected_datafile(stt_user, stt):
    """Fixture for aggregates_rejected."""
    return util.create_test_datafile('aggregates_rejected.txt', stt_user, stt)

@pytest.fixture
def no_records_file(stt_user, stt):
    """Fixture for tanf_section4_with_errors."""
    return util.create_test_datafile('no_records.txt', stt_user, stt)

@pytest.fixture
def tanf_section_1_file_with_bad_update_indicator(stt_user, stt):
    """Fixture for tanf_section_1_file_with_bad_update_indicator."""
    return util.create_test_datafile('tanf_s1_bad_update_indicator.txt', stt_user, stt, "Active Case Data")

@pytest.fixture
def tribal_section_4_bad_quarter(stt_user, stt):
    """Fixture for tribal_section_4_bad_quarter."""
    return util.create_test_datafile('tribal_section_4_fake_bad_quarter.txt', stt_user, stt, "Tribal Stratum Data")

@pytest.fixture
def t4_t5_empty_values():
    """Fixture for T3 file."""
    # T3 record is space filled correctly
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q3',
        original_filename='t4_t5_empty_values.txt',
        section=DataFile.Section.CLOSED_CASE_DATA,
        file__filename='t4_t5_empty_values.txt',
        file__data=(b'HEADER20212C06   TAN1ED\n' +
                    b'T420210411111111158253  400141123113                                   \n' +
                    b'T520210411111111158119970123WTTTTTP@Y2222212222221011212100946200000000\n' +
                    b'TRAILER0000001         ')
    )
    return parsing_file

@pytest.fixture
def second_child_only_space_t3_file():
    """Fixture for misformatted_t3_file."""
    # T3 record: second child is not space filled correctly
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q3',
        original_filename='second_child_only_space_t3_file.txt',
        file__name='second_child_only_space_t3_file.txt',
        file__section=DataFile.Section.ACTIVE_CASE_DATA,
        file__data=(b'HEADER20212A25   TAN1 D\n' +
                    b'T120210400028221R0112014122311110232110374300000000000005450' +
                    b'320000000000000000000000000000000000222222000000002229021000' +
                    b'000000000000000000000000000000000000\n'
                    b'T320210400028221R0112014122888175617622222112204398100000000' +
                    b'                              \n' +
                    b'TRAILER0000001         ')
    )
    return parsing_file

@pytest.fixture
def one_child_t3_file():
    """Fixture for one child_t3_file."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q3',
        original_filename='one_child_t3_file.txt',
        file__name='one_child_t3_file.txt',
        file__section=DataFile.Section.ACTIVE_CASE_DATA,
        file__data=(b'HEADER20212A25   TAN1 D\n' +
                    b'T120210400028221R0112014122311110232110374300000000000005450' +
                    b'320000000000000000000000000000000000222222000000002229021000' +
                    b'000000000000000000000000000000000000\n'
                    b'T320210400028221R0112014122888175617622222112204398100000000\n' +
                    b'TRAILER0000001         ')
    )
    return parsing_file

@pytest.fixture
def t3_file():
    """Fixture for T3 file."""
    # T3 record is space filled correctly
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q3',
        original_filename='t3_file.txt',
        file__name='t3_file.txt',
        file__section=DataFile.Section.ACTIVE_CASE_DATA,
        file__data=(b'HEADER20212A25   TAN1ED\n' +
                    b'T12021044111111111512014122311110232110374300000000000005450' +
                    b'320000000000000000000000000000000000222222000000002229021000' +
                    b'000000000000000000000000000000000000\n'
                    b'T320210441111111115120160401WTTTT@BTB22212212204398100000000' +
                    b'                                                            ' +
                    b'                                    \n' +
                    b'TRAILER0000001         ')
    )
    return parsing_file


@pytest.fixture
def t3_file_two_child():
    """Fixture for T3 file."""
    # T3 record is space filled correctly
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q2',
        original_filename='t3_file.txt',
        file__name='t3_file.txt',
        file__section=DataFile.Section.ACTIVE_CASE_DATA,
        file__data=(b'HEADER20211A25   TAN1ED\n' +
                    b'T12021021111111115712014122311110232110374300000000000005450' +
                    b'320000000000000000000000000000000000222222000000002229021000' +
                    b'000000000000000000000000000000000000\n'
                    b'T320210211111111157120190527WTTTTT9WT12212122204398100000000' +
                    b'420100125WTTTT9@TB1221222220430490000\n' +
                    b'TRAILER0000001         ')
    )
    return parsing_file

@pytest.fixture
def t3_file_two_child_with_space_filled():
    """Fixture for T3 file."""
    # T3 record is space filled correctly
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q2',
        original_filename='t3_file_two_child_with_space_filled.txt',
        file__name='t3_file_two_child_with_space_filled.txt',
        file__section=DataFile.Section.ACTIVE_CASE_DATA,
        file__data=(b'HEADER20211A25   TAN1ED\n' +
                    b'T12021021111111115712014122311110232110374300000000000005450' +
                    b'320000000000000000000000000000000000222222000000002229021000' +
                    b'000000000000000000000000000000000000\n'
                    b'T320210211111111157120190527WTTTTT9WT12212122204398100000000' +
                    b'420100125WTTTT9@TB1221222220430490000                       \n' +
                    b'TRAILER0000001         ')
    )
    return parsing_file


@pytest.fixture
def two_child_second_filled():
    """Fixture for T3 file."""
    # T3 record is space filled correctly
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q2',
        original_filename='two_child_second_filled.txt',
        file__name='two_child_second_filled.txt',
        file__section=DataFile.Section.ACTIVE_CASE_DATA,
        file__data=(b'HEADER20211A25   TAN1ED\n' +
                    b'T12021021111111111512014122311110232110374300000000000005450' +
                    b'320000000000000000000000000000000000222222000000002229021000' +
                    b'000000000000000000000000000000000000\n'
                    b'T320210211111111115120160401WTTTT@BTB22212212204398100000000' +
                    b'56      111111111                                           ' +
                    b'                                    \n' +
                    b'TRAILER0000001         ')
    )
    return parsing_file


@pytest.fixture
def t3_file_zero_filled_second():
    """Fixture for T3 file."""
    # T3 record is space filled correctly
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q3',
        original_filename='t3_file_zero_filled_second.txt',
        file__name='t3_file_zero_filled_second.txt',
        file__section=DataFile.Section.ACTIVE_CASE_DATA,
        file__data=(b'HEADER20212A25   TAN1ED\n' +
                    b'T12021044111111111512014122311110232110374300000000000005450' +
                    b'320000000000000000000000000000000000222222000000002229021000' +
                    b'000000000000000000000000000000000000\n'
                    b'T320210441111111115120160401WTTTT@BTB22212212204398100000000' +
                    b'000000000000000000000000000000000000000000000000000000000000' +
                    b'000000000000000000000000000000000000\n' +
                    b'TRAILER0000001         ')
    )
    return parsing_file

def m2_cat2_invalid_37_38_39_file():
    """Fixture for M2 file with an invalid EDUCATION_LEVEL, CITIZENSHIP_STATUS, COOPERATION_CHILD_SUPPORT."""
    parsing_file = ParsingFileFactory(
        year=2024,
        quarter='Q1',
        file__name='m2_cat2_invalid_37_38_39_file.txt',
        section='SSP Active Case Data',
        file__data=(b'HEADER20234A24   SSP1ED\n'
                    b'M2202310111111111275219811103WTTT#PW@W22212222222250122000010119350000000000000000000000000000000'
                    b'00000000000000000000000000000225300000000000000000000\n'
                    b'TRAILER0000001         ')
    )
    return parsing_file

def m3_cat2_invalid_68_69_file():
    """Fixture for M3 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
    parsing_file = ParsingFileFactory(
        year=2024,
        quarter='Q1',
        file__name='m3_cat2_invalid_68_69_file.txt',
        section='SSP Active Case Data',
        file__data=(b'HEADER20234A24   SSP1ED\n'
                    b'M320231011111111127420110615WTTTP99B#22212222204300000000000\n'
                    b'M320231011111111127120110615WTTTP99B#222122222043011000000004201001013333333330000000110000009999'
                    b'8888\n'
                    b'TRAILER0000002         ')
    )
    return parsing_file

def m5_cat2_invalid_23_24_file():
    """Fixture for M5 file with an invalid EDUCATION_LEVEL and CITIZENSHIP_STATUS."""
    parsing_file = ParsingFileFactory(
        year=2024,
        quarter='Q1',
        file__name='m5_cat2_invalid_23_24_file.txt',
        section='SSP Closed Case Data',
        file__data=(b'HEADER20184C24   SSP1ED\n'
                    b'M520181011111111161519791106WTTTY0ZB922212222222210112000112970000\n'
                    b'TRAILER0000001         ')
    )
    return parsing_file

@pytest.fixture
def tanf_s1_exact_dup_file():
    """Fixture for a section 1 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='s1_exact_duplicate.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A06   TAN1 D\n'
                    b'T12020101111111111223003403361110212120000300000000000008730010000000000000000000000' +
                    b'000000000000222222000000002229012                                       \n'
                    b'T12020101111111111223003403361110212120000300000000000008730010000000000000000000000' +
                    b'000000000000222222000000002229012                                       \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s2_exact_dup_file():
    """Fixture for a section 2 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        section="Closed Case Data",
        file__name='s2_exact_duplicate.txt',
        file__section='Closed Case Data',
        file__data=(b'HEADER20204C06   TAN1ED\n'
                    b'T42020101111111115825301400141123113                                   \n'
                    b'T42020101111111115825301400141123113                                   \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s3_exact_dup_file():
    """Fixture for a section 3 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2022,
        quarter='Q1',
        section="Aggregate Data",
        file__name='s3_exact_duplicate.txt',
        file__section='Aggregate Data',
        file__data=(b'HEADER20214G06   TAN1 D\n'
                    b'T620214000127470001104500011146000043010000397700003924000084460000706800007222'
                    b'0000550428490000551413780000566432530007558100075921000755420000098100000970000'
                    b'0096800039298000393490003897200035302000356020003560200168447001690470016810700'
                    b'0464480004649800046203001219990012254900121904000001630000014900000151000003440'
                    b'000033100000276000002580000024100000187000054530000388100003884\n'
                    b'T620214000127470001104500011146000043010000397700003924000084460000706800007222'
                    b'0000550428490000551413780000566432530007558100075921000755420000098100000970000'
                    b'0096800039298000393490003897200035302000356020003560200168447001690470016810700'
                    b'0464480004649800046203001219990012254900121904000001630000014900000151000003440'
                    b'000033100000276000002580000024100000187000054530000388100003884\n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s4_exact_dup_file():
    """Fixture for a section 4 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2022,
        quarter='Q1',
        section="Stratum Data",
        file__name='s4_exact_duplicate.txt',
        file__section='Stratum Data',
        file__data=(b'HEADER20214S06   TAN1 D\n'
                    b'T720214101006853700680540068454103000312400037850003180104000347400036460003583106'
                    b'000044600004360000325299000506200036070003385202000039100002740000499             '
                    b'                                                                                   \n'
                    b'T720214101006853700680540068454103000312400037850003180104000347400036460003583106'
                    b'000044600004360000325299000506200036070003385202000039100002740000499             '
                    b'                                                                                   \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s1_exact_dup_file():
    """Fixture for a section 1 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2019,
        quarter='Q1',
        section='SSP Active Case Data',
        file__name='s1_exact_duplicate.txt',
        file__section='SSP Active Case Data',
        file__data=(b'HEADER20184A24   SSP1ED\n'
                    b'M12018101111111112721401400351021331100273000000000000000105400000000000000000000000000000'
                    b'00000222222000000002229                                     \n'
                    b'M12018101111111112721401400351021331100273000000000000000105400000000000000000000000000000'
                    b'00000222222000000002229                                     \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s2_exact_dup_file():
    """Fixture for a section 2 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2019,
        quarter='Q1',
        section="SSP Closed Case Data",
        file__name='s2_exact_duplicate.txt',
        file__section='SSP Closed Case Data',
        file__data=(b'HEADER20184C24   SSP1ED\n'
                    b'M42018101111111116120000406911161113                              \n'
                    b'M42018101111111116120000406911161113                              \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s3_exact_dup_file():
    """Fixture for a section 3 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2022,
        quarter='Q1',
        section="SSP Aggregate Data",
        file__name='s3_exact_duplicate.txt',
        file__section='SSP Aggregate Data',
        file__data=(b'HEADER20214G24   SSP1 D\n'
                    b'M6202140001586900016008000159560000086100000851000008450001490500015055000150130000010300000'
                    b'10200000098000513550005169600051348000157070001581400015766000356480003588200035582000000000'
                    b'000000000000000000000000000000000000000000000000000000012020000118900001229\n'
                    b'M6202140001586900016008000159560000086100000851000008450001490500015055000150130000010300000'
                    b'10200000098000513550005169600051348000157070001581400015766000356480003588200035582000000000'
                    b'000000000000000000000000000000000000000000000000000000012020000118900001229\n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s4_exact_dup_file():
    """Fixture for a section 4 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2022,
        quarter='Q1',
        section="SSP Stratum Data",
        file__name='s4_exact_duplicate.txt',
        file__section='SSP Stratum Data',
        file__data=(b'HEADER20214S24   SSP1 D\n'
                    b'M7202141010001769000131000011111020000748000076700007681030013352001393100140772000001202000'
                    b'11890001229                                                                                 '
                    b'                                                               \n'
                    b'M7202141010001769000131000011111020000748000076700007681030013352001393100140772000001202000'
                    b'11890001229                                                                                 '
                    b'                                                               \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s1_partial_dup_file():
    """Fixture for a section 1 file containing an partial duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        file__name='s1_partial_duplicate.txt',
        file__section='Active Case Data',
        file__data=(b'HEADER20204A06   TAN1 D\n'
                    b'T120201011111111112230034033611102121200003000000000000087300100000000000000' +
                    b'00000000000000000000222222000000002229012                                       \n'
                    b'T1202010111111111122300340336111021212000030000000000000873001000000000000000' +
                    b'0000000000000000000222222000000002229013                                       \n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def tanf_s2_partial_dup_file():
    """Fixture for a section 2 file containing an partial duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2021,
        quarter='Q1',
        section="Closed Case Data",
        file__name='s2_partial_duplicate.txt',
        file__section='Closed Case Data',
        file__data=(b'HEADER20204C06   TAN1ED\n'
                    b'T520201011111111158120160206WTTTT90TY2222212 2  2 0422981      00000000\n'
                    b'T520201011111111158120160206WTTTT90TY2222212 2  2 0422981      00000001\n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def ssp_s1_partial_dup_file():
    """Fixture for a section 1 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2019,
        quarter='Q1',
        section='SSP Active Case Data',
        file__name='s1_exact_duplicate.txt',
        file__section='SSP Active Case Data',
        file__data=(b'HEADER20184A24   SSP1ED\n'
                    b'M12018101111111112721401400351021331100273000000000000000105400000000000000000000000000'
                    b'00000000222222000000002229                                     \n'
                    b'M12018101111111112721401400351021331100273000000000000000105400000000000000000000000000'
                    b'00000000222222000000002228                                     \n'
                    b'TRAILER0000001         '
                    )
    )

@pytest.fixture
def ssp_s2_partial_dup_file():
    """Fixture for a section 2 file containing an exact duplicate record."""
    parsing_file = ParsingFileFactory(
        year=2019,
        quarter='Q1',
        section="SSP Closed Case Data",
        file__name='s2_exact_duplicate.txt',
        file__section='SSP Closed Case Data',
        file__data=(b'HEADER20184C24   SSP1ED\n'
                    b'M520181011111111161120150623WTTTYT#0W222122222222 0422981     0000\n'
                    b'M520181011111111161120150623WTTTYT#0W222122222222 0422981     0001\n'
                    b'TRAILER0000001         '
                    )
    )
    return parsing_file

@pytest.fixture
def partial_dup_t1_err_msg():
    """Fixture for t1 record partial duplicate error."""
    return ("Partial duplicate record detected with record type {record_type} at line 3. Record is a partial "
            "duplicate of the record at line number 2. Duplicated fields causing error: record type, "
            "reporting month and year, and case number.")

@pytest.fixture
def partial_dup_t5_err_msg():
    """Fixture for t5 record partial duplicate error."""
    return ("Partial duplicate record detected with record type {record_type} at line 3. Record is a partial "
            "duplicate of the record at line number 2. Duplicated fields causing error: record type, "
            "reporting month and year, case number, family affiliation, date of birth, and social security number.")
