# Generated by Django 4.1.2 on 2022-11-19 04:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('categorias', '0001_initial'),
        ('marcas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Articulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('precioCosto', models.FloatField()),
                ('tasaGanacia', models.FloatField()),
                ('stock', models.IntegerField()),
                ('detalle', models.CharField(max_length=255)),
                ('imagen', models.CharField(max_length=255)),
                ('categoria', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='categorias.categoria')),
                ('marca', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='marcas.marca')),
            ],
        ),
    ]
