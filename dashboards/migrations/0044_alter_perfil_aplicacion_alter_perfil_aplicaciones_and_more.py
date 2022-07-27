# Generated by Django 4.0.3 on 2022-07-22 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0043_alter_inspeccion_observaciones_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfil',
            name='aplicacion',
            field=models.ManyToManyField(blank=True, to='dashboards.aplicacion'),
        ),
        migrations.AlterField(
            model_name='perfil',
            name='aplicaciones',
            field=models.ManyToManyField(blank=True, related_name='aplicaciones', to='dashboards.aplicacion'),
        ),
        migrations.AlterField(
            model_name='perfil',
            name='companias',
            field=models.ManyToManyField(blank=True, related_name='companias', to='dashboards.compania'),
        ),
        migrations.AlterField(
            model_name='perfil',
            name='taller',
            field=models.ManyToManyField(blank=True, to='dashboards.taller'),
        ),
        migrations.AlterField(
            model_name='perfil',
            name='talleres',
            field=models.ManyToManyField(blank=True, related_name='talleres', to='dashboards.taller'),
        ),
        migrations.AlterField(
            model_name='perfil',
            name='ubicacion',
            field=models.ManyToManyField(blank=True, to='dashboards.ubicacion'),
        ),
        migrations.AlterField(
            model_name='perfil',
            name='ubicaciones',
            field=models.ManyToManyField(blank=True, related_name='ubicaciones', to='dashboards.ubicacion'),
        ),
    ]
