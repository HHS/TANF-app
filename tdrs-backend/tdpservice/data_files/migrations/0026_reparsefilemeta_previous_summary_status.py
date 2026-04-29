from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_files", "0025_datafile_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="reparsefilemeta",
            name="previous_summary_status",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
