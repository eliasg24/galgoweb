# Generated by Django 4.0.3 on 2022-04-17 04:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0085_remove_llanta_archivado_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inspeccion',
            name='max_profundidad',
        ),
        migrations.RemoveField(
            model_name='inspeccion',
            name='min_profundidad',
        ),
        migrations.RemoveField(
            model_name='inspeccion',
            name='observacion_1',
        ),
        migrations.RemoveField(
            model_name='inspeccion',
            name='observacion_2',
        ),
        migrations.RemoveField(
            model_name='inspeccion',
            name='observacion_3',
        ),
        migrations.RemoveField(
            model_name='inspeccion',
            name='tiempo_de_inspeccion',
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='evento',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='observaciones',
            field=models.ManyToManyField(blank=True, limit_choices_to={'nivel': 'Llanta'}, null=True, to='dashboards.observacion'),
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='presion_establecida',
            field=models.IntegerField(blank=True, default=100, null=True),
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='profundidad_central',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='profundidad_derecha',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='profundidad_izquierda',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='tipo_de_evento',
            field=models.CharField(default='Inspeccion', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='usuario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.perfil'),
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='vehiculo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.vehiculo'),
        ),
        migrations.AddField(
            model_name='inspeccion',
            name='vida',
            field=models.CharField(blank=True, choices=[('Nueva', 'Nueva'), ('1R', '1R'), ('2R', '2R'), ('3R', '3R'), ('4R', '4R'), ('5R', '5R')], default='Nueva', max_length=200, null=True),
        ),
    ]