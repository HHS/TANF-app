"""Test the new model for DataFileSummary."""

import pytest
from tdpservice.parsers import parse
from tdpservice.parsers.models import DataFileSummary
from .factories import DataFileSummaryFactory, ParserErrorFactory
from .test_parse import bad_file_missing_header, test_datafile 

import logging
logger = logging.getLogger(__name__)

@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.create()

@pytest.mark.django_db
def test_dfs_model(dfs):
    """Test that the model is created and populated correctly."""
    dfs = dfs

    assert dfs.case_aggregates['Jan']['accepted'] == 100

@pytest.mark.django_db
def test_dfs_rejected(test_datafile, dfs):
    """Ensure that an invalid file generates a rejected status."""
    dfs = dfs
    test_datafile.section = 'Closed Case Data'
    test_datafile.save()
    dfs.set_status(parse.parse_datafile(test_datafile))
    assert dfs.status == DataFileSummary.Status.REJECTED

@pytest.mark.django_db
def test_dfs_set_status(dfs):
    """Test that the status is set correctly."""
    dfs = dfs
    assert dfs.status == DataFileSummary.Status.PENDING
    dfs.set_status(errors={})
    assert dfs.status == DataFileSummary.Status.ACCEPTED

    # create category 1 ParserError list to prompt rejected status
    parser_errors = []

    # this feels precarious for tests. the defaults in the factory could cause issues should logic change
    # resulting in failures if we stop keying off category and instead go to content or msg
    for i in range(1, 4):  
        parser_errors.append(ParserErrorFactory(row_number=(i), category=i))

    dfs.set_status(errors={'document': parser_errors})

    assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS

    parser_errors.append(ParserErrorFactory(row_number=5, category=5, error_type='pre-parsing'))
    dfs.set_status(errors={'document': parser_errors})

    assert dfs.status == DataFileSummary.Status.REJECTED