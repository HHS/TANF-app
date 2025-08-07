"""Apply Grafana views to the database."""

import logging
import os

from django.db import connection

CWD = os.path.dirname(os.path.abspath(__file__))
VIEWS_PATH = os.path.join(CWD, "../plg/grafana_views/")
VIEW_TYPES_PATHS = ["user_views", "admin_views"]

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def run(*args):
    """Apply Grafana views to the database."""
    # ./manage.py runscript apply_grafana_views
    for view_type in VIEW_TYPES_PATHS:
        view_type_path = os.path.join(VIEWS_PATH, view_type)
        for view_file in sorted(os.listdir(view_type_path)):
            view_file_path = os.path.join(view_type_path, view_file)
            with open(view_file_path, "r") as file:
                view = file.read()
                try:
                    logger.info(f"Applying view: {view_file}")
                    with connection.cursor() as cursor:
                        cursor.execute(view)
                except Exception:
                    logger.exception(
                        f"An error occurred while applying view: {view_file}"
                    )

    logger.info("Grafana views applied successfully.")
