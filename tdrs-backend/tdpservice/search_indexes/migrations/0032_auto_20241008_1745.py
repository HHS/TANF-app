# Generated by Django 3.2.15 on 2024-10-08 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0031_alter_tribal_tanf_t4_closure_reason'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reparsemeta',
            name='files_completed',
        ),
        migrations.RemoveField(
            model_name='reparsemeta',
            name='files_failed',
        ),
        migrations.RemoveField(
            model_name='reparsemeta',
            name='finished',
        ),
        migrations.RemoveField(
            model_name='reparsemeta',
            name='num_files_to_reparse',
        ),
        migrations.RemoveField(
            model_name='reparsemeta',
            name='num_records_created',
        ),
        migrations.RemoveField(
            model_name='reparsemeta',
            name='success',
        ),
    ]