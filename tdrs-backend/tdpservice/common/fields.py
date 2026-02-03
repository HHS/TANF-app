"""Custom Django model fields for tdpservice."""
import logging

from django.db import models
from django.db.models.fields.files import FieldFile

logger = logging.getLogger(__name__)


class S3VersionedFieldFile(FieldFile):
    """A FieldFile that captures the S3 version ID after upload and sets it on the model."""

    def save(self, name, content, save=True):
        """Save file to storage, then capture the S3 version ID onto the model instance."""
        super().save(name, content, save=False)

        version_id_field = getattr(self.field, "version_id_field", None)
        if version_id_field and hasattr(self.storage, "bucket"):
            try:
                normalized_name = self.storage._normalize_name(self.name)
                obj = self.storage.bucket.Object(normalized_name)
                version_id = obj.version_id
                if version_id and version_id != "null":
                    setattr(self.instance, version_id_field, version_id)
            except Exception:
                logger.exception("Failed to capture S3 version ID for %s", self.name)

        if save:
            self.instance.save()


class S3VersionedFileField(models.FileField):
    """A FileField that automatically captures S3 version IDs on upload.

    The `version_id_field` argument names the model field where the S3
    version ID will be stored after a successful upload.
    """

    attr_class = S3VersionedFieldFile

    def __init__(self, *args, version_id_field: str | None = None, **kwargs):
        self.version_id_field = version_id_field
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """Include version_id_field in migration serialization."""
        name, path, args, kwargs = super().deconstruct()
        if self.version_id_field:
            kwargs["version_id_field"] = self.version_id_field
        return name, path, args, kwargs
