# Generated by Django 4.0.3 on 2022-08-04 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0068_tendencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='tendencia',
            name='buena_presion',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tendencia',
            name='correctas_pulpo',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tendencia',
            name='health',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tendencia',
            name='inspecciones_a_tiempo',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
