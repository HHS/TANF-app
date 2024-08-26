"""Admin filters used throughout apps."""

from abc import abstractmethod
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class MostRecentVersionFilter(admin.SimpleListFilter):
    """Simple filter class to show newest created datafile records."""

    title = _('Most recent version')

    # parameter_name = 'created_at'

    @property
    @abstractmethod
    def parameter_name(self):
        pass

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        return (
            (None, _('Most recent version')),
            ('all', _('All')),
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

    @abstractmethod
    def queryset(self, request, queryset):
        """Sort queryset to show latest records."""
        pass
