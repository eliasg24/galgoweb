# Generated by Django 4.0.3 on 2022-04-17 19:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0087_historicollanta_servicio_tareasservicio_tendencias_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='llanta',
            name='desecho',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dashboards.desecho'),
        ),
    ]
