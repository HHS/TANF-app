# Reparsing

**Audience**: TDP Software Engineers <br>
**Subject**:  Reparsing <br>
**Date**:     August 9, 2024 <br>

## Summary
Re-parsing improves the flexibility of TDP's workflow for ingesting data files. These enhancement requests came out of pragmatic needs by the administrator user of the tool from 3041 and theoretical concerns from the development team in addressing current system limitations with this new feature.

## Background
https://github.com/raft-tech/TANF-app/issues/2870
https://github.com/raft-tech/TANF-app/issues/2820
https://github.com/raft-tech/TANF-app/releases/tag/v3.2.0-Sprint-90
https://github.com/raft-tech/TANF-app/pull/2772
https://github.com/raft-tech/TANF-app/issues/1858
https://github.com/raft-tech/TANF-app/issues/1350

[Driving force of reparsing](https://github.com/raft-tech/TANF-app/issues/2870)
- Reparsing files that are stuck in pending to some other state because validators have changed, or the parser has better exception handling

## Out of Scope
- Parsing and/or validator logic changes
- Data Model or search_indices changes
- Systemic/Infrastructure changes to accommodate large data sets
- End-user facing changes to our frontend
- Pipeline or Orchestration changes

## Method/Design
The reparsing enhancements focus on a maturization of the clean_and_reparse.py django commando which needed CLI invocation by system administrator(s). To mature and polish this feature to meet our new deliverables, we plan to shift major functionality and visibility into the Administrator Console to leverage our existing tools within.

#3004 introduced an initial pass at reparsing. From this key components were identified that would improve both reparsing and it's usability for the system administrators. The following items were identified to enhance the reparsing feature: introduce a Django model that tracks meta data surrounding the reparsing event, managing data synchronization and parallel execution of reparsing events, and moving away from the current CLI interface in favor of a DAC specific way to execute reparsing.

### Meta Model
This enhancement will seek to improve our visibility into what has happened during execution of a re-parsing command. We believe creating a database model to store relevant fields about the run will improve usability. Fields will include (start time, end time, number of files processed, which files were targetted, number of records repopulated, etc.)

### Data Synchronization
...

### DAC Reparse Action
To mature and polish this feature it should no longer be executed from the CLI. The DAC provides all/most of the necessary filtering required to specify what datafiles to reparse. Adding a new `reparse` action to the `DataFiles` page in the DAC provides a seamless experience for the admins while also providing the reparse event with the appropriate datafiles.
  #### Confirmation dialog asking "are you sure you want to reparse?"

## Affected Systems
- Elastic
- Postgres (records, dfs, datafiles, parser errors)

## Use and Test cases to consider
provide a list of use cases and test cases to be considered when the feature is being implemented.
