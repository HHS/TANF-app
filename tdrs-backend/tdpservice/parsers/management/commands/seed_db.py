"""`seed_db` command."""

from django.core.management import BaseCommand
from django.core.files.base import ContentFile
from django.db.utils import IntegrityError
from tdpservice.parsers.schema_defs.header import header
from tdpservice.parsers.schema_defs.trailer import trailer
from tdpservice.parsers.schema_defs.utils import ProgramManager
from tdpservice.parsers.util import fiscal_to_calendar
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.scheduling.parser_task import parse as parse_task
from tdpservice.stts.models import STT
from tdpservice.users.models import User
from tdpservice.parsers.row_schema import RowSchema
from faker import Faker
import logging
import random

fake = Faker()
logger = logging.getLogger(__name__)

# https://faker.readthedocs.io/en/stable/providers/baseprovider.html#faker.providers.BaseProvider
# """ class FieldFaker(faker.providers.BaseProvider):..."""

def build_datafile(stt, year, quarter, original_filename, file_name, section, file_data):
    """Build a datafile."""
    try:
        d = DataFile.objects.create(
            user=User.objects.get_or_create(username='system')[0],
            stt=stt,
            year=year,
            quarter=quarter,
            original_filename=original_filename,
            section=section,
            version=random.randint(1, 1993415),
        )

        d.file.save(file_name, ContentFile(file_data))
    except IntegrityError as e:
        logger.error(f"Error creating datafile: {e}")
        pass
    return d


def validValues(schemaMgr, field, year, qtr):
    """Take in a field and returns a line of valid values."""
    field_len = field.endIndex - field.startIndex

    if field.name == 'RecordType':
        return schemaMgr.record_type
    if field.name == 'SSN':
        # only used by recordtypes 2,3,5
        # TODO: reverse the TransformField logic to 'encrypt' a random number
        field_format = '?' * field_len
    elif field.name in ('RPT_MONTH_YEAR'):  # previously had CALENDAR_QUARTER
        # given a quarter, set upper lower bounds for month
        qtr = qtr[1:]
        upper = int(qtr) * 3
        lower = upper - 2

        month = '{}'.format(random.randint(lower, upper)).zfill(2)
        field_format = '{}{}'.format(year, str(month))
    else:
        if field.friendly_name == 'Family Affiliation':
            print('Family Affiliation')
        field_format = '#' * field_len
    return fake.bothify(text=field_format)


def make_line(schemaMgr, section, year, qtr):
    """Take in a schema manager and returns a line of data."""
    line = ''

    # for row_schema in schemaMgr.schemas:  # this is to handle multi-schema like T6
    # if len(schemaMgr.schemas) > 1:
    row_schema = schemaMgr.schemas[0]

    for field in row_schema.fields:
        line += validValues(row_schema, field, year, qtr)
        print(f"Field: {field.name}, field length {field.position} Value: {line}")
    return line + '\n'

def make_HT(schemaMgr, prog_type, section, year, quarter, stt):
    """Handle special case of header/trailer lines."""
    line = ''

    if type(schemaMgr) is RowSchema:
        if schemaMgr.record_type == 'HEADER':
            # e.g. HEADER20201CAL000TAN1ED

            if stt.state is not None:  # this is a tribe
                my_stt = stt.state
            else:
                my_stt = stt
            state_fips = '{}'.format(my_stt.stt_code).zfill(2)
            # state_fips = stt.state.stt_code if stt.state is not None else stt.stt_code
            tribe_code = '{}'.format(stt.stt_code) if stt.type == 'tribe' else '000'

            line = f"HEADER{year}{quarter[1:]}{section}{state_fips}{tribe_code}{prog_type}1ED"

        elif schemaMgr.record_type == 'TRAILER':
            line += 'TRAILER' + '1' * 16
    else:
        print('Invalid record type')
        return None

    return line + '\n'

def make_files(stt, sub_year, sub_quarter):
    """Given a STT, parameterize calls to build_datafile and make_line."""
    sections = stt.filenames.keys()
    files_for_quarter = {}

    for long_section in sections:
        # TODO: fix this if it becomes relevant.
        prog_type = None   # TAN
        section = None  # A
        models_in_section = ProgramManager.get_schemas(prog_type, section)

        temp_file = ''

        cal_year, cal_quarter = fiscal_to_calendar(sub_year, 'Q{}'.format(sub_quarter))
        temp_file += make_HT(header, prog_type, section, cal_year, cal_quarter, stt)

        # iterate over models and generate lines
        for _, model in models_in_section.items():
            # below is equivalent to 'contains' for the tuple
            if any(section in long_section for section in ('Active Case', 'Closed Case', 'Aggregate', 'Stratum')):
                for i in range(random.randint(1, 3)):
                    temp_file += make_line(model, section, cal_year, cal_quarter)
            # elif section in ['Aggregate Data', 'Stratum Data']:
            #    # we should generate a smaller count of lines...maybe leave this as a TODO
            #    # shouldn't this be based on the active/closed case data?
            #    pass

        # make trailer line
        temp_file += make_HT(trailer, prog_type, section, cal_year, cal_quarter, stt)
        # print(temp_file)

        datafile = build_datafile(
            stt=stt,
            year=sub_year,  # fiscal submission year
            quarter=f"Q{sub_quarter}",  # fiscal submission quarter
            original_filename=f'{stt}-{section}-{sub_year}Q{sub_quarter}.txt',
            file_name=f'{stt}-{section}-{sub_year}Q{sub_quarter}',
            section=long_section,
            file_data=bytes(temp_file.rstrip(), 'utf-8'),
        )
        datafile.save()
        files_for_quarter[section] = datafile

    return files_for_quarter

def make_seed():
    """Invoke scheduling/management/commands/backup_db management command."""
    from tdpservice.scheduling.management.commands.backup_db import Command as BackupCommand
    backup = BackupCommand()
    backup.handle(file='/tdpapp/tdrs_db_seed.pg')

class Command(BaseCommand):
    """Command class."""

    help = "Populate datafiles, records, summaries, and errors for all STTs."

    def handle(self, *args, **options):
        """Populate datafiles, records, summaries, and errors for all STTs."""
        for stt in STT.objects.filter(id__in=range(1, 2)):  # .all():
            for yr in range(2020, 2021):
                for qtr in [1, 2]:  # , 3, 4]:
                    files_for_qtr = make_files(stt, yr, qtr)
                    print(files_for_qtr)
                    for f in files_for_qtr.keys():
                        df = files_for_qtr[f]
                        dfs = DataFileSummaryFactory.build()
                        dfs.datafile = df
                        parse_task(df.id, False)

        # dump db in full using `make_seed` func
        make_seed()
