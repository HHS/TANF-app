"""Preview or apply an audited repair of legacy DataFile submission states.

Dry-run (default)::

    ./manage.py runscript backfill_datafile_states

Apply changes::

    ./manage.py runscript backfill_datafile_states --script-args apply=true

The apply flag accepts true/false, yes/no, 1/0, or the bare word apply.
The lifecycle controller infers outcomes from existing summaries or stored
files. It skips pending summaries, active parser owners, and missing evidence.
Each repair records inferred history, not scans or parses executed now.
"""

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.submission_lifecycle import backfill_legacy_datafile_state

TRUTHY = {"1", "true", "t", "yes", "y", "apply"}


def _parse_apply(args: tuple[str, ...]) -> bool:
    """Accept an explicit apply argument; default to a read-only preview."""
    for arg in args:
        if arg is None:
            continue
        value = arg.split("=", 1)[1] if "=" in arg else arg
        return value.strip().lower() in TRUTHY
    return False


def run(*args: str) -> None:
    """Backfill legacy DataFile submission states through the controller."""
    apply = _parse_apply(args)
    print(f"Running in {'APPLY' if apply else 'DRY-RUN'} mode")
    files = DataFile.objects.filter(state=SubmissionState.UPLOADED).order_by("id")
    counts = {"would_update": 0, "updated": 0, "skipped": 0}

    for data_file in files.iterator():
        previous_state = data_file.state
        target_state, reason = backfill_legacy_datafile_state(data_file, apply=apply)
        if target_state is None:
            counts["skipped"] += 1
            print(f"SKIP {data_file.id}: {reason}")
            continue
        counts["updated" if apply else "would_update"] += 1
        print(
            f"{'UPDATE' if apply else 'WOULD UPDATE'} {data_file.id}: "
            f"{previous_state} -> {target_state.value} ({reason})"
        )

    print(counts)
