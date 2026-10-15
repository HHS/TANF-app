"""Join parser routing and lifecycle ownership migrations."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("data_files", "0033_datafile_parser_mode"),
        ("data_files", "0033_merge_lifecycle_and_transition_log"),
    ]

    operations = []
