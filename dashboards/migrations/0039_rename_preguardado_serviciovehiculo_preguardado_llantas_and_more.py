# Generated by Django 4.0.3 on 2022-07-06 23:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0038_serviciovehiculo_estado_serviciovehiculo_preguardado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serviciovehiculo',
            old_name='preguardado',
            new_name='preguardado_llantas',
        ),
        migrations.AddField(
            model_name='serviciovehiculo',
            name='preguardado_vehiculo',
            field=models.CharField(blank=True, max_length=5000, null=True),
        ),
    ]
