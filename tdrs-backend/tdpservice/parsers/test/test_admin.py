"""Tests for parsers admin query behavior."""

from django.contrib.admin.sites import AdminSite
from django.db import connection
from django.test import RequestFactory
from django.test.utils import CaptureQueriesContext

import pytest

from tdpservice.parsers.admin import ParserErrorAdmin
from tdpservice.parsers.models import ParserError
from tdpservice.parsers.test.factories import ParserErrorFactory


@pytest.mark.django_db
def test_parser_error_admin_changelist_relations_are_eager_loaded():
    """The ParserError admin should not query per row for linked file context."""
    ParserErrorFactory.create_batch(3)
    request = RequestFactory().get("/admin/parsers/parsererror/")
    model_admin = ParserErrorAdmin(ParserError, AdminSite())

    parser_errors = list(model_admin.get_queryset(request))

    with CaptureQueriesContext(connection) as captured_queries:
        for parser_error in parser_errors:
            str(parser_error.file)
            str(parser_error.file.stt)

    assert len(captured_queries) == 0


def test_parser_error_admin_uses_heavy_table_pagination():
    """The ParserError admin should render fewer records per page."""
    model_admin = ParserErrorAdmin(ParserError, AdminSite())

    assert model_admin.list_per_page == 25
    assert model_admin.show_full_result_count is False
