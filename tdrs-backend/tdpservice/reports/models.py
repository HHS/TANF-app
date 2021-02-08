"""Define report models."""

from django.db import models
from django.db.models import Max

from ..stts.models import STT
from ..users.models import User


# The Report File model was starting to explode, and I think that keeping this logic
# in its own abstract class is better for documentation purposes.
class File(models.Model):
    """Abstract type representing a file stored in S3."""

    class Meta:
        """Metadata."""

        abstract = True

    original_filename = models.CharField(max_length=256,
                                         blank=False,
                                         null=False)

    slug = models.CharField(max_length=256, blank=False, null=False)
    extension = models.CharField(max_length=8, default="txt")


class ReportFile(File):
    """Represents a version of a report file."""

    class Section(models.TextChoices):
        """Enum for report section."""

        ACTIVE_CASE_DATA = "Active Case Data"
        CLOSE_CASE_DATA = "Close Case Data"
        AGGREGATE_DATA = "Aggregate Data"
        STRATUM_DATA = "Stratum Data"

    class Quarter(models.TextChoices):
        """Enum for report Quarter."""

        Q1 = "Q1"
        Q2 = "Q2"
        Q3 = "Q3"
        Q4 = "Q4"

    class Meta:
        """Metadata."""

        constraints = [
            models.UniqueConstraint(
                fields=("section", "version", "quarter", "year", "stt"),
                name="constraint_name",
            )
        ]

    quarter = models.CharField(max_length=16,
                               blank=False,
                               null=False,
                               choices=Quarter.choices)
    year = models.IntegerField()
    section = models.CharField(max_length=32,
                               blank=False,
                               null=False,
                               choices=Section.choices)

    version = models.IntegerField()

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="user",
                             blank=False,
                             null=False)
    stt = models.ForeignKey(STT,
                            on_delete=models.CASCADE,
                            related_name="sttRef",
                            blank=False,
                            null=False)

    @classmethod
    def create_new_version(self, data):
        """Create a new version of a report with an incremented version."""
        # EDGE CASE
        # We may need to try to get this all in one sql query
        # if we ever encounter race conditions.
        version = (self.find_latest_version_number(year=data['year'],
                                                   quarter=data['quarter'],
                                                   section=data['section'],
                                                   stt=data['stt']) or 0) + 1

        return ReportFile.objects.create(
            version=version,
            **data,
        )

    @classmethod
    def find_latest_version_number(self, year, quarter, section, stt):
        """Locate the latest version number in a series of report files."""
        return self.objects.filter(stt=stt,
                                   year=year,
                                   quarter=quarter,
                                   section=section).aggregate(
                                       Max("version"))['version__max']

    @classmethod
    def find_latest_version(self, year, quarter, section, stt):
        """Locate the latest version of a report."""
        version = self.find_latest_version_number(year, quarter, section, stt)

        return self.objects.filter(
            version=version,
            year=year,
            quarter=quarter,
            section=section,
            stt=stt,
        )[0]
