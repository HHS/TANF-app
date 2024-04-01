"""Filter classes."""
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from tdpservice.stts.models import STT
import datetime

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


class STTFilter(SimpleListFilter):
    """Simple filter class to show records based on stt."""

    title = _('STT Code')

    parameter_name = 'stt_code'

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        options = [(None, _('All'))]
        for obj in STT.objects.all():
            options.append((obj.stt_code, _(obj.name)))
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
        """Return queryset of records based on stt code."""
        val = self.value()
        if val is not None and queryset.exists():
            if len(val) == 1:
                val = f"0{val}"
            queryset = queryset.filter(datafile__stt__stt_code=val)
        return queryset

class FiscalYearFilter(SimpleListFilter):
    """Simple filter class to filter records based on datafile fiscal year."""

    title = _('Fiscal Year')

    parameter_name = 'fiscal_year'

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
