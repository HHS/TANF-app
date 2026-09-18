"""Tests for users admin query behavior."""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

import pytest

from tdpservice.stts.test.factories import STTFactory
from tdpservice.users.admin import UserAdmin
from tdpservice.users.models import AccountApprovalStatusChoices, User
from tdpservice.users.test.factories import UserFactory


@pytest.mark.django_db
def test_user_admin_changelist_stt_relation_is_eager_loaded():
    """User admin should not query per row for displayed STT relations."""
    for _ in range(3):
        UserFactory.create(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
            stt=STTFactory.create(),
        )
    request = RequestFactory().get("/admin/users/user/")
    model_admin = UserAdmin(User, AdminSite())

    users = list(model_admin.get_queryset(request))

    with CaptureQueriesContext(connection) as captured_queries:
        for user in users:
            str(user.stt)

    assert len(captured_queries) == 0


@pytest.mark.django_db
def test_user_admin_permission_formfield_content_types_are_eager_loaded(admin_user):
    """User change form should not query per Permission label for content types."""
    content_type = ContentType.objects.get_for_model(User)
    Permission.objects.bulk_create(
        [
            Permission(
                content_type=content_type,
                codename=f"test_permission_{index}",
                name=f"Can test permission {index}",
            )
            for index in range(3)
        ]
    )
    request = RequestFactory().get("/admin/users/user/test/change/")
    request.user = admin_user
    model_admin = UserAdmin(User, AdminSite())
    db_field = User._meta.get_field("user_permissions")

    formfield = model_admin.formfield_for_manytomany(db_field, request)
    permissions = list(
        formfield.queryset.filter(codename__startswith="test_permission_")
    )

    with CaptureQueriesContext(connection) as captured_queries:
        for permission in permissions:
            str(permission)

    assert len(captured_queries) == 0
