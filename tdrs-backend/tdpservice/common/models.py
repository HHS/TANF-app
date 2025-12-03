"""Common abstract models."""
from django.db import models


# The Data File model was starting to explode, and I think that keeping this logic
# in its own abstract class is better for documentation purposes.
class FileRecord(models.Model):
    """Abstract type representing a file stored in S3."""

    class Meta:
        """Metadata."""

        abstract = True

    # Keep the file name because it will be different in s3,
    # but the interface will still want to present the file with its
    # original name.
    original_filename = models.CharField(max_length=256, blank=False, null=False)
    # Slug is the name of the file in S3
    # NOTE: Currently unused, may be removed with a later release
    slug = models.CharField(max_length=256, blank=False, null=False)
    # Not all files will have the correct extension,
    # or even have one at all. The UI will provide this information
    # separately
    extension = models.CharField(max_length=8, default="txt")
