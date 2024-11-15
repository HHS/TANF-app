# Parsing log per file upload

**Audience**: TDP Software Engineers <br>
**Subject**:  Parsing log per file upload <br>
**Date**:     November 4, 2024 <br>

## Summary
This technical memorandum discusses the implementation of features to bring more visibility into system behavior during file parsing. This includes:
* Generating a storing a file for logs generated during the parsing run. The log file should be stored in s3 associated to the submitted data file.
* ~~Generating the parsing error report "in-band" with parsing and the log file. This should also be stored in s3 and associated to the submitted data file.~~ should be considered, but is out of scope for this memo.

This memo provides a suggested implementation, including describing some refactoring of the parsing process to bring some modularity to the new features.

## Background (Optional)
TDP currently uses python's `logging` utility to capture debug messages sent by the application to the terminal. These logs are captured by Cloud.gov, Prometheus, and Sentry.

* These logs possibly leak sensitive data
* Hard to dig back through logs to file errors associated with a particular upload
* No visibility into differences in logs between parse runs for the same file

## Out of Scope
Call out what is out of scope for this technical memorandum and should be considered in a different technical memorandum.
* Generating the parsing error report "in-band" with parsing and the log file.
* Efficiency - must write logs to file on disk and upload to s3 at the end of the parser run. this will have a memory impact as well as increase the run time of the parsing process.

## Method/Design
This section should contain sub sections that provide general implementation details surrounding key components required to implement the feature.

* utilize python `logging` to write to a file - https://docs.python.org/3/howto/logging.html#logging-to-a-file
   * will this have side effects with `logger` used in other places of the app?
   * if doesn't work, custom function to open a new file per parse run, write logs as lines in file.
   - logging to two files w/ different settings - https://stackoverflow.com/questions/11232230/logging-to-two-files-with-different-settings
   * logger doesn't gzip or compress the files (could potentially override or write custom `logging.FileHandler` to do this)

* upload file to s3, provide link saved w/ datafile
   * where should file link live? DataFileSummary, ReparseFileMeta, other?
   * alternatively, could (potentially) stream the file creation to s3 with `smart_open` - https://github.com/piskvorky/smart_open/tree/develop

### 1. Set up a logger instance before parse begins

* `tdpservice.scheduling.parser_task`
   * Move `logger = logging.getLogger(__name__)` out of the global (module) context and into a setup function
      ```python
      def setup_logger(name, filename):
         handler = logging.FileHandler(filename)
         logger = logging.getLogger(name)
         logger.addHandler(handler)
         logger.setLevel(logging.INFO) # the min level this will accept logs at
         return logger, handler
      ```
   * Call the new setup function at the beginning of `parse`, close the file handler at the end
      ```python
      def parse(data_file_id, reparse_id=None):
         # ... docstrings, start of function
         logger_name = f'parse-datafile-{data_file_id}-{timestamp}'
         logger, handler = setup_logger(logger_name, f'{logger_name}.log')
         logger.info(logger_name)

         # ... existing parser code inside the try/except

         handler.close()
         # ... end of function
      ```
   * Use the method-scoped `logger` instance throughout the parse routine by passing it down through the function calls
      ```python
      # `tdpservice.scheduling.parser_task.parse`
      errors = parse_datafile(data_file, dfs, logger)
      send_data_submitted_email(dfs, recipients, logger)
      log_parser_exception(
         data_file,
         f"Encountered Database exception in parser_task.py: \n{e}",
         "error",
         logger
      )
      log_parser_exception(
         data_file,
         (f"Uncaught exception while parsing datafile: {data_file.pk}! Please review the logs to "
         f"see if manual intervention is required. Exception: \n{e}"),
         "critical",
         logger
      )
      # `tdpservice.parser.parse.parse_datafile`
      # remove the module-scoped logger - logger = logging.getLogger(__name__)
      def parse_datafile(datafile, dfs, logger): # accept a logger instance in the function params
      # this function needs to be passed to every function that uses a logger
      bulk_create_errors({} , 1, flush=True, logger) # there are many, many of these
      # ... etc etc etc
      ```
      * Or, create some sort of singleton class so that downstream functions can access the per-parse logger
         ```python
         import logging

         def setup_logger(name, filename):
            handler = logging.FileHandler(filename)
            logger = logging.getLogger(name)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)  # the min level this will accept logs at
            return logger, handler

         class ParseLogContextHandler:
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

         # in settings
         PARSE_LOG_CONTEXT_HANDLER = ParseLogContextHandler()

         # in parser functions
         settings.PARSE_LOG_CONTEXT_MANAGER.set_logger_instance(f'parse-log-{data_file_id}')
         logger = settings.PARSE_LOG_CONTEXT_MANAGER.get_logger_instance()
         ```
      * memoized factory function
   * Add s3 upload to `tdpservice.scheduling.parser_task.parse`
      * upload alongside submitted file
      * include reparse id if applicable
      ```python
      # similar to `tdpservice.search_indexes.tasks.export_queryset_to_s3_csv`
      from botocore.exceptions import ClientError
      from tdpservice.data_files.s3_client import S3Client

      def parse(data_file_id, reparse_id=None):
         logger_name = f'parse-datafile-{data_file_id}-{timestamp}'
         logger, handler = setup_logger(logger_name, f'{logger_name}.log')
         logger.info(logger_name)

         # ... everything else

         handler.close()
         s3 = S3Client()
         try:
            s3.client.upload_file(local_filename, settings.AWS_S3_DATAFILES_BUCKET_NAME, f'parsing_logs/{logger_name}.log')
         except ClientError as e:
            logger.error('log upload to s3 failed')  # this would get logged to the file unless a new logger instance is created. should also create LogEntry here.
      ```
   * (optional or later step) - Create a `ReparseFileMeta` model for every parse run
      * Rename the reparse meta models to `ParseMeta` and `ParseFileMeta` (migration is possible)
      * Rename the `DataFile` `reparses` to `parses`
      * Remove `file.reparses.add(meta_model)` from `tdpservice.search_indexes.management.commands.clean_and_reparse._handle_datafiles`
      * would this require a custom/large migration? could create a separate model
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
provide a list of systems this feature will depend on/change.

## Use and Test cases to consider
provide a list of use cases and test cases to be considered when the feature is being implemented.
