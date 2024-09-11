"""Filter classes."""
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from django.db.models import Q as Query
from tdpservice.stts.models import STT
from tdpservice.search_indexes.admin.multiselect_filter import MultiSelectDropdownFilter
from tdpservice.core.filters import MostRecentVersionFilter
import datetime


class CreationDateFilter(MostRecentVersionFilter):
    """Simple filter class to show newest created datafile records."""

    title = _('Submission')
    parameter_name = 'created_at'

    def queryset(self, request, queryset):
        """Sort queryset to show latest records."""
        if self.value() is None and queryset.exists():
            datafiles = []
            for record in queryset.order_by("datafile__stt__stt_code", "-datafile__id")\
                    .distinct("datafile__stt__stt_code"):
                datafiles.append(record.datafile)
            return queryset.filter(datafile__in=datafiles)
        return queryset


class STTFilter(MultiSelectDropdownFilter):
    """Multi-select dropdown filter class to filter records based on stt."""

    def __init__(self, field, request, params, model, model_admin, field_path):
        super(MultiSelectDropdownFilter, self).__init__(field, request, params, model, model_admin, field_path)
        self.lookup_choices = self._get_lookup_choices(request)
        self.title = _("STT")

    def _get_lookup_choices(self, request):
        """Filter queryset to guarantee lookup_choices only has STTs associated with the record type."""
        record_type = str(request.path).split('/')[-2]
        queryset = STT.objects.all()
        if 'tribal' in record_type:
            queryset = queryset.filter(type=STT.EntityType.TRIBE)
        elif 'ssp' in record_type:
            queryset = queryset.filter(ssp=True)
        else:
            type_query = Query(type=STT.EntityType.STATE) | Query(type=STT.EntityType.TERRITORY)
            queryset = queryset.filter(type_query)
        return (queryset.distinct().order_by('name').values_list('name', flat=True))

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        listing_record_type = [i for i in str(request.path).lower().split('/') if i not in ['/', '']][-1]
        options = []
        if 'tribal' in listing_record_type:
            objects = STT.objects.filter(type=STT.EntityType.TRIBE)
        elif 'ssp' in listing_record_type:
            objects = STT.objects.filter(ssp=True)
        else:
            objects = STT.objects.filter(Query(type=STT.EntityType.STATE) | Query(type=STT.EntityType.TERRITORY))
        for obj in objects:
            options.append((obj.stt_code, _(obj.name)))

        return options


class FiscalPeriodFilter(SimpleListFilter):
    """Simple filter class to filter records based on datafile fiscal year."""

    title = _('Fiscal Period')

    parameter_name = 'fiscal_period'

    def lookups(self, request, model_admin):
        """Available options in dropdown."""
        today = datetime.date.today()
        current_year = today.year + 1 if today.month > 8 else today.year
        quarters = [1, 2, 3, 4]
        months = ["(Oct - Dec)", "(Jan - Mar)", "(Apr - Jun)", "(Jul - Sep)"]
        years = [year for year in range(current_year, 2020, -1)]
        options = []

        for year in years:
            for qtr, month in zip(quarters, months):
                query = f"{year}Q{qtr}"
                display = f"{year} - Q{qtr} {month}"
                options.append((query, display))

        return options

    def queryset(self, request, queryset):
        """Filter queryset to show records matching selected fiscal year."""
        if self.value() is not None and queryset.exists():
            year = int(self.value()[0:4])
            quarter = self.value()[4:6]
            queryset = queryset.filter(datafile__quarter=quarter).filter(datafile__year=year)

        return queryset
