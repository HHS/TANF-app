import django.db.models.deletion
from django.db import migrations, models

def remove_federal_stt():
    STT=apps.get_model('stts','STT')
    User=apps.get_model('users','User')
    federal_stt=STT.objects.get(name='Federal Government')
    federal_stt_users=User.objects.filter(stt=federal_stt.id)

    for user in federal_stt_users:
        user.location_type = None
        user.location_id = None


class Migration(migrations.Migration):

    dependencies = [
        ('stts', '0002_auto_20200923_1809'),
    ]
    operations = [
        migrations.RunPython(remove_federal_stt)
    ]
