"""Core Admin class tests."""
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.contenttypes.models import ContentType

import pytest

from tdpservice.users.models import User


@pytest.mark.django_db
def test_log_entry_admin(admin_user, admin):
    """Tests the custom LogEntryAdmin."""
    log_entry = LogEntry(
        content_type_id=ContentType.objects.get_for_model(User).id,
        action_flag=ADDITION,
        object_id=admin_user.id,
        object_repr="OBJ_REPR",
    )
    assert "OBJ_REPR" in admin.object_link(log_entry)
    assert '<a href="' in admin.object_link(log_entry)
