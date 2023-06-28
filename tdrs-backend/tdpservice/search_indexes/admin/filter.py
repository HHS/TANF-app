
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

class CreationDateFilter(SimpleListFilter):
    title = _('Newest')

    parameter_name = 'created_at'

    def lookups(self, request, model_admin):
        return (
            (None, _('Newest')),
            ('all', _('All')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        if self.value() == None and len(queryset):
            max_date = queryset.latest('created_at').created_at
            return queryset.filter(created_at=max_date)
        return queryset.order_by("-created_at")
