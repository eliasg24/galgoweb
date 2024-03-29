# Generated by Django 4.0.3 on 2022-08-04 06:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0067_inspeccion_imagen'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tendencia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField()),
                ('clase', models.CharField(blank=True, max_length=255, null=True)),
                ('aplicacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.aplicacion')),
                ('compania', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.compania')),
                ('ubicacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dashboards.ubicacion')),
            ],
        ),
    ]
