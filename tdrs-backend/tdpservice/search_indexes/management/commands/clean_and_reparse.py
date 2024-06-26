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
# from tdpservice.search_indexes.models import tanf, ssp, tribal
from tdpservice.scheduling import parser_task
from django.forms.models import model_to_dict
from tdpservice.search_indexes.documents import tanf, ssp, tribal
from tdpservice.scheduling.db_backup import run_backup
from elasticsearch.helpers.errors import BulkIndexError
from django.db import models
from django.apps import apps


class Command(BaseCommand):
    """Command class."""

    help = "Delete and reparse a set of datafiles"

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument("--fiscal_quarter", type=str)
        parser.add_argument("--fiscal_year", type=str)

    def handle(self, *args, **options):
        """Delete datafiles matching a query."""
        # full db backup -> backup_database()
        # parameterize location backup
        # refine on subsequent pass
        run_backup('-b')  # or reimplement `main` to parameterize file name/loc

        fiscal_year = options.get('fiscal_year', None)
        fiscal_quarter = options.get('fiscal_quarter', None)

        # might be a little dangerous... confirm they want to delete everything if year/quarter not specified
        files = DataFile.objects.all()
        files = files.filter(year=fiscal_year) if fiscal_year else files
        files = files.filter(quarter=fiscal_quarter) if fiscal_quarter else files

        print(f'this will delete {files.count()} datafiles - continue?')
        # catch confirmation input?

        call_command('tdp_search_index', '--create', '-f')

        # file_ids = files.values_list('id', flat=True).distinct()

        # disconnect post_delete signals
        # models.signals.post_delete.disconnect()

        # sign_proc = apps.get_app_config('django_elasticsearch_dsl').signal_processor
        # sign_proc.teardown()

        # reconnect post_delete signals

        for f in files:
            f.delete()  # -> delete all data associated
            # raw_delete -> doesn't execute signals or cascade

        # sign_proc.setup()

        for f in files:
            f.save()
            parser_task.parse.delay(f.pk)

        # # parallelize - parent task (above)
        # # add model deletion, reparse to celery queue (for each datafile)

        # ## delete all parsed records matching files
        # model_types = [
        #     tanf.TANF_T1, tanf.TANF_T2, tanf.TANF_T3, tanf.TANF_T4, tanf.TANF_T5, tanf.TANF_T6, tanf.TANF_T7,
        #     ssp.SSP_M1, ssp.SSP_M2, ssp.SSP_M3, ssp.SSP_M4, ssp.SSP_M5, ssp.SSP_M6, ssp.SSP_M7,
        #     tribal.Tribal_TANF_T1, tribal.Tribal_TANF_T2, tribal.Tribal_TANF_T3, tribal.Tribal_TANF_T4, tribal.Tribal_TANF_T5, tribal.Tribal_TANF_T6, tribal.Tribal_TANF_T7
        # ]

        # # base model + cascade would allow to query only one model
        # # query by record's datafile's date
        # for model in model_types:
        #     objects = model.objects.filter(datafile_id__in=file_ids)
        #     num_deleted, models = objects.delete()
        #     if num_deleted > 0:
        #         print(f'deleted {num_deleted}, {model} objects')

        # ## delete all parser errors matching files
        # errors = ParserError.objects.filter(file_id__in=file_ids)
        # # pickle/export
        # # upload_file()
        # # delete
        # num_deleted, models = errors.delete()
        # if num_deleted > 0:
        #     print(f'deleted {num_deleted}, ParserError objects')

        # ## delete all data file summaries
        # summaries = DataFileSummary.objects.filter(datafile_id__in=file_ids)
        # # pickle/export
        # # upload_file()
        # # delete
        # num_deleted, models = summaries.delete()
        # if num_deleted > 0:
        #     print(f'deleted {num_deleted}, DataFileSummary objects')

        # ## delete data file (?) how are we going to re-parse them?
        # # datafile.delete()

        # ## delete all elastic documents ~~matching files~~ (all of them in general)
        # # call_command('tdp_search_index','--delete', '-f')
        # # don't delete old index

        # ## reindex elastic indexes
        
        # underlying library to create with new name/alias (keeps the old index around)

        ## re-parse data file (turn off emails/side-effects)
        # reparse old data (not in specified dataset) later -> update other ticket

        # load pickled data?
        # backup elastic?
        # - cf service level
        # first task before start
        # - turn off elastic - perform backup
        # - delete all DF records from postgres
        # - spin up new elastic
