# TDP Prioritized Parser Errors

**Audience**: TDP Software Engineers <br>
**Subject**:  Prioritized Errors <br>
**Date**:     October 20, 2024 <br>

## Summary
This technical memorandum provides a suggested path to implement a set of new requirements OFA has generated to alleviate the sheer number of parser errors generated during a STT's data submission. OFA has indicated that some errors are of a lower priority for STTs to review and correct. Thus, the OFA team has requested that  "critical" be assigned to parser errors so that the report STTs receive is filtered down to only the critical errors that must be reviewed and fixed. Regardless of how errors are prioritized, STTs will still retain the ability to see a summary of all errors detected in the error report.

## Background
Currently, error reports are generated in the TDP backend via the `get_xls_serialized_file` function. This function accepts the serialized queryset of the appropriate `ParserError`s queryset. This function the writes an XLSX file and returns it to the user. Apart from the lack of priotization in the report generated from this function, it also introduces the possibility to cause an out of memory (OOM) error. This can occur because, the Django model serializer brings the entire queryset into memory to serialize it into JSON. Because these ParserError querysets can be very large (hundreds of thousands), we will also alleviate the memory pressure `get_xls_serialized_file` introduces by removing the Django model serializer and make use of queryset pagination.

## Out of Scope
Current requirements from OFA do not require category two errors to be queryable by value and expected value. That feature is out of scope within the tech memo and would require more design and implementation work.

## Method/Design
Given the current OFA requirements, we can implement prioritized/critical errors, and memory efficient report generation without too much work. OFA has provided [this OneNote](https://gorafttech.sharepoint.com/:o:/s/TDRSResearchDesign/EnIa1Mn4v7pOskW7BLomXhIBxUMlYLRU_f1C0dxemW7dWw?e=m0rNyI) document which outlines the error types, errors, and fields that are most important/prioritized for STTs to see.

### Memory Efficient Report Generation
As previously mentioned in the #background section, the `get_xls_serialized_file` introduces a method to serialize parser errors into a XLSX that requires the entire queryset of parser errors to be brought into memory. Because these querysets can be very large, having them in memory regularly kills Gunicorn workers with an OOM error. To remedy the issue, this tech memo suggests updating `get_xls_serialized_file` to not use Django model serializers and instead leverage the power of Django querysets and pagination. To accomplish this, instead of passing a JSON serialized querset to `get_xls_serialized_file`, a standard (un-evaluated) queryset should be passed. Then, the body of the `get_xls_serialized_file` function should be updated appropriately to use a queryset object instead of a JSON object to generate the XLSX spreadsheet. The updates should also include paginating the queryset to avoid bringing the entirety of the queryset into memory at any one time. The code snippet below provides an example of paginating the queryset and writing the appropriate fields of each entry to the XLSX report.

```python
paginator = Paginator(parser_errors, settings.BULK_CREATE_BATCH_SIZE)
row_idx = 6
for page in paginator:
    for record in page.object_list:
        rpt_month_year = str(getattr(record, 'rpt_month_year', None))
        fields_json = getattr(record, 'fields_json', {})

        worksheet.write(row_idx, 0, record.case_number)
        worksheet.write(row_idx, 1, rpt_month_year[:4])
        worksheet.write(row_idx, 2, calendar.month_name[int(rpt_month_year[4:])] if rpt_month_year[4:] else None)
        worksheet.write(row_idx, 3, format_error_msg(record.error_message, fields_json))
        worksheet.write(row_idx, 4, record.item_number)
        worksheet.write(row_idx, 5, friendly_names(fields_json))
        worksheet.write(row_idx, 6, internal_names(fields_json))
        worksheet.write(row_idx, 7, record.row_number)
        worksheet.write(row_idx, 8, str(ParserErrorCategoryChoices(record.error_type).label))
```

The three helper functions: `format_error_msg`, `friendly_names`, `internal_names` used to write the appropriate fields can be seen below.

```python
def format_error_msg(error_msg, fields_json):
    """Format error message."""
    for key, value in fields_json['friendly_name'].items():
        error_msg = error_msg.replace(key, value) if value else error_msg
    return error_msg


def friendly_names(fields_json):
    """Return comma separated string of friendly names."""
    return ','.join([i for i in fields_json['friendly_name'].values()])


def internal_names(fields_json):
    """Return comma separated string of internal names."""
    return ','.join([i for i in fields_json['friendly_name'].keys()])
```

### Prioritized/Critical Errors
[This OneNote](https://gorafttech.sharepoint.com/:o:/s/TDRSResearchDesign/EnIa1Mn4v7pOskW7BLomXhIBxUMlYLRU_f1C0dxemW7dWw?e=m0rNyI) is invaluable to the implementation of prioritized errors. Prioritizing errors could be a very large and technically challenging feature involving new migrations, validation/validator refactors, etc... However, this can all be avoided by making a key insight for each of the category two and category three validators by way of OFA's requirements for them. For the category two case, the OneNote document generically specifies category two validation surrounding: Family Affiliation, Citizenship and Closure reason. Further discussion with OFA indicated that it is important/a priority for a STT to see all category two errors encompassing these fields in their entirety. That makes prioritizing these category two errors extremely easy because the need to query those fields by specific values and expected values is not required. The queries below provide a complete implementation to query all category two errors encompassing those fields.

```python
# All cat2 errors associated with FAMILY_AFFILIATION and (CITIZENSHIP_STATUS or CLOSURE_REASON)
second_field = "CITIZENSHIP_STATUS" if is_active else "CLOSURE_REASON"
field_query = Q(field_name="FAMILY_AFFILIATION") | Q(field_name=second_field)
filtered_errors = filtered_errors.union(all_errors.filter(
    field_query,
    error_type=ParserErrorCategoryChoices.FIELD_VALUE
    ))
```

The key insight for the category three case is less obvious. Looking at the OneNote, it seems as though we might need to query errors based on field name(s), expected value and actual value. However, for category three errors that information is encoded into the error by its existence. For example, the OneNote indicates that a high priority error a STT should have included in their report is `If fam affil = 1 then SSN must be valid `. This exact error and it's values (expected and given) can be uniquely found in any of the active or closed case record schemas. E.g.:

```python
category3.ifThenAlso(
    condition_field_name='FAMILY_AFFILIATION',
    condition_function=category3.isEqual(1),
    result_field_name='SSN',
    result_function=category3.validateSSN(),
)
```

The existence of this error, with these fields, is uniquely defined in the appropriate schemas. The same can be said for the remaining high priority category three errors. Thus, to define the high priority errors we need only know the required field(s) and their error type. Given those pieces of information, queries of the form below can be used to filter STT error reports to only show the highest priority errors.

```python
errors.filter(fields_json__friendly_name__has_keys=[FIELD_NAME, FIELD_NAME, ETC...],
              error_type=ParserErrorCategoryChoices.VALUE_CONSISTENCY)
```

By unioning the category two queries from above with the remainder of the category three queries, a queryset containing only the highest priority errors can be generated and subsequently passed to `get_xls_serialized_file` generate and return the prioritized error report to the requesting STT.

## Affected Systems
- TDP backend
- TDP frontend: latency time incurred while generating report

## Use and Test cases to consider
- Admin can get both prioritized and un-prioritized report
- STT only recieves prioritized report
- Existing tests leveraging ParserError querysets are updated and re-validated for correctness
