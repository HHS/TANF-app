"""Test the new model for DataFileSummary."""

import pytest
from tdpservice.search_indexes.parsers import tanf_parser, preparser, util
from tdpservice.search_indexes.models import T1
from tdpservice.search_indexes.parsers.models import DataFileSummary
from .factories import DataFileSummaryFactory
from .test_data_parsing import bad_file_missing_header
import logging
logger = logging.getLogger(__name__)

@pytest.mark.django_db
def test_data_file_summary_model():
    """Test that the model is created and populated correctly."""
    dfs = DataFileSummaryFactory()

    assert dfs.case_aggregates['Jan']['accepted'] == 100

def test_dfs_rejected(bad_file_missing_header):
    """Ensure that an invalid file generates a rejected status."""
    dfs = preparser.preparse(bad_file_missing_header, 'TANF', 'Active Case Data')
    assert dfs == DataFileSummary.Status.REJECTED