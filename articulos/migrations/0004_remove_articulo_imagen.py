# Generated by Django 4.1.2 on 2022-11-19 17:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articulos', '0003_articulo_preciofinal'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='articulo',
            name='imagen',
        ),
    ]