# Field Type Casting Performance Optimization

**Audience**: TDP Software Engineers <br>
**Subject**: Elimination of Type Casting in Field Validation Pipeline <br>
**Date**: September 23, 2025 <br>

## Summary

This technical memorandum documents the suggested implementation to remediate a performance bottleneck identified in the TDP parsing engine. Software based profiling identified the hotspot in `/tdpservice/parsers/validators/base.py:28` at the `_handle_kwargs` function. Specifically, the type casting operations performed during field validation. The profiler identified this small function as being responsible for roughly 20% of the parsing engines memory footprint. This change is necessitated by the Program Integrity Audit requirement which will introduce datafiles with an order of magnitude more records per file than current datafiles, making the current type casting approach not only inefficient but also infeasible. The suggested implementation eliminates millions to hundreds of millions of unnecessary string-to-integer conversions by converting numeric fields in Tribal, TANF, and SSP RowSchemas to store true integers which will meaningfully improve system performance and memory efficiency.

## Background

The performance bottleneck stems from the current field schema design where **numeric fields are defined as strings to preserve leading zeros**, but are then repeatedly cast to integers during validation. The issue manifests in the validation pipeline as:

```python
# In validators/base.py:28
def _handle_kwargs(val, **kwargs):
    if "cast" in kwargs and kwargs["cast"] is not None:
        val = _handle_cast(val, kwargs["cast"])  # ← HOTSPOT: Millions of casts
    return val
```

Example from TANF T1 schema showing the problematic pattern:

```python
Field(
    item="27",
    name="WAIVER_EVAL_CONTROL_GRPS",
    friendly_name="waiver evaluation control groups",
    type=FieldType.ALPHA_NUMERIC, # ← Stored as string
    startIndex=113,
    endIndex=114,
    required=False,
    validators=[category2.isBetween(0, 9, inclusive=True, cast=int)], # ← Triggers cast=int
)
```

This approach works adequately for typical TANF data files containing dozens to hundreds of thousands of records. However, the following factors necessitate a change to our loose typing of fields and validation to a much stricter system.

### Program Integrity Audit Requirements
The new Program Integrity Audit requirement mandates processing of significantly larger datafiles containing an order of magnitude more records per file. These files represent a 10-100x increase in size compared to typical TANF submissions.

### Memory Constraints
Our Celery worker process operates under a 1GB memory limit in the cloud.gov environment. Processing files with millions of records using the current type casting approach adds extra unnecessary overhead to the CPU and RAM which can cause worker crashes and processing failures.

### Performance Impact Analysis
Based on the profiling data:
- **Memory Usage**: 492,187.6 KiB (~492 MB) allocated at `_handle_kwargs` out of 2483895.6 KiB (~2.5GB)
- **Scale**: With large TANF data files containing hundreds of thousands or millions of records, this translates to:
  - **Millions to hundreds of millions** of type cast operations per file
  - Significant CPU cycles wasted on repetitive conversions and garbage collection
  - Memory fragmentation from constant allocation/deallocation

## Out of Scope

- Changes to the validation rules/framework logic beyond type casting elimination
- Performance optimizations beyond the core field type casting issue

## Method/Design

### Field Class Modifications

The `Field` class will not require any modifications. Instead the design already exists and simply needs to be implemented.

### Schema Definition Updates

All alpha numeric field definitions that are numerics with leading zeros will be update to numeric field definitions across tribal, TANF, and SSP schemas to eliminate type casting:

#### Removal of Cast Parameters
- **Remove `cast=int` from validators**: Validators will receive native integer values
- **Update field type assignments**: Assign appropriate field types based on leading zero requirements
- **Simplify validation logic**: Direct integer comparisons without conversion overhead

```python
# Current approach (causes hotspot)
Field(
    name="NBR_FAMILY_MEMBERS",
    type=FieldType.NUMERIC,  # Stored as string internally
    validators=[category2.isBetween(1, 99, inclusive=True, cast=int)],  # ← Triggers casting
)

# New approach (optimized)
Field(
    name="NBR_FAMILY_MEMBERS",
    type=FieldType.NUMERIC,  # Stored as native integer
    validators=[category2.isBetween(1, 99, inclusive=True)],  # ← Direct integer validation
)
```

### Removal of the Hotspot

The `_handle_kwargs` function and it's dependencies can be removed in their entirety.

### Model Updates
For any RowSchema field that is converted to a numeric, consider also changing the appropriate model schema definitions to avoid further type casting at model creation time. Thorough testing and planning should be considered with respect to migrations if the change is implemented up through to the model.

## Affected Systems

### Core Parser Components
- **Validator Base Functions**: Removal of `_handle_kwargs()` to eliminate cast parameter handling
- **Schema Definitions**: All tribal, TANF, and SSP schema files updated to remove `cast=int` parameters
- **Model Definitions**: All model definitions are updated to match the RowSchema definitions (stretch)

### Validation Pipeline
- **Validators**: All numeric validators audited to ensure minimal or no type casting

## Use and Test Cases to Consider

All existing unit tests should pass unchanged except for tests that explicitely match a value on a leading zero. E.g.

```python
assert expected_value == "001"
```

The suggested implementation represents a targeted performance optimization and stronger typing system that enables the backend to meet the Program Integrity Audit requirements under strict resource constraints while improving overall system reliability and maintainability.
