"""Management command for seeding parsed records into the postgres db."""


from django.core.management.base import BaseCommand, CommandError
from tdpservice.search_indexes.models import tanf  # , ssp, tribal
from tdpservice.parsers.test import factories
import time
import uuid


AVAILABLE_MODELS = [
    # {'model': ssp.SSP_M1, 'factory': factories.SSPM1Factory},
    # {'model': ssp.SSP_M2, 'factory': factories.SSPM2Factory},
    # {'model': ssp.SSP_M3, 'factory': factories.SSPM3Factory},
    # {'model': ssp.SSP_M4, 'factory': factories.SSPM4Factory},
    # {'model': ssp.SSP_M5, 'factory': factories.SSPM5Factory},
    # {'model': ssp.SSP_M6, 'factory': factories.SSPM6Factory},
    # {'model': ssp.SSP_M7, 'factory': factories.SSPM7Factory},

    {'model': tanf.TANF_T1, 'factory': factories.TanfT1Factory},
    {'model': tanf.TANF_T2, 'factory': factories.TanfT2Factory},
    {'model': tanf.TANF_T3, 'factory': factories.TanfT3Factory},
    {'model': tanf.TANF_T4, 'factory': factories.TanfT4Factory},
    {'model': tanf.TANF_T5, 'factory': factories.TanfT5Factory},
    {'model': tanf.TANF_T6, 'factory': factories.TanfT6Factory},
    {'model': tanf.TANF_T7, 'factory': factories.TanfT7Factory},

    # {'model': tribal.Tribal_TANF_T1, 'factory': factories.TribalTanfT1Factory},
    # {'model': tribal.Tribal_TANF_T2, 'factory': factories.TribalTanfT2Factory},
    # {'model': tribal.Tribal_TANF_T3, 'factory': factories.TribalTanfT3Factory},
    # {'model': tribal.Tribal_TANF_T4, 'factory': factories.TribalTanfT4Factory},
    # {'model': tribal.Tribal_TANF_T5, 'factory': factories.TribalTanfT5Factory},
    # {'model': tribal.Tribal_TANF_T6, 'factory': factories.TribalTanfT6Factory},
    # {'model': tribal.Tribal_TANF_T7, 'factory': factories.TribalTanfT7Factory},
]


class Command(BaseCommand):
    """Seeds records into the postgres db."""

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument(
            '--models',
            metavar='app[.model]',
            type=str,
            nargs='*',
            help="Specify the model or app to be populated."
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            dest='clear',
            help="Clear previous postgres records."
        )
        parser.add_argument("--num", type=int)

    def _get_models(self, args):
        """Get Models from registry that match the --models args."""
        if args:
            models = []
            for arg in args:
                arg = arg.lower()
                match_found = False

                for model in AVAILABLE_MODELS:
                    if model._meta.app_label == arg:
                        models.append(model)
                        match_found = True
                    elif '{}.{}'.format(
                        model._meta.app_label.lower(),
                        model._meta.model_name.lower()
                    ) == arg:
                        models.append(model)
                        match_found = True

                if not match_found:
                    raise CommandError("No model or app named {}".format(arg))
        else:
            models = AVAILABLE_MODELS
        return models

    def _clear(self, models):
        for m in models:
            Model = m['model']
            print(f'deleting {Model._meta.model_name}')
            Model.objects.all().delete()

    def _populate(self, models, num):
        for m in models:
            Model = m['model']
            Factory = m['factory']

            print(f'creating {num} {Model._meta.model_name} objects')

            objects = []
            for i in range(0, num):
                obj = Factory.build()
                obj.pk = uuid.uuid4()
                objects.append(obj)

            Model.objects.bulk_create(objects)

    def handle(self, *args, **options):
        """Handle the `seed_records` command."""
        clear = options['clear']
        models = self._get_models(options['models'])
        num = options['num']

        if not num:
            num = 1000

        if clear:
            self._clear(models)
            time.sleep(5)

        if num > 10000:
            batches = int(num / 10000)
            remainder = num - (batches * 10000)

            for b in range(0, batches):
                print(f'batch {b+1} of {batches}')
                self._populate(models, 10000)

            if remainder > 0:
                print(f'remaining {remainder}')
                self._populate(models, remainder)
        else:
            self._populate(models, num)
