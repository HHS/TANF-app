"""Admin filters used throughout apps."""

from abc import abstractmethod
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class MostRecentVersionFilter(admin.SimpleListFilter):
    """Simple filter class to show newest created datafile records."""

    @property
    @abstractmethod
    def title(self):
        """Define the widget title displayed for the form field."""
        pass

    @property
    @abstractmethod
    def parameter_name(self):
        """Define the search parameter name as a class property."""
        pass

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        return (
            (None, _('Most recent')),
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


def custom_filter_title(filter_class, title):
    """Wrap the Django Admin filter class so that a custom title can be used."""
    class Wrapper(filter_class):
        def __new__(cls, *args, **kwargs):
            instance = filter_class(*args, **kwargs)
            instance.title = title
            return instance

    return Wrapper
