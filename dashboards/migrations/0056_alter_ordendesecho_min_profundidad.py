# Generated by Django 4.0.3 on 2022-07-31 23:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0055_alter_bitacora_presion_establecida_1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordendesecho',
            name='min_profundidad',
            field=models.FloatField(blank=True, null=True),
        ),
    ]