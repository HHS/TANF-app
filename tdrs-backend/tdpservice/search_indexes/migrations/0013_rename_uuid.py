# Generated by Django 3.2.15 on 2023-06-01 14:43

from django.db import migrations


model_names = [
    'tanf_t1',
    'tanf_t2',
    'tanf_t3',
    'tanf_t4',
    'tanf_t5',
    'tanf_t6',
    'tanf_t7',
    'ssp_m1',
    'ssp_m2',
    'ssp_m3',
]

operations = []
for model_name in model_names:
    operations.append(
        migrations.RenameField(
            model_name=model_name,
            old_name='uuid',
            new_name='id',
        ),
    )


class Migration(migrations.Migration):

    dependencies = [
        ('search_indexes', '0012_set_uuid_pk'),
    ]

    operations = operations
