from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_files', '0029_program_section'),
        ('stts', '0012_stt_timezone'),
    ]

    operations = [
        migrations.CreateModel(
            name='SttProgramParticipation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('FORMER', 'Former'), ('NEVER', 'Never')], max_length=10)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stt_participations', to='data_files.program')),
                ('sections', models.ManyToManyField(blank=True, related_name='participations', to='data_files.section')),
                ('stt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_participations', to='stts.stt')),
            ],
        ),
        migrations.AddConstraint(
            model_name='sttprogramparticipation',
            constraint=models.UniqueConstraint(fields=('stt', 'program'), name='participation_uniq_stt_program'),
        ),
    ]
