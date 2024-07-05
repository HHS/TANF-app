# Clean and Re-parse DataFiles

## Background
As TDP has evolved so has it's validation mechanisms, messages, and expansiveness. As such, many of the datafiles locked in the database and S3
have not undergone TDP's latest and most stringent validation processes. Because data quality is so important to all TDP stakeholders
we wanted to introduce a way to re-parse and subsequently re-validate datafiles that have already been submitted to TDP to enhance the integrity
and the quality of the submissions. The following lays out the process TDP takes to automate and execute this process, and how this process can
be tested locally and in our deployed environments.

## Clean and Re-parse Flow
As a safety measure, this process must ALWAYS be executed manually by a system administrator. Once executed, all processes thereafter are completely
automated. The steps below outline how this process executes.

1. System admin logs in to the appropriate backend application. E.g. `tdp-backend-raft`.
2. System admin enters the Django shell. `python manage.py shell_plus`.
3. System admin executes the `clean_and_reparse` Django command.
4. System admin validates the command is selecting the appropriate set of datafiles to reparse and executes the command.
5. `clean_and_reparse` collects the appropriate datafiles that match the system admin's command choices.
6. `clean_and_reparse` executes a backup of the Postgres database.
7. `clean_and_reparse` creates/deletes appropriate Elastic indices pending the system admin's command choices.
8. `clean_and_reparse` deletes documents from appropriate Elastic indices pending the system admin's command choices.
9. `clean_and_reparse` deletes all Postgres rows associated to all selected datafiles.
10. `clean_and_reparse` deletes `DataFileSummary` and `ParserError` objects associated with the selected datafiles.
11. `clean_and_reparse` re-saves the selected datafiles to the database.
12. `clean_and_reparse` pushes a new `parser_task` onto the Redis queue for each of the selected datafiles.



