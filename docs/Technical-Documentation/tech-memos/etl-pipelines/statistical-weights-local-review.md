# Statistical Weights: Local Review For Issue 6143

Run commands from the repository root. Use a disposable local environment, never
production credentials or submissions. Do not change the machine clock, run a
production reparse, delete historical outputs, or use the synthetic loader's
`--replace` against real submissions.

## 1. Prepare The Local Stack

```bash
task --list
task backend-up
```

Confirm Docker is available and the backend `.env` contains local-only settings.
Tasks may recreate the shared backend containers against this worktree; do not
run them while another worktree is using the same Compose project.

The integration task below creates, migrates, and drops its own uniquely named
PostgreSQL database. It uses eager Celery and an in-memory email backend, not
distributed worker execution. Its test API client is authenticated as a synthetic
System Admin; it does not exercise browser login or external mail delivery.

**Always include the trailing `--basetemp` override shown below.** The Taskfile
contains a broad default `/home/tdpapp/` that pytest could clean recursively;
the final option must instead name a dedicated container temporary directory.
Do not run two commands using the same basetemp directory at the same time.

## 2. Pause A Real API-To-Publication Run

In a terminal (a separate tmux pane if following the agent test workflow), run:

```bash
task backend-pytest-etl-integration PYTEST_ARGS="--basetemp=/tmp/tdp-pytest-etl-6143-review -k 'mixed_status_publication and TAN' --trace -s -vv"
```

Expect exactly **one selected case**, the `[TAN]` mixed-status test. After
migrations, pytest stops at the start of the test with a `(Pdb)` prompt. Enter:

```text
b _published_weight_rows
c
```

The breakpoint stops in `_published_weight_rows(pipeline_run)` after the API
POST, source selection, extraction, QA, publication, and notification have run.
The following commands are Python statements entered at that debugger prompt;
do not include `(Pdb)` when pasting them.

```python
p pipeline_run.status
p pipeline_run.parameters
p pipeline_run.final_output.published
p pipeline_run.final_output.row_count
p pipeline_run.metadata["source_datafile_ids"]
```

Expect `SUCCEEDED`, `{'fiscal_year': 2026, 'program': 'TAN'}`, `True`, `2`, and
three source lists named `active`, `aggregate`, and `stratum`. IDs vary per run.

## 3. Inspect Eligibility And Newer-Rejected Fallback

```python
from tdpservice.data_files.models import DataFile
selected_ids = [pk for ids in pipeline_run.metadata["source_datafile_ids"].values() for pk in ids]
p list(DataFile.objects.filter(pk__in=selected_ids).order_by("section__name").values_list("section__name", "quarter", "version", "state", "summary__status"))
```

Expect Q1/version **3** in every family:

| Family | Lifecycle | Summary |
| --- | --- | --- |
| Active | `parse_completed` | Accepted |
| Aggregate | `parsed_with_errors` | Accepted with Errors |
| Stratum | `parsed_with_errors` | Partially Accepted with Errors |

Now inspect the higher versions that were deliberately excluded:

```python
p list(DataFile.objects.filter(year=2026, section__program__code=pipeline_run.parameters["program"], version__gte=4).order_by("section__name", "version").values_list("section__name", "version", "state", "summary__status"))
```

For each family, version 4 is Rejected despite `parse_completed`, version 5 is
Pending, version 6 is still parsing, and version 7 has no summary (`None`).
Older eligible version 2 also exists, but version 3 wins across allowed summary
statuses. Q2 has only rejected inputs and contributes no selected IDs.

## 4. Inspect Exact Intermediate And Published Values

```python
from tdpservice.etl.models import StatisticalWeightsCaseCount, ETLQAResult
p list(StatisticalWeightsCaseCount.objects.filter(pipeline_run=pipeline_run).order_by("count_kind", "stratum").values_list("count_kind", "stt_code", "reporting_month", "stratum", "count"))
p list(StatisticalWeight.objects.filter(pipeline_run=pipeline_run).order_by("stratum").values_list("stt_code", "reporting_month", "stratum", "case_count", "cases", "weight"))
p list(ETLQAResult.objects.filter(pipeline_run=pipeline_run).values_list("check_key", "status", "result_payload"))
p list(pipeline_run.node_runs.values_list("node_key", "status"))
from django.core import mail
p len(mail.outbox)
```

Expected intermediate rows:

```text
S1  55  202510  1  2
S1  55  202510  2  1
S3  55  202510     12
S4  55  202510  1  8
```

Expected published rows:

```text
55  202510  1  2  8   4.0000
55  202510  2  1  12  12.0000
```

Stratum 1 uses T7/M7's count of 8; stratum 2 falls back to T6/M6's count of 12.
There must be no stratum 9, count 999, or Q2 row from excluded inputs. All seven
node runs should be SUCCEEDED. Four QA results should exist; review payloads,
including warnings if present, rather than ignoring them. A completion email
should be captured in `mail.outbox`; inspect `mail.outbox[-1].body` if desired.

## 5. Inspect Frozen IDs And Reparse Exclusion (Optional)

These mutations affect only this disposable integration database. They do not
reparse stored bytes or dispatch another pipeline.

```python
from tdpservice.etl.pipelines.statistical_weights import StatisticalWeightsPipeline
from tdpservice.etl.pipelines.sources import DataFileSourceSnapshot
from tdpservice.etl.test.weights_fixtures import create_weights_file
from tdpservice.parsers.models import DataFileSummary
from tdpservice.data_files.enums import SubmissionState
definition = StatisticalWeightsPipeline()
sources = definition.nodes.validate_run_sources.datafile_sources(pipeline_run.parameters["program"])
active_source = next(source for source in sources if source.key == "active")
selected = DataFile.objects.get(pk=pipeline_run.metadata["source_datafile_ids"]["active"][0])
newer = create_weights_file(selected.stt, selected.user, pipeline_run.parameters["program"], active_source, version=8, status=DataFileSummary.Status.ACCEPTED_WITH_ERRORS, state=SubmissionState.PARSED_WITH_ERRORS)
snapshots = DataFileSourceSnapshot()
p snapshots.latest_datafile_ids(2026, active_source)
p snapshots.snapshot(pipeline_run, fiscal_year=2026, sources=sources)
```

Fresh selection returns the new version 8 ID. Reusing the run snapshot must
still return the original version 3 IDs. Re-run the count/weight inspections
from step 4: persisted artifacts and published rows must be unchanged. This
demonstrates ID reuse after publication; the focused tests in step 7 additionally
verify a newer upload arriving between validation and extraction.

Add unfinished reparse metadata to the original selected ID:

```python
from tdpservice.data_files.models import ReparseFileMeta
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
reparse = ReparseMeta.objects.create()
overlap = ReparseFileMeta.objects.create(data_file=selected, reparse_meta=reparse)
p snapshots.snapshot(pipeline_run, fiscal_year=2026, sources=sources)
```

Expect `ActiveReparseDataFileOverlapError`, not silent replacement by version 8.
Remove just this synthetic metadata before continuing:

```python
overlap.delete()
reparse.delete()
```

## 6. Inspect Calendar Boundaries And Repeat For SSP/Tribal

At the same debugger prompt, the following is read-only:

```python
from datetime import date
from tdpservice.etl.scheduler import reporting_fiscal_year_for_date, is_first_workday
for day in (date(2026, 9, 30), date(2026, 10, 1), date(2027, 1, 31), date(2027, 2, 1), date(2025, 2, 1), date(2025, 2, 3)): print(day, reporting_fiscal_year_for_date(day), is_first_workday(day))
```

Expect respectively:

```text
2026-09-30  2026  False
2026-10-01  2026  True
2027-01-31  2026  False
2027-02-01  2027  True
2025-02-01  2025  False
2025-02-03  2025  True
```

Enter `clear` and confirm breakpoint removal, then `c` to finish the test.
Expect one passed case and automatic temporary-database cleanup. Do not leave
the debugger open when starting another command with the same basetemp.

Repeat steps 2–4 with `SSP`, then `TRIBAL`, instead of `TAN` in the `-k` filter.
The same counts and weights should result, using each program's parsed models.

## 7. Verify Scheduling, Permissions, And Reverse Reparse Guards

```bash
task backend-pytest PYTEST_ARGS="tdpservice/etl/test/test_scheduler.py tdpservice/etl/test/test_api.py tdpservice/etl/test/test_sources.py -vv"
task backend-pytest PYTEST_ARGS="tdpservice/etl/test/test_statistical_weights.py -k mixed_status -vv"
task backend-pytest PYTEST_ARGS="tdpservice/data_files/test/test_submission_lifecycle.py::test_prepare_datafile_for_reparse_rejects_active_pipeline_source tdpservice/search_indexes/test/test_reparse.py::test_reparse_command_rejects_active_pipeline_source tdpservice/search_indexes/test/test_reparse.py::test_clean_reparse_rejects_active_pipeline_source -vv"
```

Review named cases, not only the exit code: PENDING/RUNNING/SUCCEEDED monthly
suppression, FAILED retry eligibility, active conflicts from another month,
independent programs/months, local-date defaults, and no extra weekend run.
The tests align `created_at` with simulated dates; merely calling the scheduler
twice with a historical `today` while leaving real timestamps is not a reliable
monthly-suppression check. The API cases preserve a manual FY2027 request when
the scheduler chooses FY2026, and a manual FY2026 request when it chooses FY2027.
DIGIT creation remains forbidden. Reverse guards cover both PENDING/RUNNING
ETL runs and newly eligible error-status files.

## 8. Run The Full Numerical Regression

```bash
task backend-pytest-etl-integration PYTEST_ARGS="--basetemp=/tmp/tdp-pytest-etl-6143 -k statistical_weights -vv"
```

Expect six selected cases: FY2024 legacy parity, three manual mixed-status
program cases, and scheduled all-program publication for October and January.
The FY2024 case loads the large compressed extracts and may take several minutes.
It compares every sorted output tuple and four-decimal weight against the
unchanged expected CSV. A passing FY2024 regression is not FY2026 reconciliation.

## 9. Record Review Evidence And Stop

Record branch/commit, commands, selected IDs/statuses, intermediate and output
tuples, QA outcomes, and any discrepancies without copying sensitive submissions
into the repository. Local synthetic review cannot establish recovery of the
affected production FY2026 output. Follow the data-owner reconciliation procedure
in [the dataset memo](etl-statistical-weights-dataset.md#authorized-fy2026-reconciliation).
No production rerun, deletion, deployment, or historical-output cleanup is
authorized by completing this local review.
