"""Fixtures for live Go parser integration tests."""

from contextlib import closing
from typing import Iterable

from django.conf import settings
from django.db.models.signals import post_save

import psycopg2
import pytest
from psycopg2 import sql

from tdpservice.data_files.models import DataFile, LegacyFileTransfer, ReparseFileMeta
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.search_indexes.models.program_audit import (
    ProgramAudit_T1,
    ProgramAudit_T2,
    ProgramAudit_T3,
)
from tdpservice.search_indexes.util import MODELS
from tdpservice.security.models import ClamAVFileScan
from tdpservice.stts.models import STT, Region
from tdpservice.users.models import User


@pytest.fixture(scope="session")
def django_db_setup():
    """Use the live Docker database instead of creating an isolated test DB."""
    pass


def _connect_to_default_database():
    """Create a raw connection to the same database used by Django."""
    db_cfg = settings.DATABASES["default"]
    return psycopg2.connect(
        dbname=db_cfg["NAME"],
        user=db_cfg["USER"],
        password=db_cfg["PASSWORD"],
        host=db_cfg["HOST"],
        port=db_cfg["PORT"],
    )


def _delete_datafiles_outside_transaction(datafile_ids: Iterable[int]) -> None:
    """Delete parser artifacts on a committed connection the Go worker can see."""
    datafile_ids = sorted(set(datafile_ids), reverse=True)
    if not datafile_ids:
        return

    delete_specs = [
        (DataFileSummary._meta.db_table, "datafile_id"),
        (ParserError._meta.db_table, "file_id"),
        (ReparseFileMeta._meta.db_table, "data_file_id"),
    ]
    record_models = MODELS + [ProgramAudit_T1, ProgramAudit_T2, ProgramAudit_T3]
    delete_specs.extend(
        (model._meta.db_table, "datafile_id") for model in record_models
    )
    null_specs = [
        (ClamAVFileScan._meta.db_table, "data_file_id"),
        (LegacyFileTransfer._meta.db_table, "data_file_id"),
    ]

    with closing(_connect_to_default_database()) as conn:
        conn.autocommit = True
        with conn.cursor() as cursor:
            for table_name, column_name in null_specs:
                cursor.execute(
                    sql.SQL("UPDATE {} SET {} = NULL WHERE {} = ANY(%s)").format(
                        sql.Identifier(table_name),
                        sql.Identifier(column_name),
                        sql.Identifier(column_name),
                    ),
                    [datafile_ids],
                )

            for table_name, column_name in delete_specs:
                cursor.execute(
                    sql.SQL("DELETE FROM {} WHERE {} = ANY(%s)").format(
                        sql.Identifier(table_name),
                        sql.Identifier(column_name),
                    ),
                    [datafile_ids],
                )

            cursor.execute(
                sql.SQL("DELETE FROM {} WHERE id = ANY(%s)").format(
                    sql.Identifier(DataFile._meta.db_table),
                ),
                [datafile_ids],
            )


def _delete_models(model, object_ids: Iterable[object]) -> None:
    """Delete tracked fixture records after parser artifacts are removed."""
    object_ids = sorted(set(object_ids), reverse=True)
    if object_ids:
        model.objects.filter(pk__in=object_ids).delete()


@pytest.fixture(autouse=True)
def go_parser_datafile_cleanup(request):
    """Track Go parser fixture records and clean them up after each integration test."""
    datafile_ids = set()
    user_ids = set()
    stt_ids = set()
    region_ids = set()

    def register_created_datafile(
        sender, instance: DataFile, created: bool, **kwargs
    ) -> None:
        """Register DataFiles created by Django fixtures before parser submission."""
        if created and instance.pk:
            datafile_ids.add(instance.pk)

    def register_created_user(sender, instance: User, created: bool, **kwargs) -> None:
        """Register Users created by Django fixtures."""
        if created and instance.pk:
            user_ids.add(instance.pk)

    def register_created_stt(sender, instance: STT, created: bool, **kwargs) -> None:
        """Register STTs created by Django fixtures."""
        if created and instance.pk:
            stt_ids.add(instance.pk)

    def register_created_region(
        sender, instance: Region, created: bool, **kwargs
    ) -> None:
        """Register Regions created by Django fixtures."""
        if created and instance.pk:
            region_ids.add(instance.pk)

    post_save.connect(register_created_datafile, sender=DataFile, weak=False)
    post_save.connect(register_created_user, sender=User, weak=False)
    post_save.connect(register_created_stt, sender=STT, weak=False)
    post_save.connect(register_created_region, sender=Region, weak=False)
    request.module._GO_PARSER_DATAFILE_IDS = datafile_ids

    try:
        yield datafile_ids
    finally:
        request.module._GO_PARSER_DATAFILE_IDS = None
        post_save.disconnect(register_created_datafile, sender=DataFile)
        post_save.disconnect(register_created_user, sender=User)
        post_save.disconnect(register_created_stt, sender=STT)
        post_save.disconnect(register_created_region, sender=Region)
        _delete_datafiles_outside_transaction(datafile_ids)
        _delete_models(User, user_ids)
        _delete_models(STT, stt_ids)
        _delete_models(Region, region_ids)
