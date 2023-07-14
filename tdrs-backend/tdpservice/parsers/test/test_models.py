"""Module testing for data file model."""
import pytest

from tdpservice.parsers.models import ParserError, DataFileSummary, ParserErrorCategoryChoices
from .factories import DataFileSummaryFactory, ParserErrorFactory

@pytest.fixture
def parser_error_instance():
    """Create a parser error instance."""
    return ParserErrorFactory.create()


@pytest.mark.django_db
def test_parser_error_instance(parser_error_instance):
    """Test that the parser error instance is created."""
    assert isinstance(parser_error_instance, ParserError)


@pytest.mark.django_db
def test_parser_error_rpt_month_name(parser_error_instance):
    """Test that the parser error instance is created."""
    parser_error_instance.rpt_month_year = 202001
    assert parser_error_instance.rpt_month_name == "January"


@pytest.fixture()
def dfs():
    """Fixture for DataFileSummary."""
    return DataFileSummaryFactory.create()


@pytest.mark.django_db
def test_dfs_model(dfs):
    """Test that the model is created and populated correctly."""
    assert dfs.case_aggregates['Jan']['accepted'] == 100


@pytest.mark.django_db
def test_dfs_get_status(dfs):
    """Test that the initial status is set correctly."""
    assert dfs.status == DataFileSummary.Status.PENDING
    
    # create empty Error dict to prompt accepted status
    assert dfs.get_status(errors={}) == DataFileSummary.Status.ACCEPTED

    # create category 2 ParserError list to prompt accepted with errors status
    parser_errors = []
    for i in range(2, 4):
        parser_errors.append(ParserErrorFactory(row_number=i, error_type=str(i)))

    assert dfs.get_status(errors={'document': parser_errors}) == DataFileSummary.Status.ACCEPTED_WITH_ERRORS

    # create category 1 ParserError list to prompt rejected status
    parser_errors.append(ParserErrorFactory(row_number=5, error_type=ParserErrorCategoryChoices.PRE_CHECK))
    assert dfs.get_status(errors={'document': parser_errors}) == DataFileSummary.Status.REJECTED
