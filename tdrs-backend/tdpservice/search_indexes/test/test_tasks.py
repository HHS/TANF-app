"""Tests for search indexes custom tasks."""

import pytest
from django.utils import timezone
from datetime import timedelta
from faker import Faker
from tdpservice.search_indexes.tasks import prettify_time_delta

@pytest.mark.django_db
def test_prettify_time_delta():
    """Test prettify_time_delta."""
    start = timezone.now()
    end = start + timedelta(seconds=100)

    assert prettify_time_delta(start, end) == (1, 40)

