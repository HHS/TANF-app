"""Join canonical classification and parser routing migrations."""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("data_files", "0034_merge_parser_mode_and_lifecycle"),
        ("data_files", "0036_add_program_section_choices"),
    ]

    operations = []
