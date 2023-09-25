"""Module testing for data file model."""
import pytest

from tdpservice.parsers.models import ParserError
from .factories import ParserErrorFactory

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
