# Generated by Django 4.0.3 on 2022-07-25 03:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0048_rename_link_bi_perfil_link_pulpo'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='link_operativo',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
