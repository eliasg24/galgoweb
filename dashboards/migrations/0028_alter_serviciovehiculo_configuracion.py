# Generated by Django 4.0.3 on 2022-06-23 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0027_serviciovehiculo_serviciollanta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviciovehiculo',
            name='configuracion',
            field=models.CharField(max_length=5000),
        ),
    ]
