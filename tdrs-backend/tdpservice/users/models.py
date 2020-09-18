"""Define user model."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import constraints


class Region(models.Model):
    """A model representing a US region."""

    id = models.PositiveIntegerField(primary_key=True)

    def __str__(self):
        """Return the ID."""
        return str(self.id)


class STT(models.Model):
    """A model representing a US state, tribe or territory."""

    class STTType(models.TextChoices):
        """Enum representing types of STT."""

        STATE = "state"
        TERRITORY = "territory"
        TRIBE = "tribe"

    type = models.CharField(
        max_length=200, blank=True, null=True, choices=STTType.choices
    )
    code = models.CharField(max_length=2, blank=True, null=True)
    name = models.CharField(max_length=1000)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="stts")
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


class User(AbstractUser):
    """Define user fields and methods."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stt = models.ForeignKey(STT, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        """Return the username as the string representation of the object."""
        return self.username
