"""STT model."""

from django.db import models
from django.db.models import constraints
from django.utils.functional import cached_property

class Region(models.Model):
    """A model representing a US region."""

    id = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        """Return the ID."""
        return f"Region {self.id}"

    @cached_property
    def stts(self):
        return STT.objects.filter(region=self)


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
    code = models.CharField(max_length=2, blank=True, null=True)
    name = models.CharField(max_length=1000)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="stts", null=True
    )
    # Tribes have a state, which we need to store.
    state = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        """Metadata."""

        constraints = [
            constraints.UniqueConstraint(fields=["name"], name="stt_uniq_name"),
        ]

    def __str__(self):
        """Return the STT's name."""
        return self.name
