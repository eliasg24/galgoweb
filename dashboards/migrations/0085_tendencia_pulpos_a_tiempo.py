# Generated by Django 4.0.3 on 2022-08-22 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0084_alter_vehiculo_configuracion'),
    ]

    operations = [
        migrations.AddField(
            model_name='tendencia',
            name='pulpos_a_tiempo',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]