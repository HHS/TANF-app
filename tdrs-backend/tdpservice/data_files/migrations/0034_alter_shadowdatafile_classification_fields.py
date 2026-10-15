from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("data_files", "0033_merge_lifecycle_and_transition_log"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shadowdatafile",
            name="program_type",
            field=models.CharField(max_length=32),
        ),
        migrations.AlterField(
            model_name="shadowdatafile",
            name="section",
            field=models.CharField(max_length=32),
        ),
    ]
