# Generated by Django 4.0.3 on 2022-08-19 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0080_tendencia_correctas_inspeccion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviciovehiculo',
            name='hoja',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
