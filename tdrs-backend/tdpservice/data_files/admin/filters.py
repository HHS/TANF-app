"""Filter classes for DataFiles admin page."""

from django.contrib import admin
from django.db.models import F, Max, OuterRef, Subquery
from django.utils.translation import ugettext_lazy as _

from tdpservice.core.filters import MostRecentVersionFilter
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta


class LatestReparseEvent(admin.SimpleListFilter):
    """Filter class to filter files based on the latest reparse event."""

    title = _("Reparse Event")

    parameter_name = "reparse_meta_model"

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        return (
            (None, _("All")),
            ("latest", _("Latest")),
        )

    def choices(self, cl):
        """Update query string based on selection."""
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == lookup,
                "query_string": cl.get_query_string(
                    {
                        self.parameter_name: lookup,
                    },
                    [],
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        """Sort queryset to show datafiles associated to the most recent reparse event."""
        if self.value() is not None and queryset.exists():
            latest_meta = ReparseMeta.get_latest()
            if latest_meta is not None:
                queryset = queryset.filter(reparses=latest_meta)
        return queryset


class VersionFilter(MostRecentVersionFilter):
    """Simple filter class to show newest created datafile records."""

    title = _("Version")
    parameter_name = "created_at"

    def queryset(self, request, queryset):
        """
        Sort queryset to show latest records.

        Example of what the query looks like for reference:
        SELECT df.*,
            (SELECT MAX(version)
                FROM data_files df2
                WHERE df2.stt_code = df.stt_code
                AND df2.year = df.year
                AND df2.quarter = df.quarter
                AND df2.program_type = df.program_type
                AND df2.section = df.section
            ) AS max_version
        FROM data_files df
        WHERE df.version = max_version
        """
        if self.value() is None and queryset.exists():
            # Subquery to find the max version for each group
            max_versions = (
                queryset.filter(
                    stt__stt_code=OuterRef("stt__stt_code"),
                    year=OuterRef("year"),
                    quarter=OuterRef("quarter"),
                    program_type=OuterRef("program_type"),
                    section=OuterRef("section"),
                )
                .values("stt__stt_code", "year", "quarter", "program_type", "section")
                .annotate(max_version=Max("version"))
                .values("max_version")
            )

            # Filter to only records with the max version
            return queryset.annotate(max_version=Subquery(max_versions)).filter(
                version=F("max_version")
            )

        return queryset
