from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reports", "0006_reportfile_downloaded_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="reportfile",
            name="notes",
            field=models.TextField(blank=True, default="", max_length=2000),
        ),
        migrations.AddField(
            model_name="reportsource",
            name="notes",
            field=models.TextField(blank=True, default="", max_length=2000),
        ),
    ]

