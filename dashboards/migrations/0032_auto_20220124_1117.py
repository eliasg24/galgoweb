# Generated by Django 3.2.9 on 2022-01-24 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0031_llanta_nombre_producto'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='costo_por_km',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='producto',
            name='kilometraje_proyectado',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]