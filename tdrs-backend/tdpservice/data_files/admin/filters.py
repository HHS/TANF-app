"""Filter classes for DataFiles admin page."""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.core.filters import MostRecentVersionFilter


class LatestReparseEvent(admin.SimpleListFilter):
    """Filter class to filter files based on the latest reparse event."""

    title = _('Reparse Event')

    parameter_name = 'reparse_meta_model'

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        return (
            (None, _('All')),
            ('latest', _('Latest')),
        )

    def choices(self, cl):
        """Update query string based on selection."""
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
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

    title = _('Version')
    parameter_name = 'created_at'

    def queryset(self, request, queryset):
        """Sort queryset to show latest records."""
        if self.value() is None and queryset.exists():
            return queryset.order_by(
                'stt__stt_code', 'year', 'quarter', 'section', '-version'
            ).distinct('stt__stt_code', 'year', 'quarter', 'section')
        return queryset
