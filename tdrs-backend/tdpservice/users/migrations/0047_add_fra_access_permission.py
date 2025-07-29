from django.db import migrations

def set_fra_permissions(apps, _):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Get or create groups that need FRA access
    developer = Group.objects.get(name='Developer')
    ofa_admin = Group.objects.get(name='OFA Admin')
    ofa_regional_staff = Group.objects.get(name='OFA Regional Staff')
    ofa_system_admin = Group.objects.get(name='OFA System Admin')

    # Create Permission
    contentType = ContentType.objects.get(app_label='users', model='user')
    fra_permission, _ = Permission.objects.get_or_create(
        codename='has_fra_access',
        name='Can access FRA Data Files',
        content_type=contentType,
    )

    # add FRA permissions to other groups
    developer.permissions.add(fra_permission)
    ofa_admin.permissions.add(fra_permission)
    ofa_regional_staff.permissions.add(fra_permission)
    ofa_system_admin.permissions.add(fra_permission)

def unset_fra_permissions(apps, _):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Groups to remove fra from
    developer = Group.objects.get(name='Developer')
    ofa_admin = Group.objects.get(name='OFA Admin')
    ofa_regional_staff = Group.objects.get(name='OFA Regional Staff')
    ofa_system_admin = Group.objects.get(name='OFA System Admin')

    # Remove fra permissions from groups
    fra_access_permission = Permission.objects.get(codename='has_fra_access')
    developer.permissions.remove(fra_access_permission)
    ofa_admin.permissions.remove(fra_access_permission)
    ofa_regional_staff.permissions.remove(fra_access_permission)
    ofa_system_admin.permissions.remove(fra_access_permission)

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
        ('users', '0046_user_feedback'),
    ]

    operations = [
        migrations.RunPython(
            set_fra_permissions,
            reverse_code=unset_fra_permissions
        ),
    ]


