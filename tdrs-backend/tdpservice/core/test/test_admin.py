"""Core Admin class tests."""
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.urls import reverse
from tdpservice.users.models import UserChangeRequest, UserChangeRequestStatus

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

class TestAdminTemplates(TestCase):
    """Test the admin templates for user change requests."""

    def setUp(self):
        """Create a couple of users for testing."""
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
        )
        self.admin_user.is_active = True
        self.admin_user.save()

        return super().setUp()

    def test_user_change_request_form(self):
        """Test the user change request form template."""
        client = Client()
        # get reverse URL for admin/users/userchangerequest/ list view
        client.login(username='admin', password='adminpassword')
        response = client.get(reverse('admin:users_userchangerequest_changelist'))
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response=response, text='Approve</a>')
        self.assertNotContains(response=response, text='Reject</a>')

        UserChangeRequest.objects.create(
            user=self.admin_user,
            requested_by=self.admin_user,
            field_name='first_name',
            current_value='Admin',
            requested_value='NewAdmin',
            status=UserChangeRequestStatus.PENDING,
        )

        response = client.get(reverse('admin:users_userchangerequest_changelist'))
        self.assertContains(response=response, text='Approve</a>')
        self.assertContains(response=response, text='Reject</a>')

    @pytest.mark.django_db
    def test_user_change_request_approve(self):
        """Test the user change request approval."""
        client = Client()
        client.login(username='admin', password='adminpassword')

        # Create a change request
        change_request = UserChangeRequest.objects.create(
            user=self.admin_user,
            requested_by=self.admin_user,
            field_name='first_name',
            current_value='Admin',
            requested_value='NewAdmin',
            status=UserChangeRequestStatus.PENDING,
        )
        print(f"Change Request ID: {change_request.id}")
        # Approve the change request
        response = client.post(f'/admin/users/userchangerequest/{change_request.id}/approve/')
        self.assertEqual(response.status_code, 302)
