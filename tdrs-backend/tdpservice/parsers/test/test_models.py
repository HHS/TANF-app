"""Module testing for data file model."""
import pytest

from tdpservice.parsers.models import ParserError

from .factories import ParserErrorFactory


class TestParserErrorModel:
    """Tests for parser error model."""

    @pytest.fixture
    def parser_error_instance(self):
        """Create a parser error instance."""
        return ParserErrorFactory.create()

    @pytest.mark.django_db
    def test_parser_error_instance(self, parser_error_instance):
        """Test that the parser error instance is created."""
        assert isinstance(parser_error_instance, ParserError)

    @pytest.mark.django_db
    def test_parser_error_rpt_month_name(self, parser_error_instance):
        """Test that the parser error instance is created."""
        parser_error_instance.rpt_month_year = 202001
        assert parser_error_instance.rpt_month_name == "January"
