# Generated by Django 4.0.3 on 2022-08-22 00:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calendario', '0007_rename_title_calendario_title_current'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendario',
            name='hoja',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
