# when the data_file db tables were renamed from reports_reportfile
# the indexes were not renamed to match the new table name
# now they are causing collisions when creating the new reports app

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("data_files", "0020_remove_tribal_ssp_sections"),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER INDEX IF EXISTS public.reports_reportfile_pkey RENAME TO data_files_datafile_pkey;",
            "ALTER INDEX IF EXISTS public.data_files_datafile_pkey RENAME TO reports_reportfile_pkey;",
        ),
        migrations.AlterField(
            model_name="datafile",
            name="stt",
            field=models.ForeignKey(
                "stts.STT",
                on_delete=models.deletion.CASCADE,
                related_name="sttRef",
                db_index=False,
            ),
        ),
        migrations.AlterField(
            model_name="datafile",
            name="user",
            field=models.ForeignKey(
                "users.User",
                on_delete=models.deletion.CASCADE,
                related_name="user",
                db_index=False,
            ),
        ),
        migrations.AlterField(
            model_name="datafile",
            name="stt",
            field=models.ForeignKey(
                "stts.STT",
                on_delete=models.deletion.CASCADE,
                related_name="sttRef",
                db_index=True,
            ),
        ),
        migrations.AlterField(
            model_name="datafile",
            name="user",
            field=models.ForeignKey(
                "users.User",
                on_delete=models.deletion.CASCADE,
                related_name="user",
                db_index=True,
            ),
        ),
    ]
