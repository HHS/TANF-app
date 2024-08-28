# Multi-Select Filters

**Audience**: TDP Software Engineers <br>
**Subject**:  Multi-Select Filter Integration <br>
**Date**:     August 27, 2024 <br>

## Summary
This technical memorandum provides the suggested guidelines for a future engineer to integrate TDP's need for multi-select filtering with Django 508. The memorandum provides some necessary background on both the TDP multi-select filters as well as Django 508 and it's purpose and effects. The [Method](#method) section provides the guidelines and updates required to integrate TDP's custom filtering needs with Django 508. Specifically, the [Django 508 Updates](#django-508-updates) section introduces the engineer to the area where the filtering and query string building occurs within Django 508 and the suggested changes. The [TDP Updates](#tdp-updates) section introduces the recommended changes to current TDP custom filtering with respect to how it can be simplified and how it could be unified with Django 508 to provide a seamless filtering experience.

## Background
TDP has been expanding it's Django Admin Console (DAC) filtering capabilities by introducing custom filters, specifically multi-select filters. This has introduced a myriad of issues because TDP does not use the default DAC. Instead, to assist with accessibility compliance TDP wraps the default DAC with [Django 508](https://github.com/raft-tech/django-admin-508) (henceforth referred to as 508) which makes various updates to the styling and functionality of the default DAC. A key change is that 508 introduces to the DAC is an `Apply Filters` button that intercepts query string parameters from default DAC filters and only applies them after clicking the button. The default DAC applies the filters as they are selected as opposed to all at once. The issue with 508's approach is that it assumes all filters are built-in Django filters (i.e. single select filters). This presents a discrepancy because Django allows developers to write custom templates and filters to add further filtering functionality (e.g. multi-select filters).

## Out of Scope
General filter template specification and general property based multi-select filtering mentioned in the [TDP Updates](#tdp-updates) section of this memorandum are out of scope for this memorandum.

## Method
To support multi-select/custom filtering in the DAC, both the TDP repository and the 508 repository will require updates.

### Django 508 Updates
508 builds the query string for all filters on the currently selected DAC page with the [dropdown-filter.js](https://github.com/raft-tech/django-admin-508/blob/main/admin_interface/static/admin_interface/508/dropdown-filter.js) JavaScript file. This file defines a JQuery function that operates on the `changelist-filter` element in the DOM. The function adds `onchange` event handlers to each filter in the `changelist-filter` element which extract the filter's query string template value that gets selected when it changes to construct a new query string. However, when custom templates and custom filters are introduced the JQuery function breaks down and cannot handle it. The implementation of the single-select and multi-select query building cannot be unified. This is because Django built-in single-select filters define a single prop on the `option` elements for the filter. The `value` prop that is defined on all the `option` elements is that `option`'s query parameter with the rest of the current query string appended to it. This same implementation cannot be achieved on multi-select filters because the query string cannot (and should not) contain multiple queries of the same type. This implies single-select and multi-select filters have to be handled in 508 differently. The update to `dropdown-filter.js` provided below serves as a guide towards a final solution for integrating multi-select filters, single-select filters, and the `Apply Filters` button. The implementation below relies on two key facts. One, all multi-select filters define `ariaMultiSelectable` and two, that all multi-select filters define two custom props: `key` and `value`. These key value pairs (e.g. `key=name__in`, `value=Bob`) are used to build the query string along with whatever the remaining single-select filters have chosen. When a user clicks the `Apply Filters` button, the code below executes and builds the query string for single and multi-select filters.

```javascript
if (typeof (django) !== 'undefined' && typeof (django.jQuery) !== 'undefined') {
  (function ($) {
    'use strict';
    $(document).ready(function () {
      const filters = document.querySelectorAll('#changelist-filter .list-filter-dropdown select')
      let query = '?'

      const applyFiltersButton = document.querySelector('#submit-filters');
      if (applyFiltersButton) {
        applyFiltersButton.onclick = function () {
          for (const filter of filters) {
            let conjunction = query === '?' ? '' : '&'
            if (!filter.ariaMultiSelectable) {
              if (filter.selectedIndex !== 0) {
                // Built in Django filters append the query string to the `value` field on the element. However, when we
                // have a mult-selectable filter, the select element can't have the `value` field as a query string
                // because multiple options can be selected and there is no way to track that. Therefore, we strip the
                // single select filters query param from the existing query string and build and entirely new query
                // string from that.
                let opt = filter.options[filter.selectedIndex]
                let query_str = opt.value
                let filter_query = ''
                for (let i = 1; i < query_str.length; i++) {
                  if (query_str[i] === '&') {
                    break
                  }
                  filter_query += query_str[i]
                }
                query = query.concat(conjunction, filter_query)
              }
            }
            else {
              // All multi select filters are required to set the `key` and `value` fields on the option element to the
              // individual options to be able to build the correct query string.
              let selected = ''
              for (const option of filter.options) {
                if (option.selected) {
                  selected = selected.concat(option.value, '%2C')
                }
              }
              selected = selected.substring(0, selected.lastIndexOf('%2C'))
              if (selected !== '') {
                query = query.concat(conjunction, filter.options[0].getAttribute('key'), '=', selected)
              }
            }
          }
          window.location = query
        };
      }
    });
  })(django.jQuery);
}
```

### TDP Updates
Currently, TDP implements a custom multi-select filter, with a custom template. This filter is complex and relies on a custom "filter" button to apply it's selection which is a very incohesive with the `Apply Filters` button that 508 introduces. To remedy this, the current and future multi-select/custom filters implemented in TDP need to give 508 control of constructing the appropriate query string by way of supplying 508 with the appropriate key-value pairs needed. In doing so, we can also simplify and generalize the current multi-select filter available in TDP.

TDP currently utilizes three classes to implement field based multi-select filtering. This can be simplified to the single class below when we let 508 manage query string building. There are three main features to note in this class. The first is the custom template used to create a multi-select drop down filter: [multiselectdropdownfilter.html](multiselectdropdownfilter.html). The second is the unique query string parameters that are defined in the `choices` method of the `FieldListMultiSelectFilter` class: `key` and `value`. These are the parameters that Django will populate into the aforementioned template and that 508 will parse to build the appropriate query string. The third and final feature to note is how the `FieldListMultiSelectFilter` overrides and adds new parameters in the constructor before calling `super()`. These additions and overrides help convert the parent class `AllValuesFieldListFilter` from a single-select to a multi-select filter. These three features allow TDP to support multi-select filtering based on Django model fields. However, this MVP implementation also provides a path forward for Django model property based multi-select filtering (e.g. the `fiscal_period` property on the `DataFile` model). Leveraging the aforementioned template and building a class which sub-classes the Django `SimpleListFiter` class we will have the ability to provide general multi-select filtering for Django model properties by implementing the correct `queryset`, `choices`, and `lookups` methods.

```python
class FieldListMultiSelectFilter(admin.AllValuesFieldListFilter):
    """Multi select dropdown filter for all kind of fields."""

    template = 'multiselectdropdownfilter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = '%s__in' % field_path
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        lookup_vals = request.GET.get(self.lookup_kwarg)
        self.lookup_vals = lookup_vals.split(',') if lookup_vals else list()
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull)
        self.empty_value_display = model_admin.get_empty_value_display()
        parent_model, reverse_path = reverse_field_path(model, field_path)
        # Obey parent ModelAdmin queryset when deciding which options to show
        if model == parent_model:
            queryset = model_admin.get_queryset(request)
        else:
            queryset = parent_model._default_manager.all()
        self.lookup_choices = (queryset
                               .distinct()
                               .order_by(field.name)
                               .values_list(field.name, flat=True))
        super(admin.AllValuesFieldListFilter, self).__init__(field, request, params, model, model_admin, field_path)

    def queryset(self, request, queryset):
        """Build queryset based on choices."""
        params = Q()
        for lookup_arg, value in self.used_parameters.items():
            params |= Q(**{lookup_arg: value})
        try:
            return queryset.filter(params)
        except (ValueError, ValidationError) as e:
            # Fields may raise a ValueError or ValidationError when converting
            # the parameters to the correct type.
            raise IncorrectLookupParameters(e)

    def prepare_querystring_value(self, value):
        """Mask commas."""
        return str(value).replace(',', '%~')

    def choices(self, changelist):
        """Generate choices."""
        add_facets = getattr(changelist, "add_facets", False)
        facet_counts = self.get_facet_queryset(changelist) if add_facets else None
        query_string = changelist.get_query_string({}, [self.lookup_kwarg, self.lookup_kwarg_isnull])
        yield {
            'selected': not self.lookup_vals and self.lookup_val_isnull is None,
            'query_string': query_string,
            'display': _('All'),
        }
        include_none = False
        count = None
        empty_title = self.empty_value_display
        for i, val in enumerate(self.lookup_choices):
            if add_facets:
                count = facet_counts[f"{i}__c"]
            if val is None:
                include_none = True
                empty_title = f"{empty_title} ({count})" if add_facets else empty_title
                continue

            val = str(val)
            qval = self.prepare_querystring_value(val)
            yield {
                'selected': qval in self.lookup_vals,
                'query_string': query_string,
                "display": f"{val} ({count})" if add_facets else val,
                'value': urllib.parse.quote_plus(val),
                'key': self.lookup_kwarg,
            }
        if include_none:
            yield {
                'selected': bool(self.lookup_val_isnull),
                'query_string': query_string,
                "display": empty_title,
                'value': 'True',
                'key': self.lookup_kwarg_isnull,
            }
```


## Affected Systems
- Django 508
- TANF-App

## Use and Test cases to consider
- Consider adding 508 integration tests for all/most Django fields for the suggested `FieldListMultiSelectFilter`
- Test having multiple Django built-in and `FieldListMultiSelectFilter`'s on the same page and verify the query string

