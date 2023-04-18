"""Test the new model for DataFileSummary."""

import pytest
from tdpservice.parsers import parse
from tdpservice.parsers.models import DataFileSummary
from .factories import DataFileSummaryFactory
from .test_parse import bad_file_missing_header

import logging
logger = logging.getLogger(__name__)

@pytest.mark.django_db
def test_dfs_model():
    """Test that the model is created and populated correctly."""
    dfs = DataFileSummaryFactory()

    assert dfs.case_aggregates['Jan']['accepted'] == 100

@pytest.mark.django_db
def test_dfs_rejected(bad_file_missing_header):
    """Ensure that an invalid file generates a rejected status."""
    dfs = DataFileSummaryFactory()
    dfs.set_status(parse.parse_datafile(bad_file_missing_header))
    assert dfs.status == DataFileSummary.Status.REJECTED

@pytest.mark.django_db
def test_dfs_set_status():
    """Test that the status is set correctly."""
    dfs = DataFileSummaryFactory()
    assert dfs.status == DataFileSummary.Status.PENDING
    dfs.set_status(errors={})
    assert dfs.status == DataFileSummary.Status.ACCEPTED
    dfs.set_status(errors=[1, 2, 3])
    assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS
    dfs.set_status(errors={'document': ['No headers found.']})
    assert dfs.status == DataFileSummary.Status.REJECTED
