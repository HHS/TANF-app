"""Tests for custom fields."""
from unittest.mock import MagicMock

from tdpservice.common.fields import S3VersionedFieldFile, S3VersionedFileField


class TestS3VersionedFileField:
    """Tests for S3VersionedFileField and S3VersionedFieldFile."""

    def test_versioned_file_field_attr_class(self):
        """Test that S3VersionedFileField uses S3VersionedFieldFile as its attr_class."""
        field = S3VersionedFileField(version_id_field="s3_versioning_id")
        assert field.attr_class is S3VersionedFieldFile

    def test_versioned_file_field_stores_version_id_field(self):
        """Test that the version_id_field kwarg is stored on the field."""
        field = S3VersionedFileField(version_id_field="s3_versioning_id")
        assert field.version_id_field == "s3_versioning_id"

    def test_versioned_file_field_deconstruct_includes_version_id_field(self):
        """Test that deconstruct includes version_id_field for migrations."""
        field = S3VersionedFileField(version_id_field="s3_versioning_id")
        _, _, _, kwargs = field.deconstruct()
        assert kwargs["version_id_field"] == "s3_versioning_id"

    def test_versioned_file_field_deconstruct_omits_none_version_id_field(self):
        """Test that deconstruct omits version_id_field when not set."""
        field = S3VersionedFileField()
        _, _, _, kwargs = field.deconstruct()
        assert "version_id_field" not in kwargs

    def _make_field_file(
        self, version_id_field="s3_versioning_id", s3_version_id="abc123"
    ):
        """Create an S3VersionedFieldFile with mocked storage, field, and instance."""
        mock_storage = MagicMock()
        mock_storage.save.return_value = "data_files/test.txt"
        mock_storage._normalize_name.return_value = "data_files/test.txt"

        mock_s3_obj = MagicMock()
        mock_s3_obj.version_id = s3_version_id
        mock_storage.bucket.Object.return_value = mock_s3_obj

        mock_field = MagicMock()
        mock_field.version_id_field = version_id_field
        mock_field.generate_filename.return_value = "data_files/test.txt"
        mock_field.max_length = 100
        mock_field.attname = "file"

        mock_instance = MagicMock()
        mock_instance.s3_versioning_id = None

        field_file = S3VersionedFieldFile(
            instance=mock_instance, field=mock_field, name="test.txt"
        )
        field_file.storage = mock_storage

        return field_file, mock_instance, mock_storage

    def test_versioned_field_file_save_sets_version_id(self):
        """Test that saving a file captures the S3 version ID on the model instance."""
        field_file, mock_instance, _ = self._make_field_file(s3_version_id="abc123")

        field_file.save("test.txt", MagicMock(), save=False)

        assert mock_instance.s3_versioning_id == "abc123"

    def test_versioned_field_file_save_skips_null_version_id(self):
        """Test that 'null' version IDs from S3 are not set on the model."""
        field_file, mock_instance, _ = self._make_field_file(s3_version_id="null")

        field_file.save("test.txt", MagicMock(), save=False)

        assert mock_instance.s3_versioning_id is None

    def test_versioned_field_file_save_without_version_id_field(self):
        """Test that save works normally when version_id_field is not configured."""
        field_file, mock_instance, mock_storage = self._make_field_file(
            version_id_field=None, s3_version_id="abc123"
        )

        field_file.save("test.txt", MagicMock(), save=False)

        # Should not attempt to access storage.bucket at all
        mock_storage.bucket.Object.assert_not_called()
