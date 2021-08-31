from django.contrib.auth.models import Group
from django.db import migrations

def add_regional_staff(apps, schema_editor):
    regional_staff, _ = (
        apps.get_model('auth', 'Group')
            .objects
            .get_or_create(name='OFA Regional Staff')
    )

    # Clear existing permissions that may be set so we can ensure pristine state
    regional_staff.permissions.clear()
    regional_staff.permissions.add(
        *apps.get_model('auth', 'Permission').objects.all()
            .values_list('id', flat=True)
    )

def remove_regional_staff(apps, schema_editor):
    Group.objects.delete(name="OFA Regional Staff")


class Migration(migrations.Migration):
    dependencies = [
        ('users',"0020_ofa_system_admin_permissions")
    ]
    operations = [
        migrations.RunPython(add_regional_staff, remove_regional_staff)
    ]
