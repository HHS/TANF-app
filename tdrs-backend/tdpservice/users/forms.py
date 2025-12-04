"""Forms for the user admin."""

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from tdpservice.users.models import User, Region
from tdpservice.users.constants import REGIONAL_ROLES


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

        groups = cleaned_data.get("groups", [])
        regions = cleaned_data.get("regions", [])
        stt = cleaned_data.get("stt")

        if len(groups) > 1:
            raise ValidationError("User should not have multiple groups.")

        # Check if the user belongs to any regional group
        has_regional_role = any(g.name in REGIONAL_ROLES for g in groups)

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

        return cleaned_data

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
