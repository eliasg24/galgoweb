# Generated by Django 4.0.3 on 2022-08-29 03:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0093_rendimiento_posicion_rendimiento_tipo_de_eje_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tendencia',
            name='correctas_inspeccion',
        ),
        migrations.RemoveField(
            model_name='tendenciaaplicacion',
            name='correctas_inspeccion',
        ),
        migrations.RemoveField(
            model_name='tendenciacompania',
            name='correctas_inspeccion',
        ),
        migrations.RemoveField(
            model_name='tendenciaubicacion',
            name='correctas_inspeccion',
        ),
    ]
