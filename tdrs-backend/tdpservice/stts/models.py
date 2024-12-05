"""STT model."""

from django.db import models
from django.db.models import constraints


DEFAULT_NUMBER_OF_SECTIONS = 4


class Region(models.Model):
    """A model representing a US region."""

    id = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        """Return the ID."""
        return f"Region {self.id}"


class STT(models.Model):
    """A model representing a US state, tribe or territory."""

    class EntityType(models.TextChoices):
        """Enum representing types of STT."""

        STATE = "state"
        TERRITORY = "territory"
        TRIBE = "tribe"

    type = models.CharField(
        max_length=200, blank=True, null=True, choices=EntityType.choices
    )
    postal_code = models.CharField(max_length=2, blank=True, null=True)
    name = models.CharField(max_length=1000)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="stts", null=True
    )
    filenames = models.JSONField(max_length=512, blank=True, null=True)  # largest length in data so far is 332.
    stt_code = models.CharField(max_length=3, blank=True, null=True)
    # Tribes have a state, which we need to store.
    state = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    ssp = models.BooleanField(default=False, null=True)
    sample = models.BooleanField(default=False, null=True)

    @property
    def num_sections(self):
        """The number of sections this STT submits."""
        if self.filenames is None:
            return DEFAULT_NUMBER_OF_SECTIONS
        divisor = int(self.ssp) + 1
        return len(self.filenames) // divisor

    class Meta:
        """Metadata."""

        constraints = [
            constraints.UniqueConstraint(fields=["name"], name="stt_uniq_name"),
        ]

    def __str__(self):
        """Return the STT's name."""
        return f"{self.name} ({self.stt_code})"
