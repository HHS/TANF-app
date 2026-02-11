"""Test cases for datafile_retention_tasks.py functions."""

from datetime import datetime
from unittest.mock import patch

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.scheduling.datafile_retention_tasks import remove_all_old_versions
from tdpservice.search_indexes.models.fra import TANF_Exiter1
from tdpservice.search_indexes.models.ssp import SSP_M1
from tdpservice.search_indexes.models.tanf import TANF_T1
from tdpservice.search_indexes.models.tribal import Tribal_TANF_T1
from tdpservice.stts.models import STT, Region


@pytest.fixture
def second_stt():
    """Create a second STT for tests that need multiple STTs."""
    region, _ = Region.objects.get_or_create(id=6)
    stt, _ = STT.objects.get_or_create(name="California", region=region, stt_code="06")
    return stt


def create_tanf_t1_record(datafile):
    """Create a TANF_T1 record linked to the given DataFile."""
    return TANF_T1.objects.create(
        datafile=datafile,
        RecordType="T1",
        RPT_MONTH_YEAR=202001,
        CASE_NUMBER="12345678901",
    )


def create_ssp_m1_record(datafile):
    """Create an SSP_M1 record linked to the given DataFile."""
    return SSP_M1.objects.create(
        datafile=datafile,
        RecordType="M1",
        RPT_MONTH_YEAR=202001,
        CASE_NUMBER="12345678901",
    )


def create_tribal_t1_record(datafile):
    """Create a Tribal_TANF_T1 record linked to the given DataFile."""
    return Tribal_TANF_T1.objects.create(
        datafile=datafile,
        RecordType="T1",
        RPT_MONTH_YEAR=202001,
        CASE_NUMBER="12345678901",
    )


def create_fra_exiter1_record(datafile):
    """Create a TANF_Exiter1 (FRA) record linked to the given DataFile."""
    return TANF_Exiter1.objects.create(
        datafile=datafile,
        RecordType="TE1",
        EXIT_DATE=202001,
        SSN="123456789",
    )


@pytest.mark.django_db
class TestRemoveAllOldVersions:
    """Test suite for the remove_all_old_versions function."""

    def test_retains_newest_file_when_multiple_versions_exist(self, stt, user):
        """Test that the newest file is retained when multiple versions exist.

        Given: Multiple versions of the same file (same year, quarter, program_type, section, stt)
        When: remove_all_old_versions is called
        Then: Only the newest version (highest version number) should be retained
        """
        current_year = datetime.now().year

        # Create multiple versions of the same file
        file_v1 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        file_v2 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=2,
        )
        file_v3 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=3,
        )

        # Create records for each file version
        record_v1 = create_tanf_t1_record(file_v1)
        record_v2 = create_tanf_t1_record(file_v2)
        record_v3 = create_tanf_t1_record(file_v3)

        remove_all_old_versions()

        # Records for older versions should be deleted
        assert not TANF_T1.objects.filter(id=record_v1.id).exists()
        assert not TANF_T1.objects.filter(id=record_v2.id).exists()
        # Record for newest version should be retained
        assert TANF_T1.objects.filter(id=record_v3.id).exists()

    def test_different_program_types_all_retained(self, stt, user):
        """Test that files with different program types are ALL retained.

        This is the CRITICAL test case that would have caught the production incident.
        Files with different program_type values but the same (year, quarter, section, stt)
        must all be retained because they represent different data.

        Given: Files with different program types (TANF, SSP, TRIBAL) but same
               (year, quarter, section, stt)
        When: remove_all_old_versions is called
        Then: ALL files should be retained - none should be deleted
        """
        current_year = datetime.now().year

        tanf_file = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        ssp_file = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="SSP",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        tribal_file = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TRIBAL",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )

        # Create records for each program type
        tanf_record = create_tanf_t1_record(tanf_file)
        ssp_record = create_ssp_m1_record(ssp_file)
        tribal_record = create_tribal_t1_record(tribal_file)

        remove_all_old_versions()

        # ALL records should be retained - they are different program types
        assert TANF_T1.objects.filter(id=tanf_record.id).exists()
        assert SSP_M1.objects.filter(id=ssp_record.id).exists()
        assert Tribal_TANF_T1.objects.filter(id=tribal_record.id).exists()

    def test_mixed_scenario_program_types_with_versions(self, stt, user):
        """Test a complex scenario with different program types AND multiple versions.

        Given: Multiple versions of TANF files AND a single SSP file with same
               (year, quarter, section, stt)
        When: remove_all_old_versions is called
        Then: Only older TANF versions should be deleted, newest TANF and SSP should remain
        """
        current_year = datetime.now().year

        # TANF files - multiple versions
        tanf_v1 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        tanf_v2 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=2,
        )

        # SSP file - single version
        ssp_v1 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="SSP",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )

        # Create records
        tanf_record_v1 = create_tanf_t1_record(tanf_v1)
        tanf_record_v2 = create_tanf_t1_record(tanf_v2)
        ssp_record = create_ssp_m1_record(ssp_v1)

        remove_all_old_versions()

        # tanf_v1 record should be deleted (older version of TANF)
        assert not TANF_T1.objects.filter(id=tanf_record_v1.id).exists()
        # tanf_v2 record should be retained (newest TANF version)
        assert TANF_T1.objects.filter(id=tanf_record_v2.id).exists()
        # SSP record should be retained (only version, different program type)
        assert SSP_M1.objects.filter(id=ssp_record.id).exists()

    def test_no_deletion_when_single_version_exists(self, stt, user):
        """Test that no files are deleted when only one version exists.

        Given: Single version files for different (year, quarter, program_type, section, stt)
        When: remove_all_old_versions is called
        Then: No files should be deleted
        """
        current_year = datetime.now().year

        file_1 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        file_2 = DataFileFactory.create(
            year=current_year,
            quarter="Q2",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        file_3 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="SSP",
            section="Closed Case Data",
            stt=stt,
            user=user,
            version=1,
        )

        # Create records for each file
        record_1 = create_tanf_t1_record(file_1)
        record_2 = create_tanf_t1_record(file_2)
        record_3 = create_ssp_m1_record(file_3)

        remove_all_old_versions()

        # None of these single-version files' records should be deleted
        assert TANF_T1.objects.filter(id=record_1.id).exists()
        assert TANF_T1.objects.filter(id=record_2.id).exists()
        assert SSP_M1.objects.filter(id=record_3.id).exists()

    @patch("tdpservice.scheduling.datafile_retention_tasks.log")
    def test_logs_warning_for_years_outside_valid_range(self, mock_log, stt, user):
        """Test that a warning is logged for files with years outside valid range.

        Given: Files with years before 2019 or after the current year
        When: remove_all_old_versions is called
        Then: A warning should be logged about these files
        """
        # Create a file with year outside the valid range (before 2019)
        DataFileFactory.create(
            year=2018,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )

        remove_all_old_versions()

        # Find the warning log call
        warning_calls = [
            call
            for call in mock_log.call_args_list
            if call[1].get("level") == "warning"
        ]

        assert len(warning_calls) > 0
        warning_message = warning_calls[0][0][0]
        assert (
            "outside" in warning_message.lower() or "range" in warning_message.lower()
        )

    @patch("tdpservice.scheduling.datafile_retention_tasks.log")
    def test_logs_warning_for_future_year_files(self, mock_log, stt, user):
        """Test that a warning is logged for files with future years.

        Given: Files with year greater than the current year
        When: remove_all_old_versions is called
        Then: A warning should be logged about these files needing manual cleanup
        """
        future_year = datetime.now().year + 1

        DataFileFactory.create(
            year=future_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )

        remove_all_old_versions()

        # Find the warning log call
        warning_calls = [
            call
            for call in mock_log.call_args_list
            if call[1].get("level") == "warning"
        ]

        assert len(warning_calls) > 0
        warning_message = warning_calls[0][0][0]
        assert "manual cleanup" in warning_message.lower()

    @patch("tdpservice.scheduling.datafile_retention_tasks.log")
    def test_exception_handling_continues_processing(
        self, mock_log, stt, second_stt, user
    ):
        """Test that exception handling allows processing to continue.

        Given: delete_records raises an exception for one file group
        When: remove_all_old_versions is called
        Then: Processing should continue for other file groups and log errors
        """
        current_year = datetime.now().year
        stt_2 = second_stt

        # Create files for two different STTs with multiple versions
        DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=2,
        )

        DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt_2,
            user=user,
            version=1,
        )
        DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt_2,
            user=user,
            version=2,
        )

        # Patch delete_records to raise an exception on first call only
        call_count = [0]
        original_delete_records = __import__(
            "tdpservice.search_indexes.utils", fromlist=["delete_records"]
        ).delete_records

        def side_effect(file_ids, log_context):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Test exception")
            return original_delete_records(file_ids, log_context)

        with patch(
            "tdpservice.scheduling.datafile_retention_tasks.delete_records",
            side_effect=side_effect,
        ):
            # Should not raise an exception - the function should handle it
            remove_all_old_versions()

        # Verify error was logged
        error_calls = [
            call for call in mock_log.call_args_list if call[1].get("level") == "error"
        ]
        assert len(error_calls) > 0

    def test_handles_all_quarters(self, stt, user):
        """Test that files from all quarters are processed correctly.

        Given: Files for all four quarters with multiple versions
        When: remove_all_old_versions is called
        Then: Older versions from all quarters should be deleted
        """
        current_year = datetime.now().year
        quarters = ["Q1", "Q2", "Q3", "Q4"]
        old_records = []
        new_records = []

        for quarter in quarters:
            old_file = DataFileFactory.create(
                year=current_year,
                quarter=quarter,
                program_type="TAN",
                section="Active Case Data",
                stt=stt,
                user=user,
                version=1,
            )
            new_file = DataFileFactory.create(
                year=current_year,
                quarter=quarter,
                program_type="TAN",
                section="Active Case Data",
                stt=stt,
                user=user,
                version=2,
            )
            old_records.append(create_tanf_t1_record(old_file))
            new_records.append(create_tanf_t1_record(new_file))

        remove_all_old_versions()

        # All old version records should be deleted
        for old_record in old_records:
            assert not TANF_T1.objects.filter(id=old_record.id).exists()

        # All new version records should be retained
        for new_record in new_records:
            assert TANF_T1.objects.filter(id=new_record.id).exists()

    def test_handles_all_sections(self, stt, user):
        """Test that files from all sections are processed correctly.

        Given: Files for different sections with multiple versions
        When: remove_all_old_versions is called
        Then: Older versions from all sections should be deleted
        """
        current_year = datetime.now().year
        sections = [
            "Active Case Data",
            "Closed Case Data",
            "Aggregate Data",
            "Stratum Data",
        ]
        old_records = []
        new_records = []

        for section in sections:
            old_file = DataFileFactory.create(
                year=current_year,
                quarter="Q1",
                program_type="TAN",
                section=section,
                stt=stt,
                user=user,
                version=1,
            )
            new_file = DataFileFactory.create(
                year=current_year,
                quarter="Q1",
                program_type="TAN",
                section=section,
                stt=stt,
                user=user,
                version=2,
            )
            old_records.append(create_tanf_t1_record(old_file))
            new_records.append(create_tanf_t1_record(new_file))

        remove_all_old_versions()

        for old_record in old_records:
            assert not TANF_T1.objects.filter(id=old_record.id).exists()

        for new_record in new_records:
            assert TANF_T1.objects.filter(id=new_record.id).exists()

    def test_handles_multiple_stts(self, stt, second_stt, user):
        """Test that files from multiple STTs are processed correctly.

        Given: Files for different STTs with multiple versions each
        When: remove_all_old_versions is called
        Then: Each STT's files should be processed independently
        """
        current_year = datetime.now().year
        stt_1 = stt
        stt_2 = second_stt

        # STT 1 files
        stt1_old = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt_1,
            user=user,
            version=1,
        )
        stt1_new = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt_1,
            user=user,
            version=2,
        )

        # STT 2 files
        stt2_old = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt_2,
            user=user,
            version=1,
        )
        stt2_new = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt_2,
            user=user,
            version=2,
        )

        # Create records
        stt1_old_record = create_tanf_t1_record(stt1_old)
        stt1_new_record = create_tanf_t1_record(stt1_new)
        stt2_old_record = create_tanf_t1_record(stt2_old)
        stt2_new_record = create_tanf_t1_record(stt2_new)

        remove_all_old_versions()

        # Old versions from both STTs should be deleted
        assert not TANF_T1.objects.filter(id=stt1_old_record.id).exists()
        assert not TANF_T1.objects.filter(id=stt2_old_record.id).exists()

        # New versions from both STTs should be retained
        assert TANF_T1.objects.filter(id=stt1_new_record.id).exists()
        assert TANF_T1.objects.filter(id=stt2_new_record.id).exists()

    def test_handles_fra_program_type(self, stt, user):
        """Test that FRA program type files are handled correctly.

        Given: FRA files with multiple versions
        When: remove_all_old_versions is called
        Then: Older FRA versions should be deleted, newest retained
        """
        current_year = datetime.now().year

        fra_old = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="FRA",
            section="Work Outcomes of TANF Exiters",
            stt=stt,
            user=user,
            version=1,
        )
        fra_new = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="FRA",
            section="Work Outcomes of TANF Exiters",
            stt=stt,
            user=user,
            version=2,
        )

        fra_old_record = create_fra_exiter1_record(fra_old)
        fra_new_record = create_fra_exiter1_record(fra_new)

        remove_all_old_versions()

        assert not TANF_Exiter1.objects.filter(id=fra_old_record.id).exists()
        assert TANF_Exiter1.objects.filter(id=fra_new_record.id).exists()

    def test_empty_database_no_errors(self):
        """Test that the function handles an empty database gracefully.

        Given: No files in the database
        When: remove_all_old_versions is called
        Then: No errors should occur
        """
        # Ensure no DataFiles exist
        DataFile.objects.all().delete()

        # Should not raise any exceptions
        remove_all_old_versions()

    def test_multiple_records_per_datafile_all_deleted(self, stt, user):
        """Test that all records associated with an old version are deleted.

        Given: A file with multiple associated records
        When: remove_all_old_versions is called on an older version
        Then: All associated records should be deleted
        """
        current_year = datetime.now().year

        old_file = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        new_file = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=2,
        )

        # Create multiple records for the old file
        old_record_1 = create_tanf_t1_record(old_file)
        old_record_2 = create_tanf_t1_record(old_file)
        old_record_3 = create_tanf_t1_record(old_file)

        # Create records for the new file
        new_record = create_tanf_t1_record(new_file)

        remove_all_old_versions()

        # All old file records should be deleted
        assert not TANF_T1.objects.filter(id=old_record_1.id).exists()
        assert not TANF_T1.objects.filter(id=old_record_2.id).exists()
        assert not TANF_T1.objects.filter(id=old_record_3.id).exists()

        # New file record should be retained
        assert TANF_T1.objects.filter(id=new_record.id).exists()

    def test_all_program_types_with_multiple_versions_each(self, stt, user):
        """Test all program types with multiple versions each.

        Given: Multiple versions for TANF, SSP, TRIBAL, and FRA files
        When: remove_all_old_versions is called
        Then: Only newest versions of each program type should remain
        """
        current_year = datetime.now().year

        # TANF
        tanf_v1 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        tanf_v2 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TAN",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=2,
        )

        # SSP
        ssp_v1 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="SSP",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        ssp_v2 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="SSP",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=2,
        )

        # TRIBAL
        tribal_v1 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TRIBAL",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=1,
        )
        tribal_v2 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="TRIBAL",
            section="Active Case Data",
            stt=stt,
            user=user,
            version=2,
        )

        # FRA
        fra_v1 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="FRA",
            section="Work Outcomes of TANF Exiters",
            stt=stt,
            user=user,
            version=1,
        )
        fra_v2 = DataFileFactory.create(
            year=current_year,
            quarter="Q1",
            program_type="FRA",
            section="Work Outcomes of TANF Exiters",
            stt=stt,
            user=user,
            version=2,
        )

        # Create records
        tanf_record_v1 = create_tanf_t1_record(tanf_v1)
        tanf_record_v2 = create_tanf_t1_record(tanf_v2)
        ssp_record_v1 = create_ssp_m1_record(ssp_v1)
        ssp_record_v2 = create_ssp_m1_record(ssp_v2)
        tribal_record_v1 = create_tribal_t1_record(tribal_v1)
        tribal_record_v2 = create_tribal_t1_record(tribal_v2)
        fra_record_v1 = create_fra_exiter1_record(fra_v1)
        fra_record_v2 = create_fra_exiter1_record(fra_v2)

        remove_all_old_versions()

        # Old versions should be deleted
        assert not TANF_T1.objects.filter(id=tanf_record_v1.id).exists()
        assert not SSP_M1.objects.filter(id=ssp_record_v1.id).exists()
        assert not Tribal_TANF_T1.objects.filter(id=tribal_record_v1.id).exists()
        assert not TANF_Exiter1.objects.filter(id=fra_record_v1.id).exists()

        # New versions should be retained
        assert TANF_T1.objects.filter(id=tanf_record_v2.id).exists()
        assert SSP_M1.objects.filter(id=ssp_record_v2.id).exists()
        assert Tribal_TANF_T1.objects.filter(id=tribal_record_v2.id).exists()
        assert TANF_Exiter1.objects.filter(id=fra_record_v2.id).exists()
