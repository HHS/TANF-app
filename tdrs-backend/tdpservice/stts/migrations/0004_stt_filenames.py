# Generated by Django 3.2.13 on 2022-05-09 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0003_stt_code_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='stt',
            name='filenames',
            field=models.CharField(blank=True, max_length=512, null=True),
        ),
    ]