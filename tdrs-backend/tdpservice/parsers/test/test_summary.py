"""Test the new model for DataFileSummary."""

import pytest
from tdpservice.parsers import parse
from tdpservice.parsers.models import DataFileSummary, ParserErrorCategoryChoices
from .factories import DataFileSummaryFactory, ParserErrorFactory
from ..util import create_test_datafile

import logging
logger = logging.getLogger(__name__)

@pytest.fixture
def test_datafile(stt_user, stt):
    """Fixture for small_correct_file."""
    return create_test_datafile('small_correct_file', stt_user, stt)

@pytest.fixture
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory()

@pytest.mark.django_db
def test_dfs_model(dfs):
    """Test that the model is created and populated correctly."""
    assert dfs.case_aggregates['Jan']['accepted'] == 100

@pytest.mark.django_db
def test_dfs_rejected(test_datafile, dfs):
    """Ensure that an invalid file generates a rejected status."""
    test_datafile.section = 'Closed Case Data'
    test_datafile.save()

    error_ast = parse.parse_datafile(test_datafile)
    dfs.status = dfs.get_status(error_ast)
    assert DataFileSummary.Status.REJECTED == dfs.status

@pytest.mark.django_db
def test_dfs_set_status(dfs):
    """Test that the status is set correctly."""
    assert dfs.status == DataFileSummary.Status.PENDING
    dfs.status = dfs.get_status(errors={})
    assert dfs.status == DataFileSummary.Status.ACCEPTED
    # create category 1 ParserError list to prompt rejected status
    parser_errors = []

    for i in range(2, 4):
        parser_errors.append(ParserErrorFactory(row_number=i, error_type=str(i)))

    dfs.status = dfs.get_status(errors={'document': parser_errors})

    assert dfs.status == DataFileSummary.Status.ACCEPTED_WITH_ERRORS

    parser_errors.append(ParserErrorFactory(row_number=5, error_type=ParserErrorCategoryChoices.PRE_CHECK))
    dfs.status = dfs.get_status(errors={'document': parser_errors})

    assert dfs.status == DataFileSummary.Status.REJECTED

@pytest.mark.django_db
def test_dfs_set_case_aggregates(test_datafile, dfs):
    """Test that the case aggregates are set correctly."""
    test_datafile.section = 'Active Case Data'
    test_datafile.save()
    error_ast = parse.parse_datafile(test_datafile)
    dfs.case_aggregates = dfs.get_case_aggregates(error_ast)
    assert dfs.case_aggregates['Jan']['accepted'] == 1
    assert dfs.case_aggregates['Jan']['rejected'] == 0
    assert dfs.case_aggregates['Jan']['total'] == 1
