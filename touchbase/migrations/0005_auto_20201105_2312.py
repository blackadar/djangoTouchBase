# Generated by Django 3.1.3 on 2020-11-06 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('touchbase', '0004_auto_20201102_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='missingwork',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='truancy',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
    ]