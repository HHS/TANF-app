"""Converts data files into a model that can be indexed by Elasticsearch."""

import os
import logging
import argparse
from cerberus import Validator
from .schema_defs.universal import get_header_schema, get_trailer_schema
from .util import get_record_type
from . import tanf_parser

from io import BufferedReader
# from .models import ParserLog
from tdpservice.data_files.models import DataFile

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


def validate_header(line, data_type, given_section):
    """Validate the header (first line) of the datafile."""
    logger.debug('Validating header line.')
    section_map = {
        'A': 'Active Case Data',
        'C': 'Closed Case Data',
        'G': 'Aggregate Data',
        'S': 'Stratum Data',
    }

    try:
        header = {
            'title':        line[0:6],
            'year':         line[6:10],
            'quarter':      line[10:11],
            'type':         line[11:12],
            'state_fips':   line[12:14],
            'tribe_code':   line[14:17],
            'program_type': line[17:20],
            'edit':         line[20:21],
            'encryption':   line[21:22],
            'update':       line[22:23],
        }

        for key, value in header.items():
            logger.debug('Header key %s: "%s"' % (key, value))

        # TODO: Will need to be saved in parserLog, #1354

        try:
            section_type = section_map[header['type']]
            logger.debug("Given section: '%s'\t Header section: '%s'", given_section, section_type)
            program_type = header['program_type']
            logger.debug("Given program type: '%s'\t Header program type: '%s'", data_type, header['program_type'])

            if given_section != section_map[header['type']]:
                raise ValueError('Given section does not match header section.')

            if (data_type == 'TANF' and program_type != 'TAN')\
                    or (data_type == 'SSP' and program_type != 'SSP')\
                    or (data_type not in ['TANF', 'SSP']):
                raise ValueError("Given data type does not match header program type.")
        except KeyError as e:
            logger.error('Ran into issue with header type: %s', e)

        validator = Validator(get_header_schema())
        is_valid = validator.validate(header)
        logger.debug(validator.errors)

        return is_valid, validator

    except KeyError as e:
        logger.error('Exception splicing header line or referencing it, please see line and error.')
        logger.error(line)
        logger.error(e)
        return False, e

def validate_trailer(line):
    """Validate the trailer (last) line in a datafile."""
    logger.info('Validating trailer line.')
    validator = Validator(get_trailer_schema())

    trailer = {
        'title':        line[0:7],
        'record_count': line[7:14],
        'blank':        line[14:23],
    }

    is_valid = validator.validate(trailer)

    logger.debug("Trailer title: '%s'", trailer['title'])
    logger.debug("Trailer record count: '%s'", trailer['record_count'])
    logger.debug("Trailer blank: '%s'", trailer['blank'])
    logger.debug("Trailer errors: '%s'", validator.errors)

    return is_valid, validator

def get_header_line(datafile):
    """Alters header line into string."""
    # intentionally only reading first line of file
    datafile.seek(0)
    header = datafile.readline()
    datafile.seek(0)  # reset file pointer to beginning of file

    # datafile when passed via redis/db is a FileField which returns bytes
    if isinstance(header, bytes):
        header = header.decode()

    header = header.strip()

    if get_record_type(header) != 'HE':
        return False, {'preparsing': 'First line in file is not recognized as a valid header.'}
    elif len(header) != 23:
        logger.debug("line: '%s' len: %d", header, len(header))
        return False, {'preparsing': 'Header length incorrect.'}

    return True, header

def get_trailer_line(datafile):
    """Alters the trailer line into usable string."""
    # certify/transform input line to be correct form/type

    # Don't want to read whole file, just last line, only possible with binary
    # Credit: https://openwritings.net/pg/python/python-read-last-line-file
    # https://stackoverflow.com/questions/46258499/
    try:
        datafile.seek(-2, os.SEEK_END)  # Jump to the second last byte.
        while datafile.read(1) != b'\n':  # Check if new line.
            datafile.seek(-2, os.SEEK_CUR)   # Jump two bytes back
    except OSError:  # Either file is empty or contains one line.
        datafile.seek(0)
        return False, {'preparsing': 'File too short or missing trailer.'}

    # Having set the file pointer to the last line, read it in.
    line = datafile.readline().decode()
    datafile.seek(0)  # Reset file pointer to beginning of file.

    logger.info("Trailer line: '%s'", line)
    if get_record_type(line) != 'TR':
        raise ValueError('Last line is not recognized as a trailer line.')
    elif len(line) < 13:
        # Previously, we checked to ensure exact length was 24. At the business level, we
        # don't care about the exact length, just that it's long enough to contain the
        # trailer information (>=14) and can ignore the trailing spaces.
        logger.debug("line: '%s' len: %d", line, len(line))
        return False, {'preparsing': 'Trailer length incorrect.'}
    line = line.strip('\n')

    return True, line

def check_plural_count(datafile):
    """Ensure only one header and one trailer exist in file."""
    header_count = 0
    trailer_count = 0
    line_no = 0

    for line in datafile:
        line_no += 1
        if get_record_type(line) == 'HE':
            header_count += 1
            if header_count > 1:
                return False, {'preparsing': 'Multiple header lines found on ' + str(line_no) + '.'}
        elif get_record_type(line) == 'TR':
            trailer_count += 1
            if trailer_count > 1:
                return False, {'preparsing': 'Multiple trailer lines found on ' + str(line_no) + '.'}
    return True, None

def preparse(data_file, data_type, section):
    """Validate metadata then dispatches file to appropriate parser."""
    if isinstance(data_file, DataFile):
        logger.debug("Beginning preparsing on '%s'", data_file.file.name)
        datafile = data_file.file
    elif isinstance(data_file, BufferedReader):
        datafile = data_file
    else:
        logger.error("Unexpected datafile type %s", type(data_file))
        raise TypeError("Unexpected datafile type.")

    unique_header_footer, line = check_plural_count(datafile)
    if unique_header_footer is False:
        raise ValueError("Preparsing error: %s" % line['preparsing'])

    header_preparsed, line = get_header_line(datafile)
    if header_preparsed is False:
        raise ValueError("Header invalid, error: %s" % line['preparsing'])
    # logger.debug("Header: %s", line)

    header_is_valid, header_validator = validate_header(line, data_type, section)
    if isinstance(header_validator, Exception):
        raise header_validator

    trailer_preparsed, line = get_trailer_line(datafile)
    if trailer_preparsed is False:
        raise ValueError("Trailer invalid, error: %s" % line['preparsing'])
    trailer_is_valid, trailer_validator = validate_trailer(line)
    if isinstance(trailer_validator, Exception):
        raise trailer_validator

    errors = {'header': header_validator.errors, 'trailer': trailer_validator.errors}

    if header_is_valid and trailer_is_valid:
        logger.info("Preparsing succeeded.")
    else:
        # TODO: should we end here or let parser run to collect more errors?
        logger.error("Preparse failed: %s", errors)
        return False, errors
        # return ParserLog.objects.create(
        #    data_file=args.file,
        #    errors=errors,
        #    status=ParserLog.Status.REJECTED,
        # )

    logger.debug("Data type: '%s'", data_type)
    if data_type == 'TANF':
        logger.info("Dispatching to TANF parser.")
        tanf_parser.parse(datafile)
    # elif data_type == 'SSP':
    #    ssp_parser.parse(datafile)
    # elif data_type == 'Tribal TANF':
    #    tribal_tanf_parser.parse(datafile)
    else:
        raise ValueError('Preparser given invalid data_type parameter.')

    return True


if __name__ == '__main__':
    """Take in command-line arguments and run the parser."""
    parser = argparse.ArgumentParser(description='Parse TANF active cases data.')
    parser.add_argument('--file', type=argparse.FileType('r'), help='The file to parse.')
    parser.add_argument('--data_type', type=str, default='TANF', help='The type of data to parse.')
    parser.add_argument('--section', type=str, default='Active Case Data', help='The section submitted.')

    args = parser.parse_args()
    logger.debug("Arguments: %s", args)
    preparse(args.file, data_type="TANF", section="Active Case Data")
