"""Utility file for functions shared between all parsers even preparser."""

import logging
from datetime import datetime
from pathlib import Path

from django.contrib.admin.models import ADDITION

from tdpservice.core.utils import log
from tdpservice.data_files.models import DataFile

logger = logging.getLogger(__name__)


def create_test_datafile(
    filename,
    stt_user,
    stt,
    section=DataFile.Section.ACTIVE_CASE_DATA,
    program_type=DataFile.ProgramType.TANF,
):
    """Create a test DataFile instance with the given file attached."""
    path = str(Path(__file__).parent.joinpath("test/data")) + f"/{filename}"
    datafile = DataFile.create_new_version(
        {
            "quarter": "Q1",
            "year": 2021,
            "section": section,
            "program_type": program_type,
            "user": stt_user,
            "stt": stt,
        }
    )

    with open(path, "rb") as file:
        datafile.file.save(filename, file)

    return datafile


def clean_options_string(options, remove=["'", '"', " "]):
    """Return a prettied-up version of an options array."""
    options_str = ", ".join(str(o) for o in options)
    return f"[{options_str}]"


def fiscal_to_calendar(year, fiscal_quarter):
    """Decrement the input quarter text by one."""
    array = [1, 2, 3, 4]  # wrapping around an array
    int_qtr = int(fiscal_quarter[1:])  # remove the 'Q', e.g., 'Q1' -> '1'
    if int_qtr == 1:
        year = year - 1

    ind_qtr = array.index(
        int_qtr
    )  # get the index so we can easily wrap-around end of array
    return year, "Q{}".format(array[ind_qtr - 1])  # return the previous quarter


def calendar_to_fiscal(calendar_year, fiscal_quarter):
    """Decrement the calendar year if in Q1."""
    return calendar_year - 1 if fiscal_quarter == "Q1" else calendar_year


def transform_to_months(quarter):
    """Return a list of months in a quarter depending the quarter's format."""
    match quarter:
        case "Q1":
            return ["Jan", "Feb", "Mar"]
        case "Q2":
            return ["Apr", "May", "Jun"]
        case "Q3":
            return ["Jul", "Aug", "Sep"]
        case "Q4":
            return ["Oct", "Nov", "Dec"]
        case _:
            raise ValueError("Invalid quarter value.")


def month_to_int(month):
    """Return the integer value of a month."""
    return datetime.strptime(month, "%b").strftime("%m")


def year_month_to_year_quarter(year_month):
    """Return the year and quarter from a year_month string."""

    def get_quarter_from_month(month):
        """Return the quarter from a month."""
        if month in ["01", "02", "03"]:
            return "Q1"
        elif month in ["04", "05", "06"]:
            return "Q2"
        elif month in ["07", "08", "09"]:
            return "Q3"
        elif month in ["10", "11", "12"]:
            return "Q4"
        else:
            return "Invalid month value."

    year = year_month[:4]
    month = year_month[4:]
    quarter = get_quarter_from_month(month)
    return year, quarter


def get_years_apart(rpt_month_year_date, date):
    """Return the number of years (double) between rpt_month_year_date and the target date - both `datetime`s."""
    delta = rpt_month_year_date - date
    age = delta.days / 365.25
    return age


class FrozenDict(dict):
    """Frozen dictionary for use as a hashable key."""

    def __hash__(self):
        """Return a hash of the dictionary."""
        return hash((frozenset(self), frozenset(self.values())))


class Records:
    """Maintains a dict of records where Key=Model and Value=[Record]."""

    def __init__(self):
        self.cases = dict()

    def add_record(self, case_id, record_model_pair, line_num):
        """Add a record_doc_pair to the dict."""
        record, model = record_model_pair
        if case_id is not None:
            self.cases.setdefault(model, []).append(record)
        else:
            logger.error(f"Error: Case id for record at line #{line_num} was None!")

    def get_bulk_create_struct(self):
        """Return dict of form {document: {record: None}} for bulk_create_records to consume."""
        return self.cases

    def clear(self, all_created):
        """Reset the dict if all records were created."""
        if all_created:
            # We don't want to re-assign self.cases here because we lose the keys of the record/doc types we've already
            # made. If we don't maintain that state we might not delete everything if we need to roll the records back
            # at the end of, or during parsing.
            for key in self.cases.keys():
                self.cases[key].clear()


def get_t1_t4_partial_dup_fields():
    """Return field names used to identify t1/t4 partial duplicates."""
    return ["RecordType", "RPT_MONTH_YEAR", "CASE_NUMBER"]


def get_t2_t3_t5_partial_dup_fields():
    """Return field names used to identify t2/t3/t5 partial duplicates."""
    return [
        "RecordType",
        "RPT_MONTH_YEAR",
        "CASE_NUMBER",
        "FAMILY_AFFILIATION",
        "DATE_OF_BIRTH",
        "SSN",
    ]


def get_record_value_by_field_name(record, field_name):
    """Return the value of a record for a given field name, accounting for the generic record type."""
    return (
        record.get(field_name, None)
        if type(record) is dict
        else getattr(record, field_name, None)
    )


def log_parser_exception(datafile, error_msg, level):
    """Log to DAC and console on parser exception."""
    context = {
        "user_id": datafile.user.pk,
        "action_flag": ADDITION,
        "object_repr": f"Datafile id: {datafile.pk}; year: {datafile.year}, quarter: {datafile.quarter}",
        "object_id": datafile,
    }
    log(error_msg, context, level)


class DecoderUnknownException(Exception):
    """Exception raised when decoder cannot be determined."""

    pass
