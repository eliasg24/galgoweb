# Generated by Django 4.0.3 on 2022-04-18 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0089_alter_llanta_compania'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inspeccion',
            name='evento',
            field=models.CharField(max_length=1000),
        ),
    ]
