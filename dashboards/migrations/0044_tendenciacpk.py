# Generated by Django 3.0.4 on 2022-03-08 00:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dashboards', '0043_llanta_compania'),
    ]

    operations = [
        migrations.CreateModel(
            name='TendenciaCPK',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.CharField(max_length=200)),
                ('vida', models.CharField(max_length=200)),
                ('calificacion', models.CharField(max_length=200)),
                ('compania', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dashboards.Compania')),
            ],
        ),
    ]
