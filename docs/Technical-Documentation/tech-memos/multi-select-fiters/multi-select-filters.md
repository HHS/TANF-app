# Multi-Select Filters

**Audience**: TDP Software Engineers <br>
**Subject**:  Multi-Select Filter Integration <br>
**Date**:     August 8, 2024 <br>

## Summary
This is a template to use to create new technical memorandums.

## Background
TDP has been expanding it's Django Admin Console (DAC) filtering capabilities by introducing custom filters, specifically multi-select filters. This has introduced a myriad of issues because TDP does not use the default DAC. Instead, to assist with accessability compliance TDP wraps the default DAC with [Django 508](https://github.com/raft-tech/django-admin-508) (henceforth referred to as 508) which makes various updates to the styling and functionality of the default DAC. A key change is that 508 introduces to the DAC is an `Apply Filters` button that intercepts query string parameters from default DAC filters and only applies them after clicking the button. The default DAC applies the filters as they are selected as opposed to all at once. The issue with 508's approach is that it assumes all filters are builtin Django filters (i.e. single select filters). This presents a discrepancy because Django allows developers to write custom templates and filters to add further filtering functionality (e.g. multi-select filters).

## Out of Scope
Call out what is out of scope for this technical memorandum and should be considered in a different technical memorandum.

## Method/Design
This section should contain sub sections that provide general implementation details surrounding key components required to implement the feature.

### Sub header (piece of the design, can be many of these)
sub header content describing component.

## Affected Systems
provide a list of systems this feature will depend on/change.

## Use and Test cases to consider
provide a list of use cases and test cases to be considered when the feature is being implemented.
