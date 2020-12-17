"""Module for testing the core model."""
import pytest

from tdpservice.core.models import GlobalPermission


@pytest.mark.django_db
def test_manager_get_queryset():
    """Test the get queryset method returns a query."""
    GlobalPermission.objects.create(
        name="Can View User Data", codename="view_user_data"
    )
    global_permissions = GlobalPermission.objects.first()
    assert global_permissions.name == "Can View User Data"
