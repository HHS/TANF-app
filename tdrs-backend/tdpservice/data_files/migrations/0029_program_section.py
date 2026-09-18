from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_files', '0028_alter_datafile_state_alter_shadowdatafile_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=32, unique=True)),
                ('slug', models.SlugField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='data_files.program')),
            ],
        ),
        migrations.AddConstraint(
            model_name='section',
            constraint=models.UniqueConstraint(fields=('program', 'name'), name='section_uniq_program_name'),
        ),
    ]
