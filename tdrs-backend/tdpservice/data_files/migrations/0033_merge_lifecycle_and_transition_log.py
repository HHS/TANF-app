"""Join lifecycle ownership and transition history migrations."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0032_submission_state_controller"),
        ("data_files", "0032_datafilestatetransition"),
    ]

    operations = []
