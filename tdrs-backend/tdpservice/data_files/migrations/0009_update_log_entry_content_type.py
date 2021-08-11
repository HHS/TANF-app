from django.db import migrations, models
import tdpservice.data_files.models

def update_log_entry_content_type(apps, schema_editor):
    DataFile=apps.get_model("data_files","DataFile")
    LogEntry=apps.get_model("admin", "LogEntry")
    ContentType=apps.get_model("contenttypes", "ContentType")

    try:
        old_content_type=ContentType.objects.get(model="reportfile").pk
        new_content_type=ContentType.objects.get_for_model(DataFile).pk
        LogEntry.objects\
            .filter(content_type_id=old_content_type)\
            .update(content_type_id=new_content_type)
    except:
        print("running in a test system")

def revert_update_log_entry_content_type(apps, schema_editor):
    DataFile=apps.get_model("data_files","DataFile")
    LogEntry=apps.get_model("log_entry", "LogEntry")
    ContentType=apps.get_model("contenttypes", "ContentType")

    old_content_type=ContentType.objects.get(model="reportfile").pk
    new_content_type=ContentType.objects.get_for_model(DataFile).pk

    LogEntry.objects\
        .filter(content_type_id=new_content_type)\
        .update(content_type_id=old_content_type)


class Migration(migrations.Migration):

    dependencies = [
        ('data_files', '0008_alter_datafile_table'),
    ]

    operations = [
        migrations.RunPython(
            update_log_entry_content_type,
            revert_update_log_entry_content_type
        )
    ]
