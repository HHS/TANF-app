"""Fixtures for live Go parser integration tests."""

from contextlib import closing

from django.conf import settings

import psycopg2
import pytest

from tdpservice.data_files.models import DataFile, ReparseFileMeta
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.search_indexes.util import MODELS


@pytest.fixture(scope="session")
def django_db_setup():
    """Use the live Docker database instead of creating an isolated test DB."""
    pass


def _delete_datafile_outside_transaction(datafile_id):
    """Delete parser artifacts on a committed connection the Go worker can see."""
    db_cfg = settings.DATABASES["default"]
    delete_specs = [
        (DataFileSummary._meta.db_table, "datafile_id"),
        (ParserError._meta.db_table, "file_id"),
        (ReparseFileMeta._meta.db_table, "data_file_id"),
    ]
    delete_specs.extend((model._meta.db_table, "datafile_id") for model in MODELS)

    with closing(
        psycopg2.connect(
            dbname=db_cfg["NAME"],
            user=db_cfg["USER"],
            password=db_cfg["PASSWORD"],
            host=db_cfg["HOST"],
            port=db_cfg["PORT"],
        )
    ) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            for table_name, column_name in delete_specs:
                cursor.execute(
                    f"DELETE FROM {table_name} WHERE {column_name} = %s",
                    [datafile_id],
                )

            cursor.execute(
                f"DELETE FROM {DataFile._meta.db_table} WHERE id = %s",
                [datafile_id],
            )


@pytest.fixture
def go_parser_datafile_cleanup(request):
    """Track Go parser datafiles and clean them up after each integration test."""
    datafile_ids = set()
    request.module._GO_PARSER_DATAFILE_IDS = datafile_ids

    yield datafile_ids

    request.module._GO_PARSER_DATAFILE_IDS = None

    for datafile_id in sorted(datafile_ids, reverse=True):
        _delete_datafile_outside_transaction(datafile_id)
