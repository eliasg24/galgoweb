# Generated by Django 4.0.3 on 2022-08-29 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0092_rendimiento_km_rendimiento_producto'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendimiento',
            name='posicion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='rendimiento',
            name='tipo_de_eje',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='rendimiento',
            name='vida',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
