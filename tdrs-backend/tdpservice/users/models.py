"""Define user model."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Define user fields and methods."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        """Return the username as the string representation of the object."""
        return self.username
