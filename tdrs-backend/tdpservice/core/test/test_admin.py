"""Core Admin class tests."""
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from tdpservice.users.models import UserChangeRequest, UserChangeRequestStatus

import pytest

from tdpservice.core.admin import FeatureFlagAdmin
from tdpservice.core.models import FeatureFlag
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
            email='admin@example.com'
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


class TestFeatureFlagAdmin(TestCase):
    """Test the FeatureFlagAdmin interface."""

    def setUp(self):
        """Create users for testing."""
        self.superuser = User.objects.create_superuser(
            username='superadmin',
            password='superpassword',
            first_name='Super',
            last_name='Admin',
            email='superadmin@example.com'
        )
        self.superuser.is_active = True
        self.superuser.save()

        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='staffpassword',
            first_name='Staff',
            last_name='User',
            email='staff@example.com'
        )
        self.staff_user.is_staff = True
        self.staff_user.is_active = True
        self.staff_user.save()

        self.site = AdminSite()
        self.admin = FeatureFlagAdmin(FeatureFlag, self.site)
        self.factory = RequestFactory()

        return super().setUp()

    def test_feature_flag_list_view(self):
        """Test that feature flags are visible in admin list view."""
        FeatureFlag.objects.create(
            feature_name="test_feature",
            enabled=True,
            description="A test feature"
        )

        client = Client()
        client.login(username='superadmin', password='superpassword')
        response = client.get(reverse('admin:core_featureflag_changelist'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test_feature')

    def test_feature_flag_add_view(self):
        """Test that feature flags can be added via admin."""
        client = Client()
        client.login(username='superadmin', password='superpassword')
        response = client.get(reverse('admin:core_featureflag_add'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Feature Identity')
        self.assertContains(response, 'Configuration')

    def test_feature_flag_change_view(self):
        """Test that feature flags can be edited via admin."""
        flag = FeatureFlag.objects.create(
            feature_name="edit_feature",
            enabled=False
        )

        client = Client()
        client.login(username='superadmin', password='superpassword')
        response = client.get(
            reverse('admin:core_featureflag_change', args=[flag.id])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'edit_feature')

    def test_superuser_can_delete(self):
        """Test that superusers can delete feature flags."""
        flag = FeatureFlag.objects.create(feature_name="deletable_feature")

        request = self.factory.get('/')
        request.user = self.superuser

        self.assertTrue(self.admin.has_delete_permission(request, flag))

    def test_non_superuser_cannot_delete(self):
        """Test that non-superusers cannot delete feature flags."""
        flag = FeatureFlag.objects.create(feature_name="protected_feature")

        request = self.factory.get('/')
        request.user = self.staff_user

        self.assertFalse(self.admin.has_delete_permission(request, flag))

    def test_list_display_fields(self):
        """Test that list_display contains expected fields."""
        self.assertIn('feature_name', self.admin.list_display)
        self.assertIn('enabled', self.admin.list_display)
        self.assertIn('updated_at', self.admin.list_display)

    def test_list_filter_fields(self):
        """Test that list_filter contains expected fields."""
        self.assertIn('enabled', self.admin.list_filter)
        self.assertIn('created_at', self.admin.list_filter)
        self.assertIn('updated_at', self.admin.list_filter)

    def test_search_fields(self):
        """Test that search_fields contains expected fields."""
        self.assertIn('feature_name', self.admin.search_fields)
        self.assertIn('description', self.admin.search_fields)

    def test_readonly_fields(self):
        """Test that timestamps are read-only."""
        self.assertIn('created_at', self.admin.readonly_fields)
        self.assertIn('updated_at', self.admin.readonly_fields)

    def test_feature_flag_create_via_admin(self):
        """Test creating a feature flag through the admin interface."""
        client = Client()
        client.login(username='superadmin', password='superpassword')

        response = client.post(
            reverse('admin:core_featureflag_add'),
            {
                'feature_name': 'datafiles_pia_submission',
                'enabled': True,
                'config': '{"max_file_size": 1000}',
                'description': 'Enable PIA datafile submission'
            }
        )

        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            FeatureFlag.objects.filter(feature_name='datafiles_pia_submission').exists()
        )

    def test_feature_flag_search(self):
        """Test searching for feature flags."""
        FeatureFlag.objects.create(
            feature_name="searchable_feature",
            description="This feature can be searched"
        )
        FeatureFlag.objects.create(
            feature_name="another_feature",
            description="Different description"
        )

        client = Client()
        client.login(username='superadmin', password='superpassword')
        response = client.get(
            reverse('admin:core_featureflag_changelist'),
            {'q': 'searchable'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'searchable_feature')
        self.assertNotContains(response, 'another_feature')

    def test_feature_flag_filter_by_enabled(self):
        """Test filtering feature flags by enabled status."""
        FeatureFlag.objects.create(feature_name="enabled_flag", enabled=True)
        FeatureFlag.objects.create(feature_name="disabled_flag", enabled=False)

        client = Client()
        client.login(username='superadmin', password='superpassword')
        response = client.get(
            reverse('admin:core_featureflag_changelist'),
            {'enabled__exact': '1'}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'enabled_flag')
        self.assertNotContains(response, 'disabled_flag')
