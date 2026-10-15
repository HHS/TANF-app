"""Replace shadow classification strings with the canonical Section relation."""

from django.db import migrations, models
import django.db.models.deletion


def backfill_shadow_sections(apps, schema_editor) -> None:
    ShadowDataFile = apps.get_model("data_files", "ShadowDataFile")
    Section = apps.get_model("data_files", "Section")
    alias = schema_editor.connection.alias
    sections = {
        (code, name): section_id
        for section_id, code, name in Section.objects.using(alias).values_list(
            "id", "program__code", "name"
        )
    }
    files = ShadowDataFile.objects.using(alias)
    classifications = list(files.values_list("program_type", "section").distinct())
    unknown = [values for values in classifications if values not in sections]
    if unknown:
        raise RuntimeError(
            f"ShadowDataFile rows have unmapped classifications: {unknown}"
        )

    for code, name in classifications:
        files.filter(program_type=code, section=name).update(
            section_ref_id=sections[(code, name)]
        )


def restore_shadow_classifications(apps, schema_editor) -> None:
    ShadowDataFile = apps.get_model("data_files", "ShadowDataFile")
    Section = apps.get_model("data_files", "Section")
    alias = schema_editor.connection.alias
    for section in Section.objects.using(alias).select_related("program").iterator():
        ShadowDataFile.objects.using(alias).filter(section_ref_id=section.pk).update(
            section=section.name, program_type=section.program.code
        )


class Migration(migrations.Migration):
    dependencies = [
        ("data_files", "0037_merge_program_section_choices_and_parser_mode"),
    ]

    operations = [
        # Nullable legacy columns can be recreated before the reverse backfill.
        migrations.AlterField(
            model_name="shadowdatafile",
            name="program_type",
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name="shadowdatafile",
            name="section",
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AddField(
            model_name="shadowdatafile",
            name="section_ref",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_files.section",
            ),
        ),
        migrations.RunPython(backfill_shadow_sections, restore_shadow_classifications),
        migrations.RemoveField(model_name="shadowdatafile", name="program_type"),
        migrations.RemoveField(model_name="shadowdatafile", name="section"),
        migrations.RenameField(
            model_name="shadowdatafile", old_name="section_ref", new_name="section"
        ),
        migrations.AlterField(
            model_name="shadowdatafile",
            name="section",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="+",
                to="data_files.section",
            ),
        ),
    ]
