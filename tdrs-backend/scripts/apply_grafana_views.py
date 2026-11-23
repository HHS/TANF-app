"""Apply Grafana views to the database."""

import logging
import os
from pathlib import Path

from django.db import connection, transaction

CWD = os.path.dirname(os.path.abspath(__file__))
VIEWS_PATH = os.path.join(CWD, "../plg/grafana_views/")
VIEW_TYPES_PATHS = ["user_views", "admin_views"]
CUSTOM_VIEW_FILES = (
    "latest_tanf_exiters_view_prod.sql",
    "stt_section_to_type_mapping.sql",
    "mr_record_counts_by_tableview.sql",
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def apply_view(path: Path) -> None:
    """Apply one SQL file and propagate failures to the deployment caller."""
    logger.info("Applying SQL file: %s", path.name)
    try:
        with connection.cursor() as cursor:
            cursor.execute(path.read_text())
    except Exception:
        logger.error("Failed to apply SQL file: %s", path.name)
        raise


def run(*args: str) -> None:
    """Apply Grafana views to the database."""
    # ./manage.py runscript apply_grafana_views
    for view_type in VIEW_TYPES_PATHS:
        view_type_path = Path(VIEWS_PATH) / view_type
        sql_files = sorted(
            path
            for path in view_type_path.iterdir()
            if path.is_file() and path.suffix == ".sql"
        )
        if not sql_files:
            raise FileNotFoundError(f"No generated SQL files in {view_type_path}")
        for path in sql_files:
            apply_view(path)

    # Counts depend on both generated views and the custom exiter view.
    with transaction.atomic():
        for filename in CUSTOM_VIEW_FILES:
            apply_view(Path(VIEWS_PATH) / "custom_views" / filename)

    logger.info("Grafana views applied successfully.")
