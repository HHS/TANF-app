# Guarantee Sequential Reparse Events

**Audience**: TDP Software Engineers <br>
**Subject**:  Sequential Reparsing <br>
**Date**:     August 8, 2024 <br>


## Summary
This technical memorandum aims to provide a software engineer with initial research, design patterns, and ideas necessary
to implement sequential reparsing in the TDP application. This document covers distributed/parallel data safety, how
the data synchronization allows sequential execution guarantees, and a last ditch timeout calculation necessary to
guarantee sequential reparse events at the application level. This memorandum does not take into account network partition tolerance or parsing idempotence.

## Background
When a reparse event is executed by an admin user a set of size N files can be selected where N is on the range
[0, # of datafiles in DB]. For each reparsing event, a ReparseMeta Django model is created to track meta data about the
event such as: the number of files to be reparsed, the number of records deleted before reparsing, the number of records
created during reparsing, a backup location, etc... The meta model also contains the fields: `files_completed`, and
`files_failed`. These two fields were added to the model for it to be able to track when all files in it's set of files
had finished the parsing process, regardless of whether they passed or failed parsing.

## Distributed/Parallel Data Safety
In the [Background](#background) section the meta model and some of it's fields were introduced along with the idea that
a reparse event generates N parsing tasks. Because (theoretically) all the tasks can execute in parallel, and there is
only one meta model per event, the meta model inherently becomes a shared object and therefore must be synchronized
across the set of N parsing tasks. There are many ways to synchronize data in a distributed system, both custom and not.
However, because the meta model is a database object, this technical memorandum suggests using the already tested and
vetted concurrency control and synchronization mechanisms inherent to TDPs Postgres database. That is for the fields in
the meta model that need to be updated in parallel (`files_completed`, `files_failed`, `num_records_created`), the
implementing engineer should ensure to leverage Django queries that convert to minimumly scoped locking database
transactions. This memorandum suggests leveraging the [select_for_update()](https://docs.djangoproject.com/en/5.0/ref/models/querysets/#select-for-update) query provides row based locking for transactions in a Postgres environment. Using this
query ensures that whichever task executes it first will be the only task that can update the fields. All other tasks trying to query the model for updates will be blocked until the original task releases the lock. Thus, each parser task can query the appropriate meta model, update the appropriate fields, and continue on as normal. The one caveat to this approach is that whenever an update needs to be made, the task must explicitely re-query the meta model to avoid any race conditions and stale
data. An piece of example code is given below to demostrate how the implementer might update the `files_completed` field. Note the function was implemented as a static member of the ReparseMeta class.

```python
@staticmethod
def increment_files_completed(reparse_meta_models):
    """
    Increment the count of files that have completed parsing for the datafile's current/latest reparse model.

    Because this function can be called in parallel we use `select_for_update` because multiple parse tasks can
    referrence the same ReparseMeta object that is being queried below. `select_for_update` provides a DB lock on
    the object and forces other transactions on the object to wait until this one completes.
    """
    if reparse_meta_models.exists():
        with transaction.atomic():
            try:
                meta_model = reparse_meta_models.select_for_update().latest("pk")
                meta_model.files_completed += 1
                if ReparseMeta.assert_all_files_done(meta_model):
                    ReparseMeta.set_reparse_finished(meta_model)
                meta_model.save()
            except DatabaseError:
                logger.exception("Encountered exception while trying to update the `files_reparsed` field on the "
                                    f"ReparseMeta object with ID: {meta_model.pk}.")
```

## Sequential Execution
...

## Last Ditch Timeout
...
