# Generated by Django 3.2.15 on 2023-01-18 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0007_stt_ssp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stt',
            old_name='code',
            new_name='postal_code',
        ),
        migrations.RemoveField(
            model_name='stt',
            name='code_number',
        ),
    ]
