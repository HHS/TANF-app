# Parsing log per file upload

**Audience**: TDP Software Engineers <br>
**Subject**:  Parsing log per file upload <br>
**Date**:     November 4, 2024 <br>

## Summary
This technical memorandum discusses the implementation of features to bring more visibility into system behavior during file parsing. This includes:
* Generating a storing a file for logs generated during the parsing run. The log file should be stored in s3 associated to the submitted data file.

This memo provides a suggested implementation, including describing some refactoring of the parsing process to bring some modularity to the new features.

## Background
TDP currently uses python's `logging` utility to capture debug messages sent by the application to the terminal. These logs are captured by Cloud.gov, Prometheus, and Sentry.

* These logs possibly leak sensitive data
* Hard to dig back through logs to file errors associated with a particular upload
* No visibility into differences in logs between parse runs for the same file

## Out of Scope
Call out what is out of scope for this technical memorandum and should be considered in a different technical memorandum.
* Efficiency - must write logs to file on disk and upload to s3 at the end of the parser run.
   * This will have a memory impact and a disk space impact, as well as increase the run time of the parsing process (network upload).
   * The singleton solution explored here will additionally increase memory utilization.
   * Some mitigation techniques are mentioned, but not implemented.
* Association of the parse log file with a model in the Django Admin Console.
   * An MVP of this feature only includes uploading the resulting file to s3, alongside the datafile submission.
   * An exploration of this was done in Method/Design Step 6, but is out of scope for this work.

## Method/Design

In general, this solution requires two simple parts:

1. Captures the log output during parsing of a datafile and write it to a file on disk
   * This solution utilizes the `FileHandler` already included as part of python's `logging` utility, which we use extensively throughout TDP (including throughout the parser). `FileHandler` allows log output to be written to a file on disk
      * [Documentation](https://docs.python.org/3/howto/logging.html#logging-to-a-file)
      * Example:
         ```python
         import logging


         def setup_logger(name, filename):
            handler = logging.FileHandler(filename)
            logger = logging.getLogger(name)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            return logger, handler


         logger, handler = setup_logger('test123', 'test123.log')
         logger.info('test123')
         logger.warning('asdddddddd3')
         logger.error('asdfasdf')
         handler.close()
         ```
   * This step can be accomplished using a custom-built file logger. However, since `logging` is already used extensively throughout the project, we chose to extend this existing functionality rather than have to replace it for a single use-case.
   * This comes with the drawback that `logging.FileHandler` doesn't compress the resulting file by default. We could potentially address this by overriding or creating a custom version of `logging.FileHandler`.

2. Upload the resulting file to s3 once parsing completes
   * Once parsing completes and a file containing logs is written to disk, we can use existing tooling in our application to upload the resulting file to s3. An example of this is already implemented in `tdpservice.search_indexes.tasks.export_queryset_to_s3_csv`
   * Example
      ```python
      from botocore.exceptions import ClientError
      from tdpservice.data_files.s3_client import S3Client

      s3 = S3Client()
      try:
         s3.client.upload_file(local_filename, settings.AWS_S3_DATAFILES_BUCKET_NAME, s3_file_path)
      except ClientError as e:
         logger.error('upload to s3 failed')
      ```
   * This simply uploads a local file to s3, using the `boto` library.
   * To limit disk usage, we could potentially write logs to s3 on-the-fly as parsing happens using the `smart_open` library.
      * https://github.com/piskvorky/smart_open/tree/develop
      * This would incur additional network timing/cost as parsing runs, as logs would need to be transmitted to s3 many times during the parse execution, rather than once after.


The biggest complicating factor to implementing this feature is allowing functions in multiple modules throughout the app to access the same instance of the logger. In general, instances of `logging` are scoped to the module-level (file-level) via a call to `logging.getLogger(__name__)` (where `__name__` is the module name). This allows all functions within a module to access the same logger instance. In our case, however, an instance of `logging` needs to be scoped to an individual run of the parsing engine: a logger instance is created when a file starts parsing, is used by functions in multiple modules throughout the app, then is destroyed once parsing is completed and the file is transferred to s3. This means a module-scoping of `logging` won't work, and leaves us with a couple options:
* Create a logger instance that gets passed through function parameters to other areas of the parser (functional approach)
   ```python
   # `tdpservice.scheduling.parser_task.parse`
   logger = setup_logger('parse-log', 'parse-log-123.log')
   errors = parse_datafile(data_file, dfs, logger)
   # `logger` also needs to be passed by `parse_datafile()` to other funcs
   ```
   * This requires a lot of passing of variables, creating the opportunity to miss a module or function
* Create a global (singleton) class that holds on to instances of `logging` so that other functions can access them.
   ```python
   class ParseLogContextManager:
      """Caches an instance of logger for use throughout the parse routine."""

      def __init__(self, logger_instance):
         self.logger_instance = None
         self.handler_instance = None

      def set_logger_instance(self, logger_name):
         """Creates and caches a new instance of logger."""
         logger, handler = setup_logger(logger_name, f'{logger_name}.log')
         self.logger_instance = logger
         self.handler_instance = handler

      def get_logger_instance(self):
         """Returns the cached instance of logger."""
         return self.logger_instance

      def clear_logger_instance(self):
         """Closes and clears the parse logger instance."""
         self.handler_instance.close()
         # upload to s3
   ```
   * This is easier to implement as it doesn't require modifying every function call in the parser
   * This likely has a higher memory impact, though, as an instance of this class will be present in memory for every instance of the application
   * More work has to be done to ensure thread-safety if we ever increase the number of worker threads (which could theoretically share an instance of the singleton for multiple concurrent parse runs). This "memoization" is included as part of the implementation details below

The remainder of this memo will focus on the singleton design pattern as the solution to implement.

### 1. Create the singleton class and initialize an instance in `settings`

In `tdpservice.parsers.parse_log_context_manager` (or similar), create the new singleton class

```python
import logging

def setup_logger(name, filename):
   pass


class ParseLogContextManager:
   """Caches an instance of logger for use throughout the parse routine."""

   def __init__(self, logger_instance):
      self.loggers = {}
```

In `settings.common`, intialize an instance of the singleton. Settings is used because Django already ensures there is only one instance of the settings object per application - it's already a singleton!

```python
from tdpservice.parsers.parse_log_context_manager import ParseLogContextManager

PARSE_LOG_CONTEXT_MANAGER = ParseLogContextManager()
```


### 2. Initialize a new logger in `parser_task`

In `tdpservice.scheduling.parser_task`, import settings
```python
from django.conf import settings
```

Then create a new logger instance at the beginning of the `parse` function
```python
settings.PARSE_LOG_CONTEXT_MANAGER.create_logger_instance(datafile_id, reparse_id)
```

At the end of the `parse` function, close the instance
```python
settings.PARSE_LOG_CONTEXT_MANAGER.clear_logger_instance(datafile_id, reparse_id)
```


### 3. Implement the remainder of `ParseLogContextManager`

Now, in `tdpservice.parsers.parse_log_context_manager`, we need to implement `ParseLogContextManager`'s remaining methods
```python
class ParseLogContextManager:
   """Caches an instance of logger for use throughout the parse routine."""

   def __init__(self, logger_instance):
      self.loggers = {}

   # can utilize this to avoid having to pass both params every time
   # (also accept `logger_name` as the param in functions below)
   def _get_logger_name(self, datafile_id, reparse_id):
      if reparse_id is None:
         return f"parse-log-{datafile_id}"
      return f"parse-log-{datafile_id}-{reparse_id}"

   # this implements the memoization technique to store one
   # instance of logger per datafile_id/reparse_id
   def set_logger_instance(self, datafile_id, reparse_id):
      """Creates and caches a new instance of logger."""
      logger_name = self._get_logger_name(datafile_id, reparse_id)
      logger, handler = setup_logger(logger_name, f'{logger_name}.log')

      self.loggers[logger_name] = {
         'logger': logger,
         'handler': handler
      }

   def get_logger_instance(self, datafile_id, reparse_id):
      """Returns the cached instance of logger."""
      logger_name = self._get_logger_name(datafile_id, reparse_id)
      return self.loggers[logger_name].['logger']

   def clear_logger_instance(self, datafile_id, reparse_id):
      """Closes and clears the parse logger instance."""
      logger_name = self._get_logger_name(datafile_id, reparse_id)
      self.loggers[logger_name].['handler'].close()
      # upload to s3
```

`setup_logger` can be implemented like so:
```python
def setup_logger(name, filename):
   handler = logging.FileHandler(filename)
   logger = logging.getLogger(name)
   logger.addHandler(handler)
   logger.setLevel(logging.DEBUG)  # the min level this will accept logs at
   return logger, handler
```


### 4. Use `ParseLogContextManager` throughout the parser

Currently, modules in `tdpservice.parsers` use `logging` scoped at the module level, with a line like this at the top of the file:
```python
logger = logging.getLogger(__name__)
```
REMOVE this line. 


Then, import settings
```python
from django.conf import settings
```

Then, INSIDE a function definition (with access to `datafile_id` and `reparse_id`), get the logger from the new singleton class
```python
logger = settings.PARSE_LOG_CONTEXT_MANAGER.get_logger_instance(datafile_id, reparse_id)
```

This instance of `logger` can be used the same as the previous instance. This change needs to be made in every module and function where logs should be written to the parse log file. This includes
* `tdpservice.scheduling.parser_task`
* `tdpservice.parsers.parse`
* `tdpservice.parsers.case_consistency_validator`
* `tdpservice.parsers.duplicate_manager`
* `tdpservice.parsers.fields`
* `tdpservice.parsers.row_schema`
* `tdpservice.parsers.util`


### 5. Implement the s3 upload

The s3 upload can be implemented with the following simple code:
```python
from botocore.exceptions import ClientError
from tdpservice.data_files.s3_client import S3Client

s3 = S3Client()
try:
   s3.client.upload_file(local_filename, settings.AWS_S3_DATAFILES_BUCKET_NAME, s3_file_path)
except ClientError as e:
   logger.error('upload to s3 failed')
```

This just needs to be placed where it makes the most sense. Make sure `handler.close()` has been called (such as is done in `ParseLogContextManager.clear_logger_context`).

### 6. (Optional) Associate logs to a submission in the Django Admin Console

To associate the uploaded log file with a submission in the admin console, we can
1. Add the s3 url to the existing `DataFile` or `DataFileSummary` models
   * These get wiped out with every reparse, so we would be unable to see log differences between parses of the same submission.
2. Modify `ReparseFileMeta` to be created for every parse run (not just reparses), effectively creating a `ParseFileMeta`
   * Addresses reparses wiping out previous logs
   * Allows us to track all reparse meta stats for regular parse runs as well
   * Requires substantial modification of the reparse command and the parser routine, as well as numerous migrations.
3. Create a new model solely for storing the s3 url of parser logs.
   * Easier implementation
   * Would have to manually correlate with `ReparseMeta` and `ReparseFileMeta` for reparse visibility.


A light exploration of option 2 above was done for this technical memorandum, simply to prove the migrations were allowed. The implementation steps below are incomplete and untested
* Rename the reparse meta models to `ParseMeta` and `ParseFileMeta` (migration is possible)
* Rename the `DataFile` `reparses` to `parses`
* Remove `file.reparses.add(meta_model)` from `tdpservice.search_indexes.management.commands.clean_and_reparse._handle_datafiles` and modify `tdpservice.scheduling.parser_task.parse` to create the meta model instead.
   ```python
   # `tdpservice.scheduling.parser_task.parse`
   file_meta = None

   if reparse_id:
      file_meta = ReparseFileMeta.objects.get(data_file_id=data_file_id, reparse_meta_id=reparse_id)
   else:
      file.reparses.add(meta_model)
      file.save()

   file_meta.started_at = timezone.now()
   file_meta.save()
   ```
   * Add a new field to `ParseFileMeta` to store the s3 logs url
   ```python
   # end of `tdpservice.scheduling.parser_task.parse`
   handler.close()
   s3 = S3Client()
   try:
      s3.client.upload_file(local_filename, settings.AWS_S3_DATAFILES_BUCKET_NAME, f'parsing_logs/{logger_name}.log')
      file_meta.logs_uri = f'parsing_logs/{logger_name}.log'
      file_meta.save()
      # .... the rest
   ```

## Affected Systems
* Parser routine - everything from the celery task to every called function needs access to `datafile_id` and `reparse_id` (or the generated `logger_name`) so that relevant functions can access the parser context
* Settings - will store a new singleton (global class; has a memory impact)
* Application server will be storing temporary/intermediary log file before it is uploaded to s3

## Use and Test cases to consider
* Ensure all types of parser errors are logged to the file
   * every level (debug, info, error)
   * every class (parser task, parser, case consistency, duplicate management, row schema, fields, transform fields)
   * parser exceptions (handled and unhandled)
* Test large file uploads with many errors. Test concurrent uploads of large files.