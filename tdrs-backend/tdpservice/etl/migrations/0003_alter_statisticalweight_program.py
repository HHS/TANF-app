from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("etl", "0002_etl_model_verbose_names"),
    ]

    operations = [
        migrations.AlterField(
            model_name="statisticalweight",
            name="program",
            field=models.CharField(max_length=16),
        ),
    ]
