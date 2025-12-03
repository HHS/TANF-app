"""Filters for the User admin interface."""

from django.contrib import admin
from tdpservice.users.models import AccountApprovalStatusChoices


class ActiveStatusListFilter(admin.SimpleListFilter):
    """Filter to show active or inactive users."""

    title = "activation status"
    parameter_name = "active_status"

    def lookups(self, request, model_admin):
        """Define the filter options."""
        return (
            ("active_users", "Show Active Users"),
            ("all_users", "Show All Users"),
            ("inactive_users", "Show Inactive Users"),
            )

    def value(self):
        """Get the current value of the filter, defaulting to 'active_users'."""
        return super().value() or "active_users"

    def queryset(self, request, queryset):
        """Filter the queryset based on the selected value."""
        value = self.value()
        if value == "inactive_users":
            return queryset.filter(
                account_approval_status=AccountApprovalStatusChoices.DEACTIVATED
            )
        elif value == "active_users":
            return queryset.exclude(
                account_approval_status=AccountApprovalStatusChoices.DEACTIVATED
            )
        elif value == "all_users":
            return queryset

        return queryset

    def choices(self, changelist):
        """Generate the choices for the filter, modifying the All display text."""
        """Remove the 'All' option."""
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }
