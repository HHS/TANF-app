# Database-Based Duplicate Detection Migration

**Audience**: TDP Software Engineers <br>
**Subject**: Migration from In-Memory to Database-Based Duplicate Detection <br>
**Date**: January 22, 2025 <br>

## Summary

This technical memorandum documents the suggested migration path from in-memory duplicate detection to database-based duplicate detection for the TANF Data Portal backend. This change is necessitated by the Program Integrity Audit requirement which will introduce datafiles with an order of magnitude more records per file than current datafiles. This necessitates an immediate architectural change to the duplicate and case consistency validation pipelines. These pipelines currently rely on in memory hashes of ALL records and in memory sorted containers of batches records to perform their validation and removal of records. However, with only 1GB of memory to work with, there is no feasible way to keep in memory duplicate detection and in memory removal of records due to the sheer number of records and hashes that would need to be stored. The suggested implementation eliminates complex in-memory caching and duplicate detection mechanisms in favor of efficient database queries, improving system scalability in our resource constrained environments and maintainability.

## Background

The backend currently implements duplicate detection using in-memory data structures that cache hashed parsed records during file processing. This approach works adequately for typical TANF data files containing thousands to hundreds of thousands of records. However, several factors necessitated a fundamental architectural change to handle the impending increase in records per file:

### Program Integrity Audit Requirements
The new Program Integrity Audit requirement mandates processing of significantly larger datafiles containing an order of magnitude more records per file. These files represent a 10-100x increase in size compared to typical TANF submissions.

### Memory Constraints
Our Celery worker process operates under a 1GB memory limit in the cloud.gov environment. Processing files with millions of records using in-memory duplicate detection will exceed this limit, causing worker crashes and processing failures.

### Complexity and Maintainability Issues
The current in-memory duplicate detection implementation is complex and difficult to debug/modify due to:
- Complex caching mechanisms across multiple data structures
- State management across parsing iterations
- Multiple types of hashing and nomenclature clashes
- Shared cache objects
- etc...

## Out of Scope

- Changes to the validation rules/framework
- Modifications to the error reporting mechanisms
- Performance optimizations beyond the core architectural change

## Method/Design

### RowSchema Class Modifications

The `RowSchema` class will undergo significant changes to support the database-based duplicate detection approach:

#### Removal of Hash Generation
- **Remove `generate_hashes_func`**: The current implementation used hash functions to generate unique identifiers for records during parsing for in-memory duplicate detection
- **Hash-based caching removed**: Complex hash generation logic that created memory overhead will be  completely eliminated
- **Simplified record processing**: Records no longer need to generate hashes during parsing, reducing computational overhead

#### Partial Duplicate Exclusion Query
- **Replace `should_skip_partial_dup_func`**: The functional approach for determining which records to skip during partial duplicate detection should be replaced with a declarative approach
- **Introduce `partial_dup_exclusion_query`**: A Django `Q` object that defines which records should be excluded from partial duplicate detection based on field values
- **Database-native filtering**: Exclusion logic will be handled at the database level rather than in Python code, improving performance and memory usage

```python
# Previous approach (removed)
should_skip_partial_dup_func = lambda record: record.SOME_FIELD == "SKIP_VALUE"

# New approach
partial_dup_exclusion_query = Q(SOME_FIELD="SKIP_VALUE")
```

### CaseConsistencyValidator Architectural Changes

The `CaseConsistencyValidator` will require fundamental changes to support the database-first approach:

#### Elimination of In-Memory Duplicate Management
- **Remove hashing mechanisms**: All hash-based duplicate detection logic will need to be eliminated from the validator
- **Eliminate duplicate manager class**: Complex in-memory duplicate management class to be removed entirely
- **Remove duplicate detector classes**: Specialized duplicate detection classes that maintained in-memory state will be removed

#### Serialization Strategy Changes
- **Current Approach**: CaseConsistencyValidator prevents serialization of cases with Category 4 errors by removing them from in-memory caches before database operations
- **New Approach**: All records are allowed to be serialized to the database regardless of case consistency errors
- **Post-Processing Cleanup**: Cases requiring removal due to consistency errors are tracked using the `serialized_cases` set and deleted after serialization by `_delete_serialized_cases`

```python
# New case tracking approach in BaseParser
def add_case_to_remove(self, should_remove, case_id: FrozenDict):
    """Add case ID to set of IDs to be removed later."""
    if should_remove:
        self.serialized_cases.add(case_id)

def _delete_serialized_cases(self):
    """Delete all cases that have already been serialized to the DB with cat4 errors."""
    if len(self.serialized_cases):
        cases = Q()
        for case in self.serialized_cases:
            cases |= Q(**case)
        for schemas in self.schema_manager.schema_map.values():
            schema = schemas[0]
            num_deleted, _ = schema.model.objects.filter(
                cases, datafile=self.datafile
            ).delete()
```

#### Benefits
- **Simplified state management**: Removed complex state tracking across parsing iterations

### Record Management Class Simplification

The migration from in-memory to database-based duplicate detection will enable significant simplification of record management classes:

#### Removal of SortedRecords Class
- **Eliminate complex sorting logic**: The `SortedRecords` class maintains sorted collections of records in memory for duplicate detection purposes
- **Eliminate in-memory record removal**: Currently, records are removed from in-memory collections when duplicates or case consistency errors are detected during parsing
- **Eliminate memory overhead**: The `SortedRecords` class consumes significant memory maintaining sorted data structures for large files

#### Transition to Records Class
- **Simplified record tracking**: The introduction of the `Records` class will serve as a straightforward container for records awaiting database serialization
- **No duplicate management**: Records are no longer removed from collections during parsing. All records flow through to database serialization
- **Reduced complexity**: Eliminates complex sorting and removal logic that was required for in-memory duplicate detection

```python
# Current approach
class SortedRecords:
    ...

# New simplified approach
class Records:
    """Maintains a dict of records where Key=Model and Value=[Record]."""

    def __init__(self):
        self.cases = dict()

    def add_record(self, case_id, record_model_pair, line_num):
        """Add a record_doc_pair to the dict."""
        record, model = record_model_pair
        if case_id is not None:
            self.cases.setdefault(model, dict())[record] = None
        else:
            logger.error(f"Error: Case id for record at line #{line_num} was None!")

    def get_bulk_create_struct(self):
        """Return dict of form {document: {record: None}} for bulk_create_records to consume."""
        return self.cases

    def clear(self, all_created):
        """Reset the dict if all records were created."""
        if all_created:
            # We don't want to re-assign self.cases here because we lose the keys of the record/doc types we've already
            # made. If we don't maintain that state we might not delete everything if we need to roll the records back
            # at the end of, or during parsing.
            for key in self.cases.keys():
                self.cases[key] = {}
```

#### Memory and Performance Benefits
- **Reduced memory footprint**: Elimination of sorted collections significantly reduces memory usage during parsing
- **Simplified data flow**: Records flow directly from parsing to database without complex in-memory manipulations
- **Improved garbage collection**: Fewer complex data structures reduce pressure on Python's garbage collector

### Database-Based Duplicate Detection Architecture

The proposed implementation leverages PostgreSQL's efficient querying capabilities to detect duplicates after records have been persisted to the database, rather than maintaining in-memory caches during parsing.

#### Exact Duplicate Detection

The `_delete_exact_dups()` method below implements a slightly naive exact duplicate detection using database queries. This function does not take into account the queryset size brought into memory for processing which could cause problems in the event the entire datafile was duplicates.

```python
def _delete_exact_dups(self):
    """Delete exact duplicate records from the DB."""
    for schemas in self.schema_manager.schema_map.values():
        schema = schemas[0]

        fields = [f.name for f in schema.fields if f.name != "BLANK"]
        duplicate_vals = (
            schema.model.objects.filter(datafile=self.datafile)
            .values(*fields)
            .annotate(row_count=Count("line_number", distinct=True))
            .filter(row_count__gt=1)
        )

        for dup_vals_dict in duplicate_vals:
            dup_vals_dict.pop("row_count", None)
            dup_records = schema.model.objects.filter(**dup_vals_dict).order_by("line_number")
            record = dup_records.first()

            # Generate errors for duplicates and delete them
            for dup in dup_records[1:]:
                # Error generation logic...

            # Mark case for deletion and remove duplicate records
            num_deleted = dup_records._raw_delete(dup_records.db)
```

#### Partial Duplicate Detection

The `_delete_partial_dups()` method handles partial duplicates in a similar fashion to the `_delete_exact_dups` function. The key differences here are the introduction of the `partial_dup_exclusion_query` (referenced above) and the check to see if partial duplicate detection should even occur. The `partial_dup_exclusion_query` is a Django `Q` object that defines what fields and values eliminate a record from being included in the partial duplicate detection process.

```python
def _delete_partial_dups(self):
    """Delete partial duplicate records from the DB."""
    if not self.is_active_or_closed:
        return

    for schemas in self.schema_manager.schema_map.values():
        schema = schemas[0]
        fields = schema.get_partial_dup_fields()
        records = schema.model.objects.filter(datafile=self.datafile)

        if schema.partial_dup_exclusion_query is not None:
            records = records.exclude(schema.partial_dup_exclusion_query)

        partial_dups_values = (
            records.values(*fields)
            .annotate(row_count=Count("line_number", distinct=True))
            .filter(row_count__gt=1)
        )

        # Process partial duplicates...
```

### Database Cleanup Execution Order

To preserve the same validation logic as the previous in-memory method, the database cleanup operations must be executed in a specific order:

#### Required Execution Sequence

1. **`_delete_exact_dups()`** - Must be called first
   - Identifies and removes exact duplicate records from the database
   - Marks cases containing duplicates for deletion via `serialized_cases`
   - Preserves the first occurrence of each duplicate record set

2. **`_delete_partial_dups()`** - Must be called second
   - Identifies and removes partial duplicate records based on schema-defined field sets
   - Uses `partial_dup_exclusion_query` to filter out records that should not be considered
   - Marks cases containing partial duplicates for deletion via `serialized_cases`
   - Only processes active/closed case data files (`is_active_or_closed` check)

3. **`_delete_serialized_cases()`** - Must be called last
   - Removes entire cases that were marked for deletion by the duplicate detection methods and `CaseConsistencyValidator`
   - Operates on the accumulated `serialized_cases` set

#### Order Rationale

This sequence is critical because:
- **Duplicate detection first**: Both exact and partial duplicate methods identify problematic records and mark their cases for removal
- **Case cleanup last**: The serialized case deletion ensures that entire cases containing any duplicate records or case consistency  errors are removed, maintaining data integrity
- **Preserves validation logic**: This order matches the previous in-memory approach where duplicates were detected during parsing and cases were prevented from serialization

```python
# Correct execution order in parser
self._delete_exact_dups()      # Step 1: Handle exact duplicates
self._delete_partial_dups()    # Step 2: Handle partial duplicates
self._delete_serialized_cases() # Step 3: Clean up marked cases
```

### Key Architectural Changes

#### 1. Elimination of In-Memory Caching
- Removed complex in-memory data structures for duplicate tracking
- Eliminated memory pressure during large file processing
- Simplified state management during parsing

#### 2. Database-First Approach
- Records are persisted to the database immediately after validation
- Duplicate detection occurs via SQL queries on persisted data
- Leverages PostgreSQL's optimized query engine and indexing

#### 3. Batch Processing Integration
- Duplicate detection runs after bulk record creation
- Integrates seamlessly with existing batch processing mechanisms
- Maintains transactional integrity

#### 4. Error Generation Consistency
- Maintains existing error message formats and categorization
- Preserves line number references for debugging
- Continues to generate Category 4 (case consistency) errors appropriately

### Processing Flow

The new processing flow follows this sequence:

1. **Parse and Validate Records**: Records are parsed and validated using existing schemas
2. **Case Consistency Validation**: CaseConsistencyValidator validates records and tracks cases requiring removal, but allows all records to be serialized
3. **Bulk Create Records**: All valid records are persisted to the database in batches, including those from cases with Category 4 errors
4. **Detect Exact Duplicates**: Database queries identify exact duplicate records
5. **Detect Partial Duplicates**: Database queries identify partial duplicates based on schema-defined field sets
6. **Delete Serialized Cases**: Cases marked for removal due to Category 4 errors are deleted from the database
7. **Generate Errors**: Appropriate parser errors are generated for detected duplicates and case consistency issues
8. **Final Cleanup**: Any remaining cleanup operations are performed

### Memory Usage Optimization

The database-based approach provides several memory usage benefits:

- **Constant Memory Usage**: Memory usage remains constant regardless of file size for duplicate detection
- **No Caching Overhead**: Eliminates memory overhead of maintaining duplicate detection caches
- **Garbage Collection Friendly**: Reduces pressure on Python's garbage collector
- **Predictable Performance**: Memory usage is predictable and less likely to overflow

### Database Performance Considerations

To ensure efficient duplicate detection queries:

- **Indexing Strategy**: Existing database indexes on key fields (RecordType, RPT_MONTH_YEAR, CASE_NUMBER) optimize duplicate detection queries
- **Query Optimization**: Uses Django ORM's `values()` and `annotate()` for efficient aggregation
- **Batch Processing**: Processes duplicates in manageable batches to avoid long-running transactions
- **Raw Deletion**: Use `_raw_delete()` for efficient bulk deletion of duplicate records
- **Pagination**: Use paginated querysets to ensure memory safety while evaluating duplicates

## Affected Systems

### Core Parser Components
- **BaseParser**: Modified duplicate detection methods (`_delete_exact_dups`, `_delete_partial_dups`) and added case tracking (`add_case_to_remove`, `_delete_serialized_cases`)
- **TanfDataReportParser**: Updated processing flow to integrate database-based duplicate detection and case cleanup
- **CaseConsistencyValidator**: No longer prevents serialization of cases with Category 4 errors; instead tracks cases for post-processing deletion
- **Records Class**: Simplified to remove duplicate tracking functionality

### Database Layer
- **Django Models**: All TANF/SSP record models (T1-T7, M1-M7, etc.)
- **Database Indexes**: Leverages existing indexes for efficient duplicate queries
- **Query Performance**: Optimized for large-scale duplicate detection operations

## Use and Test Cases to Consider

Consider some performance testing along with a guarentee that all existing unit tests and integration tests still pass.

### Performance Testing
- **Large File Processing**: Test with files containing 3-10 million records
- **Memory Usage Monitoring**: Verify memory usage stays within 1GB limit
- **Processing Time Benchmarks**: Establish baseline performance metrics

## Implementation Benefits

### Scalability
- **Unlimited File Size**: Can process files of any size within disk space constraints
- **Predictable Resource Usage**: Memory usage independent of file size with respect to duplicate detection
- **Horizontal Scaling**: Database-based approach scales with database capacity

### Maintainability
- **Simplified Code**: Eliminates complex in-memory state management
- **Easier Debugging**: Database queries are easier to debug and optimize
- **Clear Separation of Concerns**: Duplicate detection logic isolated in dedicated methods

### Reliability
- **Reduced Memory Errors**: Significantly reduces the likelihood of out-of-memory crashes
- **Consistent Performance**: Database queries provide consistent performance characteristics
- **Better Error Handling**: Simplified error handling without memory pressure concerns

### Observability
- **Database Monitoring**: Can monitor duplicate detection performance via database metrics
- **Query Analysis**: Can analyze and optimize duplicate detection queries via Sentry
- **Resource Tracking**: Clear visibility into database resource utilization

This suggested implementation represents a significant architectural change that enables the backend to meet the Program Integrity Audit requirements under strict resource requirements while improving overall system reliability and maintainability.
