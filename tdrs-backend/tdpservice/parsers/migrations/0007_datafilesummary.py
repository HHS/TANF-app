# Generated by Django 3.2.15 on 2023-09-20 15:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_files', '0012_datafile_s3_versioning_id'),
        ('parsers', '0006_auto_20230810_1500'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataFileSummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Accepted with Errors', 'Accepted With Errors'), ('Rejected', 'Rejected')], default='Pending', max_length=50)),
                ('case_aggregates', models.JSONField(null=True)),
                ('datafile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_files.datafile')),
            ],
        ),
    ]