import csv
from pathlib import Path

from django.db import migrations, models


def populate_timezones(apps, schema_editor):
    """Populate timezone field for all STTs by reading from the seed CSVs."""
    STT = apps.get_model('stts', 'STT')
    data_dir = Path(__file__).resolve().parent.parent / 'management/commands/data'

    tribe_file = 'tribes.csv'
    for filename in ('states.csv', 'territories.csv', tribe_file):
        chars = 3 if filename == tribe_file else 2
        with open(data_dir / filename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if 'Timezone' in row and row['Timezone']:
                    stt_code = str(row['STT_CODE']).zfill(chars)
                    STT.objects.filter(stt_code=stt_code).update(
                        timezone=row['Timezone']
                    )


def reverse_timezones(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0011_add_region_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='stt',
            name='timezone',
            field=models.CharField(blank=True, default='America/New_York', max_length=63),
        ),
        migrations.RunPython(populate_timezones, reverse_timezones),
    ]
