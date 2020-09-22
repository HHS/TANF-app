"""Define user model."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from tdpservice.stts.models import STT, Region


class User(AbstractUser):
    """Define user fields and methods."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stt = models.ForeignKey(STT, on_delete=models.CASCADE, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        """Return the username as the string representation of the object."""
        return self.username
