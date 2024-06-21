"""
Delete and reparse a set of datafiles
"""

import time
from django.core.management.base import BaseCommand, CommandError
from django_elasticsearch_dsl.management.commands import search_index
from django_elasticsearch_dsl.registries import registry
from django.core.management import call_command
from django.conf import settings
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import ParserError, DataFileSummary
from tdpservice.search_indexes.models import tanf, ssp, tribal


class Command(BaseCommand):
    """Command class."""

    help = "Delete and reparse a set of datafiles"

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        # parser.add_argument(
        #     '--models',
        #     metavar='app[.model]',
        #     type=str,
        #     nargs='*',
        #     help="Specify the model or app to be populated."
        # )
        # parser.add_argument(
        #     '--clear',
        #     action='store_true',
        #     dest='clear',
        #     help="Clear previous postgres records."
        # )
        # parser.add_argument("--num", type=int)
        parser.add_argument("--fiscal_quarter", type=str)
        parser.add_argument("--fiscal_year", type=str)

    def handle(self, *args, **options):
        """Delete datafiles matching a query."""
        fiscal_year = options.get('fiscal_year', None)
        fiscal_quarter = options.get('fiscal_quarter', None)

        # might be a little dangerous... confirm they want to delete everything if year/quarter not specified
        files = DataFile.objects.all()
        if fiscal_year and fiscal_quarter:
            files = DataFile.objects.all().filter(
                year=fiscal_year,
                quarter=fiscal_quarter
            )

        for datafile in files:

            ## export all existing data matching files (old version) (?)
            # - flat file stored to s3 w/ ability to reload (!)

            ## delete all parsed records matching files
            model_types = [
                tanf.TANF_T1, tanf.TANF_T2, tanf.TANF_T3, tanf.TANF_T4, tanf.TANF_T5, tanf.TANF_T6, tanf.TANF_T7,
                ssp.SSP_M1, ssp.SSP_M2, ssp.SSP_M3, ssp.SSP_M4, ssp.SSP_M5, ssp.SSP_M6, ssp.SSP_M7,
                tribal.Tribal_TANF_T1, tribal.Tribal_TANF_T2, tribal.Tribal_TANF_T3, tribal.Tribal_TANF_T4, tribal.Tribal_TANF_T5, tribal.Tribal_TANF_T6, tribal.Tribal_TANF_T7
            ]
            for model in model_types:
                objects = model.objects.filter(datafile=datafile)
                # pickle/export
                num_deleted, models = objects.delete()
                if num_deleted > 0:
                    print(f'deleted {num_deleted}, {model} objects')

            ## delete all parser errors matching files
            errors = ParserError.objects.filter(file=datafile)
            # pickle/export
            num_deleted, models = errors.delete()
            if num_deleted > 0:
                print(f'deleted {num_deleted}, ParserError objects')

            ## delete all data file summaries
            summaries = DataFileSummary.objects.filter(datafile=datafile)
            # pickle/export
            num_deleted, models = summaries.delete()
            if num_deleted > 0:
                print(f'deleted {num_deleted}, DataFileSummary objects')

            ## delete data file (?) how are we going to re-parse them?
            # datafile.delete()

            ## delete all elastic documents ~~matching files~~ (all of them in general)
            call_command('tdp_search_index','--delete', '-f')

            ## reindex elastic indexes
            call_command('tdp_search_index', '--create', '-f')


        ## re-parse data files
