"""Forms for the user admin."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from tdpservice.users.constants import REGIONAL_ROLES
from tdpservice.users.models import Region, User


USER_ADMIN_WORKFLOW_FIELDS = [
    "username",
    "first_name",
    "last_name",
    "account_approval_status",
    "groups",
    "stt",
    "regions",
]


class UserForm(forms.ModelForm):
    """Customize the user admin form."""

    regions = forms.ModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple("Regions", is_stacked=False),
    )

    class Meta:
        """Define customizations."""

        model = User
        exclude = ["password"]
        readonly_fields = [
            "last_login",
            "date_joined",
            "login_gov_uuid",
            "hhs_id",
            "access_request",
        ]

    class Media:
        """Include custom js for toggling regions based on roles."""

        js = ("admin/js/user_form_region_toggle.js",)

    def clean(self):
        """Add extra validation for locations based on roles."""

        cleaned_data = super().clean()

        groups = cleaned_data.get("groups")
        regions = cleaned_data.get("regions", [])
        stt = cleaned_data.get("stt")

        if groups is None:
            return cleaned_data

        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups.")

        # Check if the user belongs to any regional group
        group_names = {g.name for g in groups}
        has_regional_role = bool(group_names & REGIONAL_ROLES)

        if has_regional_role and not (regions or stt):
            raise ValidationError(
                "Users in regional roles must have at least one region or location assigned."
            )

        if regions and stt:
            raise ValidationError(
                "A user may only have a Region or STT assigned, not both."
            )

        if not has_regional_role and regions:
            raise ValidationError(
                "Users without regional roles should not be assigned regions."
            )

        if groups and not has_regional_role and stt:
            raise ValidationError(
                "Users other than Regional Staff, Developers, Data Analysts do not "
                "get assigned a location"
            )

        if "OFA Regional Staff" in group_names and stt:
            raise ValidationError(
                "Regional staff cannot have a location type other than region"
            )

        if "Data Analyst" in group_names and regions:
            raise ValidationError(
                "Data Analyst cannot have a location type other than stt"
            )

        return cleaned_data

    def save(self, commit=True):
        """Attach submitted M2M values before model validation runs."""
        instance = super().save(commit=False)
        instance.set_location_validation_context(
            groups=self.cleaned_data.get("groups"),
            regions=self.cleaned_data.get("regions"),
        )

        if commit:
            instance.save()
            self.save_m2m()

        return instance

    def clean_groups(self):
        """Ensure only one group is assigned."""
        groups = self.cleaned_data.get("groups", [])
        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups")

        return groups

    def clean_feature_flags(self):
        """Ensure only one feature flag is assigned."""
        feature_flags = self.cleaned_data.get("feature_flags", {})

        if not feature_flags:
            feature_flags = {}

        return feature_flags


class UserAdminWorkflowForm(UserForm):
    """Constrained user admin form used by the React admin console."""

    class Meta:
        """Expose only the first migrated admin workflow fields."""

        model = User
        fields = USER_ADMIN_WORKFLOW_FIELDS
        labels = {
            "account_approval_status": "Account approval status",
            "stt": "STT",
        }
