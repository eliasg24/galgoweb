# Generated by Django 4.0.3 on 2022-08-01 02:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0057_alter_rendimiento_mes'),
    ]

    operations = [
        migrations.AddField(
            model_name='inspeccionvehiculo',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.perfil'),
        ),
    ]