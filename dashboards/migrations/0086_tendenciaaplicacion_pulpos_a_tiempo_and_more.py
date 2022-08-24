# Generated by Django 4.0.3 on 2022-08-22 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0085_tendencia_pulpos_a_tiempo'),
    ]

    operations = [
        migrations.AddField(
            model_name='tendenciaaplicacion',
            name='pulpos_a_tiempo',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tendenciacompania',
            name='pulpos_a_tiempo',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tendenciaubicacion',
            name='pulpos_a_tiempo',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]