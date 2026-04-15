"""Core Admin class tests."""
from django.contrib.admin.models import ADDITION, LogEntry
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

import pytest

from tdpservice.core.admin import FeatureFlagAdmin
from tdpservice.core.models import FeatureFlag
from tdpservice.users.models import User, UserChangeRequest, UserChangeRequestStatus


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
            username="admin",
            password="adminpassword",
            first_name="Admin",
            last_name="User",
            email="admin@example.com",
        )
        self.admin_user.is_active = True
        self.admin_user.save()

        return super().setUp()

    def test_user_change_request_form(self):
        """Test the user change request form template."""
        client = Client()
        # get reverse URL for admin/users/userchangerequest/ list view
        client.login(username="admin", password="adminpassword")
        response = client.get(reverse("admin:users_userchangerequest_changelist"))
        self.assertEqual(response.status_code, 200)

        self.assertNotContains(response=response, text="Approve</a>")
        self.assertNotContains(response=response, text="Reject</a>")

        UserChangeRequest.objects.create(
            user=self.admin_user,
            requested_by=self.admin_user,
            field_name="first_name",
            current_value="Admin",
            requested_value="NewAdmin",
            status=UserChangeRequestStatus.PENDING,
        )

        response = client.get(reverse("admin:users_userchangerequest_changelist"))
        self.assertContains(response=response, text="Approve</a>")
        self.assertContains(response=response, text="Reject</a>")

    @pytest.mark.django_db
    def test_user_change_request_approve(self):
        """Test the user change request approval."""
        client = Client()
        client.login(username="admin", password="adminpassword")

        # Create a change request
        change_request = UserChangeRequest.objects.create(
            user=self.admin_user,
            requested_by=self.admin_user,
            field_name="first_name",
            current_value="Admin",
            requested_value="NewAdmin",
            status=UserChangeRequestStatus.PENDING,
        )
        print(f"Change Request ID: {change_request.id}")
        # Approve the change request
        response = client.post(
            f"/admin/users/userchangerequest/{change_request.id}/approve/"
        )
        self.assertEqual(response.status_code, 302)


class TestFeatureFlagAdmin(TestCase):
    """Test the FeatureFlagAdmin interface."""

    def setUp(self):
        """Create users for testing."""
        self.superuser = User.objects.create_superuser(
            username="superadmin",
            password="superpassword",
            first_name="Super",
            last_name="Admin",
            email="superadmin@example.com",
        )
        self.superuser.is_active = True
        self.superuser.save()

        self.staff_user = User.objects.create_user(
            username="staffuser",
            password="staffpassword",
            first_name="Staff",
            last_name="User",
            email="staff@example.com",
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
            feature_name="test_feature", enabled=True, description="A test feature"
        )

        client = Client()
        client.login(username="superadmin", password="superpassword")
        response = client.get(reverse("admin:core_featureflag_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "test_feature")

    def test_feature_flag_add_view(self):
        """Test that feature flags can be added via admin."""
        client = Client()
        client.login(username="superadmin", password="superpassword")
        response = client.get(reverse("admin:core_featureflag_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Feature Identity")
        self.assertContains(response, "Configuration")

    def test_feature_flag_change_view(self):
        """Test that feature flags can be edited via admin."""
        flag = FeatureFlag.objects.create(feature_name="edit_feature", enabled=False)

        client = Client()
        client.login(username="superadmin", password="superpassword")
        response = client.get(reverse("admin:core_featureflag_change", args=[flag.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "edit_feature")

    def test_superuser_can_delete(self):
        """Test that superusers can delete feature flags."""
        flag = FeatureFlag.objects.create(feature_name="deletable_feature")

        request = self.factory.get("/")
        request.user = self.superuser

        self.assertTrue(self.admin.has_delete_permission(request, flag))

    def test_non_superuser_cannot_delete(self):
        """Test that non-superusers cannot delete feature flags."""
        flag = FeatureFlag.objects.create(feature_name="protected_feature")

        request = self.factory.get("/")
        request.user = self.staff_user

        self.assertFalse(self.admin.has_delete_permission(request, flag))

    def test_list_display_fields(self):
        """Test that list_display contains expected fields."""
        self.assertIn("feature_name", self.admin.list_display)
        self.assertIn("enabled", self.admin.list_display)
        self.assertIn("updated_at", self.admin.list_display)

    def test_list_filter_fields(self):
        """Test that list_filter contains expected fields."""
        self.assertIn("enabled", self.admin.list_filter)
        self.assertIn("created_at", self.admin.list_filter)
        self.assertIn("updated_at", self.admin.list_filter)

    def test_search_fields(self):
        """Test that search_fields contains expected fields."""
        self.assertIn("feature_name", self.admin.search_fields)
        self.assertIn("description", self.admin.search_fields)

    def test_readonly_fields(self):
        """Test that timestamps are read-only."""
        self.assertIn("created_at", self.admin.readonly_fields)
        self.assertIn("updated_at", self.admin.readonly_fields)

    def test_feature_flag_create_via_admin(self):
        """Test creating a feature flag through the admin interface."""
        client = Client()
        client.login(username="superadmin", password="superpassword")

        response = client.post(
            reverse("admin:core_featureflag_add"),
            {
                "feature_name": "datafiles_pia_submission",
                "enabled": True,
                "config": '{"max_file_size": 1000}',
                "description": "Enable PIA datafile submission",
            },
        )

        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            FeatureFlag.objects.filter(feature_name="datafiles_pia_submission").exists()
        )

    def test_feature_flag_search(self):
        """Test searching for feature flags."""
        FeatureFlag.objects.create(
            feature_name="searchable_feature",
            description="This feature can be searched",
        )
        FeatureFlag.objects.create(
            feature_name="another_feature", description="Different description"
        )

        client = Client()
        client.login(username="superadmin", password="superpassword")
        response = client.get(
            reverse("admin:core_featureflag_changelist"), {"q": "searchable"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "searchable_feature")
        self.assertNotContains(response, "another_feature")

    def test_feature_flag_filter_by_enabled(self):
        """Test filtering feature flags by enabled status."""
        FeatureFlag.objects.create(feature_name="enabled_flag", enabled=True)
        FeatureFlag.objects.create(feature_name="disabled_flag", enabled=False)

        client = Client()
        client.login(username="superadmin", password="superpassword")
        response = client.get(
            reverse("admin:core_featureflag_changelist"), {"enabled__exact": "1"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "enabled_flag")
        self.assertNotContains(response, "disabled_flag")

    def test_history_records_created_on_create(self):
        """Test that creating a FeatureFlag generates a history record."""
        flag = FeatureFlag.objects.create(
            feature_name="history_create_test",
            enabled=False,
            description="Initial description",
        )

        self.assertEqual(flag.history.count(), 1)
        record = flag.history.first()
        self.assertEqual(record.feature_name, "history_create_test")
        self.assertFalse(record.enabled)
        self.assertEqual(record.history_type, "+")

    def test_history_records_created_on_update(self):
        """Test that updating a FeatureFlag generates additional history records."""
        flag = FeatureFlag.objects.create(
            feature_name="history_update_test",
            enabled=False,
        )
        flag.enabled = True
        flag.description = "Updated description"
        flag.save()

        self.assertEqual(flag.history.count(), 2)
        latest = flag.history.first()
        self.assertTrue(latest.enabled)
        self.assertEqual(latest.description, "Updated description")
        self.assertEqual(latest.history_type, "~")

    def test_history_tracks_config_changes(self):
        """Test that history captures JSON config field changes."""
        flag = FeatureFlag.objects.create(
            feature_name="config_history_test", config={"max_size": 100}
        )
        flag.config = {"max_size": 200, "retry": True}
        flag.save()

        self.assertEqual(flag.history.count(), 2)
        latest = flag.history.first()
        self.assertEqual(latest.config, {"max_size": 200, "retry": True})
        oldest = flag.history.last()
        self.assertEqual(oldest.config, {"max_size": 100})

    def test_history_records_created_on_delete(self):
        """Test that deleting a FeatureFlag generates a delete history record."""
        flag = FeatureFlag.objects.create(feature_name="history_delete_test")
        flag_history_model = flag.history.model
        flag.delete()

        history = flag_history_model.objects.filter(feature_name="history_delete_test")
        self.assertEqual(history.count(), 2)
        self.assertEqual(history.first().history_type, "-")

    def test_history_page_accessible(self):
        """Test that the SimpleHistoryAdmin history page loads for a FeatureFlag."""
        flag = FeatureFlag.objects.create(
            feature_name="history_page_test",
            enabled=True,
        )

        client = Client()
        client.login(username="superadmin", password="superpassword")
        response = client.get(reverse("admin:core_featureflag_history", args=[flag.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "history_page_test")

    def test_history_page_shows_multiple_changes(self):
        """Test that the history page displays all change records."""
        flag = FeatureFlag.objects.create(
            feature_name="multi_change_test",
            enabled=False,
        )
        flag.enabled = True
        flag.save()
        flag.description = "Added description"
        flag.save()

        client = Client()
        client.login(username="superadmin", password="superpassword")
        response = client.get(reverse("admin:core_featureflag_history", args=[flag.id]))

        self.assertEqual(response.status_code, 200)
        # History page should show all 3 records (create + 2 updates)
        self.assertEqual(flag.history.count(), 3)
        self.assertContains(response, "Changed")

    def test_history_detail_page_accessible(self):
        """Test that an individual history record detail page loads."""
        flag = FeatureFlag.objects.create(
            feature_name="history_detail_test",
            enabled=False,
        )
        flag.enabled = True
        flag.save()
        history_record = flag.history.first()

        client = Client()
        client.login(username="superadmin", password="superpassword")
        url = reverse(
            "admin:core_featureflag_simple_history",
            args=[flag.id, history_record.history_id],
        )
        response = client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "history_detail_test")

    def test_rollback_restores_previous_state(self):
        """Test that reverting to a historical record restores model state."""
        flag = FeatureFlag.objects.create(
            feature_name="rollback_test",
            enabled=False,
            config={"version": 1},
            description="Original",
        )
        original_record = flag.history.first()

        flag.enabled = True
        flag.config = {"version": 2}
        flag.description = "Modified"
        flag.save()

        # Revert to the original historical record
        original_record.instance.save()
        flag.refresh_from_db()

        self.assertFalse(flag.enabled)
        self.assertEqual(flag.config, {"version": 1})
        self.assertEqual(flag.description, "Original")

    def test_rollback_creates_new_history_record(self):
        """Test that reverting a FeatureFlag creates an additional history entry."""
        flag = FeatureFlag.objects.create(
            feature_name="rollback_history_test",
            enabled=False,
        )
        original_record = flag.history.first()

        flag.enabled = True
        flag.save()
        self.assertEqual(flag.history.count(), 2)

        # Revert to original state
        original_record.instance.save()
        flag.refresh_from_db()

        # Should have 3 records: create, update, revert
        self.assertEqual(flag.history.count(), 3)
        latest = flag.history.first()
        self.assertFalse(latest.enabled)
        self.assertEqual(latest.history_type, "~")

    def test_rollback_config_field(self):
        """Test that rollback correctly restores complex JSON config."""
        flag = FeatureFlag.objects.create(
            feature_name="rollback_config_test",
            config={"limits": {"max": 10, "min": 1}, "tags": ["a", "b"]},
        )
        original_record = flag.history.first()

        flag.config = {"limits": {"max": 999}, "tags": []}
        flag.save()

        original_record.instance.save()
        flag.refresh_from_db()

        self.assertEqual(
            flag.config,
            {"limits": {"max": 10, "min": 1}, "tags": ["a", "b"]},
        )
