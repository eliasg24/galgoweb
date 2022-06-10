# Generated by Django 4.0.3 on 2022-05-23 00:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='perfil',
            name='taller',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.taller'),
        ),
        migrations.AlterField(
            model_name='perfil',
            name='compania',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.compania'),
        ),
    ]
