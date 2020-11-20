from django.contrib.auth.models import Group
from django.db import migrations


def add_groups(apps, schema_editor):
    groups = [
        Group(name="OFA Admin"),
        Group(name="Data Prepper"),
        Group(name="OFA Analyst"),
    ]
    Group.objects.bulk_create(groups)


def remove_groups(apps, schema_editor):
    Group.objects.filter(name__in={"OFA Admin", "Data Prepper", "OFA Analyst"}).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0005_auto_20201022_1423"),
    ]

    operations = [
        migrations.RunPython(add_groups, remove_groups),
    ]
