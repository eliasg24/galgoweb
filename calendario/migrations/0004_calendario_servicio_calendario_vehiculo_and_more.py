# Generated by Django 4.0.3 on 2022-07-02 23:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0037_serviciovehiculo_fecha_final_and_more'),
        ('calendario', '0003_calendario_horario_end_calendario_horario_start'),
    ]

    operations = [
        migrations.AddField(
            model_name='calendario',
            name='servicio',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.serviciovehiculo'),
        ),
        migrations.AddField(
            model_name='calendario',
            name='vehiculo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.vehiculo'),
        ),
        migrations.AlterField(
            model_name='calendario',
            name='compania',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.compania'),
        ),
    ]
