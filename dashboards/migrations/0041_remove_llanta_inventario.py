# Generated by Django 3.0.4 on 2022-02-27 03:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0040_llanta_inventario'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='llanta',
            name='inventario',
        ),
    ]