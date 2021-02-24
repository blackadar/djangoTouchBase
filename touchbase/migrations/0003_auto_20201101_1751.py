# Generated by Django 3.1.2 on 2020-11-01 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('touchbase', '0002_auto_20201101_1739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='missingwork',
            name='subject',
            field=models.IntegerField(choices=[(0, 'HOMEROOM'), (1, 'ELA'), (2, 'MATH'), (3, 'CIVICS'), (4, 'SCIENCE'), (5, 'ESL'), (6, 'NUMERACY')], null=True),
        ),
        migrations.AlterField(
            model_name='truancy',
            name='subject',
            field=models.IntegerField(choices=[(0, 'HOMEROOM'), (1, 'ELA'), (2, 'MATH'), (3, 'CIVICS'), (4, 'SCIENCE'), (5, 'ESL'), (6, 'NUMERACY')], null=True),
        ),
    ]
