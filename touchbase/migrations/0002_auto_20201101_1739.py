# Generated by Django 3.1.2 on 2020-11-01 22:39

from django.db import migrations, models
import touchbase.utils


class Migration(migrations.Migration):

    dependencies = [
        ('touchbase', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='missingwork',
            name='subject',
            field=models.IntegerField(choices=[(0, 'HOMEROOM'), (1, 'ELA'), (2, 'MATH'), (3, 'CIVICS'), (4, 'SCIENCE'), (5, 'ESL'), (6, 'NUMERACY'), (7, 'HOMEROOM')], default=touchbase.utils.SubjectTypes['HOMEROOM']),
        ),
        migrations.AlterField(
            model_name='truancy',
            name='subject',
            field=models.IntegerField(choices=[(0, 'GENERAL'), (1, 'ELA'), (2, 'MATH'), (3, 'CIVICS'), (4, 'SCIENCE'), (5, 'ESL'), (6, 'NUMERACY'), (7, 'HOMEROOM')], null=True),
        ),
    ]
