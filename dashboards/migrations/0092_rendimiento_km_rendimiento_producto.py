# Generated by Django 4.0.3 on 2022-08-29 02:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0091_bitacora_estado_llanta_1_bitacora_estado_llanta_10_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rendimiento',
            name='km',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rendimiento',
            name='producto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.producto'),
        ),
    ]
