"""`populate_stts` command."""

import csv
import json
import logging
from pathlib import Path

from django.core.management import BaseCommand
from django.utils import timezone

from ...models import STT, Region

DATA_DIR = BASE_DIR = Path(__file__).resolve().parent / "data"
logger = logging.getLogger(__name__)


def _populate_regions():
    with open(DATA_DIR / "regions.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            Region.objects.get_or_create(id=row["Id"], name=row["name"])
        Region.objects.get_or_create(id=1000, name=None)


def _load_csv(filename, entity):
    with open(DATA_DIR / filename) as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            stt, stt_created = STT.objects.get_or_create(name=row["Name"])
            if stt_created:  # These lines are spammy, should remove before merge
                logger.debug("Created new entry for " + row["Name"])

            stt.postal_code = row["Code"]
            stt.region_id = row["Region"]
            if filename == "tribes.csv":
                stt.state = STT.objects.get(
                    postal_code=row["Code"], type=STT.EntityType.STATE
                )

            chars = 3 if entity == STT.EntityType.TRIBE else 2
            stt.stt_code = str(row["STT_CODE"]).zfill(chars)

            stt.type = entity
            stt.filenames = json.loads(row["filenames"].replace("'", '"'))
            stt.ssp = row["SSP"]
            stt.sample = row["Sample"]
            # TODO: Was seeing lots of references to STT.objects.filter(pk=...
            #       We could probably one-line this but we'd miss .save() signals
            #       https://stackoverflow.com/questions/41744096/
            # TODO: we should finish the last columns from the csvs: Sample, SSN_Encrypted
            stt.save()


def _maybe_bool(value):
    """Convert common string boolean values to actual booleans."""
    if isinstance(value, str):
        return value.lower() in ("1", "true", "t", "yes", "y")
    return value


def _get_override_path(overrides_path):
    return Path(overrides_path) if overrides_path else DATA_DIR / "stt_overrides.json"


def _find_stt_for_override(override):
    """Find an STT to update using name or postal_code (optionally type)."""
    name = override.get("name") or override.get("Name")
    if name:
        return STT.objects.filter(name=name).first()

    postal_code = override.get("postal_code") or override.get("Code")
    if not postal_code:
        return None

    lookup = {"postal_code": postal_code}
    stt_type = override.get("type")
    if stt_type:
        lookup["type"] = stt_type
    return STT.objects.filter(**lookup).first()


def _apply_overrides(overrides_path=None):
    """
    Apply overrides from a JSON file.

    The override file should be a list of objects. Each object must provide a
    lookup key (`name` or `postal_code`) and any fields to override (e.g., `ssp`,
    `sample`, `filenames`, `region_id`, `stt_code`, `type`, `postal_code`).
    """
    path = _get_override_path(overrides_path)
    if not path.exists():
        logger.info("No STT overrides found at %s; skipping.", path)
        return

    with open(path) as overrides_file:
        overrides = json.load(overrides_file)

    for override in overrides:
        stt = _find_stt_for_override(override)
        if not stt:
            logger.warning("No STT found for override: %s", override)
            continue

        # Only override fields explicitly provided
        for field in [
            "ssp",
            "sample",
            "filenames",
            "region_id",
            "stt_code",
            "type",
            "postal_code",
        ]:
            if field in override:
                setattr(stt, field, _maybe_bool(override[field]))

        stt.save()
        logger.info("Applied override for STT %s", stt.name)


class Command(BaseCommand):
    """Command class."""

    help = "Populate regions, states, territories, and tribes."

    def add_arguments(self, parser):
        """Register command-line arguments for the populate_stts command."""
        parser.add_argument(
            "--apply-overrides",
            action="store_true",
            help="Apply overrides from stt_overrides.json (or --overrides path).",
        )
        parser.add_argument(
            "--overrides",
            type=str,
            default=None,
            help="Optional path to an overrides JSON file.",
        )

    def handle(self, *args, **options):
        """Populate the various regions, states, territories, and tribes."""
        _populate_regions()

        stt_map = [
            ("states.csv", STT.EntityType.STATE),
            ("territories.csv", STT.EntityType.TERRITORY),
            ("tribes.csv", STT.EntityType.TRIBE),
        ]

        for datafile, entity in stt_map:
            _load_csv(datafile, entity)

        if options.get("apply_overrides"):
            _apply_overrides(options.get("overrides"))

        logger.info("STT import executed by Admin at %s", timezone.now())
