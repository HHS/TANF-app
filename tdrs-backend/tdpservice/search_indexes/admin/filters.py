"""Filter classes."""
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from tdpservice.stts.models import STT
import datetime


class MultipleChoiceListFilter(SimpleListFilter):
    template = 'multiselectlistfilter.html'

    def lookups(self, request, model_admin):
        """
        Must be overridden to return a list of tuples (value, verbose value)
        """
        raise NotImplementedError(
            'The MultipleChoiceListFilter.lookups() method must be overridden to '
            'return a list of tuples (value, verbose value).'
        )

    def queryset(self, request, queryset):
        if request.GET.get(self.parameter_name):
            kwargs = {self.parameter_name: request.GET[self.parameter_name].split(',')}
            queryset = queryset.filter(**kwargs)
        return queryset

    def value_as_list(self):
        return self.value().split(',') if self.value() else []

    def choices(self, changelist):

        def amend_query_string(include=None, exclude=None):
            selections = self.value_as_list()
            if include and include not in selections:
                selections.append(include)
            if exclude and exclude in selections:
                selections.remove(exclude)
            if selections:
                csv = ','.join(selections)
                return changelist.get_query_string({self.parameter_name: csv})
            else:
                return changelist.get_query_string(remove=[self.parameter_name])

        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': 'All',
            'reset': True,
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': str(lookup) in self.value_as_list(),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'include_query_string': amend_query_string(include=str(lookup)),
                'exclude_query_string': amend_query_string(exclude=str(lookup)),
                'display': title,
            }


class CreationDateFilter(SimpleListFilter):
    """Simple filter class to show newest created datafile records."""

    title = _('Newest')

    parameter_name = 'created_at'

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        return (
            (None, _('Newest')),
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

    def queryset(self, request, queryset):
        """Sort queryset to show latest records."""
        if self.value() is None and queryset.exists():
            datafile = queryset.order_by("-datafile__id").first().datafile
            return queryset.filter(datafile=datafile)
        return queryset


class STTFilter(MultipleChoiceListFilter):
    """Simple filter class to show records based on stt."""

    title = _('STT Code')

    parameter_name = 'stt_code'

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        options = []
        for obj in STT.objects.all():
            options.append((obj.stt_code, _(obj.name)))
        return options

    def queryset(self, request, queryset):
        """Return queryset of records based on stt code."""

        if self.value() is not None and queryset.exists():
            stts = self.value().split(',')
            print(stts)
            print(queryset.count())
            queryset = queryset.filter(datafile__stt__stt_code__in=stts)
            print(queryset.count())
        return queryset

class FiscalPeriodFilter(SimpleListFilter):
    """Simple filter class to filter records based on datafile fiscal year."""

    title = _('Fiscal Period')

    parameter_name = 'fiscal_period'

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        current_year = datetime.date.today().year
        quarters = [1, 2, 3, 4]
        months = ["(Oct - Dec)", "(Jan - Mar)", "(Apr - Jun)", "(Jul - Sep)"]
        years = [year for year in range(current_year - 5, current_year + 1)]
        options = [(None, _('All'))]

        for year in years:
            for qtr, month in zip(quarters, months):
                query = f"{year}Q{qtr}"
                display = f"{year} - Q{qtr} {month}"
                options.append((query, display))

        return options

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
        """Filter queryset to show records matching selected fiscal year."""
        if self.value() is not None and queryset.exists():
            year = int(self.value()[0:4])
            quarter = self.value()[4:6]
            queryset = queryset.filter(datafile__quarter=quarter).filter(datafile__year=year)

        return queryset
