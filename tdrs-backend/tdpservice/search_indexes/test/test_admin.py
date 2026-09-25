"""Search indexes admin tests."""

from django.contrib.admin.sites import AdminSite
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

import pytest
from rest_framework import status

from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.parsers.test.factories import TanfT1Factory
from tdpservice.search_indexes.admin.tanf import TANF_T1Admin
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.search_indexes.models.tanf import TANF_T1


@pytest.mark.django_db
def test_search_index_admin_changelist_relations_are_eager_loaded():
    """Search index admin should not query per row for displayed relations."""
    for _ in range(3):
        TanfT1Factory.create(datafile=DataFileFactory())
    request = RequestFactory().get("/admin/search_indexes/tanf_t1/")
    model_admin = TANF_T1Admin(TANF_T1, AdminSite())

    records = list(model_admin.get_queryset(request))

    with CaptureQueriesContext(connection) as captured_queries:
        for record in records:
            str(record.datafile)
            model_admin.stt_name(record)
            model_admin.stt_code(record)

    assert len(captured_queries) == 0


def test_search_index_admin_uses_heavy_table_pagination():
    """Search index admins should render fewer records per page."""
    model_admin = TANF_T1Admin(TANF_T1, AdminSite())

    assert model_admin.list_per_page == 25
    assert model_admin.show_full_result_count is False


@pytest.mark.django_db
def test_reparse_meta_change_view_displays_record_totals_once(client, admin_user):
    """Reparse record totals are not duplicated on the admin change page."""
    reparse_meta = ReparseMeta.objects.create(db_backup_location="/tmp/backup.pg")
    client.login(username=admin_user.username, password="test_password")

    response = client.get(
        reverse("admin:search_indexes_reparsemeta_change", args=(reparse_meta.id,))
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.rendered_content.count("Total num records initial:") == 1
    assert response.rendered_content.count("Total num records post:") == 1
