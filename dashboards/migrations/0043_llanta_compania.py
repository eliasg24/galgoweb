# Generated by Django 3.0.4 on 2022-03-04 04:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0042_llanta_inventario'),
    ]

    operations = [
        migrations.AddField(
            model_name='llanta',
            name='compania',
            field=models.ForeignKey(default=6, on_delete=django.db.models.deletion.CASCADE, to='dashboards.Compania'),
        ),
    ]